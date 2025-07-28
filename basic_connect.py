"""
Basic IB Gateway connection test using ib_insync.

This script attempts a minimal connection to IB Gateway.
"""

from ib_insync import IB
import random
import time
import socket

def check_port_availability(port):
    """Check if a port is available or in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('127.0.0.1', port))
            if result == 0:
                print(f"[PASS] Port {port} is OPEN and listening")
                return True
            else:
                print(f"[FAIL] Port {port} is CLOSED or not accessible")
                return False
    except Exception as e:
        print(f"[FAIL] Error checking port {port}: {str(e)}")
        return False

def basic_connect(port=4002):
    """Perform a basic connection test with minimal operations."""
    try:
        # First check if the port is available
        if not check_port_availability(port):
            print(f"Port {port} is not accessible. IB Gateway might not be running or listening on this port.")
            return False
            
        # Create a new IB instance
        ib = IB()
        
        # Connection parameters
        host = '127.0.0.1'
        client_id = random.randint(10000, 99999)
        
        print(f"Attempting to connect to {host}:{port} with client ID {client_id}...")
        
        # Connect to IB Gateway with a timeout
        ib.connect(host, port, clientId=client_id, readonly=True, timeout=10)
        
        if ib.isConnected():
            print("SUCCESS: Connected to IB Gateway!")
            print("Requesting server time...")
            
            # Get server time (simple operation)
            current_time = ib.reqCurrentTime()
            print(f"Server time: {current_time}")
            
            # Wait a moment
            time.sleep(1)
            
            print("Disconnecting...")
            ib.disconnect()
            print("Disconnected successfully.")
            return True
        else:
            print("FAILED: Could not establish connection.")
            return False
    
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    print("\n===== Basic IB Gateway Connection Test =====\n")
    
    # Try both ports commonly used by IB
    ports = [4001, 4002, 7496, 7497]
    
    print("Checking all common IB Gateway/TWS ports...")
    for port in ports:
        print(f"\nTesting port {port}:")
        success = basic_connect(port)
        if success:
            print(f"\nSuccessfully connected on port {port}")
            print("Use this port in your configuration.")
            break
    else:
        print("\nCould not connect to any IB ports.")
        print("\nTroubleshooting tips:")
        print("1. Make sure IB Gateway or TWS is running")
        print("2. Verify API settings in IB Gateway/TWS:")
        print("   - Open IB Gateway/TWS")
        print("   - Go to Edit -> Global Configuration -> API -> Settings")
        print("   - Make sure 'Enable ActiveX and Socket Clients' is checked")
        print("   - Add '127.0.0.1' to the 'Trusted IPs' list")
        print("3. Check that your firewall is not blocking the connection")
        print("4. Try a different client ID if another application might be connected")
        print("5. Restart IB Gateway/TWS")
