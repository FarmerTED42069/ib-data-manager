"""
Debug script to test data fetching directly
"""

import asyncio
import logging
from ib_data_manager.api.async_ib_connector import AsyncIBConnector

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_data_fetch():
    """Test data fetching directly"""
    connector = AsyncIBConnector()
    
    try:
        # Connect
        print("Connecting to IB Gateway...")
        connected = await connector.connect()
        if not connected:
            print("❌ Failed to connect to IB Gateway")
            return
        
        print("✅ Connected successfully")
        
        # Test simple contract qualification first
        print("\n--- Testing Contract Qualification ---")
        contract = connector.create_contract("SPY", "STK", "SMART", "USD")
        print(f"Created contract: {contract}")
        
        try:
            qualified = await connector.ib.qualifyContractsAsync(contract)
            if qualified:
                print(f"✅ Contract qualified: {qualified[0]}")
            else:
                print("❌ Contract qualification failed")
                return
        except Exception as e:
            print(f"❌ Contract qualification error: {e}")
            return
        
        # Test historical data fetch
        print("\n--- Testing Historical Data Fetch ---")
        try:
            bars = await connector.get_historical_data(
                symbol="SPY",
                sec_type="STK", 
                exchange="SMART",
                currency="USD",
                duration="1 D",
                bar_size="1 min"
            )
            
            if bars:
                print(f"✅ Successfully fetched {len(bars)} bars")
                print(f"First bar: {bars[0]}")
                print(f"Last bar: {bars[-1]}")
            else:
                print("❌ No data returned")
                
        except Exception as e:
            print(f"❌ Historical data fetch error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test with a different symbol
        print("\n--- Testing with AAPL ---")
        try:
            bars = await connector.get_historical_data(
                symbol="AAPL",
                sec_type="STK", 
                exchange="SMART",
                currency="USD",
                duration="1 D",
                bar_size="5 mins"
            )
            
            if bars:
                print(f"✅ AAPL: Successfully fetched {len(bars)} bars")
            else:
                print("❌ AAPL: No data returned")
                
        except Exception as e:
            print(f"❌ AAPL fetch error: {e}")
        
    finally:
        # Disconnect
        await connector.disconnect()
        print("Disconnected")

if __name__ == "__main__":
    asyncio.run(test_data_fetch())
