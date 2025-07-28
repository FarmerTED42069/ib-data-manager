# IB Data Manager - Connection Troubleshooting Guide

## Connection Failed Issue

If you're seeing "Failed to Connect" in the application, follow these steps:

### Step 1: Check IB Gateway Status

1. **Is IB Gateway running?**
   - Look for the IB Gateway window on your desktop
   - It should show your username and connection status
   - If not running, start IB Gateway and log in

2. **Is IB Gateway fully initialized?**
   - Wait for the login process to complete
   - The gateway should show "Connected" status
   - Wait 30-60 seconds after logging in before trying to connect

### Step 2: Verify API Settings in IB Gateway

1. Open IB Gateway
2. Go to **Configure → Settings → API → Settings**
3. Verify these settings:
   - ✅ **Enable ActiveX and Socket Clients** is checked
   - ✅ **Read-Only API** is UNCHECKED (if you want full functionality)
   - ✅ **Download open orders on connection** is checked
   - ✅ **127.0.0.1** is in the "Trusted IP Addresses" list

4. Click **OK** to save any changes
5. You may need to restart IB Gateway for changes to take effect

### Step 3: Check Port Configuration

1. **Default Ports:**
   - Live Trading: Port 4001
   - Paper Trading: Port 4002

2. **Verify the correct port:**
   - In IB Gateway: Configure → Settings → API → Settings
   - Look for "Socket port" setting
   - Make sure it matches what you're using in the application

### Step 4: Run Connection Diagnostic

1. Navigate to the application folder
2. Double-click `RUN_CONNECTION_DIAGNOSTIC.bat`
3. Review the output for specific issues:
   - Port availability
   - Process conflicts
   - Firewall issues

### Step 5: Common Solutions

#### A. Port Conflict
If the diagnostic shows the port is already in use:
1. Close all other IB API applications
2. Try a different Client ID (edit configuration)
3. Restart IB Gateway

#### B. Firewall Issues
1. Temporarily disable Windows Firewall to test
2. Add IB Gateway to firewall exceptions:
   - Windows Security → Firewall & network protection
   - Allow an app through firewall
   - Add IB Gateway executable

#### C. Try Different Connection Settings
1. Double-click `EDIT_CONFIG.bat`
2. Try these settings:
   - Host: `127.0.0.1` (instead of localhost)
   - Client ID: Try 2, 3, or 999
   - Port: Verify 4001 (live) or 4002 (paper)

### Step 6: Alternative Solutions

1. **Run as Administrator:**
   - Right-click on the application
   - Select "Run as administrator"

2. **Check for Multiple IB Gateway Instances:**
   - Open Task Manager
   - Look for multiple java.exe processes
   - End duplicate processes

3. **Restart Everything:**
   - Close the application
   - Close IB Gateway
   - Restart your computer
   - Start IB Gateway first, wait for full initialization
   - Then start the application

### Step 7: If Still Not Working

1. **Check IB Gateway Logs:**
   - In IB Gateway: View → Diagnostics → API Log
   - Look for error messages

2. **Try Manual Connection Test:**
   - Open Command Prompt
   - Run: `telnet 127.0.0.1 4001`
   - If it connects, the port is open

3. **Contact Support:**
   - Interactive Brokers technical support
   - Provide the diagnostic output

## Quick Checklist

Before connecting, ensure:
- [ ] IB Gateway is running and logged in
- [ ] API is enabled in IB Gateway settings
- [ ] Correct port is configured (4001/4002)
- [ ] 127.0.0.1 is in trusted IP addresses
- [ ] No other applications are using the same Client ID
- [ ] Firewall is not blocking the connection

## Test Connection Command

After making changes, use this test sequence:
1. Start IB Gateway
2. Wait 1 minute for full initialization
3. Run `RUN_CONNECTION_DIAGNOSTIC.bat`
4. If all checks pass, try the application again
