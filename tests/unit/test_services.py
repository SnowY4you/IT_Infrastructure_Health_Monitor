import pytest
from src.monitor import check_service_status

############################################
#             Service Testing              #
############################################

def test_service_stopped_trigger():
    # Simulate the 'Spooler' service being in a 'stopped' state
    assert check_service_status("Spooler", mock_status="stopped") == "RECOVERY_REQUIRED"

def test_service_running_fine():
    # Simulate the 'Spooler' service being 'running'
    assert check_service_status("Spooler", mock_status="running") == "HEALTHY"