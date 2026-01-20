import psutil
import subprocess
from src.config import ENTERPRISE_SERVICES
from src.diagnostics import perform_quick_triage

# 1. The Logic Function
def check_service_status(service_name, mock_status=None):
    if mock_status:
        return "RECOVERY_REQUIRED" if mock_status == "stopped" else "HEALTHY"

    try:
        service = psutil.win_service_get(service_name)
        status = service.status()
        return "HEALTHY" if status == 'running' else "RECOVERY_REQUIRED"
    except psutil.NoSuchProcess:
        return "NOT_FOUND"

# 2. The Execution Loop
def run_monitor():
    print("--- Starting Enterprise Health Check ---")
    for friendly_name, internal_name in ENTERPRISE_SERVICES.items():
        status = check_service_status(internal_name)
        print(f"Checking {friendly_name:.<40} [{status}]")

        if status == "RECOVERY_REQUIRED":
            print(f"CRITICAL: {friendly_name} is down!")

            # --- START OF DIAGNOSTIC TRIAGE (RCA) ---
            # Before fixing, we log the state for Root Cause Analysis
            perform_quick_triage(internal_name)

            # --- START OF AUTOMATED FIX ---
            success = recover_service(internal_name)

            if success:
                print(f"SUCCESS: {friendly_name} has been restored.")
            else:
                print(f"ALERT: Automated recovery failed for {friendly_name}. Manual intervention required.")

# 3. The Self-Heal
def recover_service(service_name):
    print(f"Attempting to restart {service_name}...")
    try:
        # Use shell=True for Windows built-in commands
        subprocess.run(["net", "start", service_name], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart {service_name}: {e}")
        return False

def calculate_impact_score(server_ip):
    """
    Watchdog Impact Analysis.
    Prioritizes fixes based on active user count.
    """
    # Mock logic: in reality, you'd query Citrix API or count active TCP connections
    active_sessions = len([p for p in psutil.process_iter() if p.name() == "vdtui.exe"])

    if active_sessions > 50: return "P1 - CRITICAL IMPACT"
    if active_sessions > 10: return "P2 - MODERATE IMPACT"
    return "P3 - LOW IMPACT"

# Critical Services
def check_critical_services():
    """
    Watchdog for Enterprise Windows Services.
    Covers: Print Spooler, WSUS, Licensing, MDM.
    """
    summary = {"total": len(ENTERPRISE_SERVICES), "down": 0, "list": []}

    for friendly, internal in ENTERPRISE_SERVICES.items():
        try:
            service = psutil.win_service_get(internal)
            state = service.status()
            if state != "running":
                summary["down"] += 1
                summary["list"].append(friendly)
        except Exception:
            summary["down"] += 1
            summary["list"].append(f"{friendly} (NOT FOUND)")

    status = "HEALTHY" if summary["down"] == 0 else "CRITICAL"
    return {"status": status, "details": summary}