class SonarDns:
    """DNS checks resource for Sonar API."""
    
    def __init__(self, connection):
        """
        Initialize the DNS checks resource.
        
        :param connection: SonarConnection instance
        """
        self.connection = connection
    
    def get_all(self):
        """
        Get all DNS check details.
        
        :return: API response containing all DNS checks
        """
        return self.connection.get("/dns")
    
    def get(self, dnsv2_check_id):
        """
        Get DNS check detail by ID.
        
        :param dnsv2_check_id: The DNS check ID
        :return: API response containing DNS check details
        """
        return self.connection.get(f"/dns/{dnsv2_check_id}")
    
    def delete(self, dnsv2_check_id):
        """
        Delete DNS check by ID.
        
        :param dnsv2_check_id: The DNS check ID to delete
        :return: API response
        """
        return self.connection.delete(f"/dns/{dnsv2_check_id}")
    
    def create(self, name, fqdn, port=53, resolver="8.8.8.8", expected_response=None, 
               note="", schedule_interval="NONE", resolver_ip_version="IPV4", 
               record_type="A", query_protocol="UDP", compare_options="ANYMATCH", 
               dnssec=False, interval="THIRTYSECONDS", monitor_interval_policy="PARALLEL",
               check_sites=None, notification_groups=None, schedule_id=0,
               notification_report_timeout=1440, verification_policy="SIMPLE"):
        """
        Create a DNS check.
        
        :param name: Required. The check name
        :param fqdn: Required. The host to query
        :param port: Port number (default: 53)
        :param resolver: Resolver address (default: "8.8.8.8")
        :param expected_response: List of expected response strings (default: [])
        :param note: Note string (default: "")
        :param schedule_interval: Schedule interval - NONE, DAILY, WEEKLY, MONTHLY (default: "NONE")
        :param resolver_ip_version: IP version - IPV4 or IPV6 (default: "IPV4")
        :param record_type: Record type - A, AAAA, ANAME, CAA, CERT, CNAME, HINFO, HTTP, MX, NAPTR, NS, PTR, RP, SPF, SRV, TXT (default: "A")
        :param query_protocol: Query protocol - UDP or TCP (default: "UDP")
        :param compare_options: Compare options - EQUALS, CONTAINS, ONEOFF, ANYMATCH (default: "ANYMATCH")
        :param dnssec: Enable DNSSEC (default: False)
        :param interval: Check interval - FIVESECONDS, THIRTYSECONDS, ONEMINUTE, TWOMINUTES, THREEMINUTES, FOURMINUTES, FIVEMINUTES, TENMINUTES, THIRTYMINUTES, HALFDAY, DAY (default: "THIRTYSECONDS")
        :param monitor_interval_policy: Monitor interval policy - PARALLEL, ONCEPERSITE, ONCEPERREGION (default: "PARALLEL")
        :param check_sites: List of site IDs (default: [1])
        :param notification_groups: List of notification group strings (default: [])
        :param schedule_id: Schedule ID (default: 0)
        :param notification_report_timeout: Notification report timeout in minutes (default: 1440)
        :param verification_policy: Verification policy - SIMPLE or MAJORITY (default: "SIMPLE")
        :return: API response containing created DNS check
        """
        if check_sites is None:
            check_sites = [1]
        if notification_groups is None:
            notification_groups = []
        
        # Build payload - send expectedResponse as string (empty string if None/empty)
        if not expected_response:
            expected_response_value = ""
        elif isinstance(expected_response, list):
            expected_response_value = ",".join(str(x) for x in expected_response)
        else:
            expected_response_value = str(expected_response)
        
        payload = {
            "name": name,
            "fqdn": fqdn,
            "port": port,
            "resolver": resolver,
            "expectedResponse": expected_response_value,
            "note": note if note else "",
            "scheduleInterval": schedule_interval,
            "resolverIPVersion": resolver_ip_version,
            "recordType": record_type,
            "queryProtocol": query_protocol,
            "compareOptions": compare_options,
            "dnssec": dnssec,
            "interval": interval,
            "monitorIntervalPolicy": monitor_interval_policy,
            "checkSites": check_sites,
            "notificationGroups": notification_groups,
            "scheduleId": schedule_id,
            "notificationReportTimeout": notification_report_timeout,
            "verificationPolicy": verification_policy
        }
        
        return self.connection.post("/dns", data=payload)

