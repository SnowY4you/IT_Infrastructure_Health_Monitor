import pytest
import os
import numpy as np
from src.metrics import (
    check_cpu_threshold, check_ram_threshold,
    check_disk_threshold, check_disk_capacity,
    check_memory_pressure
)
from src.network_tools import (
    check_network_latency, check_network_health,
    diagnose_dependency_failure, check_tls_health,
    check_endpoint, run_ping
)
from src.monitor import (
    check_service_status, recover_service,
    calculate_impact_score, check_critical_services
)
from src.diagnostics import DiagnosticEngine, get_user_impact_by_ip, get_app_health_summary
from src.network_analytics import NetworkAnalytics
from src.ml_engine import MLEngine, AlertEngine
from src.db_manager import ITAMDatabase

################################
### Testing all Network Tool ###
################################

def test_check_network_latency():
    result = check_network_latency("8.8.8.8", count=1)
    assert isinstance(result, dict)
    assert "status" in result

def test_check_network_health():
    result = check_network_health()
    assert "DNS" in result["details"]
    assert "status" in result

def test_diagnose_dependency_failure():
    # Requires itam.db to be populated via create_db.py
    result = diagnose_dependency_failure("Outlook")
    assert isinstance(result, list)

def test_check_tls_health():
    result = check_tls_health("google.com")
    assert result["status"] in ["HEALTHY", "WARNING", "CRITICAL"]

def test_check_endpoint():
    # Standard check for Google HTTPS
    result = check_endpoint("google.com", 443)
    assert result == "OPEN"

def test_run_ping():
    result = run_ping("127.0.0.1")
    assert result == "UP"

###########################
### Testing all Metrics ###
###########################

@pytest.mark.parametrize("function, mock_val, expected", [
    (check_cpu_threshold, 95, True),
    (check_cpu_threshold, 20, False),
    (check_ram_threshold, 90, True),
    (check_ram_threshold, 40, False),
    (check_disk_threshold, 95, True),
    (check_disk_threshold, 50, False),
])
def test_thresholds(function, mock_val, expected):
    assert function(mock_value=mock_val) is expected

def test_check_disk_capacity_structure():
    result = check_disk_capacity("C:")
    assert "status" in result
    assert "%" in result["value"]

def test_check_memory_pressure():
    result = check_memory_pressure()
    assert result["status"] in ["HEALTHY", "WARNING"]

############################
### Testing all Monitors ###
############################

def test_check_service_status_logic():
    # Testing the mock bypass logic
    assert check_service_status("Spooler") in ["HEALTHY", "RECOVERY_REQUIRED", "NOT_FOUND"]

def test_calculate_impact_score():
    score = calculate_impact_score()
    assert "IMPACT" in score or "P" in score

def test_check_critical_services():
    result = check_critical_services()
    assert "status" in result
    assert "total" in result["details"]

##############################
### Testing all ML Engines ###
##############################

def test_ml_anomaly_detection():
    engine = MLEngine()
    history = [20, 21, 19, 22, 20, 21, 20, 19, 20, 21] * 2 # 20 points
    # Value 90 is clearly an anomaly compared to 20
    result = engine.check_anomaly_alert("TestHost", 90, min_threshold=15)
    # Note: engine uses internal memory_buffer, we populated it via the loop in logic
    for val in history:
        engine.check_anomaly_alert("TestHost", val)
    result = engine.check_anomaly_alert("TestHost", 95)
    assert result == "ANOMALY_DETECTED"

def test_predict_capacity_exhaustion():
    engine = MLEngine()
    growth_history = [10, 20, 30, 40, 50]
    result = engine.predict_capacity_exhaustion(growth_history)
    assert result["trend"] == "INCREASING"
    assert result["growth_rate_per_cycle"] > 0

def test_alert_engine_std_dev():
    alert = AlertEngine(80, 90)
    # Fill history with stable data
    for _ in range(35):
        alert.check_anomaly(10)
    # Trigger 3-sigma anomaly
    assert alert.check_anomaly(100) == "CRITICAL_ANOMALY"

###############################
### Testing all Diagnostics ###
###############################

def test_perform_quick_triage():
    diag = DiagnosticEngine()
    report = diag.perform_quick_triage("Outlook")
    assert isinstance(report, list)

def test_run_rca_triage():
    diag = DiagnosticEngine()
    result = diag.run_rca_triage("Outlook")
    assert isinstance(result, str)

def test_get_full_impact_chain():
    diag = DiagnosticEngine()
    # Assuming 'EXCHANGE_SRV' exists in your mock data
    result = diag.get_full_impact_chain("EXCHANGE_SRV_01")
    assert isinstance(result, list)

#######################################
###  Testing all Network Analytics  ###
#######################################

def test_network_analytics_flows():
    analytics = NetworkAnalytics()
    mock_traffic = [{'src_ip': '192.168.1.15', 'dest_ip': '10.20.1.50', 'bytes': 5000}]
    enriched = analytics.get_grouped_flows(mock_traffic)
    assert "service_tag" in enriched[0]

def test_health_distribution():
    analytics = NetworkAnalytics()
    dist = analytics.calculate_health_distribution()
    assert isinstance(dist, dict)

################################
### Testing all DB functions ###
################################

def test_db_lifecycle():
    db = ITAMDatabase()
    # Test update and fetch
    db.update_device_status('hosts', 'TEST_HOST', 'UP')
    # Use internal helper to verify
    check = db._execute_query("SELECT status FROM hosts WHERE hostname = 'TEST_HOST'")
    if check:
        assert check[0]['status'] == 'UP'

def test_get_app_health_summary():
    summary = get_app_health_summary()
    assert isinstance(summary, list)