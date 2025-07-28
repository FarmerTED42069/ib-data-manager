"""
Diagnostic script to troubleshoot IB Gateway connection and data issues
"""

from ib_insync import *
import logging
import time
from datetime import datetime

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def diagnose_connection():
    """Run comprehensive diagnostics"""
    print("=== IB Gateway Connection Diagnostics ===")
    print(f"Time: {datetime.now()}")
    print("-" * 50)
    
    ib = IB()
    
    # Test 1: Basic Connection
    print("\n1. Testing basic connection...")
    try:
        ib.connect('127.0.0.1', 4001, clientId=1)
        print("✓ Connected successfully!")
        print(f"  Connected: {ib.isConnected()}")
        print(f"  Client ID: {ib.client.clientId}")
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        return
    
    # Test 2: Account information
    print("\n2. Testing account access...")
    try:
        account_values = ib.accountSummary()
        if account_values:
            print(f"✓ Account access successful! Found {len(account_values)} values")
            print(f"  Sample values:")
            for av in account_values[:3]:
                print(f"    {av.tag}: {av.value}")
        else:
            print("✗ No account values returned")
    except Exception as e:
        print(f"✗ Account access error: {str(e)}")
    
    # Test 3: Market data subscription
    print("\n3. Testing market data subscription...")
    try:
        # Create SPY contract
        spy = Stock('SPY', 'SMART', 'USD')
        
        # Qualify the contract
        qualified = ib.qualifyContracts(spy)
        if qualified:
            print(f"✓ Contract qualified: {qualified[0]}")
            
            # Request market data
            ticker = ib.reqMktData(spy, '', False, False)
            print("  Waiting for market data...")
            ib.sleep(2)  # Wait for data
            
            if ticker.last:
                print(f"✓ Market data received! Last price: {ticker.last}")
            else:
                print("✗ No market data received")
                print(f"  Bid: {ticker.bid}, Ask: {ticker.ask}")
                print(f"  Market data type: {ticker.marketDataType}")
        else:
            print("✗ Contract qualification failed")
            
    except Exception as e:
        print(f"✗ Market data error: {str(e)}")
    
    # Test 4: Historical data
    print("\n4. Testing historical data request...")
    try:
        # Try different approaches
        approaches = [
            ("SPY with default settings", Stock('SPY', 'SMART', 'USD'), '1 D', '30 mins', 'TRADES'),
            ("SPY with MIDPOINT", Stock('SPY', 'SMART', 'USD'), '1 D', '30 mins', 'MIDPOINT'),
            ("AAPL test", Stock('AAPL', 'SMART', 'USD'), '1 D', '1 hour', 'TRADES'),
            ("SPY with shorter duration", Stock('SPY', 'SMART', 'USD'), '2 H', '5 mins', 'TRADES')
        ]
        
        for description, contract, duration, bar_size, what_to_show in approaches:
            print(f"\n  Testing: {description}")
            try:
                # Qualify contract
                qualified = ib.qualifyContracts(contract)
                if qualified:
                    print(f"    Contract qualified: {qualified[0].symbol}")
                    
                    # Request historical data
                    bars = ib.reqHistoricalData(
                        contract,
                        endDateTime='',
                        durationStr=duration,
                        barSizeSetting=bar_size,
                        whatToShow=what_to_show,
                        useRTH=True,
                        formatDate=1
                    )
                    
                    if bars:
                        print(f"    ✓ Received {len(bars)} bars")
                        print(f"    First bar: {bars[0].date} - {bars[0].close}")
                        print(f"    Last bar: {bars[-1].date} - {bars[-1].close}")
                    else:
                        print("    ✗ No bars received")
                else:
                    print("    ✗ Contract qualification failed")
                    
            except Exception as e:
                print(f"    ✗ Error: {str(e)}")
                
    except Exception as e:
        print(f"✗ Historical data error: {str(e)}")
    
    # Test 5: Check market data subscriptions
    print("\n5. Checking market data subscriptions...")
    try:
        # Check if market data is available
        market_data_lines = ib.reqMarketDataType(1)  # 1 = Live, 2 = Frozen, 3 = Delayed, 4 = Delayed-Frozen
        print(f"  Market data type: {market_data_lines}")
        
        # Check account
        accounts = ib.managedAccounts()
        print(f"  Managed accounts: {accounts}")
        
    except Exception as e:
        print(f"✗ Market data check error: {str(e)}")
    
    # Test 6: Server time
    print("\n6. Checking server time...")
    try:
        server_time = ib.reqCurrentTime()
        print(f"✓ Server time: {datetime.fromtimestamp(server_time)}")
    except Exception as e:
        print(f"✗ Server time error: {str(e)}")
    
    # Disconnect
    ib.disconnect()
    print("\n=== Diagnostics Complete ===")

if __name__ == "__main__":
    diagnose_connection()
