from datetime import datetime
from pydantic import BaseModel


class EvidenceResponse(BaseModel):
    id: int
    original_filename: str
    file_size: int
    sha256_hash: str
    status: str
    uploaded_at: datetime
    uploaded_by: int

    class Config:
        from_attributes = True