import os
import joblib
import numpy as np


MODEL_PATH = "app/ml/anomaly_model.pkl"

model = None


def load_model():
    global model

    if model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "Anomaly detection model not found"
            )

        model = joblib.load(MODEL_PATH)

    return model


def predict_anomaly(
    failed_logins: int,
    file_access_count: int,
    data_transfer_mb: float,
    unique_ips: int,
    login_frequency: int,
    execution_count: int
):

    model = load_model()

    features = np.array([[
        failed_logins,
        file_access_count,
        data_transfer_mb,
        unique_ips,
        login_frequency,
        execution_count
    ]])

    prediction = model.predict(features)[0]

    score = model.decision_function(features)[0]

    if prediction == -1:
        risk_level = "HIGH"
    elif score < 0.1:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "prediction": int(prediction),
        "anomaly_score": float(score),
        "risk_level": risk_level
    }