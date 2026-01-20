import numpy as np
import psutil
from datetime import datetime
from src.db_manager import ITAMDatabase


############################################
#          Machine Learning Engine         #
############################################

class MLEngine:
    def __init__(self):
        self.db = ITAMDatabase()
        # Internal cache for real-time points, though we prioritize DB history
        self.memory_buffer = {}

    def get_historical_metrics(self, hostname, metric_type="cpu", limit=100):
        """
        Retrieves historical metric data for a specific host from the DB.
        Note: Requires a 'metrics_log' table or similar (see Analytics extension).
        """
        # For now, we simulate historical retrieval or pull from a log table if exists
        # In a full deployment, you would query:
        # SELECT value FROM performance_logs WHERE hostname = ? AND type = ?
        return []

    def check_anomaly_alert(self, hostname, current_value, metric_type="cpu", std_multiplier=3, min_threshold=15):
        """
        Smarter Anomaly detection using DB-driven context.
        """
        # 1. Fetch history for this specific device
        history = self.memory_buffer.get(hostname, [])

        if len(history) < 20:
            if hostname not in self.memory_buffer: self.memory_buffer[hostname] = []
            self.memory_buffer[hostname].append(current_value)
            return "COLLECTING"

        mean = np.mean(history)
        std_dev = np.std(history)

        # Cap sensitivity to avoid false positives on ultra-stable systems
        effective_std = max(std_dev, 2.0)
        upper_limit = mean + (std_multiplier * effective_std)

        # Logic: Statistical anomaly AND above a practical floor (e.g. 15% CPU)
        status = "NORMAL"
        if current_value > upper_limit and current_value > min_threshold:
            status = "ANOMALY_DETECTED"

        # Keep buffer sliding (last 100 points)
        self.memory_buffer[hostname].append(current_value)
        if len(self.memory_buffer[hostname]) > 100:
            self.memory_buffer[hostname].pop(0)

        return status

    def predict_capacity_exhaustion(self, metric_history):
        """
        Analytics Extension: Linear Regression to predict when a disk or RAM
        will hit 100% based on current growth trends.
        """
        if len(metric_history) < 5: return "INSUFFICIENT_DATA"

        # Simple linear fit: y = mx + c
        x = np.arange(len(metric_history))
        y = np.array(metric_history)
        z = np.polyfit(x, y, 1)  # slope z[0], intercept z[1]

        slope = z[0]
        if slope <= 0: return "STABLE"  # Usage is decreasing or flat

        # Calculate steps until 100
        current_val = metric_history[-1]
        steps_to_fail = (100 - current_val) / slope

        return {
            "trend": "INCREASING",
            "growth_rate_per_cycle": round(slope, 2),
            "estimated_cycles_to_failure": round(steps_to_fail, 1)
        }

    def get_fleet_baseline(self):
        """
        Analytics Extension: Calculates the 'Normal' operating baseline
        for the entire fleet of laptops/hosts.
        """
        # Logic to be used for Dashboard "Health Score"
        pass


# Legacy Support Class (Adjusted for DB usage)
class AlertEngine:
    def __init__(self, warning_threshold, alert_threshold):
        self.history = []
        self.warn = warning_threshold
        self.crit = alert_threshold

    def check_anomaly(self, new_value):
        """Calculates if the new value is an anomaly based on 3 standard deviations"""
        if len(self.history) < 30:
            self.history.append(new_value)
            return "COLLECTING_DATA"

        mean = np.mean(self.history)
        std = np.std(self.history)

        if new_value > (mean + (3 * std)):
            return "CRITICAL_ANOMALY"

        self.history.append(new_value)
        # Prevent history from growing infinitely in memory
        if len(self.history) > 500: self.history.pop(0)
        return "NORMAL"