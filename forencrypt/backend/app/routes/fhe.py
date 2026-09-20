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


@router.post("/test")
def test_fhe(
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

    # Encrypt
    context, encrypted_features = encrypt_features(
        features
    )

    # Compute while encrypted
    encrypted_result = perform_encrypted_computation(
        encrypted_features
    )

    # Decrypt only the final result
    result = decrypt_result(
        encrypted_result
    )

    return {
        "message": "FHE computation completed",
        "input_features": features,
        "encrypted_computation": True,
        "result": result
    }