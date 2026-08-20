from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography

from app.core.database import Base
from app.models.enums import VerificationStatus


class ServiceProvider(Base):
    __tablename__ = "service_providers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    business_name = Column(String(180), nullable=False, index=True)
    description = Column(Text, nullable=False)
    experience = Column(Integer, nullable=False, default=0)
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, default="Madhya Pradesh")
    pincode = Column(String(12), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    location = Column(Geography(geometry_type="POINT", srid=4326, spatial_index=True))
    working_hours = Column(String(255), nullable=False, default="Mon-Sat, 9:00 AM - 6:00 PM")
    verification_status = Column(Enum(VerificationStatus), nullable=False, default=VerificationStatus.pending, index=True)
    verification_rejection_reason = Column(Text)
    is_verified = Column(Boolean, nullable=False, default=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    profile_views = Column(Integer, nullable=False, default=0)
    profile_image = Column(String(500))
    cover_image = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="provider_profile")
    services = relationship("ProviderService", back_populates="provider", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="provider", cascade="all, delete-orphan")
    documents = relationship("VerificationDocument", back_populates="provider", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_provider_city_district_active", "city", "district", "is_active"),
    )


class ServiceCategory(Base):
    __tablename__ = "service_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(120), unique=True, nullable=False, index=True)
    description = Column(Text)
    icon = Column(String(500))
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    providers = relationship("ProviderService", back_populates="category")


class ProviderService(Base):
    __tablename__ = "provider_services"

    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey("service_providers.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("service_categories.id", ondelete="RESTRICT"), nullable=False)

    provider = relationship("ServiceProvider", back_populates="services")
    category = relationship("ServiceCategory", back_populates="providers")

    __table_args__ = (UniqueConstraint("provider_id", "category_id", name="uq_provider_category"),)
