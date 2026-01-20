from PySide6.QtCore import QObject, Slot
from src.network_tools import run_ping
from src.network_tools import diagnose_dependency_failure, check_network_latency
from src.metrics import check_cpu_threshold
from src.monitor import check_service_status


class EnterpriseController(QObject):
    def __init__(self, main_ui):
        super().__init__()
        self.main_ui = main_ui
        self.setup_tabs()

    def setup_tabs(self):
        """Connects the GUI buttons to the backend logic"""
        # Example: When 'Refresh' is clicked on the Network Tab
        # self.main_ui.network_tab.btn_refresh.clicked.connect(self.update_network_view)
        pass

    @Slot()
    def update_network_view(self):
        """Watchdog RCA: Correlate VPN, Citrix, and DNS"""
        vpn_state = run_ping("10.0.0.1")  # VPN Tunnel
        dns_state = run_ping("8.8.8.8")  # External DNS

        # If both are down, RCA points to local 'Networking' service
        if vpn_state == "DOWN" and dns_state == "DOWN":
            self.main_ui.network_tab.label_rca.setText("Root Cause: Local Network Adapter / DNS Service")


@Slot(str)
def run_app_analytics(self, app_name):
    """Triggered from the Apps Tab to show why an app is failing."""
    # 1. Run TLS Check
    tls = check_tls_health("citrix.enterprise.com")

    # 2. Run Dependency Check
    dep_failures = diagnose_dependency_failure(app_name)

    # 3. Update the GUI with the Impact Analysis
    self.ui.apps_tab.label_tls_status.setText(f"TLS: {tls['status']}")

    if dep_failures:
        self.ui.apps_tab.list_dependencies.addItems(dep_failures)
        self.ui.apps_tab.label_rca.setText(f"RCA: Missing dependencies: {', '.join(dep_failures)}")


def process_device_check(self, device_name, cpu_val):
    # 1. Is it an anomaly?
    status = self.ml_engine.analyze(device_name, cpu_val)

    # 2. If it's critical, what's the impact?
    if status == "CRITICAL":
        impact = calculate_impact_score(device_name)
        self.ui.network_tab.log_alert(f"ALERT: {device_name} is unstable. Impact: {impact}")