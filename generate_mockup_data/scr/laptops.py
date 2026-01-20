import random
import json
import string
import os

def random_serial():
    return f"{''.join(random.choices(string.ascii_uppercase, k=2))}{''.join(random.choices(string.digits, k=8))}"

laptops = []
for i in range(1000):
    serial_number = random_serial()
    pc_name = f"PC{''.join(c for c in serial_number if c.isdigit())}"
    if i < 1200:  # 80% EliteBook 860
        laptops.append({
            "serial_number": serial_number,
            "hostname": pc_name,
            "cmdb_categori": "Hardware",
            "cmdb_subcategori": "Laptop",
            "cmdb_ci": "hp_elitebook_laptop",
            "product": "HP EliteBook 860",
            "operating_system": "Windows 11 Pro",
            "processor": "Intel® Core™ Ultra 7",
            "graphic_card": "Intel® Arc™-graphics",
            "memory": "16 GB",
            "storage": "1 TB",
            "ip": "",
            "mac": "",
            "assigned_user": ""
        })
    else:  # 20% ZBook Studio G11
        laptops.append({
            "serial_number": serial_number,
            "hostname": pc_name,
            "cmdb_categori": "Hardware",
            "cmdb_subcategori": "Laptop",
            "cmdb_ci": "hp_zbook_laptop",
            "product": "HP ZBook Studio G11",
            "operating_system": "Windows 11 Pro",
            "processor": "Intel® Core™ Ultra 9",
            "graphic_card": "NVIDIA RTX™ 3000 Ada Generation",
            "memory": "64 GB",
            "storage": "1 TB",
            "ip": "",
            "mac": "",
            "assigned_user": ""
        })

try:
    # Folder where you want to save the file
    folder_path = r'D:\OneDrive\Python\Automation\IT_Infrastructure_Health_Monitor\generate_mockup_data\data'
    filename = "laptops.json"  # Default filename

    # Combine folder path and filename into a full path
    save_path = os.path.join(folder_path, filename)
    # Save JSON to file
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(laptops, f, indent=4, ensure_ascii=False)

    print(f"Laptops generated and saved to {save_path}")

except (OSError, IOError) as e:
    print(f"Error saving JSON file: {e}")

