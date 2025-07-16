"""
Basic IB Gateway connection test using ib_insync.

This script attempts a minimal connection to IB Gateway with an increased timeout.
"""

from ib_insync import IB
import random
import time
import asyncio

def basic_connect():
    """Perform a basic connection test with minimal operations."""
    try:
        # Create a new IB instance
        ib = IB()
        
        # Connection parameters
        host = '127.0.0.1'
        port = 4002  # IB Gateway Paper Trading
        client_id = random.randint(10000, 99999)
        
        print(f"Attempting to connect to {host}:{port} with client ID {client_id}...")
        
        # Connect to IB Gateway with a longer timeout (10 seconds)
        ib.connect(host, port, clientId=client_id, readonly=True, timeout=10)
        
        if ib.isConnected():
            print("SUCCESS: Connected to IB Gateway!")
            print("Requesting server time...")
            
            # Get server time (simple operation)
            current_time = ib.reqCurrentTime()
            print(f"Server time: {current_time}")
            
            # Wait a moment
            time.sleep(3)
            
            print("Disconnecting...")
            ib.disconnect()
            print("Disconnected successfully.")
            return True
        else:
            print("FAILED: Could not establish connection.")
            return False
    
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        print(f"Make sure that in IB Gateway:")
        print("1. Settings -> API -> Settings has 'Enable ActiveX and Socket Clients' checked")
        print("2. Settings -> API -> Settings has 'Read-Only API' unchecked")
        print("3. The 'API' indicator shows 'connected' in the main IB Gateway window")
        return False


if __name__ == "__main__":
    print("\n===== Basic IB Gateway Connection Test =====\n")
    success = basic_connect()
    
    if not success:
        print("\nTroubleshooting tips:")
        print("1. Make sure IB Gateway is running")
        print("2. Verify API settings in IB Gateway")
        print("3. Try restarting IB Gateway")
        print("4. Check if another application is using the connection")
