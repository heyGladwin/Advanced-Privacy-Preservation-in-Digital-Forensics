from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    ForeignKey
)

from sqlalchemy.sql import func
from sqlalchemy import DateTime

from app.core.database import Base


class ForensicAnalysis(Base):

    __tablename__ = "forensic_analysis"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    evidence_id = Column(
        Integer,
        ForeignKey("evidence.id"),
        nullable=False
    )

    failed_logins = Column(
        Integer,
        nullable=False
    )

    file_access_count = Column(
        Integer,
        nullable=False
    )

    data_transfer_mb = Column(
        Float,
        nullable=False
    )

    unique_ips = Column(
        Integer,
        nullable=False
    )

    login_frequency = Column(
        Integer,
        nullable=False
    )

    execution_count = Column(
        Integer,
        nullable=False
    )

    anomaly_score = Column(
        Float,
        nullable=False
    )

    risk_level = Column(
        String(20),
        nullable=False
    )

    analyzed_at = Column(
        DateTime,
        server_default=func.now()
    )