import numpy as np
from sklearn.ensemble import IsolationForest

# Initialize and pre-train the model with baseline data at module level
# In a real production environment, you would load a model trained on historical logs.
BASELINE_TRAIN_DATA = np.array([
    [1, 1], [1.2, 0.8], [0.9, 1.1], [1.5, 1.5], [2, 1],
    [0.5, 0.5], [1.1, 1.2], [1.3, 0.9], [1.8, 1.6], [2.1, 1.3],
    [1.1, 1.1], [1.4, 0.9], [0.8, 1.0], [1.6, 1.4], [1.9, 1.1],
    [0.6, 0.6], [1.2, 1.3], [1.4, 0.8], [1.7, 1.7], [2.2, 1.2]
])
MODEL = IsolationForest(contamination=0.1, random_state=42)
MODEL.fit(BASELINE_TRAIN_DATA)

def classify_spike(anomaly_data):
    """
    Classifies a traffic anomaly using a combination of heuristic thresholds
    and a pre-trained IsolationForest for outlier detection.
    """
    try:
        impact = float(anomaly_data.get('impact', 0))
        confidence = float(anomaly_data.get('confidence', 0))
    except (TypeError, ValueError):
        impact = 0
        confidence = 0

    # Heuristic classification
    status = "INFO"
    if impact >= 4 and confidence >= 4:
        status = "CRITICAL"
    elif impact >= 3:
        status = "WARNING"

    # Machine Learning Component:
    # Use the pre-trained IsolationForest to identify if this (impact, confidence)
    # pair is an outlier compared to the baseline fluctuations.
    try:
        # Predict the current anomaly
        X_test = np.array([[impact, confidence]])
        prediction = MODEL.predict(X_test)[0] # -1 for anomaly, 1 for normal

        ml_label = "Unusual Activity" if prediction == -1 else "Expected Activity"

        return f"{status}: {ml_label} (Imp: {impact}, Conf: {confidence})"
    except Exception:
        return f"{status}: Threshold Reached"

def detect_anomalies_timeseries(series):
    """
    Performs time-series anomaly detection on raw traffic data.
    """
    if len(series) < 10:
        return [False] * len(series)

    # For time-series, we still fit a temporary model as the baseline is the series itself
    clf = IsolationForest(contamination=0.1, random_state=42)
    series_reshaped = np.array(series).reshape(-1, 1)
    preds = clf.fit_predict(series_reshaped)
    return (preds == -1).tolist()
