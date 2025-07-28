"""
Test script to verify IB Gateway connection
"""

import logging
from ib_connector import IBConnector
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_connection():
    """Test IB Gateway connection"""
    print("Testing IB Gateway connection...")
    
    # Create connector
    connector = IBConnector()
    
    # Try to connect
    if connector.connect():
        print("✓ Successfully connected to IB Gateway!")
        
        # Test fetching data
        print("\nTesting historical data fetch...")
        try:
            bars = connector.get_historical_data("AAPL", duration="1 D", bar_size="1 hour")
            if bars:
                print(f"✓ Received {len(bars)} bars")
                print(f"Latest bar: {bars[-1].date} - Close: {bars[-1].close}")
            else:
                print("✗ No data received")
        except Exception as e:
            print(f"✗ Error fetching data: {str(e)}")
        
        # Test account info
        print("\nTesting account info fetch...")
        try:
            account_info = connector.get_account_info()
            if account_info:
                print("✓ Account info received")
                print(f"Account keys: {list(account_info.keys())[:5]}...")
            else:
                print("✗ No account info received")
        except Exception as e:
            print(f"✗ Error fetching account info: {str(e)}")
        
        # Disconnect
        connector.disconnect()
        print("\n✓ Disconnected successfully")
    else:
        print("✗ Failed to connect to IB Gateway")
        print("\nTroubleshooting tips:")
        print("1. Make sure IB Gateway is running")
        print("2. Check that API is enabled in IB Gateway settings")
        print("3. Verify the port number (default: 4002)")
        print("4. Ensure 127.0.0.1 is in trusted IP addresses")

if __name__ == "__main__":
    test_connection()
