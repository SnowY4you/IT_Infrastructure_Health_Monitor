import pytest
from src.metrics import check_cpu_threshold, check_ram_threshold, check_disk_threshold, check_disk_capacity

############################################
#             Metrics Testing              #
############################################

def test_cpu_alert_trigger():
    # We want to check if the function returns True when CPU is over 80%
    # We "mock" the value to be 95%
    assert check_cpu_threshold(mock_value=95) is True

def test_cpu_normal_status():
    # It should return False when CPU is healthy (e.g., 20%)
    assert check_cpu_threshold(mock_value=20) is False

def check_cpu_threshold():
    assert check_cpu_threshold(mock_value=95) is True

def check_ram_threshold():
    assert check_ram_threshold(mock_value=95) is True

def check_disk_threshold():
    assert check_disk_threshold(mock_value=50) is True

def check_disk_capacity():
    assert check_disk_threshold(mock_value=95) is True

# This decorator runs the function 3 times with different arguments
@pytest.mark.parametrize("function, mock_val, expected", [
    (check_cpu_threshold, 95, True),   # High CPU
    (check_cpu_threshold, 20, False),  # Low CPU
    (check_ram_threshold, 90, True),   # High RAM
    (check_ram_threshold, 40, False),  # Low RAM
    (check_disk_threshold, 95, True),  # High Disk
    (check_disk_threshold, 50, False),  # Low Disk
    (check_disk_capacity, 90, True),    # High disk capacity
    (check_disk_capacity, 40, False),    # Low disk capacity
])
def test_thresholds(function, mock_val, expected):
    assert function(mock_value=mock_val) is expected