"""
Troubleshooting script for IB Data Manager
"""

from ib_insync import *
import logging
from datetime import datetime, timedelta
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def troubleshoot():
    """Run troubleshooting diagnostics"""
    print("="*60)
    print("IB Data Manager - Troubleshooting Diagnostics")
    print("="*60)
    print(f"Current time: {datetime.now()}")
    print()
    
    ib = IB()
    
    try:
        # Connect to IB Gateway
        print("1. Testing connection to IB Gateway...")
        ib.connect('127.0.0.1', 4001, clientId=999)  # Use different client ID
        print("✓ Connected successfully!")
        
        # Check server time
        print("\n2. Checking server time...")
        server_time = ib.reqCurrentTime()
        server_datetime = datetime.fromtimestamp(server_time)
        print(f"✓ Server time: {server_datetime}")
        print(f"✓ Local time: {datetime.now()}")
        
        # Check if market is open
        current_time = datetime.now()
        is_weekend = current_time.weekday() >= 5  # Saturday=5, Sunday=6
        
        if is_weekend:
            print("\n⚠️ WARNING: It's weekend. Market is closed.")
            print("Historical data might be limited or unavailable for some instruments.")
        
        # Test with different symbols and data types
        print("\n3. Testing data retrieval with different configurations...")
        
        test_configs = [
            # (symbol, exchange, duration, bar_size, what_to_show, useRTH)
            ("SPY", "SMART", "1 D", "30 mins", "TRADES", True),
            ("SPY", "SMART", "1 D", "30 mins", "MIDPOINT", True),
            ("AAPL", "SMART", "1 D", "1 hour", "TRADES", True),
            ("EUR.USD", "IDEALPRO", "1 D", "1 hour", "MIDPOINT", True),
            ("SPY", "SMART", "1 D", "30 mins", "TRADES", False),  # Include extended hours
        ]
        
        for symbol, exchange, duration, bar_size, what_to_show, use_rth in test_configs:
            print(f"\nTesting: {symbol} on {exchange}")
            print(f"Settings: {duration}, {bar_size}, {what_to_show}, RTH={use_rth}")
            
            try:
                if symbol == "EUR.USD":
                    contract = Forex('EURUSD')
                else:
                    contract = Stock(symbol, exchange, 'USD')
                
                # Qualify contract
                qualified = ib.qualifyContracts(contract)
                
                if qualified:
                    print(f"✓ Contract qualified: {qualified[0]}")
                    
                    # Request historical data
                    bars = ib.reqHistoricalData(
                        qualified[0],
                        endDateTime='',
                        durationStr=duration,
                        barSizeSetting=bar_size,
                        whatToShow=what_to_show,
                        useRTH=use_rth,
                        formatDate=1,
                        timeout=10
                    )
                    
                    if bars:
                        print(f"✓ SUCCESS: Received {len(bars)} bars")
                        print(f"  First bar: {bars[0].date} - Close: {bars[0].close}")
                        print(f"  Last bar: {bars[-1].date} - Close: {bars[-1].close}")
                    else:
                        print("✗ FAILED: No data received")
                else:
                    print("✗ FAILED: Could not qualify contract")
                    
            except Exception as e:
                print(f"✗ ERROR: {str(e)}")
        
        # Check market data subscriptions
        print("\n4. Checking market data subscriptions...")
        try:
            # Request market data type
            ib.reqMarketDataType(3)  # 3 = Delayed
            print("✓ Set market data type to DELAYED")
            
            # Try to get delayed quotes
            spy = Stock('SPY', 'SMART', 'USD')
            qualified = ib.qualifyContracts(spy)
            
            if qualified:
                ticker = ib.reqMktData(qualified[0], '', False, False)
                ib.sleep(5)  # Wait for data
                
                print("\nMarket Data Status:")
                print(f"Last Price: {ticker.last}")
                print(f"Bid: {ticker.bid}")
                print(f"Ask: {ticker.ask}")
                print(f"Volume: {ticker.volume}")
                print(f"Market Data Type: {ticker.marketDataType}")
                
                ib.cancelMktData(qualified[0])
        except Exception as e:
            print(f"✗ Market data error: {str(e)}")
        
        # Provide recommendations
        print("\n5. Recommendations:")
        print("-" * 40)
        
        if is_weekend:
            print("• It's weekend. Try testing during market hours (Mon-Fri 9:30 AM - 4:00 PM ET)")
        
        print("• Make sure you have market data subscriptions for the instruments you're trying to access")
        print("• Check IB Gateway logs for any error messages")
        print("• Try using delayed market data (in IB Gateway: Configure > Settings > API > Settings)")
        print("• For SPY historical data issues, try:")
        print("  - Shorter duration (e.g., '1 H' instead of '1 D')")
        print("  - Different bar sizes (e.g., '5 mins' or '1 hour')")
        print("  - Set useRTH=False to include extended hours data")
        print("  - Use MIDPOINT instead of TRADES for whatToShow parameter")
        
    except Exception as e:
        print(f"\n✗ Critical error: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Ensure IB Gateway is running")
        print("2. Check that API connections are enabled in IB Gateway")
        print("3. Verify port 4001 is correct (4002 for paper trading)")
        print("4. Check if another application is using the same client ID")
        
    finally:
        if ib.isConnected():
            ib.disconnect()
            print("\n✓ Disconnected from IB Gateway")
        
        print("\n" + "="*60)
        print("Diagnostics complete. Check the output above for issues.")
        print("="*60)

if __name__ == "__main__":
    troubleshoot()
