"""
Test script for the AsyncIBConnector
"""

import asyncio
import logging
from ib_data_manager.api.async_ib_connector import AsyncIBConnector


async def test_async_connector():
    """Test the async IB connector"""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create connector
    connector = AsyncIBConnector()
    
    try:
        # Connect to IB Gateway
        print("Connecting to IB Gateway...")
        if await connector.connect():
            print("Connected successfully!")
            
            # Test account info
            print("Getting account information...")
            account_info = await connector.get_account_info()
            if account_info:
                print(f"Account info retrieved: {len(account_info)} items")
                # Print a few key items
                for key in ['NetLiquidation', 'TotalCashValue', 'AvailableFunds']:
                    if key in account_info:
                        print(f"  {key}: {account_info[key]}")
            
            # Test positions
            print("Getting positions...")
            positions = await connector.get_positions()
            if positions is not None:
                print(f"Positions retrieved: {len(positions)} items")
            
            # Test market data
            print("Getting real-time quotes for AAPL...")
            ticker = await connector.start_realtime_quotes("AAPL")
            if ticker:
                print(f"Started real-time quotes for AAPL")
                print(f"  Bid: {ticker.bid}, Ask: {ticker.ask}")
                # Stop the quotes
                connector.stop_realtime_quotes(ticker)
            
            # Test historical data
            print("Getting historical data for AAPL...")
            bars = await connector.get_historical_data("AAPL", duration="1 D", bar_size="1 hour")
            if bars:
                print(f"Received {len(bars)} bars")
                for bar in bars[:3]:  # Show first 3 bars
                    print(f"  {bar.date}: O={bar.open}, H={bar.high}, L={bar.low}, C={bar.close}, V={bar.volume}")
            
            # Test market depth (Level 2 data)
            print("Testing market depth subscription...")
            depth_ticker = await connector.start_market_depth("AAPL", num_rows=5)
            if depth_ticker:
                print("Started market depth for AAPL")
                # Let it run for a few seconds to collect data
                await asyncio.sleep(3)
                # Stop the depth data
                connector.stop_market_depth(depth_ticker)
            
            # Disconnect
            print("Disconnecting...")
            await connector.disconnect()
            print("Disconnected successfully!")
        else:
            print("Connection failed!")
            
    except Exception as e:
        logging.error(f"Error during test: {str(e)}")
        # Ensure we disconnect even if there's an error
        await connector.disconnect()


def main():
    """Main function to run the test"""
    print("Starting AsyncIBConnector test...")
    asyncio.run(test_async_connector())
    print("Test completed.")


if __name__ == "__main__":
    main()
