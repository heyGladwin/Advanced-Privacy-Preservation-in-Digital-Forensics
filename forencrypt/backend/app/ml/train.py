import numpy as np
import joblib

from sklearn.ensemble import IsolationForest


# Training data
# [failed_logins, file_access_count,
#  data_transfer_mb, unique_ips,
#  login_frequency, execution_count]

X = np.array([
    [1, 5, 50, 1, 3, 2],
    [2, 8, 80, 1, 4, 3],
    [1, 6, 60, 1, 3, 2],
    [3, 10, 100, 2, 5, 4],
    [2, 7, 70, 1, 4, 3],
    [1, 9, 90, 1, 5, 3],
    [2, 12, 120, 2, 6, 5],
    [3, 11, 110, 2, 5, 4],
    [1, 4, 40, 1, 2, 2],
    [2, 6, 65, 1, 3, 3],

    # Some unusual activity
    [25, 150, 5000, 15, 80, 100],
    [30, 200, 8000, 20, 100, 150]
])


model = IsolationForest(
    contamination=0.1,
    random_state=42
)

model.fit(X)


joblib.dump(
    model,
    "anomaly_model.pkl"
)

print("Anomaly detection model trained successfully.")  
print("Model trained successfully.")
print("Model saved successfully.")