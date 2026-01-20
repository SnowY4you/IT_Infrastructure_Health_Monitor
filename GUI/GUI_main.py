from GUI.main import MainWindow  # Import your template class
from src.monitor import check_service_status
from scr import network_tools # Network and Application tabs
from ui_function import * # A FILE WHERE ALL THE FUNCTION LIKE BUTTON PRESSES, SILDER, PROGRESS BAR E.T.C ARE DONE.
from about import * # CONTAIN STRING VARIABLE CONTAINING THE ABOUT OF EACH PAGE IN THE APPLICATION


############################################
#                Main GUI                  #
############################################


class EnterpriseMonitorGUI(MainWindow):
    def __init__(self):
        super().__init__()
        # Connect your 'Network' button to a function
        self.ui.btn_network.clicked.connect(self.show_network_stats)

    def show_network_stats(self):
        # Example: Updating a label in your GUI with live data
        status = check_service_status("Dhcp")
        self.ui.label_status.setText(f"Network Service: {status}")