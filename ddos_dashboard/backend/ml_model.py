import numpy as np
from sklearn.ensemble import IsolationForest
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnomalyDetector:
    def __init__(self, contamination=0.1):
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.is_trained = False

    def train(self, data):
        """
        Trains the model on historical timeseries data.
        data: List of float values (e.g., attack volume).
        """
        if not data or len(data) < 10:
            logger.warning("Not enough data to train AnomalyDetector.")
            return

        try:
            X = np.array(data).reshape(-1, 1)
            self.model.fit(X)
            self.is_trained = True
            logger.info(f"AnomalyDetector trained on {len(X)} data points.")
        except Exception as e:
            logger.error(f"Error training AnomalyDetector: {e}")

    def is_anomaly(self, value):
        """
        Checks if a single value is an anomaly based on the trained model.
        Returns True if anomaly, False otherwise.
        """
        if not self.is_trained:
            return False

        try:
            X = np.array([[value]])
            prediction = self.model.predict(X)[0]
            return prediction == -1
        except Exception:
            return False

# Global instances for Layer 3 and Layer 7 attacks
l3_detector = AnomalyDetector(contamination=0.05)
l7_detector = AnomalyDetector(contamination=0.05)

def classify_anomaly(value, detector_type="l7"):
    """
    Classifies a value as an anomaly or not using the specified detector.
    """
    detector = l7_detector if detector_type == "l7" else l3_detector

    if detector.is_anomaly(value):
        return "CRITICAL: High-Confidence Attack Spike"
    return "Normal Activity"

def detect_anomalies_in_series(series):
    """
    Batch detect anomalies in a series.
    """
    if len(series) < 10:
        return [False] * len(series)

    clf = IsolationForest(contamination=0.05, random_state=42)
    X = np.array(series).reshape(-1, 1)
    preds = clf.fit_predict(X)
    return (preds == -1).tolist()
