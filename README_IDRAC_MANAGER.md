# iDRAC Comprehensive Manager 🚀

The **all-in-one** iDRAC management tool via Redfish API. Manage users, network, power, firmware, BIOS, monitoring, and more - all from one script!

## 🎯 Features

This script provides **26+ management functions** organized into categories:

### 👤 **User Management**
- ✅ List all users with roles and status
- ✅ Add new users with specific roles
- ✅ Delete users
- ✅ Change passwords (bulk password rotation)
- ✅ View account lock status

### 🌐 **Network Configuration**
- ✅ View complete network configuration
- ✅ Set static IP address
- ✅ Configure DNS servers
- ✅ Configure NTP servers
- ✅ Enable/disable protocols (IPMI, Telnet, SNMP, SSH, etc.)
- ✅ View DHCP status

### ⚡ **Power Management**
- ✅ Power on/off servers
- ✅ Graceful shutdown
- ✅ Force power off
- ✅ Graceful restart
- ✅ Force restart
- ✅ Get current power state

### 🖥️ **Hardware Inventory & Monitoring**
- ✅ Complete hardware inventory (CPU, RAM, storage, NICs)
- ✅ Temperature sensors
- ✅ Fan speeds
- ✅ Power supply status
- ✅ Component health status
- ✅ Service tag and serial numbers

### 🔄 **Firmware Management**
- ✅ List all firmware versions
- ✅ Identify updateable components
- ✅ View iDRAC firmware version

### ⚙️ **BIOS Configuration**
- ✅ View BIOS attributes
- ✅ Modify BIOS settings
- ✅ Virtualization settings
- ✅ Boot configuration

### 📋 **Jobs & Tasks**
- ✅ List job queue
- ✅ View job status and progress
- ✅ Monitor running jobs

### 💾 **Configuration Management**
- ✅ Backup iDRAC configuration
- ✅ Export system configuration profile

### 📊 **System Health & Logs**
- ✅ Overall system health status
- ✅ Component health checks
- ✅ System Event Log (SEL)
- ✅ Health status by severity

### 🔒 **Security**
- ✅ Security audit scan
- ✅ Identify insecure protocols
- ✅ Check for default accounts
- ✅ Protocol hardening recommendations

## 📦 Prerequisites

### 1. Python 3.6+
```bash
python3 --version
```

### 2. Install Dependencies
```bash
pip3 install requests urllib3
```

### 3. iDRAC Access
- iDRAC web interface must be accessible
- Valid credentials with appropriate permissions
- HTTPS (port 443) access

## 🚀 Installation

```bash
# Make executable
chmod +x idrac_manager.py

# Run
python3 idrac_manager.py
```

## 💻 Usage

### Interactive Menu Mode (Recommended)

```bash
python3 idrac_manager.py
```

You'll see a comprehensive menu:

```
==================================================
              iDRAC COMPREHENSIVE MANAGER
                 Redfish API Edition
==================================================

iDRAC IP/Hostname: 192.168.1.100
Username [root]: root
Password: ********

✓ Connected successfully

==================================================
MAIN MENU
==================================================

USER MANAGEMENT:
  1. List users
  2. Add user
  3. Delete user
  4. Change user password

NETWORK CONFIGURATION:
  5. Show network configuration
  6. Set static IP address
  7. Configure DNS servers
  8. Configure NTP servers
  9. Disable protocol (IPMI/Telnet/SNMP)

POWER MANAGEMENT:
  10. Power on server
  11. Power off server (graceful)
  12. Power off server (force)
  13. Restart server (graceful)
  14. Restart server (force)
  15. Get power state

HARDWARE & MONITORING:
  16. Get hardware inventory
  17. Get sensor data (temps/fans)
  18. Get system health
  19. Get firmware inventory
  20. Get system event log

BIOS CONFIGURATION:
  21. Show BIOS attributes
  22. Set BIOS attribute

JOBS & CONFIGURATION:
  23. List jobs
  24. Backup configuration

OTHER:
  25. Run all health checks
  26. Security audit
  0. Exit

Enter choice:
```

### Command Line Mode

```bash
# Specify credentials
python3 idrac_manager.py -H 192.168.1.100 -u root -p password

# With log file
python3 idrac_manager.py -H 192.168.1.100 -u root -p password -l my_log.txt
```

### Command Line Options

```
-H, --host      iDRAC hostname or IP address
-u, --username  iDRAC username
-p, --password  iDRAC password
-l, --log       Log file path (optional)
```

## 📖 Feature Examples

### Example 1: User Management

```
Choose option: 2

New username: john.doe
Password: ********
Role [Administrator/Operator/ReadOnly]: Operator

✓ User 'john.doe' added successfully
```

### Example 2: Network Configuration

```
Choose option: 5

==================================================
NETWORK CONFIGURATION
==================================================

📡 Network Interface:
  Hostname: idrac-svr01
  MAC Address: B8:2A:72:XX:XX:XX
  IP Address: 192.168.1.100
  Subnet Mask: 255.255.255.0
  Gateway: 192.168.1.1
  DHCP: Disabled

🌐 Network Services:
  Hostname: idrac-svr01
  FQDN: idrac-svr01.company.com

⏰ NTP Configuration:
  Enabled: True
  Server 1: time.nist.gov
  Server 2: pool.ntp.org

🔌 Protocol Status:
  SSH        Port: 22     🟢 Enabled
  HTTPS      Port: 443    🟢 Enabled
  IPMI       Port: 623    🔴 Disabled
  SNMP       Port: 161    🔴 Disabled
  Telnet     Port: 23     🔴 Disabled
```

### Example 3: Hardware Inventory

```
Choose option: 16

==================================================
HARDWARE INVENTORY
==================================================

🖥️  System Information:
  Manufacturer: Dell Inc.
  Model: PowerEdge R740
  Service Tag: ABC1234
  Serial Number: CN123456789
  BIOS Version: 2.15.1
  Power State: On

🔧 Processors:
  Count: 2
  Model: Intel(R) Xeon(R) Gold 6148 CPU @ 2.40GHz

💾 Memory:
  Total: 384 GiB

💿 Storage Controllers:
  Controllers: 1

🌐 Network Adapters:
  Adapters: 4

📡 iDRAC Information:
  Firmware Version: 6.10.30.00
  Model: iDRAC9
```

### Example 4: System Health Check

```
Choose option: 25

==================================================
RUNNING COMPREHENSIVE HEALTH CHECKS
==================================================

✓ Overall System Health: OK
  State: Enabled

📊 Component Health:
  Processors: 2 detected
  Memory: 12 detected
  Storage: 8 detected

🌡️  Temperature Sensors:
  System Board Inlet Temp      28°C  [OK]
  System Board Exhaust Temp    35°C  [OK]
  CPU1 Temp                    52°C  [OK]
  CPU2 Temp                    48°C  [OK]

🌀 Fans:
  System Board Fan1A           7920 RPM  [OK]
  System Board Fan1B           7920 RPM  [OK]
  System Board Fan2A           7920 RPM  [OK]
```

### Example 5: Security Audit

```
Choose option: 26

==================================================
SECURITY AUDIT
==================================================

Checking for insecure configurations...

Security Issues Found:
  ⚠️  IPMI is enabled: IPMI over LAN should be disabled
  ⚠️  Telnet is enabled: Telnet should be disabled (use SSH)

Checking user accounts...

Found 3 user accounts:

  User: root                Role: Administrator   🟢 Enabled
  User: backup-admin        Role: Administrator   🟢 Enabled
  User: readonly            Role: ReadOnly        🟢 Enabled
```

### Example 6: Power Management

```
Choose option: 13

==================================================
POWER MANAGEMENT - GracefulRestart
==================================================

Current power state: On
Executing power operation: GracefulRestart

✓ Power operation 'GracefulRestart' executed successfully
```

## 🎯 Common Use Cases

### 1. **Initial Server Setup**
```
1. Set static IP (option 6)
2. Configure DNS (option 7)
3. Configure NTP (option 8)
4. Add admin users (option 2)
5. Disable insecure protocols (option 9)
6. Backup configuration (option 24)
```

### 2. **Security Hardening**
```
1. Run security audit (option 26)
2. Disable IPMI (option 9 → IPMI)
3. Disable Telnet (option 9 → Telnet)
4. Disable SNMP v1/v2 (option 9 → SNMP)
5. Change default passwords (option 4)
6. Review user list (option 1)
```

### 3. **Health Monitoring**
```
1. Run all health checks (option 25)
2. Check system event log (option 20)
3. View sensor data (option 17)
4. Get firmware versions (option 19)
```

### 4. **Password Rotation**
```
1. List users (option 1)
2. Change password for each user (option 4)
3. Test login with new credentials
```

### 5. **Maintenance Window**
```
1. Backup configuration (option 24)
2. Check system health (option 18)
3. Graceful shutdown (option 11)
4. [Perform maintenance]
5. Power on (option 10)
6. Verify health (option 25)
```

## 🔧 Advanced Features

### Batch Operations

You can wrap the script in a shell script for batch operations:

```bash
#!/bin/bash
# batch_config.sh

IDRAC_PASS="YourPassword"

# List of iDRAC IPs
IDRACS=(
  "192.168.1.100"
  "192.168.1.101"
  "192.168.1.102"
)

for idrac in "${IDRACS[@]}"; do
  echo "Processing $idrac..."
  
  # Example: Disable IPMI on all
  # You'd need to modify the script to accept actions as CLI args
  
done
```

### Automated Reporting

```bash
#!/bin/bash
# health_report.sh

python3 idrac_manager.py \
  -H 192.168.1.100 \
  -u root \
  -p "$IDRAC_PASSWORD" \
  -l "health_report_$(date +%Y%m%d).log"

# Parse log file and email report
mail -s "iDRAC Health Report" admin@company.com < health_report_*.log
```

## 📊 Logging

All operations are logged to a timestamped file:

**Format**: `idrac_manager_YYYYMMDD_HHMMSS.log`

**Contents**:
- All commands executed
- API requests and responses
- Results and error messages
- Timestamps for audit trail

**Example log entry**:
```
[2025-12-16 10:30:15] Adding user: john.doe with role: Operator
[2025-12-16 10:30:16] ✓ User 'john.doe' added successfully
```

## 🛠️ Troubleshooting

### Connection Failed

**Problem**: Can't connect to iDRAC

**Solutions**:
```bash
# Test connectivity
ping 192.168.1.100

# Test HTTPS access
curl -k https://192.168.1.100

# Check if web interface is accessible in browser
https://192.168.1.100
```

### Authentication Failed

**Problem**: Invalid credentials

**Check**:
- Username is correct (usually `root`)
- Password is correct
- Account is not locked
- Account has sufficient privileges

### Timeout Errors

**Problem**: Operations timing out

**Solutions**:
- Increase timeout in script (modify `self.timeout`)
- Check network latency
- Verify iDRAC is not overloaded
- Check if jobs are stuck in queue

### Permission Denied

**Problem**: User lacks permissions

**Solutions**:
- Use Administrator role for full access
- Operator role has limited permissions
- ReadOnly role cannot make changes

## 🔐 Security Best Practices

### 1. **Credential Management**
```bash
# Use environment variables
export IDRAC_PASSWORD="SecurePassword123"
python3 idrac_manager.py -p "$IDRAC_PASSWORD"

# Or use a secure credential store
```

### 2. **Regular Audits**
- Run security audit (option 26) monthly
- Review user list regularly
- Check for unauthorized changes

### 3. **Protocol Hardening**
- Disable IPMI if not needed
- Disable Telnet (use SSH)
- Use SNMP v3 only (disable v1/v2)
- Keep SSH enabled for management

### 4. **Password Policy**
- Rotate passwords quarterly
- Use strong passwords (12+ chars)
- Don't reuse passwords
- Document password changes

### 5. **Access Control**
- Use least privilege principle
- Create role-specific accounts
- Remove accounts when users leave
- Use ReadOnly accounts for monitoring

## 📚 Supported iDRAC Versions

- ✅ **iDRAC 9** (14th/15th/16th gen) - Full support
- ✅ **iDRAC 8** (13th gen) - Full support
- ⚠️ **iDRAC 7** (12th gen) - Partial support (some features may vary)
- ❌ **iDRAC 6** (11th gen) - Not supported (no Redfish API)

## 🎁 What Makes This Different?

### vs. Dell OpenManage
- ✅ No agent installation required
- ✅ Works remotely over HTTPS
- ✅ Lightweight Python script
- ✅ Cross-platform (Windows/Linux/macOS)

### vs. RACADM
- ✅ No SSH required
- ✅ Modern REST API
- ✅ Better error handling
- ✅ Interactive menu interface

### vs. Web Interface
- ✅ Scriptable and automatable
- ✅ Batch operations
- ✅ Comprehensive logging
- ✅ Multiple servers at once

### vs. Ansible/Salt
- ✅ No infrastructure required
- ✅ Single executable script
- ✅ Quick ad-hoc operations
- ✅ Interactive troubleshooting

## 🚀 Future Enhancements

Potential features for future versions:

- [ ] Firmware upload and update
- [ ] Virtual media mounting
- [ ] RAID configuration
- [ ] Certificate upload integration
- [ ] Restore from backup
- [ ] Batch multi-server operations
- [ ] Email alert configuration
- [ ] LDAP/AD integration
- [ ] Export reports to CSV/PDF
- [ ] Web UI frontend

## 💡 Tips & Tricks

### Quick Health Check

```
Start script → Option 25 → Review output → Exit
```

### Password Rotation Script

```python
# password_rotation.py
import subprocess
import getpass

new_password = getpass.getpass("New password for all: ")

idracs = ["192.168.1.100", "192.168.1.101", "192.168.1.102"]
users = ["root", "admin", "backup"]

for idrac in idracs:
    for user in users:
        # Call idrac_manager for each combination
        pass
```

### Monitoring Integration

```bash
# Add to cron for daily health checks
0 8 * * * /usr/bin/python3 /opt/scripts/idrac_manager.py -H 192.168.1.100 -u monitor -p pass -l /var/log/idrac_health.log
```

## 📞 Support & Resources

- **Dell iDRAC Documentation**: https://www.dell.com/support/manuals/idrac
- **Redfish API**: https://www.dmtf.org/standards/redfish
- **Dell Support**: https://www.dell.com/support

## 📝 Notes

- ⚠️ Some operations (power off, IP changes) can cause downtime
- ⚠️ BIOS changes require server reboot to take effect
- ⚠️ Always backup configuration before major changes
- ✅ Script uses HTTPS only (secure by default)
- ✅ All API calls are logged for audit trail
- ✅ No persistent connections (stateless operation)

## 🎯 Quick Reference

| Category | Option Numbers |
|----------|----------------|
| Users | 1-4 |
| Network | 5-9 |
| Power | 10-15 |
| Hardware | 16-20 |
| BIOS | 21-22 |
| Jobs/Config | 23-24 |
| Special | 25-26 |

## 📄 License

This script is provided as-is for Dell iDRAC management. Use responsibly and always test in non-production first!

---

**Created for comprehensive iDRAC management via Redfish API** 🚀
