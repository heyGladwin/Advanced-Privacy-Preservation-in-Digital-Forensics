import os
import uuid
import shutil

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.evidence import Evidence
from app.models.user import User

from app.routes.auth import get_current_user

from app.schemas.evidence import EvidenceResponse

from app.services.hashing import calculate_sha256

router = APIRouter(
    prefix="/evidence",
    tags=["Evidence"]
)
UPLOAD_DIRECTORY = "uploads"

@router.post(
    "/upload",
    response_model=EvidenceResponse
)
async def upload_evidence(

    file: UploadFile = File(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)

):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )

    os.makedirs(
        UPLOAD_DIRECTORY,
        exist_ok=True
    )

    file_extension = os.path.splitext(
        file.filename
    )[1]

    unique_filename = (
        f"{uuid.uuid4()}"
        f"{file_extension}"
    )

    file_path = os.path.join(
        UPLOAD_DIRECTORY,
        unique_filename
    )

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    file_size = os.path.getsize(
        file_path
    )

    sha256_hash = calculate_sha256(
        file_path
    )

    evidence = Evidence(

        original_filename=file.filename,

        stored_filename=unique_filename,

        file_path=file_path,

        file_size=file_size,

        sha256_hash=sha256_hash,

        uploaded_by=current_user.id,

        status="ACTIVE"
    )

    db.add(evidence)

    db.commit()

    db.refresh(evidence)

    return evidence
