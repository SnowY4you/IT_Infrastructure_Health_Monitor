

## Enhanced Project Architecture: "The Self-Healing Guardian"

![Tests Status](https://github.com/SnowY4you/IT_Infrastructure_Health_Monitor/SnowY4you/<REPOSITORY>/actions/workflows/test_all_functions.yml/badge.svg)

### 1. Diagnostic Automation & RCA Logic
- **The Triage Script**: When a service fails, Python triggers a diagnostic suite (using Subprocess to run PowerShell or Bash scripts) that checks:
- **Logs**: Scans the last 100 lines of system logs for specific error codes (e.g., OOM Killer or Segmentation Fault).
- **Dependencies**: Checks if the database or networking layer is also down.
- **The Output**: A generated RCA Report (JSON or PDF) that says: "Service X failed because of Memory Leak in Module Y, not a network timeout."

### 2. AI/ML & Observability (Predictive Analytics)
- **Anomaly Detection**: Use Scikit-learn or PyTorch to train a simple Isolation Forest model on your historical CPU/RAM data.
- **The Goal**: The system should alert you before a crash happens. For example: "CPU usage is 15% higher than the usual Tuesday average; potential memory leak detected."
- **Visualization**: Export your Python metrics to a Grafana Dashboard to show real-time health scores.

### 3. Implementation of TDD/BDD
- **TDD (Unit Testing)**: Use Pytest to ensure your monitoring logic works.
- **Example**: Write a test that mocks a "Disk Full" scenario and asserts that your script correctly triggers the "Clean Temp Files" function.
- **BDD (User Stories)**: Use Behave (Gherkin syntax) to define business logic.
- **Example: > Feature**: Automated Service Recovery

````
**Given** the "Nginx" service is stopped
**When** the monitor script runs 
**Then** the script should attempt to restart "Nginx" 
**And** an alert email should be sent to the admin
````
### Folder Structure
````
/IT_Infrastructure_Health_Monitor
│
├── /src
│   ├── monitor.py        # Main loop
│   ├── diagnostics.py    # RCA & PowerShell/Bash scripts
│   └── ml_engine.py      # Anomaly detection models
│
├── /tests
│   ├── /unit             # TDD: Pytest files
│   └── /features         # BDD: Behave/Gherkin files
│
├── /dashboards           # Grafana JSON exports
├── requirements.txt
└── README.md             # Documenting the "Digital Transformation" aspect
````

Tab,Backend Module,Key Functionality
Network,network_analytics.py,Correlation of traces with ICMP/TCP/SSL health.
Apps,monitor.py,Watchdog for TLS issues and dependency resolution.
Devices,metrics.py,"HW metrics (CPU/Disk) for Servers, Laptops, and Switches."