import sqlite3

class ITAMDatabase:
    def __init__(self, db_path="itam.db"):
        self.db_path = db_path

    def _execute_query(self, query, params=()):
        """Helper to handle connection lifecycle."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row # Returns results as dictionaries
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def get_device_summary(self, search_text=""):
        """Search across Laptops and Hosts for the Devices Tab."""
        query = """
            SELECT hostname, type, product, ip, cmdb_category 
            FROM laptops WHERE hostname LIKE ? OR ip LIKE ?
            UNION
            SELECT hostname, type, product, ip, cmdb_category 
            FROM hosts WHERE hostname LIKE ? OR ip LIKE ?
        """
        wildcard = f"%{search_text}%"
        return self._execute_query(query, (wildcard, wildcard, wildcard, wildcard))

    def get_app_inventory(self):
        """Fetch all apps for the Apps Tab."""
        return self._execute_query("SELECT * FROM applications ORDER BY app_name ASC")