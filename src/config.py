import psutil


# 1. Configuration (Top of the file or in a separate config.py)


ENTERPRISE_SERVICES = {
    "OneDrive Sync": "OneDrive",
    "Print Spooler": "Spooler",
    "Windows Update": "wuauserv",
    "Software Protection (Licensing)": "sppsvc",
    "MDM Push": "dmwappushservice"
}