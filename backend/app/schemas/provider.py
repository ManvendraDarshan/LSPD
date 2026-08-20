from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import VerificationStatus
from app.schemas.common import Page
from app.schemas.user import UserRead


class CategoryBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=120)
    description: str | None = None
    icon: str | None = None
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    provider_count: int = 0


class ProviderCreate(BaseModel):
    business_name: str = Field(min_length=2, max_length=180)
    description: str = Field(min_length=20)
    experience: int = Field(ge=0, le=80)
    address: str = Field(min_length=5, max_length=500)
    city: str
    district: str
    state: str = "Madhya Pradesh"
    pincode: str = Field(min_length=5, max_length=12)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    working_hours: str = "Mon-Sat, 9:00 AM - 6:00 PM"
    category_ids: list[int] | None = Field(default=None, min_length=1)
    category_name: str | None = Field(default=None, min_length=2, max_length=100)
    profile_image: str | None = None
    cover_image: str | None = None


class ProviderUpdate(BaseModel):
    business_name: str | None = None
    description: str | None = None
    experience: int | None = Field(default=None, ge=0, le=80)
    address: str | None = None
    city: str | None = None
    district: str | None = None
    state: str | None = None
    pincode: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    working_hours: str | None = None
    category_ids: list[int] | None = None
    profile_image: str | None = None
    cover_image: str | None = None


class ProviderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user: UserRead
    business_name: str
    description: str
    experience: int
    address: str
    city: str
    district: str
    state: str
    pincode: str
    latitude: float | None
    longitude: float | None
    working_hours: str
    verification_status: VerificationStatus
    verification_rejection_reason: str | None = None
    is_verified: bool
    is_active: bool
    profile_views: int
    profile_image: str | None = None
    cover_image: str | None = None
    categories: list[CategoryRead] = []
    average_rating: float = 0
    review_count: int = 0
    distance_km: float | None = None
    rank_score: float | None = None
    created_at: datetime

class ProviderList(BaseModel):
    items: list[ProviderRead]
    page: Page
