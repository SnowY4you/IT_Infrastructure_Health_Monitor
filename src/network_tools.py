import psutil
import subprocess
import socket
import ssl
from datetime import datetime
from src.db_manager import ITAMDatabase


############################################
#      "Network" and "Application" tools    #
############################################

def diagnose_dependency_failure(app_name):
    """
    RCA Logic: Finds the Server (Host) IP associated with an app in the DB.
    Checks if that server is reachable (Ping) and Port-accessible.
    """
    db = ITAMDatabase()
    # SQL to find the server linked to this application
    query = """
        SELECT h.hostname, h.ip, h.status, h.assigned_app
        FROM hosts h
        WHERE h.assigned_app = ?
    """

    server_data = db._execute_query(query, (app_name,))
    results = []

    if not server_data:
        return [{"status": "MISSING", "details": f"No host server mapped to {app_name}"}]

    for server in server_data:
        target = server['ip'] if server['ip'] else server['hostname']
        ping_status = run_ping(target)

        # Specific Port Checks based on App Name
        port_status = "N/A"
        if "Citrix" in app_name:
            port_status = check_endpoint(target, 1494)  # ICA Protocol
        elif "Outlook" in app_name:
            port_status = check_endpoint(target, 443)  # HTTPS/MAPI
        elif "GlobalProtect" in app_name:
            port_status = check_endpoint(target, 443)  # VPN Gateway

        results.append({
            "hostname": server['hostname'],
            "ip": target,
            "ping": ping_status,
            "port_access": port_status
        })

    return results


def check_tls_health(hostname, port=443):
    """Diagnoses SSL certificate issues for Web Apps/VPN."""
    context = ssl.create_default_context()
    try:
        # Use a short timeout for network checks
        with socket.create_connection((hostname, port), timeout=3) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                # Format: 'Jan 20 13:27:10 2027 GMT'
                expire_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                remaining_days = (expire_date - datetime.now()).days

                status = "HEALTHY" if remaining_days > 14 else "WARNING"
                return {
                    "status": status,
                    "days_remaining": remaining_days,
                    "issuer": dict(x[0] for x in cert['issuer'])['commonName']
                }
    except Exception as e:
        return {"status": "CRITICAL", "details": f"TLS Handshake Failed: {str(e)}"}


def check_endpoint(host, port, timeout=2):
    """Checks if a specific TCP port is open (App Health)."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return "OPEN"
    except Exception:
        return "CLOSED"


def run_ping(ip):
    """Windows-optimized ICMP Ping."""
    if not ip: return "NO_IP"
    try:
        output = subprocess.run(["ping", "-n", "1", "-w", "1000", ip],
                                capture_output=True, text=True, timeout=2)
        return "UP" if "Reply from" in output.stdout else "DOWN"
    except Exception:
        return "ERROR"


def check_network_latency(target="8.8.8.8", count=2):
    """Detects 'Slowness' reported by users."""
    try:
        cmd = ["ping", "-n", str(count), target]
        output = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

        if "Average =" in output.stdout:
            avg_latency = output.stdout.split("Average =")[-1].strip()
            return {"status": "HEALTHY", "value": avg_latency}
        return {"status": "CRITICAL", "details": "High Latency or Packet Loss"}
    except Exception as e:
        return {"status": "ERROR", "details": str(e)}


def check_network_health():
    """Checks Local DNS and NIC errors."""
    results = {}
    try:
        socket.gethostbyname("google.com")
        results["DNS"] = "UP"
    except socket.gaierror:
        results["DNS"] = "DOWN"

    net_io = psutil.net_io_counters()
    results["Errors_In"] = net_io.errin
    results["Drop_In"] = net_io.dropin

    status = "HEALTHY" if results["DNS"] == "UP" and net_io.errin == 0 else "WARNING"
    return {"status": status, "details": results}
