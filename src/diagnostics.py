import psutil
from src.metrics import check_disk_capacity
from src.monitor import check_critical_services
from src.network_tools import check_network_latency
from db_manager import *


############################################
#               Diagnostic                 #
############################################

# 1. Triage check
def perform_quick_triage(service_name):
    """
    Automates initial hardware/software health checks during a failure.
    Slashing manual troubleshooting time.
    """
    print(f"Running Diagnostic Triage for {service_name}...")

    # Example: Check if System Disk is full (common cause for service failure)
    disk_usage = psutil.disk_usage('C:').percent
    if disk_usage > 95:
        print(f"POSSIBLE ROOT CAUSE: Disk usage is at {disk_usage}%. Service cannot write logs.")

    # Example: Check for high memory pressure
    mem_usage = psutil.virtual_memory().percent
    if mem_usage > 95:
        print(f"POSSIBLE ROOT CAUSE: Memory exhaustion ({mem_usage}%).")

# 2. RootCause Analysis
def run_rca_triage():
    """Correlates metrics with logs and network calls"""
    results = {
        "network": check_network_latency(),
        "disk": check_disk_capacity(),
        "services": check_critical_services()
    }

    # Simple Correlation Logic
    if results["disk"] == "CRITICAL" and results["services"] == "DOWN":
        return "RCA: Service failure due to Disk Maximum Capacity (Log bloat)"

    return "RCA: Analyzing logs for version history/traffic spikes..."

def perform_watchdog_rca():
    """
    Watchdog RCA Diagnostics: Correlates metrics to find WHY a failure happened.
    """
    disk = check_disk_capacity()
    services = check_critical_services()

    # RCA Scenario: If services are down AND disk is full
    if services["status"] == "CRITICAL" and disk["status"] == "CRITICAL":
        return {
            "root_cause": "Disk Exhaustion",
            "impact": "Services unable to write logs/cache. Immediate cleanup required.",
            "priority": "P1"
        }

    # RCA Scenario: Networking
    # (Add logic for DNS vs VPN here)
    return {"root_cause": "Unknown", "impact": "Pending Triage", "priority": "P3"}

def get_user_impact_by_ip(ip_address):
    """Correlate a network issue to a specific human user."""
    db = ITAMDatabase()
    query = """
        SELECT u.first_name, u.last_name, u.email, l.hostname
        FROM users u
        JOIN laptops l ON u.userid = l.assigned_user
        WHERE l.ip = ?
    """
    return db._execute_query(query, (ip_address,))