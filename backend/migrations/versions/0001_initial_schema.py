"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-19
"""
from typing import Sequence, Union

from alembic import op
import geoalchemy2
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    role = sa.Enum("customer", "provider", "admin", name="userrole")
    verification = sa.Enum("pending", "under_review", "verified", "rejected", name="verificationstatus")
    review_status = sa.Enum("published", "hidden", "reported", name="reviewstatus")
    role.create(op.get_bind(), checkfirst=True)
    verification.create(op.get_bind(), checkfirst=True)
    review_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(24), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", role, nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column("profile_image", sa.String(500)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])

    op.create_table(
        "service_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("slug", sa.String(120), nullable=False, unique=True),
        sa.Column("description", sa.Text()),
        sa.Column("icon", sa.String(500)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_service_categories_slug", "service_categories", ["slug"])

    op.create_table(
        "service_providers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("business_name", sa.String(180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("experience", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("address", sa.String(500), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column("state", sa.String(100), nullable=False, server_default="Madhya Pradesh"),
        sa.Column("pincode", sa.String(12), nullable=False),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
        sa.Column("location", geoalchemy2.types.Geography(geometry_type="POINT", srid=4326, spatial_index=True)),
        sa.Column("working_hours", sa.String(255), nullable=False),
        sa.Column("verification_status", verification, nullable=False, server_default="pending"),
        sa.Column("verification_rejection_reason", sa.Text()),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("profile_views", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("profile_image", sa.String(500)),
        sa.Column("cover_image", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_provider_city_district_active", "service_providers", ["city", "district", "is_active"])
    op.create_index("ix_service_providers_verification_status", "service_providers", ["verification_status"])
    op.create_index("ix_service_providers_is_verified", "service_providers", ["is_verified"])

    op.create_table(
        "provider_services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider_id", sa.Integer(), sa.ForeignKey("service_providers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("service_categories.id", ondelete="RESTRICT"), nullable=False),
        sa.UniqueConstraint("provider_id", "category_id", name="uq_provider_category"),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider_id", sa.Integer(), sa.ForeignKey("service_providers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("status", review_status, nullable=False, server_default="published"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_range"),
        sa.UniqueConstraint("customer_id", "provider_id", name="uq_customer_provider_review"),
    )
    op.create_index("ix_reviews_provider_status", "reviews", ["provider_id", "status"])

    op.create_table(
        "verification_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider_id", sa.Integer(), sa.ForeignKey("service_providers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_type", sa.String(100), nullable=False),
        sa.Column("file_path", sa.String(700), nullable=False),
        sa.Column("status", verification, nullable=False, server_default="pending"),
        sa.Column("rejection_reason", sa.Text()),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("reviewed_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
    )


def downgrade() -> None:
    op.drop_table("verification_documents")
    op.drop_index("ix_reviews_provider_status", table_name="reviews")
    op.drop_table("reviews")
    op.drop_table("provider_services")
    op.drop_index("ix_service_providers_is_verified", table_name="service_providers")
    op.drop_index("ix_service_providers_verification_status", table_name="service_providers")
    op.drop_index("ix_provider_city_district_active", table_name="service_providers")
    op.drop_table("service_providers")
    op.drop_index("ix_service_categories_slug", table_name="service_categories")
    op.drop_table("service_categories")
    op.drop_index("ix_users_role", table_name="users")
    op.drop_index("ix_users_phone", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    sa.Enum(name="reviewstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="verificationstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="userrole").drop(op.get_bind(), checkfirst=True)
