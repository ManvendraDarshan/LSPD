from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import current_user, require_roles
from app.core.database import get_db
from app.models.enums import ReviewStatus, UserRole
from app.models.provider import ServiceProvider
from app.models.review import Review
from app.models.user import User
from app.schemas.common import Message
from app.schemas.review import ReviewCreate, ReviewModerate, ReviewRead

router = APIRouter(tags=["Reviews"])


@router.get("/providers/{provider_id}/reviews", response_model=list[ReviewRead])
def provider_reviews(provider_id: int, db: Session = Depends(get_db), include_hidden: bool = False):
    provider = db.get(ServiceProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    stmt = select(Review).options(joinedload(Review.customer)).where(Review.provider_id == provider_id)
    if not include_hidden:
        stmt = stmt.where(Review.status == ReviewStatus.published)
    return db.scalars(stmt.order_by(Review.created_at.desc())).all()


@router.post("/providers/{provider_id}/reviews", response_model=ReviewRead)
def create_review(provider_id: int, payload: ReviewCreate, user: User = Depends(require_roles(UserRole.customer)), db: Session = Depends(get_db)):
    if not db.get(ServiceProvider, provider_id):
        raise HTTPException(status_code=404, detail="Provider not found")
    existing = db.scalar(select(Review).where(Review.provider_id == provider_id, Review.customer_id == user.id))
    if existing:
        raise HTTPException(status_code=409, detail="You have already reviewed this provider")
    review = Review(provider_id=provider_id, customer_id=user.id, rating=payload.rating, comment=payload.comment.strip())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.put("/admin/reviews/{review_id}", response_model=ReviewRead)
def moderate_review(review_id: int, payload: ReviewModerate, _: User = Depends(require_roles(UserRole.admin)), db: Session = Depends(get_db)):
    review = db.scalar(select(Review).options(joinedload(Review.customer)).where(Review.id == review_id))
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    review.status = payload.status
    db.commit()
    db.refresh(review)
    return review


@router.delete("/reviews/{review_id}", response_model=Message)
def delete_review(review_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    review = db.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if user.role != UserRole.admin and review.customer_id != user.id:
        raise HTTPException(status_code=403, detail="Cannot delete this review")
    db.delete(review)
    db.commit()
    return Message(message="Review deleted")
