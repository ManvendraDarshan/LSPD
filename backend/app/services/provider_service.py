from sqlalchemy import func, select
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_MakePoint, ST_SetSRID

from app.models.enums import ReviewStatus, VerificationStatus
from app.models.provider import ProviderService, ServiceCategory, ServiceProvider
from app.models.review import Review
from app.schemas.provider import CategoryRead, ProviderRead


def make_location(longitude: float, latitude: float):
    return func.Geography(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326))


def provider_stats(db: Session, provider_id: int) -> tuple[float, int]:
    avg, count = db.execute(
        select(func.coalesce(func.avg(Review.rating), 0), func.count(Review.id)).where(
            Review.provider_id == provider_id,
            Review.status == ReviewStatus.published,
        )
    ).one()
    return round(float(avg or 0), 1), int(count or 0)


def to_provider_read(db: Session, provider: ServiceProvider, distance_m: float | None = None, rank_score: float | None = None) -> ProviderRead:
    avg, count = provider_stats(db, provider.id)
    categories = [
        CategoryRead(
            id=item.category.id,
            name=item.category.name,
            slug=item.category.slug,
            description=item.category.description,
            icon=item.category.icon,
            is_active=item.category.is_active,
            created_at=item.category.created_at,
            provider_count=0,
        )
        for item in provider.services
        if item.category
    ]
    return ProviderRead(
        id=provider.id,
        user=provider.user,
        business_name=provider.business_name,
        description=provider.description,
        experience=provider.experience,
        address=provider.address,
        city=provider.city,
        district=provider.district,
        state=provider.state,
        pincode=provider.pincode,
        latitude=provider.latitude,
        longitude=provider.longitude,
        working_hours=provider.working_hours,
        verification_status=provider.verification_status,
        verification_rejection_reason=provider.verification_rejection_reason,
        is_verified=provider.is_verified,
        is_active=provider.is_active,
        profile_views=provider.profile_views,
        profile_image=provider.profile_image,
        cover_image=provider.cover_image,
        categories=categories,
        average_rating=avg,
        review_count=count,
        distance_km=round(distance_m / 1000, 2) if distance_m is not None else None,
        rank_score=round(rank_score, 2) if rank_score is not None else None,
        created_at=provider.created_at,
    )


def sync_provider_categories(db: Session, provider: ServiceProvider, category_ids: list[int]) -> None:
    categories = db.scalars(
        select(ServiceCategory).where(ServiceCategory.id.in_(category_ids), ServiceCategory.is_active.is_(True))
    ).all()
    provider.services.clear()
    provider.services.extend([ProviderService(category=category) for category in categories])


def set_provider_verified(provider: ServiceProvider, verified: bool, reason: str | None = None) -> None:
    provider.is_verified = verified
    provider.verification_status = VerificationStatus.verified if verified else VerificationStatus.rejected
    provider.verification_rejection_reason = reason
