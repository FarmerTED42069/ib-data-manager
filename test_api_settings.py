"""
Test Interactive Brokers API settings and permissions

This script specifically focuses on verifying API settings in IB Gateway
"""

from ib_insync import IB
import logging
import time
import random

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_api_connection():
    """Test API connectivity with strict focus on settings"""
    
    ib = IB()
    
    # Connection parameters
    host = '127.0.0.1'
    port = 4002  # IB Gateway Paper Trading port
    client_id = random.randint(10000, 99999)
    
    try:
        logger.info(f"Attempting to connect to {host}:{port} with client ID {client_id}...")
        logger.info("Setting read-only mode to FALSE to test full permissions...")
        
        # First try with explicit timeout and debug mode
        ib.connect(host, port, clientId=client_id, readonly=False, timeout=15)
        
        if ib.isConnected():
            logger.info("CONNECTION SUCCESSFUL! Testing basic API command...")
            
            # Test if a simple command works
            server_time = ib.reqCurrentTime()
            logger.info(f"Server Time: {server_time}")
            
            # Check managed accounts (should be available if properly authorized)
            accounts = ib.managedAccounts()
            logger.info(f"Managed Accounts: {accounts}")
            
            logger.info("Tests completed successfully! API connection is working.")
            return True
        else:
            logger.error("Initial connection failed.")
            return False
            
    except Exception as e:
        logger.error(f"Connection error: {type(e).__name__}: {e}")
        return False
        
    finally:
        # Always disconnect
        if ib.isConnected():
            ib.disconnect()
            logger.info("Disconnected from IB Gateway")

if __name__ == "__main__":
    print("\n===== Interactive Brokers API Settings Test =====\n")
    
    print("IMPORTANT IB GATEWAY SETTINGS TO CHECK:")
    print("1. In IB Gateway: Configure -> Settings -> API -> Settings")
    print("2. Ensure 'Enable ActiveX and Socket Clients' is CHECKED")
    print("3. Ensure 'Read-Only API' is UNCHECKED")
    print("4. Check that socket port is set to 4002")
    print("5. Make sure no other application is using the same client ID\n")
    
    success = test_api_connection()
    
    if not success:
        print("\nAPI SETTINGS TROUBLESHOOTING:")
        print("1. Restart IB Gateway completely")
        print("2. Make sure your login credentials are correct")
        print("3. Verify the API configuration screen shows API status as 'Enabled'")
        print("4. Try to toggle the 'Enable ActiveX and Socket Clients' off and back on")
        print("5. Check the IB Gateway log tab for any error messages")
