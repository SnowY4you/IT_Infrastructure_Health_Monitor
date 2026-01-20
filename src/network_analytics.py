from src.db_manager import ITAMDatabase
from collections import Counter


class NetworkAnalytics:
    def __init__(self):
        self.db = ITAMDatabase()

    def get_service_tags_from_db(self):
        """
        Dynamically builds a mapping of IP addresses to Service Names 
        from the Hosts and Applications tables.
        """
        query = """
            SELECT h.ip, a.app_name 
            FROM hosts h
            JOIN applications a ON h.assigned_app = a.app_name
            WHERE h.ip IS NOT NULL
        """
        rows = self.db._execute_query(query)
        # Returns: {'10.20.1.50': 'Citrix Virtual Apps and Desktops', ...}
        return {row['ip']: row['app_name'] for row in rows}

    def get_grouped_flows(self, raw_traffic_data):
        """
        Enriches raw traffic data with Service Tags and Device Context.
        """
        service_map = self.get_service_tags_from_db()

        for flow in raw_traffic_data:
            dest_ip = flow.get('dest_ip')
            # Tag the traffic based on our DB infrastructure map
            flow['service_tag'] = service_map.get(dest_ip, "Unknown Infrastructure")

        return raw_traffic_data

    def calculate_health_distribution(self):
        """
        Analytics: Provides a breakdown of status percentages for the Dashboard.
        Useful for Pie Charts.
        """
        query = "SELECT status, COUNT(*) as count FROM hosts GROUP BY status"
        results = self.db._execute_query(query)
        return {row['status']: row['count'] for row in results}

    def get_impact_report(self):
        """
        RCA Analytics: If a host is DOWN, which Users and Laptops are affected?
        This links User -> Laptop -> App -> Host.
        """
        query = """
            SELECT u.first_name || ' ' || u.last_name as user_name, 
                   l.hostname as laptop, 
                   h.hostname as server, 
                   h.assigned_app
            FROM users u
            JOIN laptops l ON u.userid = l.assigned_user
            JOIN hosts h ON l.assigned_app_laptop = h.assigned_app
            WHERE h.status = 'DOWN'
        """
        return self.db._execute_query(query)


# Example Usage for Testing
if __name__ == "__main__":
    analytics = NetworkAnalytics()

    # Mock traffic data from a firewall or router
    mock_traffic = [
        {'src_ip': '192.168.1.15', 'dest_ip': '10.20.1.50', 'bytes': 5000},
        {'src_ip': '192.168.1.20', 'dest_ip': '8.8.8.8', 'bytes': 1200}
    ]

    enriched = analytics.get_grouped_flows(mock_traffic)
    print("Enriched Traffic Flow:", enriched)

    print("\nHealth Distribution:", analytics.calculate_health_distribution())