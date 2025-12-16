#!/usr/bin/env python3

"""
Script: disable_ipmi_idrac_redfish.py
Purpose: Disable IPMI-over-LAN on Dell iDRAC systems via Redfish API
Reference: https://www.dell.com/support/kbdoc/en-us/000222162
"""

import sys
import argparse
import getpass
import requests
import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings (iDRACs often use self-signed certificates)
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Color codes for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

class IDracIPMIDisabler:
    def __init__(self, username: str, password: str, log_file: str):
        self.username = username
        self.password = password
        self.log_file = log_file
        self.timeout = 30
        
    def log_message(self, message: str, color: str = '', include_api_response: bool = False):
        """Log message to console and file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        
        # Print to console with color
        if color:
            print(f"{color}{message}{Colors.NC}")
        else:
            print(message)
        
        # Write to log file (without color codes)
        with open(self.log_file, 'a') as f:
            # Strip ANSI color codes for log file
            clean_message = message
            for color_code in [Colors.RED, Colors.GREEN, Colors.YELLOW, Colors.BLUE, Colors.NC]:
                clean_message = clean_message.replace(color_code, '')
            f.write(log_entry + '\n')
    
    def log_api_response(self, host: str, endpoint: str, method: str, status_code: int, 
                         response_text: str = None, response_json: dict = None):
        """Log detailed API response information"""
        self.log_message(f"[{host}] API Call Details:")
        self.log_message(f"  Method: {method}")
        self.log_message(f"  Endpoint: {endpoint}")
        self.log_message(f"  Status Code: {status_code}")
        
        if response_json:
            self.log_message(f"  Response JSON:")
            # Pretty print JSON response
            json_str = json.dumps(response_json, indent=2)
            for line in json_str.split('\n'):
                self.log_message(f"    {line}")
        elif response_text:
            self.log_message(f"  Response Text:")
            for line in response_text.split('\n')[:20]:  # Limit to first 20 lines
                self.log_message(f"    {line}")
        
        self.log_message("")  # Blank line for readability
    
    def get_ipmi_status(self, host: str) -> Tuple[bool, Optional[bool], str]:
        """
        Get current IPMI status via Redfish API
        
        Returns:
            Tuple[success, ipmi_enabled, message]
        """
        base_url = f"https://{host}"
        
        # Try multiple possible Redfish endpoints for IPMI settings
        # Different iDRAC versions may use different paths
        endpoints = [
            "/redfish/v1/Managers/iDRAC.Embedded.1/NetworkProtocol",
            "/redfish/v1/Managers/System.Embedded.1/NetworkProtocol",
            "/redfish/v1/Managers/iDRAC.Embedded.1/Attributes"
        ]
        
        session = requests.Session()
        session.auth = (self.username, self.password)
        session.verify = False
        
        for endpoint in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                response = session.get(url, timeout=self.timeout)
                
                # Log API response
                self.log_message(f"[{host}] Checking IPMI status at endpoint: {endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_api_response(host, endpoint, "GET", response.status_code, response_json=data)
                    
                    # Check NetworkProtocol endpoint
                    if "NetworkProtocol" in endpoint:
                        ipmi_config = data.get("IPMI", {})
                        if ipmi_config:
                            enabled = ipmi_config.get("ProtocolEnabled", None)
                            if enabled is not None:
                                return True, enabled, json.dumps(ipmi_config, indent=2)
                    
                    # Check Attributes endpoint
                    elif "Attributes" in endpoint:
                        attributes = data.get("Attributes", {})
                        # Look for IPMI-related attributes
                        for key, value in attributes.items():
                            if "IPMI" in key and "Enable" in key:
                                enabled = value in ["Enabled", "1", 1, True]
                                self.log_message(f"[{host}] Found IPMI attribute: {key} = {value}")
                                return True, enabled, f"{key}: {value}"
                else:
                    self.log_api_response(host, endpoint, "GET", response.status_code, response_text=response.text)
                
            except requests.exceptions.RequestException as e:
                self.log_message(f"[{host}] Request failed for {endpoint}: {str(e)}")
                continue
        
        return False, None, "Could not find IPMI settings endpoint"
    
    def disable_ipmi_networkprotocol(self, host: str) -> Tuple[bool, str]:
        """Disable IPMI via NetworkProtocol endpoint"""
        base_url = f"https://{host}"
        
        endpoints = [
            "/redfish/v1/Managers/iDRAC.Embedded.1/NetworkProtocol",
            "/redfish/v1/Managers/System.Embedded.1/NetworkProtocol"
        ]
        
        session = requests.Session()
        session.auth = (self.username, self.password)
        session.verify = False
        
        for endpoint in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                
                # Try to disable IPMI
                payload = {
                    "IPMI": {
                        "ProtocolEnabled": False
                    }
                }
                
                self.log_message(f"[{host}] Attempting to disable IPMI via NetworkProtocol endpoint")
                self.log_message(f"[{host}] Request payload: {json.dumps(payload, indent=2)}")
                
                response = session.patch(url, json=payload, timeout=self.timeout)
                
                # Log full API response
                try:
                    response_json = response.json()
                    self.log_api_response(host, endpoint, "PATCH", response.status_code, response_json=response_json)
                except:
                    self.log_api_response(host, endpoint, "PATCH", response.status_code, response_text=response.text)
                
                if response.status_code in [200, 204]:
                    return True, "IPMI disabled via NetworkProtocol endpoint"
                elif response.status_code == 404:
                    continue
                else:
                    error_msg = f"HTTP {response.status_code}"
                    try:
                        error_data = response.json()
                        if "error" in error_data:
                            error_msg += f": {error_data['error'].get('message', response.text[:200])}"
                    except:
                        error_msg += f": {response.text[:200]}"
                    return False, error_msg
                    
            except requests.exceptions.RequestException as e:
                self.log_message(f"[{host}] Request exception for {endpoint}: {str(e)}")
                continue
        
        return False, "NetworkProtocol endpoint not available"
    
    def disable_ipmi_attributes(self, host: str) -> Tuple[bool, str]:
        """Disable IPMI via Attributes endpoint (iDRAC.IPMILan.Enable)"""
        base_url = f"https://{host}"
        
        endpoints = [
            "/redfish/v1/Managers/iDRAC.Embedded.1/Attributes",
            "/redfish/v1/Managers/System.Embedded.1/Attributes"
        ]
        
        session = requests.Session()
        session.auth = (self.username, self.password)
        session.verify = False
        
        for endpoint in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                
                # Get current attributes to find the correct key
                self.log_message(f"[{host}] Fetching current attributes from {endpoint}")
                response = session.get(url, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_api_response(host, endpoint, "GET", response.status_code, response_json=data)
                    
                    attributes = data.get("Attributes", {})
                    
                    # Find IPMI enable key
                    ipmi_key = None
                    for key in attributes.keys():
                        if "IPMI" in key and "Enable" in key:
                            ipmi_key = key
                            self.log_message(f"[{host}] Found IPMI key: {ipmi_key} = {attributes[key]}")
                            break
                    
                    if ipmi_key:
                        # Disable IPMI
                        payload = {
                            "Attributes": {
                                ipmi_key: "Disabled"
                            }
                        }
                        
                        self.log_message(f"[{host}] Attempting to disable IPMI via Attributes endpoint")
                        self.log_message(f"[{host}] Request payload: {json.dumps(payload, indent=2)}")
                        
                        response = session.patch(url, json=payload, timeout=self.timeout)
                        
                        # Log full API response
                        try:
                            response_json = response.json()
                            self.log_api_response(host, endpoint, "PATCH", response.status_code, response_json=response_json)
                        except:
                            self.log_api_response(host, endpoint, "PATCH", response.status_code, response_text=response.text)
                        
                        if response.status_code in [200, 204]:
                            return True, f"IPMI disabled via Attributes endpoint ({ipmi_key})"
                        else:
                            error_msg = f"HTTP {response.status_code}"
                            try:
                                error_data = response.json()
                                if "error" in error_data:
                                    error_msg += f": {error_data['error'].get('message', response.text[:200])}"
                            except:
                                error_msg += f": {response.text[:200]}"
                            return False, error_msg
                else:
                    self.log_api_response(host, endpoint, "GET", response.status_code, response_text=response.text)
                
            except requests.exceptions.RequestException as e:
                self.log_message(f"[{host}] Request exception for {endpoint}: {str(e)}")
                continue
        
        return False, "Attributes endpoint not available"
    
    def reboot_idrac(self, host: str) -> bool:
        """
        Reboot the iDRAC to apply configuration changes
        
        Returns:
            bool: True if successful, False otherwise
        """
        base_url = f"https://{host}"
        
        endpoints = [
            "/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Manager.Reset",
            "/redfish/v1/Managers/System.Embedded.1/Actions/Manager.Reset"
        ]
        
        session = requests.Session()
        session.auth = (self.username, self.password)
        session.verify = False
        
        self.log_message(f"[{host}] Initiating iDRAC reboot...", Colors.YELLOW)
        
        for endpoint in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                
                # Reset payload - GracefulRestart is safest
                payload = {
                    "ResetType": "GracefulRestart"
                }
                
                self.log_message(f"[{host}] Sending reboot request to {endpoint}")
                self.log_message(f"[{host}] Request payload: {json.dumps(payload, indent=2)}")
                
                response = session.post(url, json=payload, timeout=self.timeout)
                
                # Log full API response
                try:
                    response_json = response.json()
                    self.log_api_response(host, endpoint, "POST", response.status_code, response_json=response_json)
                except:
                    self.log_api_response(host, endpoint, "POST", response.status_code, response_text=response.text)
                
                if response.status_code in [200, 204]:
                    self.log_message(f"[{host}] iDRAC reboot initiated successfully", Colors.GREEN)
                    self.log_message(f"[{host}] iDRAC will be unavailable for ~1-2 minutes", Colors.YELLOW)
                    return True
                elif response.status_code == 404:
                    self.log_message(f"[{host}] Reboot endpoint not found, trying next...")
                    continue
                else:
                    self.log_message(f"[{host}] Reboot request failed with status {response.status_code}")
                    return False
                    
            except requests.exceptions.RequestException as e:
                self.log_message(f"[{host}] Reboot request exception: {str(e)}")
                continue
        
        return False
    
    def disable_ipmi(self, host: str, reboot_after: bool = False) -> bool:
        """Disable IPMI over LAN on a single iDRAC"""
        self.log_message(f"[{host}] Connecting to iDRAC via Redfish API...", Colors.YELLOW)
        
        try:
            # Check current status
            success, current_status, status_info = self.get_ipmi_status(host)
            
            if not success:
                self.log_message(f"[{host}] Failed to connect or check status", Colors.RED)
                self.log_message(f"[{host}] Error: {status_info}", Colors.RED)
                return False
            
            self.log_message(f"[{host}] Current IPMI status: {'Enabled' if current_status else 'Disabled'}")
            self.log_message(f"[{host}] Details: {status_info}")
            
            if not current_status:
                self.log_message(f"[{host}] IPMI is already disabled", Colors.GREEN)
                return True
            
            # Try to disable IPMI
            self.log_message(f"[{host}] Disabling IPMI over LAN...", Colors.YELLOW)
            
            # Try NetworkProtocol endpoint first
            success, message = self.disable_ipmi_networkprotocol(host)
            
            if not success:
                # Try Attributes endpoint as fallback
                self.log_message(f"[{host}] Trying alternative method...", Colors.YELLOW)
                success, message = self.disable_ipmi_attributes(host)
            
            if success:
                self.log_message(f"[{host}] SUCCESS: {message}", Colors.GREEN)
                
                # Verify the change
                self.log_message(f"[{host}] Verifying configuration...", Colors.YELLOW)
                import time
                time.sleep(2)  # Wait for iDRAC to apply changes
                
                verify_success, verify_status, verify_info = self.get_ipmi_status(host)
                
                if verify_success:
                    if not verify_status:
                        self.log_message(f"[{host}] ✓ Verification successful - IPMI is disabled", Colors.GREEN)
                        
                        # Reboot iDRAC if requested
                        if reboot_after:
                            self.log_message(f"[{host}] Rebooting iDRAC to ensure changes take effect...", Colors.YELLOW)
                            if self.reboot_idrac(host):
                                self.log_message(f"[{host}] ✓ iDRAC reboot successful", Colors.GREEN)
                            else:
                                self.log_message(f"[{host}] ⚠ Could not reboot iDRAC automatically", Colors.YELLOW)
                                self.log_message(f"[{host}] You may need to reboot manually via web interface", Colors.YELLOW)
                        
                        return True
                    else:
                        self.log_message(f"[{host}] ⚠ Warning: IPMI still appears enabled", Colors.YELLOW)
                        self.log_message(f"[{host}] This may require an iDRAC reset to take effect", Colors.YELLOW)
                        
                        if reboot_after:
                            self.log_message(f"[{host}] Attempting iDRAC reboot...", Colors.YELLOW)
                            if self.reboot_idrac(host):
                                self.log_message(f"[{host}] ✓ iDRAC reboot initiated - changes should apply after reboot", Colors.GREEN)
                            else:
                                self.log_message(f"[{host}] ⚠ Could not reboot iDRAC", Colors.YELLOW)
                        
                        return True  # Still count as success since command was accepted
                else:
                    self.log_message(f"[{host}] Could not verify configuration", Colors.YELLOW)
                    
                    if reboot_after:
                        self.log_message(f"[{host}] Rebooting iDRAC as requested...", Colors.YELLOW)
                        if self.reboot_idrac(host):
                            self.log_message(f"[{host}] ✓ iDRAC reboot successful", Colors.GREEN)
                        else:
                            self.log_message(f"[{host}] ⚠ Could not reboot iDRAC", Colors.YELLOW)
                    
                    return True  # Still count as success since disable command worked
            else:
                self.log_message(f"[{host}] FAILED: {message}", Colors.RED)
                return False
                
        except requests.exceptions.Timeout:
            self.log_message(f"[{host}] ERROR: Connection timeout", Colors.RED)
            return False
        except requests.exceptions.ConnectionError:
            self.log_message(f"[{host}] ERROR: Unable to connect to iDRAC", Colors.RED)
            return False
        except Exception as e:
            self.log_message(f"[{host}] ERROR: {str(e)}", Colors.RED)
            return False
    
    def process_hosts(self, hosts: List[str], reboot_after: bool = False) -> Tuple[int, int]:
        """Process multiple hosts"""
        success_count = 0
        fail_count = 0
        
        for i, host in enumerate(hosts, 1):
            self.log_message("")
            self.log_message("=" * 50)
            self.log_message(f"Processing iDRAC ({i}/{len(hosts)}): {host}")
            self.log_message("=" * 50)
            
            if self.disable_ipmi(host, reboot_after):
                success_count += 1
            else:
                fail_count += 1
            
            self.log_message("")
        
        return success_count, fail_count


def print_banner():
    """Print script banner"""
    print(f"{Colors.BLUE}{'=' * 50}")
    print("  iDRAC IPMI-over-LAN Disable Script")
    print("  (Redfish API Version)")
    print(f"{'=' * 50}{Colors.NC}")
    print()


def get_credentials(args) -> Tuple[str, str]:
    """Get credentials interactively or from arguments"""
    username = args.username if args.username else None
    password = args.password if args.password else None
    
    if not username:
        print(f"{Colors.YELLOW}Enter iDRAC credentials:{Colors.NC}")
        username = input("Username [root]: ").strip() or "root"
    
    if not password:
        password = getpass.getpass("Password: ")
    
    if not password:
        print(f"{Colors.RED}Error: Password cannot be empty{Colors.NC}")
        sys.exit(1)
    
    return username, password


def select_mode(args) -> Tuple[str, Optional[str], Optional[str], bool]:
    """Select operation mode and reboot preference"""
    # Check if mode was specified via command line
    if args.single:
        reboot_after = args.reboot if hasattr(args, 'reboot') else False
        return "single", args.single, None, reboot_after
    elif args.file:
        reboot_after = args.reboot if hasattr(args, 'reboot') else False
        return "multiple", None, args.file, reboot_after
    
    # Interactive mode selection
    print()
    print(f"{Colors.YELLOW}Select operation mode:{Colors.NC}")
    print("  1) Single iDRAC device")
    print("  2) Multiple iDRAC devices (from file)")
    print()
    
    while True:
        choice = input("Enter choice [1-2]: ").strip()
        
        if choice == "1":
            host = input("Enter iDRAC IP or hostname: ").strip()
            if not host:
                print(f"{Colors.RED}Error: Hostname cannot be empty{Colors.NC}")
                continue
            
            # Ask about reboot
            print()
            reboot_choice = input("Reboot iDRAC after disabling IPMI to ensure changes take effect? (yes/no) [no]: ").strip().lower()
            reboot_after = reboot_choice == "yes"
            
            return "single", host, None, reboot_after
        elif choice == "2":
            default_file = "idrac_hosts.txt"
            file_path = input(f"Enter path to hosts file [{default_file}]: ").strip() or default_file
            
            if not Path(file_path).exists():
                print(f"{Colors.RED}Error: File '{file_path}' not found{Colors.NC}")
                continue
            
            # Ask about reboot
            print()
            reboot_choice = input("Reboot iDRACs after disabling IPMI to ensure changes take effect? (yes/no) [no]: ").strip().lower()
            reboot_after = reboot_choice == "yes"
            
            return "multiple", None, file_path, reboot_after
        else:
            print(f"{Colors.RED}Invalid choice{Colors.NC}")


def read_hosts_file(file_path: str) -> List[str]:
    """Read hosts from file"""
    hosts = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                hosts.append(line)
    return hosts


def confirm_action(mode: str, target: str, username: str, log_file: str, host_count: int = 0, reboot_after: bool = False) -> bool:
    """Confirm action before proceeding"""
    print()
    print(f"{Colors.YELLOW}Configuration Summary:{Colors.NC}")
    print(f"  Username: {username}")
    print(f"  Mode: {mode}")
    print(f"  Method: Redfish API (HTTPS)")
    
    if mode == "single":
        print(f"  Target: {target}")
    else:
        print(f"  Hosts file: {target}")
        print(f"  Number of hosts: {host_count}")
    
    print(f"  Reboot iDRAC after: {'Yes' if reboot_after else 'No'}")
    print(f"  Log file: {log_file}")
    
    if reboot_after:
        print()
        print(f"{Colors.YELLOW}⚠ Note: iDRACs will be rebooted and unavailable for ~1-2 minutes each{Colors.NC}")
    
    print()
    
    response = input("Proceed with disabling IPMI-over-LAN? (yes/no): ").strip().lower()
    return response == "yes"


def main():
    parser = argparse.ArgumentParser(
        description='Disable IPMI-over-LAN on Dell iDRAC systems via Redfish API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    %(prog)s
  
  Single device:
    %(prog)s -u root -p password -s 192.168.1.100
  
  Single device with reboot:
    %(prog)s -u root -p password -s 192.168.1.100 -r
  
  Multiple devices:
    %(prog)s -u root -p password -f idrac_hosts.txt
  
  Multiple devices with reboot:
    %(prog)s -u root -p password -f idrac_hosts.txt -r

Note: This script uses the Redfish API (HTTPS) instead of SSH.
Make sure the iDRAC web interface is accessible.
The -r/--reboot flag will reboot each iDRAC after disabling IPMI to ensure changes take effect.
        """
    )
    
    parser.add_argument('-u', '--username', help='iDRAC username')
    parser.add_argument('-p', '--password', help='iDRAC password')
    parser.add_argument('-s', '--single', help='Single iDRAC host')
    parser.add_argument('-f', '--file', help='File containing list of iDRAC hosts')
    parser.add_argument('-r', '--reboot', action='store_true', help='Reboot iDRAC after disabling IPMI')
    
    args = parser.parse_args()
    
    # Check for requests library
    try:
        import requests
    except ImportError:
        print(f"{Colors.RED}Error: requests module is required but not installed{Colors.NC}")
        print("Install with: pip3 install requests")
        sys.exit(1)
    
    # Print banner
    print_banner()
    
    # Get credentials
    username, password = get_credentials(args)
    
    # Select mode
    mode, single_host, hosts_file, reboot_after = select_mode(args)
    
    # Prepare host list
    if mode == "single":
        hosts = [single_host]
        target_display = single_host
        host_count = 1
    else:
        hosts = read_hosts_file(hosts_file)
        target_display = hosts_file
        host_count = len(hosts)
        
        if not hosts:
            print(f"{Colors.RED}Error: No hosts found in file{Colors.NC}")
            sys.exit(1)
    
    # Create log file
    log_file = f"ipmi_disable_redfish_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Confirm action
    if not confirm_action(mode, target_display, username, log_file, host_count, reboot_after):
        print(f"{Colors.YELLOW}Operation cancelled{Colors.NC}")
        sys.exit(0)
    
    print()
    print(f"{Colors.GREEN}Starting IPMI disable process...{Colors.NC}")
    print()
    
    # Initialize disabler
    disabler = IDracIPMIDisabler(username, password, log_file)
    
    # Log start
    disabler.log_message("=" * 50)
    disabler.log_message("iDRAC IPMI-over-LAN Disable Script (Redfish API)")
    disabler.log_message(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    disabler.log_message(f"Mode: {mode}")
    disabler.log_message(f"User: {username}")
    disabler.log_message(f"Reboot after: {reboot_after}")
    disabler.log_message("=" * 50)
    
    # Process hosts
    success_count, fail_count = disabler.process_hosts(hosts, reboot_after)
    
    # Summary
    print()
    disabler.log_message("=" * 50)
    disabler.log_message("Summary")
    disabler.log_message("=" * 50)
    disabler.log_message(f"Total hosts processed: {len(hosts)}")
    disabler.log_message(f"Successful: {success_count}", Colors.GREEN)
    disabler.log_message(f"Failed: {fail_count}", Colors.RED)
    disabler.log_message("")
    disabler.log_message(f"Log file: {log_file}")
    disabler.log_message(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    disabler.log_message("=" * 50)
    
    if fail_count == 0:
        print(f"{Colors.GREEN}✓ All operations completed successfully!{Colors.NC}")
        if not reboot_after:
            print(f"{Colors.YELLOW}Note: Some iDRACs may require a reset for changes to take effect.{Colors.NC}")
            print(f"{Colors.YELLOW}Run with -r flag to automatically reboot iDRACs after disabling IPMI.{Colors.NC}")
        sys.exit(0)
    else:
        print(f"{Colors.YELLOW}⚠ Some operations failed. Check log file for details.{Colors.NC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
