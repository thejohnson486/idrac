# iDRAC IPMI-over-LAN Disable Script (Python Version)

## Overview
Python version of the script that automates disabling IPMI-over-LAN on Dell iDRAC systems via SSH. This addresses the security vulnerability documented in Dell's security advisory.

**Reference:** https://www.dell.com/support/kbdoc/en-us/000222162/data-domain-ipmi-v2-0-password-hash-disclosure

## Features
- ✅ Interactive mode with prompts for credentials and options
- ✅ Single device or multiple devices mode
- ✅ Secure password input (hidden)
- ✅ Color-coded output for easy reading
- ✅ Detailed logging with timestamps
- ✅ Connection verification and status checking
- ✅ Post-change verification
- ✅ Summary report with success/failure counts

## Prerequisites

### 1. Python 3.6 or higher
```bash
python3 --version
```

### 2. Install Required Python Packages

#### Linux / macOS
```bash
pip3 install -r requirements.txt
```

Or manually:
```bash
pip3 install paramiko
```

#### macOS Specific
macOS comes with Python 3 pre-installed:
```bash
# Check Python version
python3 --version

# Install paramiko
pip3 install paramiko

# If you encounter permission issues, use:
pip3 install --user paramiko
```

#### Windows
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install paramiko
```

### 3. Enable SSH on iDRAC
SSH must be enabled on each iDRAC system:
- iDRAC web interface: iDRAC Settings > Network > Services > SSH

## Installation

### Linux / macOS
```bash
# Make the script executable
chmod +x disable_ipmi_idrac.py

# Or run with python3
python3 disable_ipmi_idrac.py
```

### Windows
```bash
# Run with Python
python disable_ipmi_idrac.py
```

### macOS Notes
- ✅ Python 3 is pre-installed on modern macOS
- ✅ Paramiko works perfectly on Mac
- ✅ No additional system configuration needed
- ✅ All SSH features fully supported

## Usage Modes

### Interactive Mode (Recommended)
Simply run the script with no arguments:
```bash
./disable_ipmi_idrac.py
```
or
```bash
python3 disable_ipmi_idrac.py
```

The script will interactively prompt you for:
1. **Username** (default: root)
2. **Password** (hidden input)
3. **Operation mode**:
   - Single device → Enter one IP/hostname
   - Multiple devices → Enter path to hosts file
4. **Confirmation** before making changes

#### Example Interactive Session:
```
==================================================
  iDRAC IPMI-over-LAN Disable Script (Python)
==================================================

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

Starting IPMI disable process...

==================================================
Processing iDRAC (1/1): 192.168.1.100
==================================================
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
[192.168.1.100] ✓ Verification successful - IPMI is disabled

==================================================
Summary
==================================================
Total hosts processed: 1
Successful: 1
Failed: 0

Log file: ipmi_disable_20251215_103000.log
Completed: 2025-12-15 10:30:45
==================================================
✓ All operations completed successfully!
```

### Command Line Mode

#### Single Device
```bash
python3 disable_ipmi_idrac.py -u root -p YourPassword -s 192.168.1.100
```

#### Multiple Devices
Create `idrac_hosts.txt` with your iDRAC IPs (one per line):
```
192.168.1.100
192.168.1.101
idrac-server1.domain.com
idrac-server2.domain.com
```

Then run:
```bash
python3 disable_ipmi_idrac.py -u root -p YourPassword -f idrac_hosts.txt
```

### Command Line Options
```
-h, --help              Show help message
-u, --username USERNAME iDRAC username (skips interactive prompt)
-p, --password PASSWORD iDRAC password (skips interactive prompt)
-s, --single HOSTNAME   Single iDRAC host (enables single device mode)
-f, --file FILE         Path to hosts file for multiple devices
```

## Hosts File Format

Create a text file with one iDRAC IP or hostname per line:

```
# iDRAC Hosts List
# Lines starting with # are comments

192.168.1.100
192.168.1.101
192.168.1.102

# Production servers
idrac-server1.domain.com
idrac-server2.domain.com

# Development servers
idrac-dev1.domain.com
```

## What the Script Does

1. **Connects** to each iDRAC via SSH using Paramiko
2. **Checks** current IPMI-over-LAN status with: `racadm get iDRAC.IPMILan.Enable`
3. **Disables** IPMI with: `racadm set iDRAC.IPMILan.Enable 0`
4. **Verifies** the change was successful
5. **Logs** all actions with timestamps
6. **Reports** summary of successful and failed operations

## Security Considerations

### Password Security
The password can be provided via:
1. **Interactive prompt** (most secure - hidden input)
2. **Command line argument** (least secure - visible in process list)
3. **Environment variable** (recommended for automation):
   ```bash
   export IDRAC_PASSWORD="YourPassword"
   python3 disable_ipmi_idrac.py -u root -p "$IDRAC_PASSWORD" -f hosts.txt
   ```

### SSH Key Authentication
For better security in production, consider:
1. Setting up SSH key authentication to iDRAC
2. Modifying the script to use key-based auth instead of passwords

### Network Isolation
- Run from a secure management network
- Ensure iDRAC interfaces are on isolated management VLANs
- Use firewall rules to restrict SSH access to iDRAC

## Troubleshooting

### Import Error: No module named 'paramiko'
```bash
pip3 install paramiko
```

### Authentication Failed
- Verify username and password are correct
- Check that the account has administrative privileges
- Ensure SSH is enabled on iDRAC

### Connection Timeout
- Verify network connectivity: `ping <idrac-ip>`
- Check firewall rules allow SSH (port 22)
- Verify iDRAC SSH service is running

### Permission Denied
- Ensure the user account has admin/root privileges on iDRAC
- Default iDRAC username is typically `root`

### Script Hangs
- Check if iDRAC is responsive via web interface
- Verify no other sessions are blocking RACADM commands
- Try reducing the number of concurrent operations

## Advantages of Python Version

✅ **Cross-platform**: Works on Windows, Linux, macOS  
✅ **Native SSH library**: Uses Paramiko (no external dependencies like sshpass)  
✅ **Better error handling**: More detailed exception handling  
✅ **Easier to extend**: Object-oriented design for customization  
✅ **Cleaner code**: More readable and maintainable  

## Log Files

The script creates timestamped log files:
- **Format**: `ipmi_disable_YYYYMMDD_HHMMSS.log`
- **Contents**: All operations with timestamps
- **Location**: Current directory
- **Purpose**: Audit trail and troubleshooting

Example log entry:
```
[2025-12-15 10:30:15] ==========================================
[2025-12-15 10:30:15] Processing iDRAC: 192.168.1.100
[2025-12-15 10:30:15] [192.168.1.100] Connecting to iDRAC...
[2025-12-15 10:30:16] [192.168.1.100] IPMI over LAN disabled successfully
```

## Comparison: Bash vs Python

| Feature | Bash Script | Python Script |
|---------|-------------|---------------|
| Dependencies | sshpass, ssh | paramiko (pip install) |
| Platform | Linux/Unix/Mac | Windows/Linux/Mac |
| Error Handling | Basic | Advanced |
| Code Readability | Good | Excellent |
| Extensibility | Limited | Easy |
| Installation | Often pre-installed | Requires Python 3.6+ |

## Manual Verification

After running the script, verify via:

### Web Interface
1. Login to iDRAC
2. Navigate to: System > iDRAC Settings > Network/Security > Network > IPMI Settings
3. Verify "Enable IPMI Over LAN" is deselected

### SSH/RACADM
```bash
ssh root@<idrac-ip>
racadm get iDRAC.IPMILan.Enable
# Should show: Enable=Disabled or Enable=0
```

### Alternative Python Check
```python
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.100', username='root', password='password')
stdin, stdout, stderr = ssh.exec_command('racadm get iDRAC.IPMILan.Enable')
print(stdout.read().decode())
ssh.close()
```

## Support and Resources

- **Dell iDRAC Documentation**: https://www.dell.com/support/manuals/idrac
- **Security Advisory**: https://www.dell.com/support/kbdoc/en-us/000222162
- **Paramiko Documentation**: https://docs.paramiko.org/
- **Dell Support**: https://www.dell.com/support

## License

This script is provided as-is for managing Dell iDRAC systems. Use at your own risk.
