import numpy as np
from sklearn.ensemble import IsolationForest

def classify_spike(anomaly_data):
    """
    Classifies a traffic anomaly based on impact and confidence.
    """
    impact = anomaly_data.get('impact', 0)
    confidence = anomaly_data.get('confidence', 0)

    # Example logic: Impact and Confidence are typically on a scale (e.g. 1-5 or 0-100)
    # Cloudflare Radar anomalies have impact levels.
    if impact >= 4 and confidence >= 4:
        return "CRITICAL: High Confidence DDoS Spike"
    elif impact >= 3:
        return "WARNING: Probable Traffic Anomaly"
    else:
        return "INFO: Minor Traffic Fluctuaton"

# Example of how we might use IsolationForest if we had timeseries data
def detect_anomalies_timeseries(series):
    if len(series) < 10:
        return []

    clf = IsolationForest(contamination=0.1)
    series_reshaped = np.array(series).reshape(-1, 1)
    preds = clf.fit_predict(series_reshaped)
    return preds == -1 # True if anomaly
