import psutil

# Get CPU usage as a percentage
cpu_usage = psutil.cpu_percent(interval=1)

print(f"Current CPU Usage: {cpu_usage}%")

if cpu_usage > 80:
    print("ALERT: High CPU usage detected!")
else:
    print("System health is OK.")