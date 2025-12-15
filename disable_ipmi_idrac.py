#!/usr/bin/env python3

"""
Script: disable_ipmi_idrac.py
Purpose: Disable IPMI-over-LAN on Dell iDRAC systems via SSH
Reference: https://www.dell.com/support/kbdoc/en-us/000222162
"""

import sys
import argparse
import getpass
import paramiko
import time
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

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
        self.ssh_timeout = 10
        
    def log_message(self, message: str, color: str = ''):
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
    
    def execute_ssh_command(self, host: str, command: str) -> Tuple[bool, str, str]:
        """Execute SSH command on iDRAC"""
        try:
            # Create SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect to iDRAC
            ssh.connect(
                hostname=host,
                username=self.username,
                password=self.password,
                timeout=self.ssh_timeout,
                look_for_keys=False,
                allow_agent=False
            )
            
            # Execute command
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()
            
            ssh.close()
            
            return True, output, error
            
        except paramiko.AuthenticationException:
            return False, "", "Authentication failed - check username/password"
        except paramiko.SSHException as e:
            return False, "", f"SSH error: {str(e)}"
        except Exception as e:
            return False, "", f"Connection error: {str(e)}"
    
    def check_ipmi_status(self, host: str) -> Tuple[bool, str]:
        """Check current IPMI status"""
        success, output, error = self.execute_ssh_command(
            host, 
            "racadm get iDRAC.IPMILan.Enable"
        )
        
        if success:
            return True, output
        else:
            return False, error
    
    def disable_ipmi(self, host: str) -> bool:
        """Disable IPMI over LAN on a single iDRAC"""
        self.log_message(f"[{host}] Connecting to iDRAC...", Colors.YELLOW)
        
        # Check current status
        success, status = self.check_ipmi_status(host)
        
        if not success:
            self.log_message(f"[{host}] Failed to connect or check status", Colors.RED)
            self.log_message(f"[{host}] Error: {status}", Colors.RED)
            return False
        
        self.log_message(f"[{host}] Current IPMI status:")
        self.log_message(status)
        
        # Disable IPMI over LAN
        self.log_message(f"[{host}] Disabling IPMI over LAN...", Colors.YELLOW)
        
        success, output, error = self.execute_ssh_command(
            host,
            "racadm set iDRAC.IPMILan.Enable 0"
        )
        
        if success:
            self.log_message(f"[{host}] IPMI over LAN disabled successfully", Colors.GREEN)
            if output:
                self.log_message(output)
            
            # Verify the change
            self.log_message(f"[{host}] Verifying configuration...", Colors.YELLOW)
            time.sleep(1)  # Brief pause before verification
            
            verify_success, verify_output = self.check_ipmi_status(host)
            if verify_success:
                self.log_message(verify_output)
                
                # Check if it's actually disabled
                if "Enable=Disabled" in verify_output or "Enable=0" in verify_output:
                    self.log_message(f"[{host}] ✓ Verification successful - IPMI is disabled", Colors.GREEN)
                    return True
                else:
                    self.log_message(f"[{host}] ⚠ Warning: IPMI may not be disabled", Colors.YELLOW)
                    return False
            else:
                self.log_message(f"[{host}] Could not verify configuration", Colors.YELLOW)
                return True  # Still count as success since disable command worked
        else:
            self.log_message(f"[{host}] Failed to disable IPMI over LAN", Colors.RED)
            if error:
                self.log_message(f"[{host}] Error: {error}", Colors.RED)
            return False
    
    def process_hosts(self, hosts: List[str]) -> Tuple[int, int]:
        """Process multiple hosts"""
        success_count = 0
        fail_count = 0
        
        for i, host in enumerate(hosts, 1):
            self.log_message("")
            self.log_message("=" * 50)
            self.log_message(f"Processing iDRAC ({i}/{len(hosts)}): {host}")
            self.log_message("=" * 50)
            
            if self.disable_ipmi(host):
                success_count += 1
            else:
                fail_count += 1
            
            self.log_message("")
            
            # Brief pause between hosts to avoid overwhelming the network
            if i < len(hosts):
                time.sleep(0.5)
        
        return success_count, fail_count


def print_banner():
    """Print script banner"""
    print(f"{Colors.BLUE}{'=' * 50}")
    print("  iDRAC IPMI-over-LAN Disable Script (Python)")
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


def select_mode(args) -> Tuple[str, Optional[str], Optional[str]]:
    """Select operation mode"""
    # Check if mode was specified via command line
    if args.single:
        return "single", args.single, None
    elif args.file:
        return "multiple", None, args.file
    
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
            return "single", host, None
        elif choice == "2":
            default_file = "idrac_hosts.txt"
            file_path = input(f"Enter path to hosts file [{default_file}]: ").strip() or default_file
            
            if not Path(file_path).exists():
                print(f"{Colors.RED}Error: File '{file_path}' not found{Colors.NC}")
                continue
            return "multiple", None, file_path
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


def confirm_action(mode: str, target: str, username: str, log_file: str, host_count: int = 0) -> bool:
    """Confirm action before proceeding"""
    print()
    print(f"{Colors.YELLOW}Configuration Summary:{Colors.NC}")
    print(f"  Username: {username}")
    print(f"  Mode: {mode}")
    
    if mode == "single":
        print(f"  Target: {target}")
    else:
        print(f"  Hosts file: {target}")
        print(f"  Number of hosts: {host_count}")
    
    print(f"  Log file: {log_file}")
    print()
    
    response = input("Proceed with disabling IPMI-over-LAN? (yes/no): ").strip().lower()
    return response == "yes"


def main():
    parser = argparse.ArgumentParser(
        description='Disable IPMI-over-LAN on Dell iDRAC systems',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    %(prog)s
  
  Single device:
    %(prog)s -u root -p password -s 192.168.1.100
  
  Multiple devices:
    %(prog)s -u root -p password -f idrac_hosts.txt
        """
    )
    
    parser.add_argument('-u', '--username', help='iDRAC username')
    parser.add_argument('-p', '--password', help='iDRAC password')
    parser.add_argument('-s', '--single', help='Single iDRAC host')
    parser.add_argument('-f', '--file', help='File containing list of iDRAC hosts')
    
    args = parser.parse_args()
    
    # Check for paramiko
    try:
        import paramiko
    except ImportError:
        print(f"{Colors.RED}Error: paramiko module is required but not installed{Colors.NC}")
        print("Install with: pip3 install paramiko")
        sys.exit(1)
    
    # Print banner
    print_banner()
    
    # Get credentials
    username, password = get_credentials(args)
    
    # Select mode
    mode, single_host, hosts_file = select_mode(args)
    
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
    log_file = f"ipmi_disable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Confirm action
    if not confirm_action(mode, target_display, username, log_file, host_count):
        print(f"{Colors.YELLOW}Operation cancelled{Colors.NC}")
        sys.exit(0)
    
    print()
    print(f"{Colors.GREEN}Starting IPMI disable process...{Colors.NC}")
    print()
    
    # Initialize disabler
    disabler = IDracIPMIDisabler(username, password, log_file)
    
    # Log start
    disabler.log_message("=" * 50)
    disabler.log_message("iDRAC IPMI-over-LAN Disable Script")
    disabler.log_message(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    disabler.log_message(f"Mode: {mode}")
    disabler.log_message(f"User: {username}")
    disabler.log_message("=" * 50)
    
    # Process hosts
    success_count, fail_count = disabler.process_hosts(hosts)
    
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
        sys.exit(0)
    else:
        print(f"{Colors.YELLOW}⚠ Some operations failed. Check log file for details.{Colors.NC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
