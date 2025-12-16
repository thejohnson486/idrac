# iDRAC IPMI-over-LAN Disable Script (Redfish API Version)

## Overview
Python script that uses the **Redfish REST API** to disable IPMI-over-LAN on Dell iDRAC systems. This is the modern, API-based approach that works over HTTPS without requiring SSH access.

**Reference:** https://www.dell.com/support/kbdoc/en-us/000222162/data-domain-ipmi-v2-0-password-hash-disclosure

## Why Redfish API?

### ✅ Advantages:
- **No SSH required**: Works over standard HTTPS (port 443)
- **Simpler dependencies**: Only needs `requests` library (no paramiko/SSH)
- **Modern standard**: Industry-standard REST API for hardware management
- **Better for automation**: JSON-based, easier to integrate with orchestration tools
- **Cross-platform**: Works identically on Windows, Linux, macOS
- **Firewall-friendly**: Most environments already allow HTTPS

### 📋 Comparison:

| Feature | SSH/RACADM | Redfish API |
|---------|------------|-------------|
| Protocol | SSH (port 22) | HTTPS (port 443) |
| Dependencies | paramiko | requests |
| Authentication | SSH keys/password | HTTP Basic Auth |
| Response Format | Text output | JSON |
| iDRAC Requirement | SSH enabled | Web interface enabled |
| Best For | Traditional admins | Modern automation |

## Features
- ✅ Interactive mode with prompts
- ✅ Single device or multiple devices
- ✅ Secure password input (hidden)
- ✅ Color-coded output
- ✅ **Optional iDRAC reboot** after disabling IPMI 🆕
- ✅ Automatic endpoint detection (tries multiple API paths)
- ✅ Detailed logging with timestamps
- ✅ Pre and post verification
- ✅ Summary report

## Prerequisites

### 1. Python 3.6 or higher
```bash
python3 --version
```

### 2. Install Required Packages

#### Linux / macOS
```bash
pip3 install -r requirements.txt
```

Or manually:
```bash
pip3 install requests urllib3
```

#### macOS Specific
macOS comes with Python 3 pre-installed. Just install the required packages:
```bash
# Check Python version
python3 --version

# Install packages
pip3 install requests urllib3

# If pip3 is not found, you may need to install it
python3 -m ensurepip --upgrade
```

#### Windows
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install requests urllib3
```

### 3. Enable Web Interface on iDRAC
The Redfish API is accessed via the iDRAC web interface:
- Ensure the web interface is accessible
- Default port: 443 (HTTPS)
- No need to enable SSH

## Installation

### Linux / macOS
```bash
# Make the script executable
chmod +x disable_ipmi_idrac_redfish.py

# Run it
./disable_ipmi_idrac_redfish.py
```

Or run directly with Python:
```bash
python3 disable_ipmi_idrac_redfish.py
```

### Windows
```bash
# Run with Python
python disable_ipmi_idrac_redfish.py
```

### macOS Notes
- ✅ Python 3 is pre-installed on modern macOS
- ✅ No additional system packages needed
- ✅ Works natively without any special setup
- ✅ All features fully supported

## Usage

### Interactive Mode (Recommended)
```bash
python3 disable_ipmi_idrac_redfish.py
```

You'll be prompted for:
1. Username (default: root)
2. Password (hidden)
3. Single or multiple device mode
4. **Whether to reboot iDRAC after disabling IPMI** 🆕
5. Confirmation before making changes

### Command Line Mode

#### Single Device
```bash
python3 disable_ipmi_idrac_redfish.py -u root -p password -s 192.168.1.100
```

#### Single Device with Automatic Reboot 🆕
```bash
python3 disable_ipmi_idrac_redfish.py -u root -p password -s 192.168.1.100 -r
```
The `-r` flag automatically reboots the iDRAC after disabling IPMI to ensure changes take effect immediately.

#### Multiple Devices
Create `idrac_hosts.txt`:
```
192.168.1.100
192.168.1.101
idrac-server1.domain.com
```

Run:
```bash
python3 disable_ipmi_idrac_redfish.py -u root -p password -f idrac_hosts.txt
```

#### Multiple Devices with Automatic Reboot 🆕
```bash
python3 disable_ipmi_idrac_redfish.py -u root -p password -f idrac_hosts.txt -r
```

### Command Line Options
```
-h, --help              Show help message
-u, --username USERNAME iDRAC username
-p, --password PASSWORD iDRAC password
-s, --single HOSTNAME   Single iDRAC host
-f, --file FILE         File with list of iDRAC hosts
-r, --reboot            Reboot iDRAC after disabling IPMI (recommended) 🆕
```

### Why Reboot? 🔄
Some iDRAC versions require a reboot for IPMI disable to take full effect. The `-r` flag:
- ✅ Automatically reboots iDRAC after making changes
- ✅ Ensures IPMI is fully disabled immediately
- ✅ iDRAC will be unavailable for ~1-2 minutes during reboot
- ✅ Recommended for maximum security assurance

## How It Works

### 1. Connection
```python
# Connects via HTTPS to Redfish API
base_url = f"https://{host}"
session.auth = (username, password)
```

### 2. Check Current Status
The script tries multiple API endpoints to find IPMI settings:
- `/redfish/v1/Managers/iDRAC.Embedded.1/NetworkProtocol`
- `/redfish/v1/Managers/System.Embedded.1/NetworkProtocol`
- `/redfish/v1/Managers/iDRAC.Embedded.1/Attributes`

### 3. Disable IPMI
Sends a PATCH request with JSON payload:
```json
{
  "IPMI": {
    "ProtocolEnabled": false
  }
}
```

### 4. Verify
Checks the setting again to confirm it was disabled.

## Example Output

```
==================================================
  iDRAC IPMI-over-LAN Disable Script
  (Redfish API Version)
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
  Method: Redfish API (HTTPS)
  Target: 192.168.1.100
  Log file: ipmi_disable_redfish_20251215_103000.log

Proceed with disabling IPMI-over-LAN? (yes/no): yes

Starting IPMI disable process...

==================================================
Processing iDRAC (1/1): 192.168.1.100
==================================================
[192.168.1.100] Connecting to iDRAC via Redfish API...
[192.168.1.100] Current IPMI status: Enabled
[192.168.1.100] Details: {
  "ProtocolEnabled": true,
  "Port": 623
}
[192.168.1.100] Disabling IPMI over LAN...
[192.168.1.100] SUCCESS: IPMI disabled via NetworkProtocol endpoint
[192.168.1.100] Verifying configuration...
[192.168.1.100] ✓ Verification successful - IPMI is disabled

==================================================
Summary
==================================================
Total hosts processed: 1
Successful: 1
Failed: 0

Log file: ipmi_disable_redfish_20251215_103000.log
Completed: 2025-12-15 10:30:45
==================================================
✓ All operations completed successfully!
Note: Some iDRACs may require a reset for changes to take effect.
```

## API Endpoints Used

The script automatically detects and uses the appropriate endpoint for your iDRAC version:

### NetworkProtocol Endpoint (Preferred)
```
PATCH /redfish/v1/Managers/iDRAC.Embedded.1/NetworkProtocol
Content-Type: application/json

{
  "IPMI": {
    "ProtocolEnabled": false
  }
}
```

### Attributes Endpoint (Fallback)
```
PATCH /redfish/v1/Managers/iDRAC.Embedded.1/Attributes
Content-Type: application/json

{
  "Attributes": {
    "IPMILan.1#Enable": "Disabled"
  }
}
```

## SSL Certificate Handling

iDRACs typically use self-signed SSL certificates. The script:
- **Disables SSL verification** by default (using `verify=False`)
- **Suppresses SSL warnings** to keep output clean

⚠️ **Security Note**: This is normal for internal infrastructure, but be aware that SSL verification is disabled.

## Troubleshooting

### Module Not Found: requests
```bash
pip3 install requests
```

### Connection Error
- Verify iDRAC web interface is accessible: `https://<idrac-ip>`
- Check network connectivity: `ping <idrac-ip>`
- Ensure port 443 is not blocked by firewall

### Authentication Failed
- Verify username/password are correct
- Ensure account has admin privileges
- Check if account is locked in iDRAC

### HTTP 404 Error
- Your iDRAC version may use different API paths
- The script tries multiple endpoints automatically
- Check iDRAC firmware version (Redfish requires iDRAC 7/8/9)

### Changes Not Taking Effect
Some iDRAC versions require a reset after configuration changes:
```bash
# Via web interface: iDRAC Settings > Diagnostics > Reset iDRAC
# Or via API:
curl -k -u root:password -X POST \
  https://<idrac-ip>/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Manager.Reset \
  -H "Content-Type: application/json" \
  -d '{"ResetType": "GracefulRestart"}'
```

## Supported iDRAC Versions

- ✅ **iDRAC 9** (13th/14th/15th gen servers) - Full support
- ✅ **iDRAC 8** (12th gen servers) - Full support  
- ✅ **iDRAC 7** (11th gen servers) - Limited support (may need firmware update)
- ❌ **iDRAC 6 and older** - No Redfish support (use SSH version instead)

Check your iDRAC version:
- Login to web interface
- Look at the top right corner for version number
- Or check via API: `https://<idrac-ip>/redfish/v1/`

## Manual Verification

### Via Web Interface
1. Login to iDRAC
2. Navigate to: **System** > **iDRAC Settings** > **Network/Security** > **Network** > **IPMI Settings**
3. Verify **"Enable IPMI Over LAN"** is deselected

### Via Redfish API
```bash
curl -k -u root:password https://<idrac-ip>/redfish/v1/Managers/iDRAC.Embedded.1/NetworkProtocol | grep -A2 IPMI
```

Should show:
```json
"IPMI": {
  "ProtocolEnabled": false,
  "Port": 623
}
```

### Via Python
```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.get(
    'https://192.168.1.100/redfish/v1/Managers/iDRAC.Embedded.1/NetworkProtocol',
    auth=HTTPBasicAuth('root', 'password'),
    verify=False
)

ipmi_status = response.json()['IPMI']['ProtocolEnabled']
print(f"IPMI Enabled: {ipmi_status}")
```

## Security Best Practices

1. **Use Strong Passwords**: Don't use default credentials
2. **Environment Variables**: Store passwords in env vars for automation
   ```bash
   export IDRAC_PASSWORD="SecurePassword123"
   python3 disable_ipmi_idrac_redfish.py -p "$IDRAC_PASSWORD"
   ```
3. **Restrict Access**: Limit who can access iDRAC interfaces
4. **Network Isolation**: Keep iDRAC on separate management VLAN
5. **Log Review**: Check log files regularly for audit trail
6. **Credential Rotation**: Change passwords periodically

## Comparison with SSH Version

| Aspect | Redfish API (This Script) | SSH/RACADM |
|--------|---------------------------|------------|
| **Port** | 443 (HTTPS) | 22 (SSH) |
| **Library** | requests | paramiko |
| **Setup** | Just enable web UI | Enable SSH service |
| **Firewall** | Usually already open | Often needs approval |
| **Windows** | Native support | Needs SSH client |
| **Speed** | Fast (HTTP) | Fast (SSH) |
| **Complexity** | Simple REST calls | SSH session management |

**Recommendation**: Use this Redfish version unless you specifically need SSH or have older iDRAC 6 systems.

## Log Files

Timestamped log files are created in the current directory:
- **Format**: `ipmi_disable_redfish_YYYYMMDD_HHMMSS.log`
- **Contents**: All operations with timestamps
- **Use**: Audit trail, troubleshooting, compliance

Example log:
```
[2025-12-15 10:30:15] ==========================================
[2025-12-15 10:30:15] Processing iDRAC: 192.168.1.100
[2025-12-15 10:30:16] [192.168.1.100] Connecting to iDRAC via Redfish API...
[2025-12-15 10:30:17] [192.168.1.100] SUCCESS: IPMI disabled via NetworkProtocol endpoint
```

## Additional Resources

- **Dell Redfish API Guide**: https://www.dell.com/support/manuals/idrac
- **Redfish Standard**: https://www.dmtf.org/standards/redfish
- **Security Advisory**: https://www.dell.com/support/kbdoc/en-us/000222162
- **iDRAC User Guide**: Check Dell support site for your server model

## License

This script is provided as-is for managing Dell iDRAC systems. Use at your own risk.
