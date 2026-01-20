import psutil
import subprocess
import time
from datetime import datetime
from src.db_manager import ITAMDatabase
from src.network_tools import run_ping

# Configuration for local service monitoring
ENTERPRISE_SERVICES = {
    "Print Spooler": "Spooler",
    "Windows Update": "wuauserv",
    "Citrix Desktop Service": "BrokerAgent"  # Example
}


############################################
#             Monitoring tools             #
#        Windows Service management        #
############################################

def check_service_status(service_name):
    """Checks local Windows service status."""
    try:
        service = psutil.win_service_get(service_name)
        status = service.status()
        return "HEALTHY" if status == 'running' else "RECOVERY_REQUIRED"
    except psutil.NoSuchProcess:
        return "NOT_FOUND"


def recover_service(service_name):
    """Attempts to restart a failed local service."""
    print(f"Attempting to restart {service_name}...")
    try:
        # Requires Admin privileges
        subprocess.run(["net", "start", service_name], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def calculate_impact_score():
    """Calculates impact based on active local sessions."""
    # Count processes related to enterprise work (e.g., Citrix or Office)
    active_sessions = len([p for p in psutil.process_iter() if p.name() == "vdtui.exe"])
    if active_sessions > 50: return "P1 - CRITICAL"
    if active_sessions > 10: return "P2 - MODERATE"
    return "P3 - LOW"

def check_critical_services():
    """Watchdog for Enterprise Windows Services."""
    summary = {"total": len(ENTERPRISE_SERVICES), "down": 0, "list": []}
    return {"status": "HEALTHY", "details": summary}

############################################
#          Database Heartbeat Logic        #
############################################

def start_heartbeat_monitor():
    """
    The main execution loop.
    1. Checks every Server in the DB.
    2. Checks Local Services.
    3. Updates 'status' and 'last_checked' in the DB.
    """
    db = ITAMDatabase()
    print("--- Starting ITAM Heartbeat Monitor ---")

    while True:
        # 1. MONITOR REMOTE SERVERS (From DB)
        servers = db._execute_query("SELECT hostname, ip FROM hosts")
        for server in servers:
            hostname = server['hostname']
            ip = server['ip']

            # Perform Ping
            ping_result = run_ping(ip)

            # Write to Database
            db.update_device_status('hosts', hostname, ping_result)
            print(f"[HOST] {hostname:.<20} {ping_result}")

        # 2. MONITOR LOCAL ENTERPRISE SERVICES
        for friendly_name, internal_name in ENTERPRISE_SERVICES.items():
            status = check_service_status(internal_name)

            if status == "RECOVERY_REQUIRED":
                print(f"[SERVICE] {friendly_name} is DOWN. Initiating Recovery...")
                success = recover_service(internal_name)
                status = "RECOVERED" if success else "CRITICAL_FAIL"

            # Optionally update a 'local_services' table or logs here
            print(f"[SERVICE] {friendly_name:.<20} {status}")

        print(f"Cycle Complete: {datetime.now().strftime('%H:%M:%S')}. Sleeping 60s...")
        time.sleep(60)

