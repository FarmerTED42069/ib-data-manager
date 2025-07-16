"""
IB Gateway Connection Diagnostics Tool

This script performs a comprehensive diagnosis of your IB Gateway API connection,
checking multiple aspects of the connection and providing detailed feedback.
"""

import os
import sys
import socket
import random
import time
import logging
import traceback
from datetime import datetime
try:
    from ib_insync import IB, util
    IB_INSYNC_AVAILABLE = True
except ImportError:
    IB_INSYNC_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Connection settings - adjust as needed
HOST = '127.0.0.1'
PORTS_TO_TEST = [
    (4001, "IB Gateway Live Trading"),
    (4002, "IB Gateway Paper Trading"),
    (7496, "TWS Live Trading"),
    (7497, "TWS Paper Trading"),
]
CLIENT_IDS = [random.randint(10000, 99999) for _ in range(3)]

def print_separator(message=""):
    """Print a separator line with optional message."""
    width = 80
    if message:
        padding = (width - len(message) - 2) // 2
        print("\n" + "=" * padding + f" {message} " + "=" * padding + "\n")
    else:
        print("\n" + "=" * width + "\n")

def test_port_open(host, port):
    """Test if a specific port is open."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        if result == 0:
            logger.info(f"✓ Port {port} is OPEN")
            open_status = True
        else:
            logger.info(f"✗ Port {port} is CLOSED (error code: {result})")
            open_status = False
        sock.close()
        return open_status
    except Exception as e:
        logger.error(f"Error testing port {port}: {e}")
        return False

def test_ib_gateway_connection(host, port, client_id, readonly=True):
    """
    Test connection to IB Gateway with detailed diagnostics.
    
    Returns tuple of (success, details, error_type)
    """
    if not IB_INSYNC_AVAILABLE:
        return (False, "ib_insync library not installed", "ImportError")
    
    ib = IB()
    connected = False
    api_verified = False
    error_type = None
    error_details = None
    commands_tested = []
    
    try:
        # Step 1: Initial connection
        logger.info(f"Attempting to connect to {host}:{port} with client ID {client_id}...")
        ib.connect(host, port, clientId=client_id, readonly=readonly, timeout=10)
        
        if ib.isConnected():
            connected = True
            logger.info("✓ Initial connection established")
            
            # Step 2: Test basic API command
            try:
                server_time = ib.reqCurrentTime()
                logger.info(f"✓ Server time command successful: {server_time}")
                commands_tested.append("reqCurrentTime")
                api_verified = True
            except Exception as cmd_error:
                logger.error(f"✗ Server time command failed: {cmd_error}")
                error_type = type(cmd_error).__name__
                error_details = str(cmd_error)
            
            # Step 3: Test account info (if not in readonly mode)
            if not readonly:
                try:
                    account_values = ib.accountSummary()
                    if account_values:
                        logger.info(f"✓ Account summary command successful")
                        commands_tested.append("accountSummary")
                    else:
                        logger.warning("? Account summary returned no data")
                except Exception as acct_error:
                    logger.error(f"✗ Account summary command failed: {acct_error}")
                    if not error_type:  # Only record first error
                        error_type = type(acct_error).__name__
                        error_details = str(acct_error)
        else:
            logger.error("✗ Could not establish connection")
            error_type = "ConnectionError"
            error_details = "isConnected() returned False"
    
    except Exception as e:
        logger.error(f"✗ Connection error: {type(e).__name__}: {e}")
        error_type = type(e).__name__
        error_details = str(e)
        
    finally:
        # Always disconnect if connected
        if ib and ib.isConnected():
            ib.disconnect()
            logger.info("Connection closed")
    
    # Prepare result summary
    status = api_verified  # Only consider success if API commands worked
    
    details = {
        "host": host,
        "port": port,
        "client_id": client_id,
        "connected": connected,
        "api_verified": api_verified,
        "commands_tested": commands_tested,
        "error_type": error_type,
        "error_details": error_details,
        "readonly_mode": readonly
    }
    
    return (status, details, error_type)

def run_ib_diagnostics():
    """Run a comprehensive set of IB Gateway connection diagnostics."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "python_version": sys.version,
            "ib_insync_available": IB_INSYNC_AVAILABLE,
            "platform": sys.platform
        },
        "port_tests": {},
        "connection_tests": []
    }
    
    print_separator("INTERACTIVE BROKERS GATEWAY DIAGNOSTICS")
    print("This tool will test your IB Gateway connection")
    print("and help diagnose any connectivity issues.\n")
    
    # Stage 1: Test all ports
    print_separator("PORT AVAILABILITY TESTS")
    print("Testing if IB API ports are accessible on your system...\n")
    
    for port, description in PORTS_TO_TEST:
        print(f"Testing {description} ({port}):")
        port_open = test_port_open(HOST, port)
        results["port_tests"][port] = {
            "description": description,
            "open": port_open
        }
        print("")
    
    # Find open ports for further testing
    open_ports = [port for port, data in results["port_tests"].items() if data["open"]]
    
    if not open_ports:
        print_separator("DIAGNOSTIC RESULT")
        print("❌ No IB Gateway or TWS ports are open.")
        print("\nPossible reasons:")
        print("1. IB Gateway or TWS is not running")
        print("2. API connections are not enabled in settings")
        print("3. Firewall is blocking connections")
        print("\nPlease start IB Gateway and enable API connections")
        return results
    
    # Stage 2: Test API connections for each open port
    print_separator("API CONNECTION TESTS")
    print("Testing API connectivity on each open port...\n")
    
    for port in open_ports:
        port_desc = next((desc for p, desc in PORTS_TO_TEST if p == port), f"Port {port}")
        print(f"Testing connection to {port_desc}:")
        
        # Try with different client IDs
        for client_id in CLIENT_IDS:
            print(f"\nAttempting with client ID: {client_id}")
            
            # Test in read-only mode first
            status, details, error_type = test_ib_gateway_connection(HOST, port, client_id, readonly=True)
            results["connection_tests"].append(details)
            
            if status:
                print(f"✅ Connection successful in read-only mode with client ID {client_id}")
                
                # If readonly worked, try with full permissions
                print("\nTesting with full permissions (readonly=False):")
                full_status, full_details, full_error = test_ib_gateway_connection(HOST, port, client_id + 1, readonly=False)
                results["connection_tests"].append(full_details)
                
                if full_status:
                    print(f"✅ Connection successful with full permissions using client ID {client_id + 1}")
                else:
                    print(f"⚠️ Read-only connection works, but full permissions failed: {full_error}")
                
                # No need to try other client IDs if one worked
                break
            else:
                print(f"❌ Connection failed with client ID {client_id}: {error_type}")
    
    # Stage 3: Diagnostics summary
    print_separator("DIAGNOSTIC SUMMARY")
    
    # Check if any connections were successful
    successful_connections = [test for test in results["connection_tests"] if test["api_verified"]]
    
    if successful_connections:
        best_connection = successful_connections[0]
        print("✅ CONNECTION DIAGNOSTIC RESULT: SUCCESS")
        print(f"\nWorking connection found:")
        print(f"- Port: {best_connection['port']} ({next((desc for p, desc in PORTS_TO_TEST if p == best_connection['port']), 'Unknown')})")
        print(f"- Client ID: {best_connection['client_id']}")
        print(f"- Read-only mode: {best_connection['readonly_mode']}")
        print(f"- API commands verified: {', '.join(best_connection['commands_tested'])}")
        
        # Configuration recommendations
        print("\nRECOMMENDED CONFIGURATION:")
        print(f"TWS_HOST = '127.0.0.1'")
        print(f"TWS_PORT = {best_connection['port']}")
        print(f"TWS_CLIENT_ID = {best_connection['client_id']}")
        
    else:
        print("❌ CONNECTION DIAGNOSTIC RESULT: FAILED")
        print("\nNo working connections found. Common issues:")
        
        # Analyze common error patterns
        error_types = [test.get("error_type") for test in results["connection_tests"] if test.get("error_type")]
        
        if "TimeoutError" in error_types:
            print("- API Server is running but client-side connection times out")
            print("  → Check if 'API Client' shows as 'disconnected' in IB Gateway")
            print("  → Go to Configure → Settings → API → Settings and verify settings")
            
        if "ConnectionRefusedError" in error_types:
            print("- Connection was refused")
            print("  → Ensure IB Gateway is running and API is enabled")
            print("  → Check firewall settings")
            
        if "PermissionError" in error_types:
            print("- Permission denied for API operations")
            print("  → Make sure 'Read-Only API' is unchecked in IB Gateway settings")
            
        # General troubleshooting tips
        print("\nTROUBLESHOOTING TIPS:")
        print("1. Restart IB Gateway completely")
        print("2. Verify API settings in Configure → Settings → API → Settings")
        print("3. Ensure 'Enable ActiveX and Socket Clients' is checked")
        print("4. Check firewall is not blocking connections")
        print("5. Try a different client ID")
    
    return results

if __name__ == "__main__":
    try:
        run_ib_diagnostics()
    except Exception as e:
        print(f"\nERROR: Diagnostic tool encountered an error: {type(e).__name__}: {e}")
        print("\nException details:")
        traceback.print_exc()
    
    print("\nDiagnostic completed. Press Enter to exit...")
    input()
