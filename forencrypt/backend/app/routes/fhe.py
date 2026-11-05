from fastapi import APIRouter, Depends

from app.models.user import User
from app.routes.auth import get_current_user

from app.services.fhe import (
    encrypt_features,
    perform_encrypted_computation,
    decrypt_result
)

router = APIRouter(
    prefix="/fhe",
    tags=["FHE"]
)


@router.post("/analyze")
def fhe_analyze(
    failed_logins: float,
    file_access_count: float,
    data_transfer_mb: float,
    current_user: User = Depends(get_current_user)
):

    features = [
        failed_logins,
        file_access_count,
        data_transfer_mb
    ]

    # 1. Encrypt
    context, encrypted_features = encrypt_features(
        features
    )

    # 2. Compute while encrypted
    encrypted_processed = perform_encrypted_computation(
        encrypted_features
    )

    # 3. Decrypt processed values
    processed_features = decrypt_result(
        encrypted_processed
    )

    return {
        "encrypted_computation": True,
        "processed_features": processed_features
    }   