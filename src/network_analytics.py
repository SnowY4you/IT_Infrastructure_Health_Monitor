# Logic to group flows by Service Tags
SERVICE_TAGS = {
    "10.20.1.50": "Citrix App Server",
    "10.20.1.100": "Palo Alto Firewall",
    "172.16.0.5": "Aruba Access Point"
}

def get_grouped_flows(raw_traffic_data):
    """
    Groups traffic: { 'Service': 'Citrix', 'Source': '192.168.1.5', 'Dest': '10.20.1.50' }
    """
    for flow in raw_traffic_data:
        tag = SERVICE_TAGS.get(flow['dest_ip'], "Unknown Device")
        flow['service_tag'] = tag
    return raw_traffic_data

