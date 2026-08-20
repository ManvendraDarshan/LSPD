from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ReviewStatus
from app.schemas.user import UserRead


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=5, max_length=2000)


class ReviewModerate(BaseModel):
    status: ReviewStatus


class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer: UserRead
    provider_id: int
    rating: int
    comment: str
    status: ReviewStatus
    created_at: datetime
