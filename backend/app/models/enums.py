import enum


class UserRole(str, enum.Enum):
    customer = "customer"
    provider = "provider"
    admin = "admin"


class VerificationStatus(str, enum.Enum):
    pending = "pending"
    under_review = "under_review"
    verified = "verified"
    rejected = "rejected"


class ReviewStatus(str, enum.Enum):
    published = "published"
    hidden = "hidden"
    reported = "reported"
