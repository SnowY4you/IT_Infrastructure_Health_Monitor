import json
import random
from faker import Faker

# Instantiate the Faker class
fake = Faker()

# Generate IP and MAC addresses
pc_address = []

for i in range(2500):
    # Generate random IP and MAC addresses
    ip_address = f"{random.randint(192, 192)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
    mac_address = fake.mac_address()

    # Append the generated data as a dictionary to the list
    pc_address.append({
        "ip": ip_address,
        "mac": mac_address
    })

# Save the IP and MAC addresses to a JSON file
with open(r'D:\OneDrive\Python\Automation\IT_Infrastructure_Health_Monitor\generate_mockup_data\data\ip_mac.json', 'w', encoding='utf-8') as f:
    json.dump(pc_address, f, ensure_ascii=False, indent=4)
    print("IP and MAC addresses saved to ip_mac.json")
