#!/usr/bin/env python3
"""
Quick test to verify Level 2 connection and data flow
"""

import asyncio
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_level2_connection():
    """Test Level 2 connection and data flow"""
    try:
        # Import the required modules
        from ib_data_manager.api.async_ib_connector import AsyncIBConnector
        from ib_data_manager.core.volume_profile import EnhancedTickCapture
        
        print("✅ Imports successful")
        
        # Create connector
        ib_conn = AsyncIBConnector()
        
        # Connect to IB Gateway
        print("🔌 Connecting to IB Gateway...")
        connected = await ib_conn.connect()
        
        if not connected:
            print("❌ Failed to connect to IB Gateway")
            return False
        
        print("✅ Connected to IB Gateway")
        
        # Create tick capture
        tick_capture = EnhancedTickCapture()
        
        # Test callback functions
        def tick_callback(tick_data):
            print(f"📊 Tick: {tick_data}")
        
        def orderbook_callback(orderbook):
            print(f"📈 Order Book: {orderbook}")
        
        # Start tick capture for ES
        print("🚀 Starting Level 2 capture for ES...")
        success = await tick_capture.start_tick_capture(
            symbol="ES",
            ib_connector=ib_conn,
            tick_callback=tick_callback,
            orderbook_callback=orderbook_callback
        )
        
        if success:
            print("✅ Level 2 capture started successfully")
            print("⏳ Waiting for data (10 seconds)...")
            await asyncio.sleep(10)
        else:
            print("❌ Failed to start Level 2 capture")
            return False
        
        # Stop capture
        await tick_capture.stop_tick_capture("ES")
        print("🛑 Level 2 capture stopped")
        
        # Disconnect
        await ib_conn.disconnect()
        print("✅ Test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logging.error(f"Test error: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    print("🧪 Testing Level 2 Connection and Data Flow")
    print("=" * 50)
    
    # Run the test
    result = asyncio.run(test_level2_connection())
    
    if result:
        print("\n🎉 Level 2 system is working correctly!")
    else:
        print("\n❌ Level 2 system has issues that need to be resolved.")
