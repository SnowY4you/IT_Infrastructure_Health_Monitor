import json
import random
import os

# List to store all generated hostnames
hostnames = []


# Generate hostnames for AP routers
products_ap = ["Aruba"]
for _ in range(20):
    hostname = f"AP_{random.randint(100, 999)}"
    hostnames.append({
        "hostname": hostname,
        "type": "ap_router",
        "product": random.choice(products_ap),
        "cmdb_categori": "Network",
        "cmdb_subcategori": "Access Point",
        "cmdb_ci": "aruba_access_point",
        "ip": ""
    })

# Generate hostnames for switches
products_switch = ["Aruba"]
for _ in range(10):
    hostname = f"Switch_{random.randint(100, 999)}"
    hostnames.append({
        "hostname": hostname,
        "type": "switch",
        "product": random.choice(products_switch),
        "cmdb_categori": "Network",
        "cmdb_subcategori": "Switch",
        "cmdb_ci": "aruba_switch",
        "ip": ""
    })

# Generate hostnames for firewalls
products_firewall = ["Palo Alto"]
for _ in range(5):
    hostname = f"Firewall_{random.randint(100, 999)}"
    hostnames.append({
        "hostname": hostname,
        "type": "firewall",
        "product": random.choice(products_firewall),
        "cmdb_categori": "Network",
        "cmdb_subcategori": "Firewall",
        "cmdb_ci": "palo_also_firewall",
        "ip": ""
    })

# Generate hostnames for storage servers
products_storage = ["Windows Server"]
for _ in range(20):
    hostname = f"Storage_{random.randint(100, 999)}"
    hostnames.append({
        "hostname": hostname,
        "type": "storage_server",
        "product": random.choice(products_storage),
        "cmdb_categori": "Network",
        "cmdb_subcategori": "Storage",
        "cmdb_ci": "windows_storage_server",
        "ip": ""
    })

# Generate hostnames for DNS servers
products_dns = ["Azure DNS"]
for _ in range(10):
    hostname = f"DNS_{random.randint(100, 999)}"
    hostnames.append({
        "hostname": hostname,
        "type": "dns_server",
        "product": random.choice(products_dns),
        "cmdb_categori": "Network",
        "cmdb_subcategori": "DNS",
        "cmdb_ci": "azure_dns_server",
        "ip": ""
    })

# Generate hostnames for mail servers
products_mail = ["Microsoft Exchange"]
for _ in range(10):
    hostname = f"Mail_{random.randint(100, 999)}"
    hostnames.append({
        "hostname": hostname,
        "type": "mail_server",
        "product": random.choice(products_mail),
        "cmdb_categori": "Network",
        "cmdb_subcategori": "Exchange",
        "cmdb_ci": "microsoft_exchange_server",
        "ip": ""
    })

# Generate hostnames for VMs
products_vm = ["VMware"]
for _ in range(20):
    hostname = f"VMware_{random.randint(100, 999)}"
    hostnames.append({
        "hostname": hostname,
        "type": "vm",
        "product": random.choice(products_vm),
        "cmdb_categori": "Network",
        "cmdb_subcategori": "VMware",
        "cmdb_ci": "vmware_vmware_server",
        "ip": ""
    })



    try:
        # Folder where you want to save the file
        folder_path = r'D:\OneDrive\Python\Automation\IT_Infrastructure_Health_Monitor\generate_mockup_data\data'
        filename = "hosts.json"  # Default filename

        # Combine folder path and filename into a full path
        save_path = os.path.join(folder_path, filename)
        # Save JSON to file
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(hostnames, f, indent=4, ensure_ascii=False)

        print("Hostnames generated and saved to hosts.json")

    except (OSError, IOError) as e:
        print(f"Error saving JSON file: {e}")

