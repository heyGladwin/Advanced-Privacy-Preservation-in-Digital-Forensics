from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.analysis_ai import ForensicAnalysis
from app.models.evidence import Evidence
from app.models.user import User

from app.routes.auth import get_current_user

from app.services.forensic import predict_anomaly


router = APIRouter(
    prefix="/analysis",
    tags=["AI Analysis"]
)


@router.post("/{evidence_id}")
def analyze_evidence(
    evidence_id: int,

    failed_logins: int,
    file_access_count: int,
    data_transfer_mb: float,
    unique_ips: int,
    login_frequency: int,
    execution_count: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    evidence = db.query(
        Evidence
    ).filter(
        Evidence.id == evidence_id
    ).first()

    if not evidence:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found"
        )

    result = predict_anomaly(
        failed_logins=failed_logins,
        file_access_count=file_access_count,
        data_transfer_mb=data_transfer_mb,
        unique_ips=unique_ips,
        login_frequency=login_frequency,
        execution_count=execution_count
    )

    analysis = ForensicAnalysis(
        evidence_id=evidence_id,

        failed_logins=failed_logins,
        file_access_count=file_access_count,
        data_transfer_mb=data_transfer_mb,
        unique_ips=unique_ips,
        login_frequency=login_frequency,
        execution_count=execution_count,

        anomaly_score=result["anomaly_score"],
        risk_level=result["risk_level"]
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {
        "evidence_id": evidence_id,
        "prediction": result["prediction"],
        "anomaly_score": result["anomaly_score"],
        "risk_level": result["risk_level"]
    }