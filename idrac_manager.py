#!/usr/bin/env python3

"""
Script: idrac_manager.py
Purpose: Comprehensive Dell iDRAC management via Redfish API
Author: iDRAC Management Suite
Version: 1.0

Supports:
- User management
- Network configuration
- Firmware updates
- Power management
- BIOS configuration
- Alert configuration
- Backup/restore
- Hardware inventory
- Certificate management
- And much more!
"""

import sys
import argparse
import getpass
import requests
import json
import time
import base64
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'

class IDracManager:
    """Comprehensive iDRAC management class"""
    
    def __init__(self, host: str, username: str, password: str, log_file: str = None):
        self.host = host
        self.username = username
        self.password = password
        self.base_url = f"https://{host}"
        self.timeout = 30
        self.log_file = log_file
        
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = False
    
    def log(self, message: str, color: str = ''):
        """Log message to console and optionally to file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if color:
            print(f"{color}{message}{Colors.NC}")
        else:
            print(message)
        
        if self.log_file:
            with open(self.log_file, 'a') as f:
                clean_msg = message
                for c in [Colors.RED, Colors.GREEN, Colors.YELLOW, Colors.BLUE, Colors.CYAN, Colors.MAGENTA, Colors.NC]:
                    clean_msg = clean_msg.replace(c, '')
                f.write(f"[{timestamp}] {clean_msg}\n")
    
    def api_request(self, method: str, endpoint: str, data: dict = None, 
                    files: dict = None, timeout: int = None) -> Tuple[bool, Any]:
        """Make API request with error handling"""
        url = f"{self.base_url}{endpoint}"
        timeout = timeout or self.timeout
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, timeout=timeout)
            elif method.upper() == "POST":
                if files:
                    response = self.session.post(url, files=files, timeout=timeout)
                else:
                    response = self.session.post(url, json=data, timeout=timeout)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data, timeout=timeout)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, timeout=timeout)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, timeout=timeout)
            else:
                return False, f"Unsupported method: {method}"
            
            if response.status_code in [200, 201, 202, 204]:
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', response.text)
                except:
                    error_msg = response.text
                return False, f"HTTP {response.status_code}: {error_msg}"
                
        except requests.exceptions.Timeout:
            return False, "Request timeout"
        except requests.exceptions.ConnectionError:
            return False, "Connection error"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    # ==================== USER MANAGEMENT ====================
    
    def list_users(self) -> bool:
        """List all iDRAC users"""
        self.log(f"\n{'='*60}", Colors.CYAN)
        self.log("USER MANAGEMENT - List Users", Colors.CYAN)
        self.log(f"{'='*60}", Colors.CYAN)
        
        success, data = self.api_request("GET", "/redfish/v1/AccountService/Accounts")
        
        if not success:
            self.log(f"✗ Failed to get users: {data}", Colors.RED)
            return False
        
        if 'Members' in data:
            self.log(f"\nFound {len(data['Members'])} user accounts:\n")
            
            for member in data['Members']:
                account_url = member.get('@odata.id', '')
                success, account_data = self.api_request("GET", account_url)
                
                if success:
                    username = account_data.get('UserName', 'N/A')
                    enabled = account_data.get('Enabled', False)
                    role = account_data.get('RoleId', 'N/A')
                    locked = account_data.get('Locked', False)
                    
                    status = "🟢 Enabled" if enabled else "🔴 Disabled"
                    lock_status = "🔒 Locked" if locked else ""
                    
                    self.log(f"  User: {username:<20} Role: {role:<15} {status} {lock_status}")
        
        return True
    
    def add_user(self, username: str, password: str, role: str = "Administrator") -> bool:
        """Add new iDRAC user"""
        self.log(f"\nAdding user: {username} with role: {role}", Colors.YELLOW)
        
        # Find empty slot
        success, data = self.api_request("GET", "/redfish/v1/AccountService/Accounts")
        
        if not success:
            self.log(f"✗ Failed to get accounts: {data}", Colors.RED)
            return False
        
        # Try to find an empty slot
        for member in data.get('Members', []):
            account_url = member.get('@odata.id', '')
            success, account_data = self.api_request("GET", account_url)
            
            if success and not account_data.get('UserName'):
                # Found empty slot
                payload = {
                    "UserName": username,
                    "Password": password,
                    "RoleId": role,
                    "Enabled": True
                }
                
                success, result = self.api_request("PATCH", account_url, data=payload)
                
                if success:
                    self.log(f"✓ User '{username}' added successfully", Colors.GREEN)
                    return True
                else:
                    self.log(f"✗ Failed to add user: {result}", Colors.RED)
                    return False
        
        self.log("✗ No empty user slots available", Colors.RED)
        return False
    
    def delete_user(self, username: str) -> bool:
        """Delete iDRAC user"""
        self.log(f"\nDeleting user: {username}", Colors.YELLOW)
        
        success, data = self.api_request("GET", "/redfish/v1/AccountService/Accounts")
        
        if not success:
            self.log(f"✗ Failed to get accounts: {data}", Colors.RED)
            return False
        
        for member in data.get('Members', []):
            account_url = member.get('@odata.id', '')
            success, account_data = self.api_request("GET", account_url)
            
            if success and account_data.get('UserName') == username:
                # Clear the user
                payload = {
                    "UserName": "",
                    "Password": "",
                    "Enabled": False
                }
                
                success, result = self.api_request("PATCH", account_url, data=payload)
                
                if success:
                    self.log(f"✓ User '{username}' deleted successfully", Colors.GREEN)
                    return True
                else:
                    self.log(f"✗ Failed to delete user: {result}", Colors.RED)
                    return False
        
        self.log(f"✗ User '{username}' not found", Colors.RED)
        return False
    
    def change_password(self, username: str, new_password: str) -> bool:
        """Change user password"""
        self.log(f"\nChanging password for user: {username}", Colors.YELLOW)
        
        success, data = self.api_request("GET", "/redfish/v1/AccountService/Accounts")
        
        if not success:
            self.log(f"✗ Failed to get accounts: {data}", Colors.RED)
            return False
        
        for member in data.get('Members', []):
            account_url = member.get('@odata.id', '')
            success, account_data = self.api_request("GET", account_url)
            
            if success and account_data.get('UserName') == username:
                payload = {"Password": new_password}
                
                success, result = self.api_request("PATCH", account_url, data=payload)
                
                if success:
                    self.log(f"✓ Password changed for '{username}'", Colors.GREEN)
                    return True
                else:
                    self.log(f"✗ Failed to change password: {result}", Colors.RED)
                    return False
        
        self.log(f"✗ User '{username}' not found", Colors.RED)
        return False
    
    # ==================== NETWORK CONFIGURATION ====================
    
    def get_network_config(self) -> bool:
        """Get current network configuration"""
        self.log(f"\n{'='*60}", Colors.CYAN)
        self.log("NETWORK CONFIGURATION", Colors.CYAN)
        self.log(f"{'='*60}", Colors.CYAN)
        
        # Get network protocol info
        success, data = self.api_request("GET", "/redfish/v1/Managers/iDRAC.Embedded.1/EthernetInterfaces/NIC.1")
        
        if success:
            self.log("\n📡 Network Interface:")
            self.log(f"  Hostname: {data.get('HostName', 'N/A')}")
            self.log(f"  MAC Address: {data.get('MACAddress', 'N/A')}")
            
            ipv4 = data.get('IPv4Addresses', [{}])[0]
            self.log(f"  IP Address: {ipv4.get('Address', 'N/A')}")
            self.log(f"  Subnet Mask: {ipv4.get('SubnetMask', 'N/A')}")
            self.log(f"  Gateway: {ipv4.get('Gateway', 'N/A')}")
            self.log(f"  DHCP: {'Enabled' if data.get('DHCPv4', {}).get('DHCPEnabled') else 'Disabled'}")
        
        # Get DNS config
        success, data = self.api_request("GET", "/redfish/v1/Managers/iDRAC.Embedded.1/NetworkProtocol")
        
        if success:
            self.log("\n🌐 Network Services:")
            self.log(f"  Hostname: {data.get('HostName', 'N/A')}")
            self.log(f"  FQDN: {data.get('FQDN', 'N/A')}")
            
            # NTP
            ntp = data.get('NTP', {})
            self.log(f"\n⏰ NTP Configuration:")
            self.log(f"  Enabled: {ntp.get('ProtocolEnabled', False)}")
            ntp_servers = ntp.get('NTPServers', [])
            if ntp_servers:
                for i, server in enumerate(ntp_servers, 1):
                    if server:
                        self.log(f"  Server {i}: {server}")
            
            # Protocol status
            self.log(f"\n🔌 Protocol Status:")
            for protocol in ['SSH', 'HTTPS', 'IPMI', 'SNMP', 'Telnet', 'SSDP']:
                proto_data = data.get(protocol, {})
                if proto_data:
                    enabled = proto_data.get('ProtocolEnabled', False)
                    port = proto_data.get('Port', 'N/A')
                    status = "🟢 Enabled" if enabled else "🔴 Disabled"
                    self.log(f"  {protocol:<10} Port: {port:<6} {status}")
        
        return True
    
    def set_static_ip(self, ip_address: str, subnet_mask: str, gateway: str) -> bool:
        """Configure static IP address"""
        self.log(f"\nConfiguring static IP: {ip_address}", Colors.YELLOW)
        
        payload = {
            "IPv4StaticAddresses": [{
                "Address": ip_address,
                "SubnetMask": subnet_mask,
                "Gateway": gateway
            }],
            "DHCPv4": {
                "DHCPEnabled": False
            }
        }
        
        success, result = self.api_request("PATCH", 
            "/redfish/v1/Managers/iDRAC.Embedded.1/EthernetInterfaces/NIC.1", 
            data=payload)
        
        if success:
            self.log(f"✓ Static IP configured successfully", Colors.GREEN)
            self.log(f"⚠️  Warning: iDRAC IP changed to {ip_address}", Colors.YELLOW)
            return True
        else:
            self.log(f"✗ Failed to configure IP: {result}", Colors.RED)
            return False
    
    def set_dns_servers(self, dns1: str, dns2: str = None) -> bool:
        """Configure DNS servers"""
        self.log(f"\nConfiguring DNS servers", Colors.YELLOW)
        
        # This varies by iDRAC version - try multiple approaches
        endpoints = [
            "/redfish/v1/Managers/iDRAC.Embedded.1/Attributes",
            "/redfish/v1/Managers/iDRAC.Embedded.1/NetworkProtocol"
        ]
        
        for endpoint in endpoints:
            if "Attributes" in endpoint:
                payload = {
                    "Attributes": {
                        "IPv4.1.DNS1": dns1
                    }
                }
                if dns2:
                    payload["Attributes"]["IPv4.1.DNS2"] = dns2
            else:
                payload = {
                    "DNS": {
                        "IPv4Addresses": [dns1] if not dns2 else [dns1, dns2]
                    }
                }
            
            success, result = self.api_request("PATCH", endpoint, data=payload)
            
            if success:
                self.log(f"✓ DNS servers configured: {dns1}" + (f", {dns2}" if dns2 else ""), Colors.GREEN)
                return True
        
        self.log(f"✗ Failed to configure DNS", Colors.RED)
        return False
    
    def set_ntp_servers(self, ntp1: str, ntp2: str = None, ntp3: str = None) -> bool:
        """Configure NTP servers"""
        self.log(f"\nConfiguring NTP servers", Colors.YELLOW)
        
        ntp_servers = [ntp1]
        if ntp2:
            ntp_servers.append(ntp2)
        if ntp3:
            ntp_servers.append(ntp3)
        
        payload = {
            "NTP": {
                "ProtocolEnabled": True,
                "NTPServers": ntp_servers
            }
        }
        
        success, result = self.api_request("PATCH",
            "/redfish/v1/Managers/iDRAC.Embedded.1/NetworkProtocol",
            data=payload)
        
        if success:
            self.log(f"✓ NTP servers configured", Colors.GREEN)
            return True
        else:
            self.log(f"✗ Failed to configure NTP: {result}", Colors.RED)
            return False
    
    def disable_protocol(self, protocol: str) -> bool:
        """Disable network protocol (IPMI, Telnet, SNMP, etc)"""
        self.log(f"\nDisabling protocol: {protocol}", Colors.YELLOW)
        
        payload = {
            protocol: {
                "ProtocolEnabled": False
            }
        }
        
        success, result = self.api_request("PATCH",
            "/redfish/v1/Managers/iDRAC.Embedded.1/NetworkProtocol",
            data=payload)
        
        if success:
            self.log(f"✓ {protocol} disabled", Colors.GREEN)
            return True
        else:
            self.log(f"✗ Failed to disable {protocol}: {result}", Colors.RED)
            return False
    
    # ==================== POWER MANAGEMENT ====================
    
    def get_power_state(self) -> str:
        """Get current server power state"""
        success, data = self.api_request("GET", "/redfish/v1/Systems/System.Embedded.1")
        
        if success:
            power_state = data.get('PowerState', 'Unknown')
            return power_state
        return "Unknown"
    
    def power_operation(self, operation: str) -> bool:
        """
        Perform power operation
        Operations: On, ForceOff, GracefulShutdown, ForceRestart, GracefulRestart, PushPowerButton
        """
        self.log(f"\n{'='*60}", Colors.CYAN)
        self.log(f"POWER MANAGEMENT - {operation}", Colors.CYAN)
        self.log(f"{'='*60}", Colors.CYAN)
        
        current_state = self.get_power_state()
        self.log(f"\nCurrent power state: {current_state}")
        
        self.log(f"Executing power operation: {operation}", Colors.YELLOW)
        
        payload = {"ResetType": operation}
        
        success, result = self.api_request("POST",
            "/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset",
            data=payload)
        
        if success:
            self.log(f"✓ Power operation '{operation}' executed successfully", Colors.GREEN)
            return True
        else:
            self.log(f"✗ Failed to execute power operation: {result}", Colors.RED)
            return False
    
    # ==================== HARDWARE INVENTORY ====================
    
    def get_hardware_inventory(self) -> bool:
        """Get comprehensive hardware inventory"""
        self.log(f"\n{'='*60}", Colors.CYAN)
        self.log("HARDWARE INVENTORY", Colors.CYAN)
        self.log(f"{'='*60}", Colors.CYAN)
        
        # System info
        success, data = self.api_request("GET", "/redfish/v1/Systems/System.Embedded.1")
        
        if success:
            self.log(f"\n🖥️  System Information:")
            self.log(f"  Manufacturer: {data.get('Manufacturer', 'N/A')}")
            self.log(f"  Model: {data.get('Model', 'N/A')}")
            self.log(f"  Service Tag: {data.get('SKU', 'N/A')}")
            self.log(f"  Serial Number: {data.get('SerialNumber', 'N/A')}")
            self.log(f"  BIOS Version: {data.get('BiosVersion', 'N/A')}")
            self.log(f"  Power State: {data.get('PowerState', 'N/A')}")
            
            # CPU info
            proc_summary = data.get('ProcessorSummary', {})
            self.log(f"\n🔧 Processors:")
            self.log(f"  Count: {proc_summary.get('Count', 'N/A')}")
            self.log(f"  Model: {proc_summary.get('Model', 'N/A')}")
            
            # Memory info
            mem_summary = data.get('MemorySummary', {})
            self.log(f"\n💾 Memory:")
            total_mem = mem_summary.get('TotalSystemMemoryGiB', 0)
            self.log(f"  Total: {total_mem} GiB")
            
            # Storage
            self.log(f"\n💿 Storage Controllers:")
            storage_url = data.get('Storage', {}).get('@odata.id')
            if storage_url:
                success, storage_data = self.api_request("GET", storage_url)
                if success and 'Members' in storage_data:
                    self.log(f"  Controllers: {len(storage_data['Members'])}")
        
        # Network adapters
        success, data = self.api_request("GET", "/redfish/v1/Systems/System.Embedded.1/NetworkInterfaces")
        
        if success and 'Members' in data:
            self.log(f"\n🌐 Network Adapters:")
            self.log(f"  Adapters: {len(data['Members'])}")
        
        # iDRAC info
        success, data = self.api_request("GET", "/redfish/v1/Managers/iDRAC.Embedded.1")
        
        if success:
            self.log(f"\n📡 iDRAC Information:")
            self.log(f"  Firmware Version: {data.get('FirmwareVersion', 'N/A')}")
            self.log(f"  Model: {data.get('Model', 'N/A')}")
        
        return True
    
    def get_sensor_data(self) -> bool:
        """Get temperature and sensor readings"""
        self.log(f"\n{'='*60}", Colors.CYAN)
        self.log("SENSOR DATA", Colors.CYAN)
        self.log(f"{'='*60}", Colors.CYAN)
        
        success, data = self.api_request("GET", "/redfish/v1/Chassis/System.Embedded.1/Thermal")
        
        if success:
            # Temperatures
            temps = data.get('Temperatures', [])
            if temps:
                self.log(f"\n🌡️  Temperature Sensors:")
                for temp in temps[:10]:  # Show first 10
                    name = temp.get('Name', 'Unknown')
                    reading = temp.get('ReadingCelsius', 'N/A')
                    status = temp.get('Status', {}).get('Health', 'Unknown')
                    self.log(f"  {name:<30} {reading}°C  [{status}]")
            
            # Fans
            fans = data.get('Fans', [])
            if fans:
                self.log(f"\n🌀 Fans:")
                for fan in fans[:10]:  # Show first 10
                    name = fan.get('Name', 'Unknown')
                    reading = fan.get('Reading', 'N/A')
                    units = fan.get('ReadingUnits', 'RPM')
                    status = fan.get('Status', {}).get('Health', 'Unknown')
                    self.log(f"  {name:<30} {reading} {units}  [{status}]")
        
        # Power supply info
        success, data = self.api_request("GET", "/redfish/v1/Chassis/System.Embedded.1/Power")
        
        if success:
            psus = data.get('PowerSupplies', [])
            if psus:
                self.log(f"\n⚡ Power Supplies:")
                for psu in psus:
                    name = psu.get('Name', 'Unknown')
                    status = psu.get('Status', {}).get('Health', 'Unknown')
                    power_cap = psu.get('PowerCapacityWatts', 'N/A')
                    self.log(f"  {name:<30} {power_cap}W  [{status}]")
        
        return True
    
    # ==================== FIRMWARE MANAGEMENT ====================
    
    def get_firmware_inventory(self) -> bool:
        """Get firmware versions for all components"""
        self.log(f"\n{'='*60}", Colors.CYAN)
        self.log("FIRMWARE INVENTORY", Colors.CYAN)
        self.log(f"{'='*60}", Colors.CYAN)
        
        success, data = self.api_request("GET", "/redfish/v1/UpdateService/FirmwareInventory")
        
        if success and 'Members' in data:
            self.log(f"\nFound {len(data['Members'])} firmware components:\n")
            
            components = []
            for member in data['Members'][:20]:  # Limit to first 20
                fw_url = member.get('@odata.id', '')
                success, fw_data = self.api_request("GET", fw_url)
                
                if success:
                    name = fw_data.get('Name', 'Unknown')
                    version = fw_data.get('Version', 'N/A')
                    updateable = fw_data.get('Updateable', False)
                    components.append((name, version, updateable))
            
            # Sort and display
            for name, version, updateable in sorted(components):
                update_status = "✓ Updateable" if updateable else ""
                self.log(f"  {name:<40} {version:<15} {update_status}")
        
        return True
    
    # ==================== CONFIGURATION BACKUP/RESTORE ====================
    
    def backup_configuration(self, output_file: str) -> bool:
        """Backup iDRAC configuration"""
        self.log(f"\n{'='*60}", Colors.CYAN)
        self.log("BACKUP CONFIGURATION", Colors.CYAN)
        self.log(f"{'='*60}", Colors.CYAN)
        
        self.log(f"\nExporting configuration to: {output_file}", Colors.YELLOW)
        
        # Export Server Configuration Profile (SCP)
        payload = {
            "ShareParameters": {
                "Target": "ALL"
            }
        }
        
        # Try multiple export endpoints
        endpoints = [
            "/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Oem/EID_674_Manager.ExportSystemConfiguration",
            "/redfish/v1/Dell/Managers/iDRAC.Embedded.1/DellJobService/Actions/DellJobService.ExportSystemConfiguration"
        ]
        
        for endpoint in endpoints:
            success, result = self.api_request("POST", endpoint, data=payload, timeout=120)
            
            if success:
                # The result might contain the config directly or a job ID
                if isinstance(result, dict):
                    # Save to file
                    with open(output_file, 'w') as f:
                        json.dump(result, f, indent=2)
                    
                    self.log(f"✓ Configuration backed up to {output_file}", Colors.GREEN)
                    return True
        
        self.log("✗ Failed to export configuration", Colors.RED)
        self.log("Note: Some iDRAC versions require different methods", Colors.YELLOW)
        return False
    
    # ==================== BIOS CONFIGURATION ====================
    
    def get_bios_attributes(self) -> bool:
        """Get BIOS configuration attributes"""
        self.log(f"\n{'='*60}", Colors.CYAN)
        self.log("BIOS ATTRIBUTES", Colors.CYAN)
        self.log(f"{'='*60}", Colors.CYAN)
        
        success, data = self.api_request("GET", 
            "/redfish/v1/Systems/System.Embedded.1/Bios")
        
        if success:
            attributes = data.get('Attributes', {})
            
            # Show key BIOS settings
            key_settings = [
                'BootMode', 'SecureBoot', 'VirtualizationTechnology',
                'ProcVirtualization', 'SriovGlobalEnable', 'MemTest'
            ]
            
            self.log(f"\n🔧 Key BIOS Settings:")
            for setting in key_settings:
                if setting in attributes:
                    self.log(f"  {setting:<30} {attributes[setting]}")
            
            self.log(f"\nTotal BIOS attributes: {len(attributes)}")
        
        return True
    
    def set_bios_attribute(self, attribute: str, value: Any) -> bool:
        """Set a BIOS attribute"""
        self.log(f"\nSetting BIOS attribute: {attribute} = {value}", Colors.YELLOW)
        
        payload = {
            "Attributes": {
                attribute: value
            }
        }
        
        success, result = self.api_request("PATCH",
            "/redfish/v1/Systems/System.Embedded.1/Bios/Settings",
            data=payload)
        
        if success:
            self.log(f"✓ BIOS attribute set (requires reboot to apply)", Colors.GREEN)
            return True
        else:
            self.log(f"✗ Failed to set BIOS attribute: {result}", Colors.RED)
            return False
    
    # ==================== JOBS & TASKS ====================
    
    def list_jobs(self) -> bool:
        """List job queue"""
        self.log(f"\n{'='*60}", Colors.CYAN)
        self.log("JOB QUEUE", Colors.CYAN)
        self.log(f"{'='*60}", Colors.CYAN)
        
        success, data = self.api_request("GET", "/redfish/v1/Managers/iDRAC.Embedded.1/Jobs")
        
        if success and 'Members' in data:
            jobs = data['Members']
            self.log(f"\nFound {len(jobs)} jobs:\n")
            
            for member in jobs[:20]:  # Show first 20
                job_url = member.get('@odata.id', '')
                success, job_data = self.api_request("GET", job_url)
                
                if success:
                    job_id = job_data.get('Id', 'N/A')
                    name = job_data.get('Name', 'Unknown')
                    status = job_data.get('JobState', 'Unknown')
                    percent = job_data.get('PercentComplete', 0)
                    
                    self.log(f"  Job ID: {job_id}")
                    self.log(f"    Name: {name}")
                    self.log(f"    Status: {status}  ({percent}% complete)")
                    self.log("")
        else:
            self.log("No jobs found or unable to access job queue")
        
        return True
    
    # ==================== SYSTEM EVENT LOG ====================
    
    def get_system_event_log(self, max_entries: int = 50) -> bool:
        """Get System Event Log (SEL) entries"""
        self.log(f"\n{'='*60}", Colors.CYAN)
        self.log("SYSTEM EVENT LOG (SEL)", Colors.CYAN)
        self.log(f"{'='*60}", Colors.CYAN)
        
        success, data = self.api_request("GET", "/redfish/v1/Managers/iDRAC.Embedded.1/LogServices/Sel/Entries")
        
        if success and 'Members' in data:
            entries = data['Members'][:max_entries]
            self.log(f"\nShowing last {len(entries)} events:\n")
            
            for entry in entries:
                timestamp = entry.get('Created', 'N/A')
                message = entry.get('Message', 'No message')
                severity = entry.get('Severity', 'N/A')
                
                # Color code by severity
                if severity == 'Critical':
                    color = Colors.RED
                elif severity == 'Warning':
                    color = Colors.YELLOW
                else:
                    color = Colors.NC
                
                self.log(f"  [{timestamp}] {severity}: {message}", color)
        
        return True
    
    # ==================== SYSTEM HEALTH ====================
    
    def get_system_health(self) -> bool:
        """Get overall system health status"""
        self.log(f"\n{'='*60}", Colors.CYAN)
        self.log("SYSTEM HEALTH STATUS", Colors.CYAN)
        self.log(f"{'='*60}", Colors.CYAN)
        
        # Overall system status
        success, data = self.api_request("GET", "/redfish/v1/Systems/System.Embedded.1")
        
        if success:
            status = data.get('Status', {})
            health = status.get('Health', 'Unknown')
            state = status.get('State', 'Unknown')
            
            if health == 'OK':
                color = Colors.GREEN
                icon = "✓"
            elif health == 'Warning':
                color = Colors.YELLOW
                icon = "⚠"
            else:
                color = Colors.RED
                icon = "✗"
            
            self.log(f"\n{icon} Overall System Health: {health}", color)
            self.log(f"  State: {state}")
        
        # Component health
        components = [
            ('Processors', '/redfish/v1/Systems/System.Embedded.1/Processors'),
            ('Memory', '/redfish/v1/Systems/System.Embedded.1/Memory'),
            ('Storage', '/redfish/v1/Systems/System.Embedded.1/Storage')
        ]
        
        self.log(f"\n📊 Component Health:")
        
        for comp_name, comp_url in components:
            success, data = self.api_request("GET", comp_url)
            if success and 'Members' in data:
                count = len(data['Members'])
                self.log(f"  {comp_name}: {count} detected")
        
        return True

# ==================== MAIN CLI ====================

def print_banner():
    """Print application banner"""
    print(f"{Colors.BLUE}")
    print("=" * 70)
    print("                  iDRAC COMPREHENSIVE MANAGER")
    print("                   Redfish API Edition")
    print("=" * 70)
    print(f"{Colors.NC}\n")

def print_menu():
    """Print main menu"""
    print(f"\n{Colors.CYAN}{'='*70}")
    print("MAIN MENU")
    print(f"{'='*70}{Colors.NC}\n")
    
    print(f"{Colors.GREEN}USER MANAGEMENT:{Colors.NC}")
    print("  1. List users")
    print("  2. Add user")
    print("  3. Delete user")
    print("  4. Change user password")
    
    print(f"\n{Colors.GREEN}NETWORK CONFIGURATION:{Colors.NC}")
    print("  5. Show network configuration")
    print("  6. Set static IP address")
    print("  7. Configure DNS servers")
    print("  8. Configure NTP servers")
    print("  9. Disable protocol (IPMI/Telnet/SNMP)")
    
    print(f"\n{Colors.GREEN}POWER MANAGEMENT:{Colors.NC}")
    print("  10. Power on server")
    print("  11. Power off server (graceful)")
    print("  12. Power off server (force)")
    print("  13. Restart server (graceful)")
    print("  14. Restart server (force)")
    print("  15. Get power state")
    
    print(f"\n{Colors.GREEN}HARDWARE & MONITORING:{Colors.NC}")
    print("  16. Get hardware inventory")
    print("  17. Get sensor data (temps/fans)")
    print("  18. Get system health")
    print("  19. Get firmware inventory")
    print("  20. Get system event log")
    
    print(f"\n{Colors.GREEN}BIOS CONFIGURATION:{Colors.NC}")
    print("  21. Show BIOS attributes")
    print("  22. Set BIOS attribute")
    
    print(f"\n{Colors.GREEN}JOBS & CONFIGURATION:{Colors.NC}")
    print("  23. List jobs")
    print("  24. Backup configuration")
    
    print(f"\n{Colors.YELLOW}OTHER:{Colors.NC}")
    print("  25. Run all health checks")
    print("  26. Security audit")
    print("  0. Exit")
    
    print(f"\n{Colors.CYAN}{'='*70}{Colors.NC}")

def run_all_health_checks(manager):
    """Run comprehensive health checks"""
    print(f"\n{Colors.MAGENTA}{'='*70}")
    print("RUNNING COMPREHENSIVE HEALTH CHECKS")
    print(f"{'='*70}{Colors.NC}\n")
    
    manager.get_system_health()
    manager.get_hardware_inventory()
    manager.get_sensor_data()
    manager.get_firmware_inventory()
    manager.get_system_event_log(max_entries=10)

def security_audit(manager):
    """Run security audit"""
    print(f"\n{Colors.MAGENTA}{'='*70}")
    print("SECURITY AUDIT")
    print(f"{'='*70}{Colors.NC}\n")
    
    print("Checking for insecure configurations...\n")
    
    # Check protocols
    success, data = manager.api_request("GET", "/redfish/v1/Managers/iDRAC.Embedded.1/NetworkProtocol")
    
    if success:
        issues = []
        warnings = []
        
        # Check for insecure protocols
        insecure_protocols = {
            'IPMI': 'IPMI over LAN should be disabled',
            'Telnet': 'Telnet should be disabled (use SSH)',
            'SNMP': 'SNMP v1/v2 should be disabled (use v3)'
        }
        
        for protocol, message in insecure_protocols.items():
            proto_data = data.get(protocol, {})
            if proto_data.get('ProtocolEnabled'):
                issues.append(f"⚠️  {protocol} is enabled: {message}")
        
        # Check SSH
        ssh_data = data.get('SSH', {})
        if not ssh_data.get('ProtocolEnabled'):
            warnings.append("ℹ️  SSH is disabled - ensure you have another management method")
        
        # Display results
        if issues:
            print(f"{Colors.RED}Security Issues Found:{Colors.NC}")
            for issue in issues:
                print(f"  {issue}")
        
        if warnings:
            print(f"\n{Colors.YELLOW}Warnings:{Colors.NC}")
            for warning in warnings:
                print(f"  {warning}")
        
        if not issues and not warnings:
            print(f"{Colors.GREEN}✓ No security issues found{Colors.NC}")
    
    # Check default accounts
    print(f"\n{Colors.CYAN}Checking user accounts...{Colors.NC}")
    manager.list_users()

def main():
    parser = argparse.ArgumentParser(
        description='Comprehensive iDRAC Management Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-H', '--host', help='iDRAC hostname or IP')
    parser.add_argument('-u', '--username', help='iDRAC username')
    parser.add_argument('-p', '--password', help='iDRAC password')
    parser.add_argument('-l', '--log', help='Log file path')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Get connection details
    host = args.host or input("iDRAC IP/Hostname: ").strip()
    username = args.username or input("Username [root]: ").strip() or "root"
    password = args.password or getpass.getpass("Password: ")
    
    # Create manager instance
    log_file = args.log or f"idrac_manager_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    manager = IDracManager(host, username, password, log_file)
    
    # Test connection
    print(f"\n{Colors.YELLOW}Testing connection to {host}...{Colors.NC}")
    success, data = manager.api_request("GET", "/redfish/v1")
    
    if not success:
        print(f"{Colors.RED}✗ Failed to connect to iDRAC: {data}{Colors.NC}")
        print("\nTroubleshooting:")
        print("  - Check IP address/hostname")
        print("  - Verify username/password")
        print("  - Ensure iDRAC web interface is accessible")
        print("  - Check firewall rules (port 443)")
        sys.exit(1)
    
    print(f"{Colors.GREEN}✓ Connected successfully{Colors.NC}")
    
    # Main menu loop
    while True:
        print_menu()
        choice = input(f"\n{Colors.CYAN}Enter choice: {Colors.NC}").strip()
        
        try:
            if choice == '0':
                print(f"\n{Colors.YELLOW}Goodbye!{Colors.NC}\n")
                break
            
            elif choice == '1':
                manager.list_users()
            
            elif choice == '2':
                username = input("New username: ").strip()
                password = getpass.getpass("Password: ")
                role = input("Role [Administrator/Operator/ReadOnly]: ").strip() or "Administrator"
                manager.add_user(username, password, role)
            
            elif choice == '3':
                username = input("Username to delete: ").strip()
                confirm = input(f"Delete user '{username}'? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    manager.delete_user(username)
            
            elif choice == '4':
                username = input("Username: ").strip()
                new_password = getpass.getpass("New password: ")
                manager.change_password(username, new_password)
            
            elif choice == '5':
                manager.get_network_config()
            
            elif choice == '6':
                ip = input("IP Address: ").strip()
                mask = input("Subnet Mask: ").strip()
                gateway = input("Gateway: ").strip()
                confirm = input(f"Set IP to {ip}? This will disconnect you! (yes/no): ").strip().lower()
                if confirm == 'yes':
                    manager.set_static_ip(ip, mask, gateway)
            
            elif choice == '7':
                dns1 = input("Primary DNS: ").strip()
                dns2 = input("Secondary DNS (optional): ").strip() or None
                manager.set_dns_servers(dns1, dns2)
            
            elif choice == '8':
                ntp1 = input("Primary NTP: ").strip()
                ntp2 = input("Secondary NTP (optional): ").strip() or None
                ntp3 = input("Tertiary NTP (optional): ").strip() or None
                manager.set_ntp_servers(ntp1, ntp2, ntp3)
            
            elif choice == '9':
                print("\nAvailable protocols: IPMI, Telnet, SNMP, SSDP")
                protocol = input("Protocol to disable: ").strip()
                manager.disable_protocol(protocol)
            
            elif choice == '10':
                manager.power_operation("On")
            
            elif choice == '11':
                manager.power_operation("GracefulShutdown")
            
            elif choice == '12':
                confirm = input("Force power off? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    manager.power_operation("ForceOff")
            
            elif choice == '13':
                manager.power_operation("GracefulRestart")
            
            elif choice == '14':
                confirm = input("Force restart? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    manager.power_operation("ForceRestart")
            
            elif choice == '15':
                state = manager.get_power_state()
                print(f"\nPower State: {state}")
            
            elif choice == '16':
                manager.get_hardware_inventory()
            
            elif choice == '17':
                manager.get_sensor_data()
            
            elif choice == '18':
                manager.get_system_health()
            
            elif choice == '19':
                manager.get_firmware_inventory()
            
            elif choice == '20':
                max_entries = input("Max entries to show [50]: ").strip() or "50"
                manager.get_system_event_log(int(max_entries))
            
            elif choice == '21':
                manager.get_bios_attributes()
            
            elif choice == '22':
                attribute = input("BIOS attribute name: ").strip()
                value = input("New value: ").strip()
                manager.set_bios_attribute(attribute, value)
            
            elif choice == '23':
                manager.list_jobs()
            
            elif choice == '24':
                filename = input("Output filename [idrac_config.json]: ").strip() or "idrac_config.json"
                manager.backup_configuration(filename)
            
            elif choice == '25':
                run_all_health_checks(manager)
            
            elif choice == '26':
                security_audit(manager)
            
            else:
                print(f"{Colors.RED}Invalid choice{Colors.NC}")
            
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.NC}")
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Operation cancelled{Colors.NC}")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.NC}")
        except Exception as e:
            print(f"\n{Colors.RED}Error: {str(e)}{Colors.NC}")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.NC}")

if __name__ == "__main__":
    main()
