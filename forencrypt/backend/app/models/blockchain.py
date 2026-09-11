from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime
)

from sqlalchemy.sql import func

from app.core.database import Base
class BlockchainBlock(Base):

    __tablename__ = "blockchain_blocks"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    block_index = Column(
        Integer,
        nullable=False,
        unique=True
    )

    evidence_id = Column(
        Integer,
        ForeignKey("evidence.id"),
        nullable=False
    )

    action = Column(
        String(100),
        nullable=False
    )

    performed_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    evidence_hash = Column(
        String(64),
        nullable=False
    )

    previous_hash = Column(
        String(64),
        nullable=False
    )

    block_hash = Column(
        String(64),
        nullable=False,
        unique=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )