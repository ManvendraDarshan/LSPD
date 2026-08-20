from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.enums import ReviewStatus, UserRole, VerificationStatus
from app.models.provider import ProviderService, ServiceCategory, ServiceProvider
from app.models.review import Review
from app.models.user import User
from app.schemas.provider import ProviderRead
from app.schemas.review import ReviewRead
from app.schemas.user import UserRead
from app.services.provider_service import to_provider_read

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_roles(UserRole.admin))])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    total_users = db.scalar(select(func.count(User.id))) or 0
    total_providers = db.scalar(select(func.count(ServiceProvider.id))) or 0
    verified = db.scalar(select(func.count(ServiceProvider.id)).where(ServiceProvider.is_verified.is_(True))) or 0
    pending = db.scalar(select(func.count(ServiceProvider.id)).where(ServiceProvider.verification_status.in_([VerificationStatus.pending, VerificationStatus.under_review]))) or 0
    reviews = db.scalar(select(func.count(Review.id))) or 0
    avg_rating = db.scalar(select(func.coalesce(func.avg(Review.rating), 0)).where(Review.status == ReviewStatus.published)) or 0
    categories = db.scalar(select(func.count(ServiceCategory.id)).where(ServiceCategory.is_active.is_(True))) or 0
    recent_users = db.scalars(select(User).order_by(User.created_at.desc()).limit(8)).all()
    return {
        "total_users": total_users,
        "total_providers": total_providers,
        "verified_providers": verified,
        "pending_providers": pending,
        "total_reviews": reviews,
        "average_platform_rating": round(float(avg_rating), 2),
        "total_service_categories": categories,
        "recent_registrations": [UserRead.model_validate(user, from_attributes=True) for user in recent_users],
    }


@router.get("/providers", response_model=list[ProviderRead])
def admin_providers(status: VerificationStatus | None = None, q: str | None = None, db: Session = Depends(get_db)):
    stmt = select(ServiceProvider).options(joinedload(ServiceProvider.user), joinedload(ServiceProvider.services).joinedload(ProviderService.category))
    if status:
        stmt = stmt.where(ServiceProvider.verification_status == status)
    if q:
        stmt = stmt.where(func.lower(ServiceProvider.business_name).like(f"%{q.lower()}%"))
    return [to_provider_read(db, provider) for provider in db.scalars(stmt.order_by(ServiceProvider.created_at.desc())).unique().all()]


@router.get("/customers", response_model=list[UserRead])
def customers(db: Session = Depends(get_db)):
    return db.scalars(select(User).where(User.role == UserRole.customer).order_by(User.created_at.desc())).all()


@router.get("/reviews", response_model=list[ReviewRead])
def reviews(status: ReviewStatus | None = None, db: Session = Depends(get_db)):
    stmt = select(Review).options(joinedload(Review.customer)).order_by(Review.created_at.desc())
    if status:
        stmt = stmt.where(Review.status == status)
    return db.scalars(stmt).all()
