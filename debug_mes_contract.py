"""
Debug script to test MES contract recognition
"""
import asyncio
import logging
from ib_data_manager.api.async_ib_connector import AsyncIBConnector

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_mes_contract():
    """Test MES contract recognition with different approaches"""
    connector = AsyncIBConnector()
    
    try:
        # Connect
        print("🔌 Connecting to IB Gateway...")
        connected = await connector.connect()
        if not connected:
            print("❌ Failed to connect to IB Gateway")
            return
        
        print("✅ Connected successfully")
        
        # Test 1: Try different MES contract variations
        print("\n--- Test 1: MES Contract Variations ---")
        
        test_contracts = [
            ("MES", "GLOBEX", "USD"),
            ("MES", "CME", "USD"),
            ("MES", "SMART", "USD"),
            ("MES", "", "USD"),  # No exchange
        ]
        
        for symbol, exchange, currency in test_contracts:
            try:
                print(f"\n🧪 Testing: {symbol} on {exchange or 'DEFAULT'}")
                contract = connector.create_contract(symbol, "FUT", exchange, currency)
                print(f"   Created contract: {contract}")
                
                # Try to qualify the contract
                qualified = await connector.ib.qualifyContractsAsync(contract)
                if qualified:
                    print(f"   ✅ Qualified: {qualified[0]}")
                else:
                    print(f"   ❌ Failed to qualify")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        # Test 2: Search for ES (regular E-mini) to compare
        print("\n--- Test 2: ES Contract (for comparison) ---")
        try:
            es_contract = connector.create_contract("ES", "FUT", "GLOBEX", "USD")
            print(f"ES Contract: {es_contract}")
            
            qualified_es = await connector.ib.qualifyContractsAsync(es_contract)
            if qualified_es:
                print(f"✅ ES Qualified: {qualified_es[0]}")
            else:
                print(f"❌ ES Failed to qualify")
                
        except Exception as e:
            print(f"❌ ES Error: {str(e)}")
        
        # Test 3: Try contract details search
        print("\n--- Test 3: Contract Details Search ---")
        try:
            from ib_insync import Future
            mes_future = Future("MES", exchange="GLOBEX", currency="USD")
            print(f"Searching contract details for: {mes_future}")
            
            details = await connector.ib.reqContractDetailsAsync(mes_future)
            if details:
                print(f"✅ Found {len(details)} contract details:")
                for detail in details[:3]:  # Show first 3
                    contract = detail.contract
                    print(f"   - {contract.symbol} {contract.lastTradeDateOrContractMonth} ({contract.exchange})")
            else:
                print("❌ No contract details found")
                
        except Exception as e:
            print(f"❌ Contract details error: {str(e)}")
        
        # Test 4: Check account permissions
        print("\n--- Test 4: Account Info ---")
        try:
            account_info = await connector.get_account_info()
            if account_info:
                print("✅ Account info retrieved")
                # Look for futures-related permissions
                futures_keys = [k for k in account_info.keys() if 'fut' in k.lower() or 'margin' in k.lower()]
                if futures_keys:
                    print("   Futures-related account info:")
                    for key in futures_keys[:5]:  # Show first 5
                        print(f"   - {key}: {account_info[key]}")
            else:
                print("❌ No account info")
        except Exception as e:
            print(f"❌ Account info error: {str(e)}")
            
    except Exception as e:
        print(f"❌ General error: {str(e)}")
    
    finally:
        await connector.disconnect()
        print("\n🔌 Disconnected")

if __name__ == "__main__":
    asyncio.run(test_mes_contract())
