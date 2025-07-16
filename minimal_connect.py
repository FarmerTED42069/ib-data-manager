"""
Minimal IB Gateway connection test.
Tests only the basic connectivity with no API operations.
"""

from ib_insync import IB
import random
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def minimal_connect():
    """Perform a minimal connection test with no API operations."""
    
    # Create IB instance
    ib = IB()
    
    try:
        # Connection settings
        host = '127.0.0.1'
        port = 4002  # IB Gateway Paper Trading port
        client_id = random.randint(10000, 99999)
        
        print(f"Attempting connection to {host}:{port} with client ID {client_id}...")
        
        # Set a custom timeout (seconds)
        timeout = 5
        
        # Connect with readonly mode
        ib.connect(host, port, clientId=client_id, readonly=True, timeout=timeout)
        
        # Check connection status
        if ib.isConnected():
            print("SUCCESS: Connected to IB Gateway!")
            
            # Don't run any API operations, just test the connection
            print("Connection test successful. No API operations performed.")
            return True
        else:
            print("FAILED: Could not establish connection.")
            return False
            
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return False
        
    finally:
        # Always disconnect if connected
        if ib and ib.isConnected():
            print("Disconnecting...")
            ib.disconnect()
            print("Disconnected successfully.")

if __name__ == "__main__":
    print("\n===== Minimal IB Gateway Connection Test =====\n")
    print("IMPORTANT: In IB Gateway, check:")
    print("1. Settings -> API -> Settings")
    print("2. 'Enable ActiveX and Socket Clients' must be CHECKED")
    print("3. Socket port should be set to 4002")
    print("----------------------------------------------\n")
    
    success = minimal_connect()
    
    if not success:
        print("\nTroubleshooting tips:")
        print("1. Make sure IB Gateway is running")
        print("2. Verify API settings in IB Gateway")
        print("3. Check if the API Client shows 'connected' in IB Gateway status")
        print("4. Restart IB Gateway completely")
