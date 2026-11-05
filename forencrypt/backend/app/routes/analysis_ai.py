from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.analysis_ai import ForensicAnalysis
from app.models.evidence import Evidence
from app.models.user import User
from app.routes.auth import get_current_user

from app.services.fhe import (
    encrypt_features,
    perform_encrypted_computation,
    decrypt_result
)

from app.services.forensic_ai import predict_anomaly


router = APIRouter(
    prefix="/analysis",
    tags=["AI Analysis"]
)


@router.post("/{evidence_id}")
def analyze_evidence(
    evidence_id: int,

    failed_logins: float,
    file_access_count: float,
    data_transfer_mb: float,
    unique_ips: float,
    login_frequency: float,
    execution_count: float,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # --------------------------------
    # 1. Check evidence
    # --------------------------------

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


    # --------------------------------
    # 2. Prepare forensic features
    # --------------------------------

    features = [
        failed_logins,
        file_access_count,
        data_transfer_mb,
        unique_ips,
        login_frequency,
        execution_count
    ]


    # --------------------------------
    # 3. Encrypt features using FHE
    # --------------------------------

    context, encrypted_features = (
        encrypt_features(features)
    )


    # --------------------------------
    # 4. Perform computation
    #    while encrypted
    # --------------------------------

    encrypted_processed = (
        perform_encrypted_computation(
            encrypted_features
        )
    )


    # --------------------------------
    # 5. Decrypt processed features
    # --------------------------------

    processed_features = decrypt_result(
        encrypted_processed
    )


    # --------------------------------
    # 6. Send processed data to AI
    # --------------------------------

    result = predict_anomaly(
        failed_logins=processed_features[0],
        file_access_count=processed_features[1],
        data_transfer_mb=processed_features[2],
        unique_ips=processed_features[3],
        login_frequency=processed_features[4],
        execution_count=processed_features[5]
    )


    # --------------------------------
    # 7. Store analysis
    # --------------------------------

    analysis = ForensicAnalysis(
        evidence_id=evidence_id,

        failed_logins=int(
            processed_features[0]
        ),

        file_access_count=int(
            processed_features[1]
        ),

        data_transfer_mb=float(
            processed_features[2]
        ),

        unique_ips=int(
            processed_features[3]
        ),

        login_frequency=int(
            processed_features[4]
        ),

        execution_count=int(
            processed_features[5]
        ),

        anomaly_score=result[
            "anomaly_score"
        ],

        risk_level=result[
            "risk_level"
        ]
    )


    db.add(analysis)
    db.commit()
    db.refresh(analysis)


    # --------------------------------
    # 8. Return result
    # --------------------------------

    return {
        "evidence_id": evidence_id,

        "fhe_enabled": True,

        "processed_features":
            processed_features,

        "prediction":
            result["prediction"],

        "anomaly_score":
            result["anomaly_score"],

        "risk_level":
            result["risk_level"]
    }