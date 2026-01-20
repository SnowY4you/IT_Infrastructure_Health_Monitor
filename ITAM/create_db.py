import os
import sqlite3
import json

def load_data(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        return json.load(file)


def create_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS laptops")
    cursor.execute("DROP TABLE IF EXISTS ip_mac")
    cursor.execute("DROP TABLE IF EXISTS hosts")
    cursor.execute("DROP TABLE IF EXISTS applications")

    cursor.execute("CREATE TABLE ip_mac (ip TEXT PRIMARY KEY, mac TEXT)")

    cursor.execute("""
        CREATE TABLE users (
            userid TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            phone_number TEXT,
            email TEXT,
            hostname TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE laptops (
            hostname TEXT PRIMARY KEY,
            serial_number TEXT,
            cmdb_category TEXT,
            cmdb_subcategory TEXT,
            cmdb_ci TEXT,
            type TEXT,
            product TEXT,
            operating_system TEXT,
            processor TEXT,
            graphic_card TEXT,
            memory TEXT,
            storage TEXT,
            ip TEXT,
            mac TEXT,
            assigned_user TEXT,
            FOREIGN KEY (assigned_user) REFERENCES users(userid),
            FOREIGN KEY (ip) REFERENCES ip_mac(ip)
        )
    """)

    cursor.execute("""
        CREATE TABLE hosts (
            hostname TEXT PRIMARY KEY,
            type TEXT,
            product TEXT,
            cmdb_category TEXT,
            cmdb_subcategory TEXT,
            cmdb_ci TEXT,
            ip TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE applications (
            app_name TEXT PRIMARY KEY,
            app_version NUMERIC,
            build NUMERIC,
            cmdb_category TEXT,
            cmdb_subcategory TEXT,
            cmdb_ci TEXT,
            vendor TEXT,
            device_type  TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Database and tables created successfully.")


def insert_data(db_name, table_name, data):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    try:
        if table_name == "users":
            cursor.executemany(
                "INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?, ?, ?)",
                [(d.get('userid'), d.get('first_name'), d.get('last_name'),
                  d.get('phone_number'), d.get('email'), d.get('hostname', ''))
                 for d in data])

        elif table_name == "laptops":
            cursor.executemany(
                "INSERT OR REPLACE INTO laptops VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [(d.get('hostname'), d.get('serial_number'), d.get('cmdb_category', 'N/A'),
                  d.get('cmdb_subcategory', 'N/A'), d.get('cmdb_ci', 'N/A'),
                  d.get('type', 'Laptop'), d.get('product', 'N/A'),
                  d.get('operating_system', 'Windows'), d.get('processor', 'N/A'),
                  d.get('graphic_card', 'N/A'), d.get('memory', 'N/A'),
                  d.get('storage', 'N/A'), d.get('ip', ''),
                  d.get('mac', ''), d.get('assigned_user', '')) for d in data])

        elif table_name == "ip_mac":
            cursor.executemany("INSERT OR REPLACE INTO ip_mac VALUES (?, ?)",
                               [(d.get('ip'), d.get('mac')) for d in data])

        elif table_name == "hosts":
            cursor.executemany("INSERT OR REPLACE INTO hosts VALUES (?, ?, ?, ?, ?, ?, ?)",
                               [(d.get('hostname'), d.get('type', 'Server'),
                                 d.get('product', 'N/A'), d.get('cmdb_category', 'N/A'),
                                 d.get('cmdb_subcategory', 'N/A'), d.get('cmdb_ci', 'N/A'),
                                 d.get('ip', '')) for d in data])

        elif table_name == "applications":
            cursor.executemany("INSERT OR REPLACE INTO applications VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [(d.get('app_name'), d.get('app_version', 'N/A'),
                  d.get('build', 'N/A'), d.get('cmdb_category', 'N/A'),
                  d.get('cmdb_subcategory', 'N/A'), d.get('cmdb_ci', 'N/A'),
                  d.get('vendor', 'N/A'), d.get('device_type', 'N/A')) for d in data])

        conn.commit()
    except Exception as e:
        print(f"Error inserting into {table_name}: {e}")
    finally:
        conn.close()

def assign_laptops(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT userid FROM users")
    users = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT hostname FROM laptops")
    laptops = [row[0] for row in cursor.fetchall()]

    for i, user in enumerate(users):
        if i < len(laptops):
            laptop = laptops[i]
            cursor.execute("UPDATE users SET hostname = ? WHERE userid = ?", (laptop, user))
            cursor.execute("UPDATE laptops SET assigned_user = ? WHERE hostname = ?", (user, laptop))
    conn.commit()
    conn.close()
    print("Laptops assigned successfully.")


def assign_laptop_ip_mac(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT ip, mac FROM ip_mac")
    network_configs = cursor.fetchall()
    for ip, mac in network_configs:
        cursor.execute("""
            UPDATE laptops 
            SET ip = ?, mac = ? 
            WHERE hostname = (
                SELECT hostname FROM laptops 
                WHERE (ip IS NULL OR ip = '') 
                AND assigned_user IS NOT NULL 
                LIMIT 1
            )
        """, (ip, mac))
    conn.commit()
    conn.close()
    print("IP and MAC addresses assigned to laptops.")


if __name__ == "__main__":
    # Ensure correct paths to your JSON files
    db_name = "itam.db"
    json_files = {
        "ip_mac": r"D:\OneDrive\Python\Automation\IT_Infrastructure_Health_Monitor\generate_mockup_data\data\ip_mac.json",
        "users": r"D:\OneDrive\Python\Automation\IT_Infrastructure_Health_Monitor\generate_mockup_data\data\users.json",
        "laptops": r"D:\OneDrive\Python\Automation\IT_Infrastructure_Health_Monitor\generate_mockup_data\data\laptops.json",
        "hosts": r"D:\OneDrive\Python\Automation\IT_Infrastructure_Health_Monitor\generate_mockup_data\data\hosts.json",
        "applications": r"D:\OneDrive\Python\Automation\IT_Infrastructure_Health_Monitor\generate_mockup_data\data\apps.json"
    }

    create_database(db_name)
    for table_name, json_file in json_files.items():
        if os.path.exists(json_file):
            data = load_data(json_file)
            insert_data(db_name, table_name, data)
        else:
            print(f"File not found: {json_file}")

    assign_laptops(db_name)
    assign_laptop_ip_mac(db_name)
    print("Database build and assignment process complete.")