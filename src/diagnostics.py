import psutil
from datetime import datetime
from src.db_manager import ITAMDatabase


############################################
#                Diagnostic                #
############################################

class DiagnosticEngine:
    def __init__(self):
        self.db = ITAMDatabase()

    def perform_quick_triage(self, service_name):
        """
        Automates initial hardware/software health checks during a failure.
        Slashing manual troubleshooting time by checking common local failure points.
        """
        # Local imports to prevent circular dependency
        from src.metrics import check_disk_capacity
        from src.network_tools import diagnose_dependency_failure

        triage_report = []
        print(f"Running Diagnostic Triage for {service_name}...")

        # 1. Local Hardware Checks
        disk = check_disk_capacity()
        if disk['status'] == "CRITICAL":
            triage_report.append(
                f"CRITICAL DISK: {disk['value']} used. Service {service_name} likely failed writing logs.")

        mem_usage = psutil.virtual_memory().percent
        if mem_usage > 90:
            triage_report.append(f"MEMORY PRESSURE: {mem_usage}% usage detected. Risk of OOM kill.")

        # 2. Network Dependency Check (Linked to DB)
        dependencies = diagnose_dependency_failure(service_name)
        for dep in dependencies:
            # Check if any part of the dependency chain reports failure
            if isinstance(dep, dict) and (dep.get('ping') == "DOWN" or dep.get('port_access') == "CLOSED"):
                triage_report.append(f"BACKEND FAILURE: Host {dep.get('hostname')} is unreachable.")

        return triage_report

    def run_rca_triage(self, app_name):
        """
        Correlates local metrics with database relationships.
        RCA: Why is THIS application failing for THIS user?
        """
        # Local imports to prevent circular dependency
        from src.monitor import check_critical_services
        from src.metrics import check_disk_capacity
        from src.network_tools import diagnose_dependency_failure, check_network_latency

        disk = check_disk_capacity()
        services = check_critical_services()
        latency = check_network_latency()  # Defined the missing variable

        # Scenario 1: Local Resource Exhaustion
        if disk["status"] == "CRITICAL":
            return f"RCA for {app_name}: Service failure due to Disk Maximum Capacity (Log bloat)."

        # Scenario 2: Network Latency
        if latency["status"] == "CRITICAL":
            return f"RCA for {app_name}: User-facing slowness caused by high network latency ({latency.get('value')})."

        # Scenario 3: Backend Database Lookup
        deps = diagnose_dependency_failure(app_name)
        for d in deps:
            if d.get('ping') == "DOWN":
                return f"RCA for {app_name}: Critical backend server ({d.get('hostname')}) is unreachable."

        return f"RCA for {app_name}: Analyzing system logs for traffic spikes or version conflicts..."

    def get_full_impact_chain(self, failing_host_name):
        """
        Advanced Analytics: Trace a failing Host to every impacted Human User.
        """
        query = """
            SELECT h.hostname as server, h.assigned_app, u.first_name, u.last_name, l.hostname as laptop
            FROM hosts h
            JOIN laptops l ON h.assigned_app = l.assigned_app_laptop
            JOIN users u ON l.assigned_user = u.userid
            WHERE h.hostname = ?
        """
        return self.db._execute_query(query, (failing_host_name,))


############################################
#       Standalone Helper Functions        #
############################################

def get_user_impact_by_ip(ip_address):
    db = ITAMDatabase()
    query = """
        SELECT u.first_name, u.last_name, u.email, l.hostname, l.status
        FROM users u
        JOIN laptops l ON u.userid = l.assigned_user
        WHERE l.ip = ?
    """
    return db._execute_query(query, (ip_address,))


def get_app_health_summary():
    db = ITAMDatabase()
    query = """
        SELECT a.app_name, h.hostname, h.status as server_status
        FROM applications a
        JOIN hosts h ON a.app_name = h.assigned_app
    """
    return db._execute_query(query)