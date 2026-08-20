from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.enums import UserRole
from app.models.provider import ProviderService, ServiceCategory
from app.schemas.common import Message
from app.schemas.provider import CategoryCreate, CategoryRead

router = APIRouter(tags=["Categories"])


def category_to_read(db: Session, category: ServiceCategory) -> CategoryRead:
    count = db.scalar(select(func.count(ProviderService.id)).where(ProviderService.category_id == category.id)) or 0
    return CategoryRead.model_validate(category, from_attributes=True).model_copy(update={"provider_count": count})


@router.get("/categories", response_model=list[CategoryRead])
def categories(db: Session = Depends(get_db), include_inactive: bool = False):
    stmt = select(ServiceCategory).order_by(ServiceCategory.name)
    if not include_inactive:
        stmt = stmt.where(ServiceCategory.is_active.is_(True))
    return [category_to_read(db, item) for item in db.scalars(stmt).all()]


@router.post("/admin/categories", response_model=CategoryRead, dependencies=[Depends(require_roles(UserRole.admin))])
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    category = ServiceCategory(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category_to_read(db, category)


@router.put("/admin/categories/{category_id}", response_model=CategoryRead, dependencies=[Depends(require_roles(UserRole.admin))])
def update_category(category_id: int, payload: CategoryCreate, db: Session = Depends(get_db)):
    category = db.get(ServiceCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in payload.model_dump().items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category_to_read(db, category)


@router.delete("/admin/categories/{category_id}", response_model=Message, dependencies=[Depends(require_roles(UserRole.admin))])
def deactivate_category(category_id: int, db: Session = Depends(get_db)):
    category = db.get(ServiceCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category.is_active = False
    db.commit()
    return Message(message="Category deactivated")
