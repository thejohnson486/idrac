# iDRAC IPMI-over-LAN Disable Script

## Overview
This script automates the process of disabling IPMI-over-LAN on Dell iDRAC systems via SSH. This addresses the security vulnerability documented in Dell's security advisory.

**Reference:** https://www.dell.com/support/kbdoc/en-us/000222162/data-domain-ipmi-v2-0-password-hash-disclosure

## What This Script Does
- Connects to each iDRAC via SSH
- Checks current IPMI-over-LAN status
- Disables IPMI-over-LAN using RACADM command: `racadm set iDRAC.IPMILan.Enable 0`
- Verifies the configuration change
- Logs all actions and results

## Prerequisites

### 1. Install sshpass

#### Ubuntu/Debian
```bash
sudo apt-get install sshpass
```

#### RHEL/CentOS/Fedora
```bash
sudo yum install sshpass
```

#### macOS
sshpass is not available in the default repositories, but can be installed via Homebrew:

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install sshpass
brew install hudochenkov/sshpass/sshpass
```

**Alternative for macOS**: If you prefer not to use Homebrew, use the Python version instead (`disable_ipmi_idrac.py`), which works natively on Mac without additional packages.

#### Verify Installation
```bash
sshpass -V
```

### 2. Enable SSH on iDRAC
SSH must be enabled on each iDRAC system. You can verify/enable it via:
- iDRAC web interface: iDRAC Settings > Network > Services > SSH

## Usage Modes

### macOS Users - Important Note
If you're on macOS and haven't installed Homebrew or prefer a simpler setup, **use the Python version instead** (`disable_ipmi_idrac_redfish.py`). It works out-of-the-box on Mac without any additional system packages.

The Bash script will work fine on Mac if you have Homebrew and sshpass installed, but the Python version is easier to set up.

### Interactive Mode (Recommended for First-Time Users)
Simply run the script with no arguments and follow the prompts:
```bash
chmod +x disable_ipmi_idrac.sh
./disable_ipmi_idrac.sh
```

The script will interactively ask you for:
1. **Username** (default: root)
2. **Password** (hidden input)
3. **Operation mode**:
   - Single device (you'll enter one IP/hostname)
   - Multiple devices (reads from file)
4. **Confirmation** before making changes

#### Example Interactive Session:
```
==========================================
  iDRAC IPMI-over-LAN Disable Script
==========================================

Enter iDRAC credentials:
Username [root]: root
Password: ********

Select operation mode:
  1) Single iDRAC device
  2) Multiple iDRAC devices (from file)

Enter choice [1-2]: 1
Enter iDRAC IP or hostname: 192.168.1.100

Configuration Summary:
  Username: root
  Mode: single
  Target: 192.168.1.100
  Log file: ipmi_disable_20251215_103000.log

Proceed with disabling IPMI-over-LAN? (yes/no): yes
```

### Command Line Mode

#### Single Device
```bash
./disable_ipmi_idrac.sh -u root -p YourPassword -s 192.168.1.100
```

#### Multiple Devices
First, create `idrac_hosts.txt` with your iDRAC IPs (one per line):
```
192.168.1.100
192.168.1.101
idrac-server1.domain.com
```

Then run:
```bash
./disable_ipmi_idrac.sh -u root -p YourPassword -f idrac_hosts.txt
```

### Command Line Options
- `-u USERNAME` : iDRAC username (skips interactive prompt)
- `-p PASSWORD` : iDRAC password (skips interactive prompt)
- `-s HOSTNAME` : Single iDRAC host (enables single device mode)
- `-f FILE` : Path to hosts file for multiple devices (default: idrac_hosts.txt)
- `-h` : Show help message

## Example Output
```
==========================================
iDRAC IPMI-over-LAN Disable Script
Started: Mon Dec 15 10:30:00 CST 2025
==========================================

==========================================
Processing iDRAC: 192.168.1.100
==========================================
[192.168.1.100] Connecting to iDRAC...
[192.168.1.100] Current IPMI status:
[Key=iDRAC.Embedded.1#IPMILan.1#Enable]
Enable=Enabled
[192.168.1.100] Disabling IPMI over LAN...
[192.168.1.100] IPMI over LAN disabled successfully
Object value modified successfully
[192.168.1.100] Verifying configuration...
[Key=iDRAC.Embedded.1#IPMILan.1#Enable]
Enable=Disabled

==========================================
Summary
==========================================
Total hosts processed: 5
Successful: 5
Failed: 0

Log file: ipmi_disable_20251215_103000.log
Completed: Mon Dec 15 10:35:00 CST 2025
==========================================
```

## Security Considerations

1. **Password Security**: The password is passed via command line. For better security:
   - Use environment variables
   - Ensure your shell history is disabled or cleared
   - Consider using SSH keys instead of passwords

2. **SSH Key Alternative**: For production use, consider setting up SSH key authentication to iDRAC instead of password authentication.

3. **Network Access**: Run this script from a secure management network with controlled access to iDRAC interfaces.

## Troubleshooting

### Connection Failures
- Verify SSH is enabled on iDRAC
- Check network connectivity: `ping <idrac-ip>`
- Verify credentials are correct
- Check firewall rules allow SSH (port 22)

### Permission Issues
- Ensure the user account has administrative privileges on iDRAC
- Default iDRAC username is typically `root`

### RACADM Command Fails
- Verify iDRAC firmware version supports the command
- Check iDRAC system logs for errors
- Some older iDRAC versions may use slightly different syntax

## Manual Verification

After running the script, you can manually verify via:

### Web Interface
1. Login to iDRAC web interface
2. Navigate to: System > iDRAC Settings > Network/Security > Network > IPMI Settings
3. Verify "Enable IPMI Over LAN" is deselected

### SSH/RACADM
```bash
ssh root@<idrac-ip>
racadm get iDRAC.IPMILan.Enable
# Should show: Enable=Disabled
```

## Log Files
The script creates timestamped log files for each run:
- Format: `ipmi_disable_YYYYMMDD_HHMMSS.log`
- Contains detailed output for audit and troubleshooting

## Support
For issues with Dell iDRAC or RACADM commands, refer to:
- Dell iDRAC Documentation
- Dell Support: https://www.dell.com/support
- Security Advisory: https://www.dell.com/support/kbdoc/en-us/000222162
