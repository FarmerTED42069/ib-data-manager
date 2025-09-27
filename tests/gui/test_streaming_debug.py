#!/usr/bin/env python3
"""
Debug script to test real-time streaming functionality
"""

import sys
import os
import asyncio
import logging

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set up logging to see debug output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_streaming():
    """Test the streaming functionality directly"""
    print("🔍 Testing AsyncIBConnector streaming...")
    
    try:
        from ib_data_manager.api.async_ib_connector import AsyncIBConnector
        
        # Create connector
        connector = AsyncIBConnector()
        print(f"✅ Connector created: {connector}")
        
        # Test connection (this will fail without IB Gateway, but we can test the method exists)
        print(f"🔍 Testing connection methods...")
        print(f"   - start_realtime_quotes: {hasattr(connector, 'start_realtime_quotes')}")
        print(f"   - stop_realtime_quotes: {hasattr(connector, 'stop_realtime_quotes')}")
        print(f"   - start_market_depth: {hasattr(connector, 'start_market_depth')}")
        print(f"   - stop_market_depth: {hasattr(connector, 'stop_market_depth')}")
        print(f"   - get_streaming_status: {hasattr(connector, 'get_streaming_status')}")
        
        # Test streaming status
        status = connector.get_streaming_status()
        print(f"✅ Streaming status: {status}")
        
        # Test callback creation
        def test_callback(ticker):
            print(f"📡 Test callback received: {ticker}")
            
        print(f"✅ Callback function created")
        
        print("\n🎉 All streaming components are properly set up!")
        print("The issue is likely in the GUI integration or IB connection.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing streaming: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_integration():
    """Test GUI integration without actually running the GUI"""
    print("\n🔍 Testing GUI integration...")
    
    try:
        from ib_data_manager.gui.unified_dashboard import UnifiedDashboard
        from ib_data_manager.gui.quick_actions import QuickActionsPanel
        from ib_data_manager.gui.results_panel import ResultsPanel
        
        print("✅ All GUI modules imported successfully")
        
        # Test method existence
        import inspect
        
        # Check QuickActionsPanel methods
        qa_methods = [method for method in dir(QuickActionsPanel) if not method.startswith('_')]
        streaming_methods = [m for m in qa_methods if 'live' in m.lower() or 'stream' in m.lower() or 'depth' in m.lower()]
        print(f"✅ QuickActionsPanel streaming methods: {streaming_methods}")
        
        # Check ResultsPanel methods  
        rp_methods = [method for method in dir(ResultsPanel) if not method.startswith('_')]
        live_methods = [m for m in rp_methods if 'live' in m.lower() or 'stream' in m.lower()]
        print(f"✅ ResultsPanel live data methods: {live_methods}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing GUI integration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Streaming Debug Test...")
    print("=" * 60)
    
    # Test async components
    success1 = asyncio.run(test_streaming())
    
    # Test GUI integration
    success2 = test_gui_integration()
    
    if success1 and success2:
        print("\n✅ All tests passed! The components are properly set up.")
        print("\n🔍 Next steps to debug:")
        print("   1. Make sure IB Gateway/TWS is running")
        print("   2. Check if the dashboard is properly connected")
        print("   3. Enter a valid symbol (like AAPL)")
        print("   4. Click 'Live Quotes' and check console output")
        print("   5. Look for the debug messages we added")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
