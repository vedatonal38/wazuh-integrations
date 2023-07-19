# Copyright (C) 2015-2023, Wazuh Inc.

import nmap
import time
import json
import platform

# The function to perform network scan on a host endpoint
def scan_subnet(subnet):
    nm = nmap.PortScanner()
    nm.scan(subnet)
    results = []

    for host in nm.all_hosts():
        for proto in nm[host].all_protocols():
            if proto not in ["tcp", "udp"]:
                continue

            lport = list(nm[host][proto].keys())
            lport.sort()
            # Iterate over each port for the current host and protocol
            for port in lport:
                hostname = ""
                json_output = {
                    'nmap_host': host,
                    'nmap_protocol': proto,
                    'nmap_port': port,
                    'nmap_hostname': "",
                    'nmap_hostname_type': "",
                    'nmap_port_name': "",
                    'nmap_port_state': "",
                    'nmap_port_service': ""
                }
                # Get the first hostname and it’s type
                if nm[host]["hostnames"]:
                    hostname = nm[host]["hostnames"][0]["name"]
                    hostname_type = nm[host]["hostnames"][0]["type"]
                    json_output['nmap_hostname'] = hostname
                    json_output['nmap_hostname_type'] = hostname_type
                # Get the port name if available
                if 'name' in nm[host][proto][port]:
                    json_output['nmap_port_name'] = nm[host][proto][port]['name']       
                # Get the port state if available
                if 'state' in nm[host][proto][port]:
                    json_output['nmap_port_state'] = nm[host][proto][port]['state']
                # Get the port service version if available
                if 'product' in nm[host][proto][port] and 'version' in nm[host][proto][port]:
                    service = nm[host][proto][port]['product'] + " " + nm[host][proto][port]['version']
                    json_output['nmap_port_service'] = service

                results.append(json_output)
    return results

# The function to append the scan results to the active response log file
def append_to_log(results, log_file):
    with open(log_file, "a") as active_response_log:
        for result in results:
            active_response_log.write(json.dumps(result))
            active_response_log.write("\n")
# Specify the address(es) to scan
subnets = ['127.0.0.1']
# path of the log file
if platform.system() == 'Windows':
	log_file = "C:\\Program Files (x86)\\ossec-agent\\active-response\\active-responses.log"
elif platform.system() == 'Linux':
	log_file = "/var/ossec/logs/active-responses.log"
else:
	log_file = "/Library/Ossec/logs/active-responses.log"

for subnet in subnets:
    results = scan_subnet(subnet)
    append_to_log(results, log_file)
    time.sleep(2)
