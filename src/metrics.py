import psutil


############################################
#           Metrics - Threshold            #
#       Hardware resource monitoring       #
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
def check_disk_capacity(drive="C:"):
    """Checks if the system disk is reaching maximum capacity."""
    try:
        usage = psutil.disk_usage(drive)
        percent = usage.percent

        status = "HEALTHY"
        if percent > 90:
            status = "CRITICAL"
        elif percent > 75:
            status = "WARNING"

        return {
            "status": status,
            "value": f"{percent}%",
            "details": f"Used: {usage.used // (2 ** 30)}GB / Total: {usage.total // (2 ** 30)}GB"
        }
    except Exception as e:
        return {"status": "ERROR", "value": "N/A", "details": str(e)}


def check_memory_pressure():
    """Checks RAM usage."""
    mem = psutil.virtual_memory()
    status = "HEALTHY" if mem.percent < 85 else "WARNING"
    return {"status": status, "value": f"{mem.percent}%"}

# Check RAM Threshold
def check_ram_threshold(threshold=80, mock_value=None):
    current_usage = mock_value if mock_value is not None else psutil.virtual_memory().percent
    return current_usage > threshold

# Check Disk Threshold
def check_disk_threshold(threshold=90, mock_value=None):
    # Checks the root partition
    current_usage = mock_value if mock_value is not None else psutil.disk_usage('/').percent
    return current_usage > threshold


