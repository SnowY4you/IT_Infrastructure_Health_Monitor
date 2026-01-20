import numpy as np
import psutil

############################################
#         Machin Learning Engine           #
############################################

# Check Anomaly
def check_anomaly_alert(metric_history, current_value, std_multiplier=3, min_threshold=15):
    """
    Smarter Anomaly detection.
    min_threshold: Ignore anomalies if the value is below this (e.g., 15% CPU).
    """
    if len(metric_history) < 20: return "COLLECTING"

    mean = np.mean(metric_history)
    std_dev = np.std(metric_history)

    # If the system is TOO stable, std_dev might be 0.1.
    # We cap it so it doesn't become over-sensitive.
    effective_std = max(std_dev, 2.0)

    upper_limit = mean + (std_multiplier * effective_std)

    # Logic: It must be statistically an anomaly AND above a practical floor.
    if current_value > upper_limit and current_value > min_threshold:
        return "ANOMALY_DETECTED"
    return "NORMAL"

# Anomaly Detection
def detect_anomaly(current_val, historical_data, deviations=3):
    """
    Standard Deviation-based Anomaly Detection.
    Triggers if current value is > (Mean + 3*StdDev).
    """
    if len(historical_data) < 10: return False  # Need data to predict

    mean = np.mean(historical_data)
    std_dev = np.std(historical_data)

    upper_bound = mean + (deviations * std_dev)
    return current_val > upper_bound


# Anomaly Alert
class AlertEngine:
    def __init__(self, warning_threshold, alert_threshold):
        self.history = []
        self.warn = warning_threshold
        self.crit = alert_threshold

    def check_anomaly(self, new_value):
        """Calculates if the new value is an anomaly based on 3 standard deviations"""
        if len(self.history) < 30:  # Need at least 30 data points
            self.history.append(new_value)
            return "COLLECTING_DATA"

        mean = np.mean(self.history)
        std = np.std(self.history)

        # Anomaly = Current value is 3 deviations away from Mean
        if new_value > (mean + (3 * std)):
            return "CRITICAL_ANOMALY"

        self.history.append(new_value)
        return "NORMAL"
