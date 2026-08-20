from fastapi import APIRouter, Depends, HTTPException, Query
import re

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import current_user, require_roles
from app.core.database import get_db
from app.models.enums import UserRole, VerificationStatus
from app.models.provider import ProviderService, ServiceCategory, ServiceProvider
from app.models.user import User
from app.repositories.providers import search_providers
from app.schemas.common import Message, Page
from app.schemas.provider import ProviderCreate, ProviderList, ProviderRead, ProviderUpdate
from app.services.provider_service import make_location, sync_provider_categories, to_provider_read

router = APIRouter(tags=["Providers"])


@router.get("/providers", response_model=ProviderList)
@router.get("/search/providers", response_model=ProviderList)
def list_providers(
    q: str | None = None,
    category_id: int | None = None,
    city: str | None = None,
    district: str | None = None,
    min_rating: float | None = Query(default=None, ge=1, le=5),
    lat: float | None = Query(default=None, ge=-90, le=90),
    lng: float | None = Query(default=None, ge=-180, le=180),
    radius_km: float | None = Query(default=None, ge=1, le=100),
    sort: str = "recommended",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    rows, total = search_providers(db, q, category_id, city, district, min_rating, lat, lng, radius_km, sort, page, page_size)
    items = [to_provider_read(db, row[0], row[3] if len(row) > 3 else None) for row in rows]
    return ProviderList(items=items, page=Page(total=total, page=page, page_size=page_size))


@router.get("/search/nearby", response_model=ProviderList)
def nearby(lat: float, lng: float, radius_km: float = 10, db: Session = Depends(get_db)):
    rows, total = search_providers(db, None, None, None, None, None, lat, lng, radius_km, "nearest", 1, 30)
    return ProviderList(items=[to_provider_read(db, row[0], row[3] if len(row) > 3 else None) for row in rows], page=Page(total=total, page=1, page_size=30))


@router.get("/providers/me/profile", response_model=ProviderRead)
def my_provider_profile(user: User = Depends(require_roles(UserRole.provider)), db: Session = Depends(get_db)):
    provider = db.scalar(
        select(ServiceProvider)
        .options(joinedload(ServiceProvider.user), joinedload(ServiceProvider.services).joinedload(ProviderService.category))
        .where(ServiceProvider.user_id == user.id)
    )
    if not provider:
        raise HTTPException(status_code=404, detail="Provider profile not found")
    return to_provider_read(db, provider)


@router.get("/providers/{provider_id}", response_model=ProviderRead)
def provider_detail(provider_id: int, db: Session = Depends(get_db)):
    provider = db.scalar(
        select(ServiceProvider)
        .options(joinedload(ServiceProvider.user), joinedload(ServiceProvider.services).joinedload(ProviderService.category))
        .where(ServiceProvider.id == provider_id, ServiceProvider.is_active.is_(True))
    )
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    provider.profile_views += 1
    db.commit()
    return to_provider_read(db, provider)


@router.post("/providers", response_model=ProviderRead)
def create_provider(payload: ProviderCreate, user: User = Depends(require_roles(UserRole.provider)), db: Session = Depends(get_db)):
    if user.provider_profile:
        raise HTTPException(status_code=409, detail="Provider profile already exists")
    category_ids = payload.category_ids or []
    if payload.category_name is not None:
        category_name = payload.category_name.strip()
        if len(category_name) < 2:
            raise HTTPException(status_code=422, detail="A valid service category is required")
        category = db.scalar(select(ServiceCategory).where(func.lower(ServiceCategory.name) == category_name.lower()))
        if not category:
            slug = re.sub(r"[^a-z0-9]+", "-", category_name.lower()).strip("-") or "service"
            slug_base = slug
            suffix = 2
            while db.scalar(select(ServiceCategory.id).where(ServiceCategory.slug == slug)):
                slug = f"{slug_base}-{suffix}"
                suffix += 1
            category = ServiceCategory(
                name=category_name,
                slug=slug,
                description=f"Local {category_name.lower()} professionals",
            )
            db.add(category)
            db.flush()
        elif not category.is_active:
            category.is_active = True
        category_ids = [category.id]
    if not category_ids:
        raise HTTPException(status_code=422, detail="A service category is required")
    provider = ServiceProvider(
        user_id=user.id,
        business_name=payload.business_name,
        description=payload.description,
        experience=payload.experience,
        address=payload.address,
        city=payload.city,
        district=payload.district,
        state=payload.state,
        pincode=payload.pincode,
        latitude=payload.latitude,
        longitude=payload.longitude,
        location=make_location(payload.longitude, payload.latitude),
        working_hours=payload.working_hours,
        profile_image=payload.profile_image,
        cover_image=payload.cover_image,
    )
    db.add(provider)
    db.flush()
    sync_provider_categories(db, provider, category_ids)
    db.commit()
    db.refresh(provider)
    return to_provider_read(db, provider)


@router.put("/providers/{provider_id}", response_model=ProviderRead)
def update_provider(provider_id: int, payload: ProviderUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    provider = db.get(ServiceProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    if user.role != UserRole.admin and provider.user_id != user.id:
        raise HTTPException(status_code=403, detail="Cannot edit this provider")
    data = payload.model_dump(exclude_unset=True)
    category_ids = data.pop("category_ids", None)
    for key, value in data.items():
        setattr(provider, key, value)
    if "latitude" in data or "longitude" in data:
        if provider.latitude is not None and provider.longitude is not None:
            provider.location = make_location(provider.longitude, provider.latitude)
    if category_ids is not None:
        sync_provider_categories(db, provider, category_ids)
    db.commit()
    db.refresh(provider)
    return to_provider_read(db, provider)


@router.delete("/providers/{provider_id}", response_model=Message)
def delete_provider(provider_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    provider = db.get(ServiceProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    if user.role != UserRole.admin and provider.user_id != user.id:
        raise HTTPException(status_code=403, detail="Cannot delete this provider")
    provider.is_active = False
    db.commit()
    return Message(message="Provider deactivated")


@router.put("/admin/providers/{provider_id}/approve", response_model=ProviderRead, dependencies=[Depends(require_roles(UserRole.admin))])
@router.put("/admin/providers/{provider_id}/verify", response_model=ProviderRead, dependencies=[Depends(require_roles(UserRole.admin))])
def approve_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = db.get(ServiceProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    provider.verification_status = VerificationStatus.verified
    provider.is_verified = True
    provider.verification_rejection_reason = None
    db.commit()
    db.refresh(provider)
    return to_provider_read(db, provider)


@router.put("/admin/providers/{provider_id}/reject", response_model=ProviderRead, dependencies=[Depends(require_roles(UserRole.admin))])
def reject_provider(provider_id: int, reason: str = "Documents did not meet verification requirements", db: Session = Depends(get_db)):
    provider = db.get(ServiceProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    provider.verification_status = VerificationStatus.rejected
    provider.is_verified = False
    provider.verification_rejection_reason = reason
    db.commit()
    db.refresh(provider)
    return to_provider_read(db, provider)


@router.put("/admin/providers/{provider_id}/revoke-verification", response_model=ProviderRead, dependencies=[Depends(require_roles(UserRole.admin))])
def revoke_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = db.get(ServiceProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    provider.is_verified = False
    provider.verification_status = VerificationStatus.under_review
    db.commit()
    db.refresh(provider)
    return to_provider_read(db, provider)
