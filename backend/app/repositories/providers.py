from sqlalchemy import Integer, and_, func, or_, select
from sqlalchemy.orm import Session, joinedload
from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_SetSRID, ST_Distance

from app.models.enums import ReviewStatus
from app.models.provider import ProviderService, ServiceCategory, ServiceProvider
from app.models.review import Review


def rating_subquery():
    return (
        select(
            Review.provider_id.label("provider_id"),
            func.coalesce(func.avg(Review.rating), 0).label("average_rating"),
            func.count(Review.id).label("review_count"),
        )
        .where(Review.status == ReviewStatus.published)
        .group_by(Review.provider_id)
        .subquery()
    )


def provider_categories(provider: ServiceProvider) -> list[ServiceCategory]:
    return [service.category for service in provider.services if service.category]


def search_providers(
    db: Session,
    query: str | None,
    category_id: int | None,
    city: str | None,
    district: str | None,
    min_rating: float | None,
    lat: float | None,
    lng: float | None,
    radius_km: float | None,
    sort: str,
    page: int,
    page_size: int,
):
    ratings = rating_subquery()
    point = None
    distance = None
    stmt = (
        select(ServiceProvider, ratings.c.average_rating, ratings.c.review_count)
        .outerjoin(ratings, ratings.c.provider_id == ServiceProvider.id)
        .options(
            joinedload(ServiceProvider.user),
            joinedload(ServiceProvider.services).joinedload(ProviderService.category),
        )
        .where(ServiceProvider.is_active.is_(True))
    )

    if query:
        like = f"%{query.lower()}%"
        stmt = stmt.join(ServiceProvider.services, isouter=True).join(ProviderService.category, isouter=True)
        stmt = stmt.where(
            or_(
                func.lower(ServiceProvider.business_name).like(like),
                func.lower(ServiceProvider.description).like(like),
                func.lower(ServiceCategory.name).like(like),
            )
        )
    if category_id:
        stmt = stmt.where(ServiceProvider.services.any(ProviderService.category_id == category_id))
    if city:
        stmt = stmt.where(func.lower(ServiceProvider.city) == city.lower())
    if district:
        stmt = stmt.where(func.lower(ServiceProvider.district) == district.lower())
    if min_rating:
        stmt = stmt.where(func.coalesce(ratings.c.average_rating, 0) >= min_rating)
    if lat is not None and lng is not None and radius_km:
        point = func.Geography(ST_SetSRID(ST_MakePoint(lng, lat), 4326))
        stmt = stmt.where(and_(ServiceProvider.location.isnot(None), ST_DWithin(ServiceProvider.location, point, radius_km * 1000)))
        distance = ST_Distance(ServiceProvider.location, point)
        stmt = stmt.add_columns(distance.label("distance_m"))
    else:
        stmt = stmt.add_columns(func.null().label("distance_m"))

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))

    avg = func.coalesce(ratings.c.average_rating, 0)
    count = func.coalesce(ratings.c.review_count, 0)
    rank_score = (ServiceProvider.is_verified.cast(Integer) * 30) + (avg * 12) + (func.least(count, 30) * 1.5)

    if sort == "nearest" and distance is not None:
        stmt = stmt.order_by(distance.asc())
    elif sort == "highest_rated":
        stmt = stmt.order_by(avg.desc(), count.desc())
    elif sort == "most_reviewed":
        stmt = stmt.order_by(count.desc(), avg.desc())
    elif sort == "verified":
        stmt = stmt.order_by(ServiceProvider.is_verified.desc(), avg.desc())
    else:
        stmt = stmt.order_by(rank_score.desc(), ServiceProvider.is_verified.desc(), avg.desc())

    rows = db.execute(stmt.offset((page - 1) * page_size).limit(page_size)).unique().all()
    return rows, total
