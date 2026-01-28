import numpy as np
from sklearn.ensemble import IsolationForest

def classify_spike(anomaly_data):
    """
    Classifies a traffic anomaly using a combination of heuristic thresholds
    and a pre-trained (simulated) IsolationForest for anomaly detection.
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
    # Use IsolationForest to identify if this (impact, confidence) pair is an outlier
    # compared to a set of normal background fluctuations.
    try:
        # Mock historical data for normal variations
        # In a real app, this would be loaded from a serialized model trained on real logs
        X_train = np.array([
            [1, 1], [1.2, 0.8], [0.9, 1.1], [1.5, 1.5], [2, 1],
            [0.5, 0.5], [1.1, 1.2], [1.3, 0.9], [1.8, 1.6], [2.1, 1.3]
        ])
        clf = IsolationForest(contamination=0.1, random_state=42)
        clf.fit(X_train)

        # Predict the current anomaly
        X_test = np.array([[impact, confidence]])
        prediction = clf.predict(X_test)[0] # -1 for anomaly, 1 for normal

        ml_label = "Unusual Activity" if prediction == -1 else "Expected Activity"

        return f"{status}: {ml_label} (Imp: {impact}, Conf: {confidence})"
    except Exception:
        return f"{status}: Threshold Reached"

def detect_anomalies_timeseries(series):
    """
    Performs time-series anomaly detection on raw traffic data.
    """
    if len(series) < 10:
        return []

    clf = IsolationForest(contamination=0.1)
    series_reshaped = np.array(series).reshape(-1, 1)
    preds = clf.fit_predict(series_reshaped)
    return preds == -1 # True if anomaly
