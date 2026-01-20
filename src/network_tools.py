import psutil
import subprocess
import socket
from datetime import datetime

############################################
#     "Network" and "Application" tools    #
############################################

# Check TLS
def check_tls_health(hostname, port=443):
    """
    Diagnoses TLS/SSL certificate issues.
    RCA: Prevents 'Connection Refused' errors in Citrix/Web Apps.
    """
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, port), timeout=3) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                # Extract expiration date
                expire_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                remaining_days = (expire_date - datetime.now()).days

                status = "HEALTHY" if remaining_days > 14 else "WARNING"
                return {
                    "status": status,
                    "days_remaining": remaining_days,
                    "issuer": cert['issuer'][1][0][1]
                }
    except Exception as e:
        return {"status": "CRITICAL", "details": f"TLS Handshake Failed: {str(e)}"}


def diagnose_dependency_failure(app_name):
    """
    Finds suspect dependencies: databases, caches, internal DNS.
    Watchdog Impact Analysis logic.
    """
    # Example mapping from your apps.json
    dependencies = {
        "Citrix": ["10.20.1.50", "DNS-Server-01", "Licensing-Srv"],
        "ERP_System": ["DB-Server-SQL", "Cache-Redis"]
    }

    app_deps = dependencies.get(app_name, [])
    failures = []

    for dep in app_deps:
        # Check if dependency IP/Hostname is reachable
        try:
            socket.gethostbyname(dep)
        except socket.gaierror:
            failures.append(dep)

    return failures

# Pinging
def check_endpoint(host, port, timeout=3):
    """Checks TCP/SSL health for Apps like Citrix or Web Services."""
    try:
        # Standard TCP Ping
        with socket.create_connection((host, port), timeout=timeout):
            return "UP"
    except Exception as e:
        return f"DOWN: {str(e)}"

def run_ping(ip):
    """Standard ICMP Ping for Network Devices (Aruba, Cisco)."""
    try:
        output = subprocess.run(["ping", "-n", "1", ip], capture_output=True, text=True)
        return "UP" if "Reply from" in output.stdout else "DOWN"
    except Exception:
        return "ERROR"

# Network Latency
def check_network_latency(target="8.8.8.8", count=3):
    """
    Diagnoses latency and packet loss.
    Impact: Detects 'Slowness' reported by Citrix/VPN users.
    """
    try:
        # Using -n for Windows, -c for Linux
        cmd = ["ping", "-n", str(count), target]
        output = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

        if output.returncode == 0:
            # Extracting average latency from Windows ping output
            if "Average =" in output.stdout:
                avg_latency = output.stdout.split("Average =")[-1].strip()
                return {"status": "HEALTHY", "value": avg_latency, "details": "Latency within norms"}
        return {"status": "CRITICAL", "value": "N/A", "details": "Packet loss detected or Timeout"}
    except Exception as e:
        return {"status": "ERROR", "value": "N/A", "details": str(e)}


# health network
def check_network_health():
    """
    Checks HTTP, SSL, and DNS resolution.
    Target: Detects 'Application Failures' caused by TLS/DNS issues.
    """
    results = {}
    # 1. DNS Resolution Check
    try:
        socket.gethostbyname("google.com")
        results["DNS"] = "UP"
    except socket.gaierror:
        results["DNS"] = "DOWN"

    # 2. Check for Interface Errors (NIC Health)
    net_io = psutil.net_io_counters()
    results["Errors_In"] = net_io.errin
    results["Drop_In"] = net_io.dropin

    status = "HEALTHY" if results["DNS"] == "UP" and net_io.errin == 0 else "WARNING"
    return {"status": status, "details": results}


