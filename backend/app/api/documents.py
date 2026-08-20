from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_roles
from app.core.config import get_settings
from app.core.database import get_db
from app.models.document import VerificationDocument
from app.models.enums import UserRole, VerificationStatus
from app.models.provider import ServiceProvider
from app.models.user import User
from app.schemas.document import DocumentRead

router = APIRouter(tags=["Verification Documents"])

ALLOWED_TYPES = {"application/pdf", "image/jpeg", "image/png", "image/webp"}


@router.post("/providers/{provider_id}/documents", response_model=DocumentRead)
async def upload_document(
    provider_id: int,
    document_type: str,
    file: UploadFile = File(...),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    provider = db.get(ServiceProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    if user.role != UserRole.admin and provider.user_id != user.id:
        raise HTTPException(status_code=403, detail="Cannot upload documents for this provider")
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    data = await file.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File is too large")
    ext = Path(file.filename or "").suffix.lower()
    folder = settings.upload_path / "private" / "verification" / str(provider_id)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{uuid4().hex}{ext}"
    path.write_bytes(data)
    doc = VerificationDocument(provider_id=provider_id, document_type=document_type, file_path=str(path), status=VerificationStatus.under_review)
    provider.verification_status = VerificationStatus.under_review
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/admin/providers/{provider_id}/documents", response_model=list[DocumentRead])
def provider_documents(provider_id: int, _: User = Depends(require_roles(UserRole.admin)), db: Session = Depends(get_db)):
    return db.scalars(select(VerificationDocument).where(VerificationDocument.provider_id == provider_id)).all()
