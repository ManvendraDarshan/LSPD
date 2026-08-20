from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.enums import VerificationStatus


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider_id: int
    document_type: str
    status: VerificationStatus
    rejection_reason: str | None = None
    uploaded_at: datetime
    reviewed_at: datetime | None = None
    reviewed_by: int | None = None
