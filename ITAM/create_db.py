import os
import sqlite3
import json

# 1. Get the directory where create_db.py lives (D:\...\ITAM)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Get the Parent directory (Main Folder: D:\...\IT_Infrastructure_Health_Monitor)
parent_dir = os.path.dirname(current_dir)

# 3. Define the database path in that main folder
db_name = os.path.join(parent_dir, "itam.db")

def load_data(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        return json.load(file)


def create_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF")

    tables = ["users", "laptops", "ip_mac", "hosts", "applications"]
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")

    # Applications first, so the Foreign Key ordering will go correctly
    cursor.execute("""
        CREATE TABLE applications (
            app_name TEXT PRIMARY KEY,
            app_version TEXT,
            build TEXT,
            cmdb_category TEXT,
            cmdb_subcategory TEXT,
            cmdb_ci TEXT,
            vendor TEXT,
            device_type TEXT
        )
    """)

    # Second hosts
    cursor.execute("""
        CREATE TABLE hosts (
            hostname TEXT PRIMARY KEY,
            type TEXT,
            product TEXT,
            cmdb_category TEXT,
            cmdb_subcategory TEXT,
            cmdb_ci TEXT,
            ip TEXT,
            mac TEXT,
            status TEXT DEFAULT 'UNKNOWN',
            last_checked TEXT,
            assigned_app TEXT,
            FOREIGN KEY (assigned_app) REFERENCES applications(app_name)
        )
    """)

    # Third ip_mac
    cursor.execute("CREATE TABLE ip_mac (ip TEXT PRIMARY KEY, mac TEXT)")

    cursor.execute("""
        CREATE TABLE users (
            userid TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            phone_number TEXT,
            email TEXT,
            status TEXT DEFAULT 'UNKNOWN',
            last_checked TEXT,
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
            status TEXT DEFAULT 'UNKNOWN',
            last_checked TEXT,
            assigned_user TEXT,
            assigned_app_laptop TEXT,
            FOREIGN KEY (assigned_user) REFERENCES users(userid),
            FOREIGN KEY (assigned_app_laptop) REFERENCES applications(app_name)
        )
    """)

    cursor.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    conn.close()
    print("Database schema created successfully.")

def insert_data(db_name, table_name, data):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    try:
        if table_name == "users":
            # 8 Columns
            cursor.executemany("INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                               [(d.get('userid'), d.get('first_name'), d.get('last_name'),
                                 d.get('phone_number'), d.get('email'), 'UNKNOWN', None, d.get('hostname', '')) for d in
                                data])

        elif table_name == "laptops":
            # 18 Columns
            cursor.executemany(
                "INSERT OR REPLACE INTO laptops VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [(d.get('hostname'), d.get('serial_number'), d.get('cmdb_category', 'N/A'),
                  d.get('cmdb_subcategory', 'N/A'), d.get('cmdb_ci', 'N/A'), d.get('type', 'Laptop'),
                  d.get('product', 'N/A'), d.get('operating_system', 'N/A'), d.get('processor', 'N/A'),
                  d.get('graphic_card', 'N/A'), d.get('memory', 'N/A'), d.get('storage', 'N/A'),
                  d.get('ip', ''), d.get('mac', ''), 'UNKNOWN', None,
                  d.get('assigned_user', ''), None) for d in data])

        elif table_name == "ip_mac":
            cursor.executemany("INSERT OR REPLACE INTO ip_mac VALUES (?, ?)",
                               [(d.get('ip'), d.get('mac')) for d in data])

        elif table_name == "hosts":
            # 11 Columns
            cursor.executemany("INSERT OR REPLACE INTO hosts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                               [(d.get('hostname'), d.get('type', 'Server'), d.get('product', 'N/A'),
                                 d.get('cmdb_category', 'N/A'), d.get('cmdb_subcategory', 'N/A'),
                                 d.get('cmdb_ci', 'N/A'), d.get('ip', ''), d.get('mac', ''),
                                 'UNKNOWN', None, None) for d in data])

        elif table_name == "applications":
            cursor.executemany("INSERT OR REPLACE INTO applications VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                               [(d.get('app_name'), d.get('app_version', 'N/A'), d.get('build', 'N/A'),
                                 d.get('cmdb_category', 'N/A'), d.get('cmdb_subcategory', 'N/A'),
                                 d.get('cmdb_ci', 'N/A'), d.get('vendor', 'N/A'), d.get('device_type', 'N/A')) for d in
                                data])

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
    print("Laptops assigned to Users.")


def assign_ip_mac_addresses(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT ip, mac FROM ip_mac")
    pool = cursor.fetchall()

    cursor.execute("SELECT hostname FROM laptops")
    laptops = [r[0] for r in cursor.fetchall()]
    for i, (ip, mac) in enumerate(pool):
        if i < len(laptops):
            cursor.execute("UPDATE laptops SET ip=?, mac=? WHERE hostname=?", (ip, mac, laptops[i]))

    cursor.execute("SELECT hostname FROM hosts")
    hosts = [r[0] for r in cursor.fetchall()]
    offset = len(laptops)
    for i, (ip, mac) in enumerate(pool[offset:]):
        if i < len(hosts):
            cursor.execute("UPDATE hosts SET ip=?, mac=? WHERE hostname=?", (ip, mac, hosts[i]))

    conn.commit()
    conn.close()
    print("IP/MAC addresses distributed.")


def assign_apps_servers(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    mapping_rules = {
        'citrix_delivery_controller': 'Citrix Virtual Apps and Desktops',
        'palo_alto_vpn': 'GlobalProtect',
        'microsoft_exchange_server': 'Outlook'
    }
    for ci_tag, app_name in mapping_rules.items():
        cursor.execute("UPDATE hosts SET assigned_app = ? WHERE cmdb_ci = ?", (app_name, ci_tag))
    conn.commit()
    conn.close()
    print("Servers connected to Applications.")


def assign_apps_laptops(db_name):
    """Assigns specific applications to laptops for Triage context."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # In a real environment, we might assign all 3 to every laptop,
    # but for this schema, we will link them to the laptop's 'Outlook' capability
    cursor.execute("UPDATE laptops SET assigned_app_laptop = 'Outlook'")

    conn.commit()
    conn.close()
    print("Laptops connected to Applications.")


if __name__ == "__main__":
    db_name = "itam.db"
    base_path = r"D:\OneDrive\Python\Automation\IT_Infrastructure_Health_Monitor\generate_mockup_data\data"

    json_files = {
        "ip_mac": os.path.join(base_path, "ip_mac.json"),
        "users": os.path.join(base_path, "users.json"),
        "laptops": os.path.join(base_path, "laptops.json"),
        "hosts": os.path.join(base_path, "hosts.json"),
        "applications": os.path.join(base_path, "apps.json")
    }

    create_database(db_name)
    print(f"Database created at {db_name}")

    for table, file_path in json_files.items():
        if os.path.exists(file_path):
            insert_data(db_name, table, load_data(file_path))

    assign_laptops(db_name)
    assign_ip_mac_addresses(db_name)
    assign_apps_servers(db_name)
    assign_apps_laptops(db_name)

    print(f"\nSUCCESS: Database created at: {db_name}")