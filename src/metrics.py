import psutil


############################################
#           Metrics - Threshold            #
############################################

# Check CPU Threshold
def check_cpu_threshold(threshold=80, mock_value=None):
    """
    Checks if CPU usage exceeds a specific threshold.
    Allows a mock_value for testing purposes.
    """
    if mock_value is not None:
        current_usage = mock_value
    else:
        current_usage = psutil.cpu_percent(interval=1)

    return current_usage > threshold

# Disk capacity
def check_disk_capacity(drive="C:", threshold=90):
    """
    Monitors Disk Maximum Capacity.
    RCA: Prevents service crashes caused by log-bloat.
    """
    usage = psutil.disk_usage(drive)
    percent = usage.percent

    status = "HEALTHY"
    if percent >= threshold:
        status = "CRITICAL"
    elif percent >= (threshold - 15):
        status = "WARNING"

    return {
        "status": status,
        "value": f"{percent}%",
        "free_gb": round(usage.free / (1024 ** 3), 2)
    }

# Check RAM Threshold
def check_ram_threshold(threshold=80, mock_value=None):
    current_usage = mock_value if mock_value is not None else psutil.virtual_memory().percent
    return current_usage > threshold

# Check Disk Threshold
def check_disk_threshold(threshold=90, mock_value=None):
    # Checks the root partition
    current_usage = mock_value if mock_value is not None else psutil.disk_usage('/').percent
    return current_usage > threshold


def check_cpu_threshold(threshold=80, mock_value=None):
    current = mock_value if mock_value is not None else psutil.cpu_percent(interval=1)
    return current > threshold

def check_ram_threshold(threshold=80, mock_value=None):
    current = mock_value if mock_value is not None else psutil.virtual_memory().percent
    return current > threshold

def check_disk_threshold(threshold=90, mock_value=None):
    current = mock_value if mock_value is not None else psutil.disk_usage('/').percent
    return current > threshold