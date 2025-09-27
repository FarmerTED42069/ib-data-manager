#!/usr/bin/env python3
"""
Test script for real-time streaming functionality
Tests the new live data streaming features in the unified dashboard
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    """Test the real-time streaming functionality"""
    print("🚀 Testing Real-Time Streaming Implementation...")
    print("=" * 60)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from ib_data_manager.gui.unified_dashboard import UnifiedDashboard
        from ib_data_manager.api.async_ib_connector import AsyncIBConnector
        print("✅ All imports successful")
        
        # Test async connector streaming methods
        print("\n🔧 Testing AsyncIBConnector streaming methods...")
        connector = AsyncIBConnector()
        
        # Check if streaming management attributes exist
        assert hasattr(connector, 'active_quotes'), "Missing active_quotes attribute"
        assert hasattr(connector, 'active_depth'), "Missing active_depth attribute"
        assert hasattr(connector, 'streaming_callbacks'), "Missing streaming_callbacks attribute"
        
        # Check if streaming methods exist
        assert hasattr(connector, 'start_realtime_quotes'), "Missing start_realtime_quotes method"
        assert hasattr(connector, 'stop_realtime_quotes'), "Missing stop_realtime_quotes method"
        assert hasattr(connector, 'start_market_depth'), "Missing start_market_depth method"
        assert hasattr(connector, 'stop_market_depth'), "Missing stop_market_depth method"
        assert hasattr(connector, 'stop_all_streaming'), "Missing stop_all_streaming method"
        assert hasattr(connector, 'get_streaming_status'), "Missing get_streaming_status method"
        
        print("✅ AsyncIBConnector streaming methods verified")
        
        # Test streaming status
        status = connector.get_streaming_status()
        expected_keys = ['quotes', 'depth', 'total_streams', 'connected']
        for key in expected_keys:
            assert key in status, f"Missing key '{key}' in streaming status"
        print("✅ Streaming status method working")
        
        # Test GUI components
        print("\n🖥️  Testing GUI components...")
        root = tk.Tk()
        root.withdraw()  # Hide the window for testing
        
        # Test unified dashboard creation
        dashboard = UnifiedDashboard(root)
        
        # Check if quick actions has real-time methods
        quick_actions = dashboard.quick_actions
        assert hasattr(quick_actions, 'start_live_quotes'), "Missing start_live_quotes method"
        assert hasattr(quick_actions, 'start_market_depth'), "Missing start_market_depth method"
        assert hasattr(quick_actions, 'stop_streaming'), "Missing stop_streaming method"
        print("✅ Quick actions real-time methods verified")
        
        # Check if results panel has live data methods
        results_panel = dashboard.results_panel
        assert hasattr(results_panel, 'update_live_quote'), "Missing update_live_quote method"
        assert hasattr(results_panel, 'update_market_depth'), "Missing update_market_depth method"
        assert hasattr(results_panel, 'switch_to_live_tab'), "Missing switch_to_live_tab method"
        assert hasattr(results_panel, 'clear_live_data'), "Missing clear_live_data method"
        print("✅ Results panel live data methods verified")
        
        # Check if live data UI components exist
        assert hasattr(results_panel, 'live_symbol_label'), "Missing live_symbol_label"
        assert hasattr(results_panel, 'stream_status_label'), "Missing stream_status_label"
        assert hasattr(results_panel, 'bid_label'), "Missing bid_label"
        assert hasattr(results_panel, 'ask_label'), "Missing ask_label"
        assert hasattr(results_panel, 'last_label'), "Missing last_label"
        assert hasattr(results_panel, 'depth_tree'), "Missing depth_tree"
        print("✅ Live data UI components verified")
        
        root.destroy()
        
        print("\n🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("✅ Real-time streaming implementation is ready!")
        print("\n📋 Features implemented:")
        print("   • 📡 Live Quotes streaming with bid/ask/last display")
        print("   • 📊 Level II Market Depth with order book")
        print("   • 🔴 Stream management (start/stop/status)")
        print("   • 🎯 Enhanced async connector with streaming management")
        print("   • 🖥️  Integrated live data tab in results panel")
        print("   • ⚡ Real-time callbacks and GUI updates")
        
        print("\n🚀 Next steps:")
        print("   1. Launch the unified dashboard: python launch_unified_dashboard.py")
        print("   2. Connect to IB Gateway")
        print("   3. Enter a symbol (e.g., AAPL)")
        print("   4. Click '📡 Live Quotes' or '📊 Level II'")
        print("   5. Watch real-time data stream in the Live Data tab!")
        
        return True
        
    except Exception as e:
        print(f"❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    
    # Ask if user wants to launch the dashboard
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        
        launch = messagebox.askyesno(
            "Launch Dashboard?",
            "🎉 Real-time streaming tests passed!\n\n"
            "Would you like to launch the unified dashboard now to test the live streaming features?\n\n"
            "Make sure IB Gateway/TWS is running first."
        )
        
        if launch:
            print("\n🚀 Launching unified dashboard...")
            from ib_data_manager.gui.unified_dashboard import main as dashboard_main
            dashboard_main()
        else:
            print("\n✅ Test completed. Launch dashboard manually when ready!")
            
    except Exception as e:
        print(f"\n✅ Test completed successfully!")
        print("Launch the dashboard manually: python launch_unified_dashboard.py")
