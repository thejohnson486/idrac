# macOS Quick Start Guide 🍎

The fastest way to disable IPMI-over-LAN on Dell iDRACs from your Mac.

## TL;DR - For the Impatient

```bash
# Install (one-time, 30 seconds)
pip3 install requests

# Run
python3 disable_ipmi_idrac_redfish.py
```

That's it! Follow the interactive prompts.

---

## Complete macOS Setup Guide

### Step 1: Verify Python (Already Installed!)

Modern macOS comes with Python 3 pre-installed:

```bash
python3 --version
```

You should see something like: `Python 3.9.6` or higher

✅ If you see this, you're ready to go!

❌ If not found, install from: https://www.python.org/downloads/

### Step 2: Install Required Package

Open Terminal and run:

```bash
pip3 install requests
```

**If you get a permission error**, try:
```bash
pip3 install --user requests
```

### Step 3: Download the Script

You should have these files:
- `disable_ipmi_idrac_redfish.py` (the main script)
- `idrac_hosts.txt` (optional, for multiple devices)

### Step 4: Run the Script

#### Option A: Interactive Mode (Easiest)
```bash
python3 disable_ipmi_idrac_redfish.py
```

Follow the prompts:
1. Enter username (default: root)
2. Enter password (hidden)
3. Choose single or multiple device mode
4. Confirm and run

#### Option B: Single Device (Quick)
```bash
python3 disable_ipmi_idrac_redfish.py -s 192.168.1.100
```

#### Option C: Multiple Devices (Batch)
Create `idrac_hosts.txt`:
```
192.168.1.100
192.168.1.101
192.168.1.102
```

Then run:
```bash
python3 disable_ipmi_idrac_redfish.py -f idrac_hosts.txt
```

---

## macOS-Specific Features

### ✅ What Works Great on Mac

1. **Pre-installed Python**: No need to install Python
2. **Native HTTPS**: Uses macOS native SSL/TLS
3. **Terminal Integration**: Works perfectly in Terminal.app or iTerm2
4. **Color Output**: Full color support in macOS Terminal
5. **Keyboard Shortcuts**: Standard Mac shortcuts work (⌘+C to cancel, etc.)

### 🎨 Terminal Recommendations

**Best Terminals for macOS**:
- ✅ Terminal.app (built-in, works great)
- ✅ iTerm2 (free, enhanced features)
- ✅ Warp (modern, AI-powered)

All support colors and interactive prompts perfectly!

---

## Common macOS Issues & Solutions

### Issue 1: "command not found: python3"

**Solution**: Install Python from python.org
```bash
# Download and install from:
open https://www.python.org/downloads/
```

### Issue 2: "command not found: pip3"

**Solution**: Ensure pip is installed
```bash
python3 -m ensurepip --upgrade
```

### Issue 3: "Permission denied"

**Solution A**: Use --user flag
```bash
pip3 install --user requests
```

**Solution B**: Make script executable
```bash
chmod +x disable_ipmi_idrac_redfish.py
./disable_ipmi_idrac_redfish.py
```

### Issue 4: SSL Certificate Warnings

This is normal! iDRACs use self-signed certificates. The script handles this automatically with:
```python
verify=False
```

### Issue 5: Can't connect to iDRAC

**Check network connectivity**:
```bash
ping 192.168.1.100

# Test HTTPS access
curl -k https://192.168.1.100
```

---

## Why Redfish API is Best for Mac

| Feature | Redfish (HTTPS) | SSH |
|---------|-----------------|-----|
| **Setup** | pip3 install requests | pip3 install paramiko OR brew install sshpass |
| **Dependencies** | 1 Python package | Python package OR Homebrew + sshpass |
| **Port** | 443 (HTTPS) | 22 (SSH) |
| **Compatibility** | Native macOS | Native macOS (Python) / Requires Homebrew (Bash) |
| **Speed** | Fast | Fast |
| **Ease** | Easiest ⭐ | Easy (Python) / Complex (Bash) |

---

## Step-by-Step Example Session

Here's what you'll see:

```
MacBook-Pro:~ user$ python3 disable_ipmi_idrac_redfish.py

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

✓ All operations completed successfully!
```

---

## Advanced macOS Tips

### Create an Alias (Optional)

Add to your `~/.zshrc` or `~/.bash_profile`:

```bash
alias disable-ipmi='python3 ~/path/to/disable_ipmi_idrac_redfish.py'
```

Then just run:
```bash
disable-ipmi
```

### Run from Anywhere

```bash
# Add to your PATH
sudo ln -s ~/path/to/disable_ipmi_idrac_redfish.py /usr/local/bin/disable-ipmi

# Now run from anywhere
disable-ipmi
```

### Schedule with launchd (Automation)

Create `~/Library/LaunchAgents/com.idrac.ipmi.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.idrac.ipmi</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/disable_ipmi_idrac_redfish.py</string>
        <string>-u</string>
        <string>root</string>
        <string>-p</string>
        <string>password</string>
        <string>-f</string>
        <string>/path/to/idrac_hosts.txt</string>
    </array>
</dict>
</plist>
```

---

## Comparison: All Three Versions on Mac

### 🥇 Redfish API (Python) - RECOMMENDED ⭐
```bash
pip3 install requests
python3 disable_ipmi_idrac_redfish.py
```
- ✅ Easiest setup
- ✅ One package to install
- ✅ Works immediately
- ✅ Uses HTTPS (usually open)
- ⭐ **Best choice for 90% of Mac users**

### 🥈 SSH (Python) - GOOD ALTERNATIVE
```bash
pip3 install paramiko
python3 disable_ipmi_idrac.py
```
- ✅ Easy setup
- ✅ One package to install
- ✅ Works for older iDRACs
- ✅ SSH-based

### 🥉 Bash - AVOID UNLESS YOU LOVE HOMEBREW
```bash
# First install Homebrew (5-10 minutes)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then install sshpass
brew install hudochenkov/sshpass/sshpass

# Finally run
./disable_ipmi_idrac.sh
```
- ⚠️ Complex setup
- ⚠️ Requires Homebrew
- ⚠️ Extra time investment
- ⚠️ Not recommended for Mac

---

## Need Help?

### Check Script Status
```bash
python3 disable_ipmi_idrac_redfish.py -h
```

### View Logs
Logs are created in the current directory:
```bash
cat ipmi_disable_redfish_*.log
```

### Test Connection to iDRAC
```bash
# Test HTTPS
curl -k https://192.168.1.100

# Test Redfish endpoint
curl -k -u root:password https://192.168.1.100/redfish/v1/
```

---

## Summary for macOS Users

**The Best Way**:
1. Open Terminal
2. Run: `pip3 install requests`
3. Run: `python3 disable_ipmi_idrac_redfish.py`
4. Follow prompts
5. Done! ✅

**Total Time**: ~2 minutes including setup

---

## macOS Version Compatibility

| macOS Version | Python 3 | Script Support |
|---------------|----------|----------------|
| macOS 15 (Sequoia) | ✅ Pre-installed | ✅ Full |
| macOS 14 (Sonoma) | ✅ Pre-installed | ✅ Full |
| macOS 13 (Ventura) | ✅ Pre-installed | ✅ Full |
| macOS 12 (Monterey) | ✅ Pre-installed | ✅ Full |
| macOS 11 (Big Sur) | ✅ Pre-installed | ✅ Full |
| macOS 10.15 (Catalina) | ✅ Pre-installed | ✅ Full |
| macOS 10.14 (Mojave) | ⚠️ May need install | ✅ Full |

**All modern Macs work perfectly!** 🎉
