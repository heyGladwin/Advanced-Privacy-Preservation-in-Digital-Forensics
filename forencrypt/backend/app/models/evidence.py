from sqlalchemy import (
    Column,
    Integer,
    String,
    BigInteger,
    ForeignKey,
    Enum,
    DateTime
)
from sqlalchemy.sql import func
from app.core.database import Base

class Evidence(Base):

    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)

    original_filename = Column(
        String(255),
        nullable=False
    )

    stored_filename = Column(
        String(255),
        nullable=False,
        unique=True
    )

    file_path = Column(
        String(500),
        nullable=False
    )

    file_size = Column(
        BigInteger,
        nullable=False
    )

    sha256_hash = Column(
        String(64),
        nullable=False,
        index=True
    )

    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    status = Column(
        Enum(
            "ACTIVE",
            "COMPROMISED",
            name="evidence_status"
        ),
        default="ACTIVE"
    )

    uploaded_at = Column(
        DateTime,
        server_default=func.now()
    )