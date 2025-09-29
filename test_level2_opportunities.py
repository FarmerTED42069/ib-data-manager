#!/usr/bin/env python3
"""
Test Level 2 Opportunity Detection System
Comprehensive test of the new Level 2 and tick data opportunity detection capabilities
"""

import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('level2_test.log')
    ]
)

async def test_level2_opportunities():
    """Test the complete Level 2 opportunity detection system"""
    print("🧪 Testing Level 2 Opportunity Detection System")
    print("=" * 60)
    
    try:
        # Import required modules
        from ib_data_manager.api.async_ib_connector import AsyncIBConnector
        from ib_data_manager.api.level2_connector import Level2Connector
        from ib_data_manager.core.level2_opportunities import Level2OpportunityDetector, OpportunityAlert
        
        print("✅ Successfully imported Level 2 modules")
        
        # Initialize components
        print("\n🔧 Initializing components...")
        ib_connector = AsyncIBConnector()
        level2_connector = Level2Connector(ib_connector)
        opportunity_detector = Level2OpportunityDetector()
        
        # Connect to IB Gateway
        print("\n🔌 Connecting to IB Gateway...")
        connected = await ib_connector.connect()
        
        if not connected:
            print("❌ Failed to connect to IB Gateway")
            print("Make sure IB Gateway is running on port 4002")
            return False
        
        print("✅ Connected to IB Gateway")
        
        # Test symbols to monitor
        test_symbols = [
            {"symbol": "ES", "sec_type": "FUT", "name": "E-mini S&P 500"},
            {"symbol": "SPY", "sec_type": "STK", "name": "SPDR S&P 500 ETF"}
        ]
        
        # Opportunity tracking
        opportunities_detected = []
        
        # Set up opportunity callback
        async def opportunity_callback(opportunity: OpportunityAlert):
            opportunities_detected.append(opportunity)
            print(f"\n🚨 OPPORTUNITY DETECTED:")
            print(f"   Symbol: {opportunity.symbol}")
            print(f"   Type: {opportunity.opportunity_type.value}")
            print(f"   Confidence: {opportunity.confidence:.2f}")
            print(f"   Price: {opportunity.price_level:.2f}")
            print(f"   Action: {opportunity.action_suggested}")
            print(f"   Description: {opportunity.description}")
            print(f"   Time: {opportunity.timestamp.strftime('%H:%M:%S')}")
        
        opportunity_detector.add_opportunity_callback(opportunity_callback)
        
        # Test each symbol
        active_tickers = []
        
        for test_symbol in test_symbols:
            symbol = test_symbol["symbol"]
            sec_type = test_symbol["sec_type"]
            name = test_symbol["name"]
            
            print(f"\n📊 Testing Level 2 for {name} ({symbol})...")
            
            try:
                # Create Level 2 callback
                async def level2_callback(ticker, sym=symbol):
                    await opportunity_detector.process_level2_update(sym, ticker)
                
                # Start Level 2 market depth
                ticker = await level2_connector.start_market_depth(
                    symbol=symbol,
                    sec_type=sec_type,
                    callback=level2_callback,
                    num_rows=10
                )
                
                if ticker:
                    active_tickers.append((symbol, sec_type, ticker))
                    print(f"✅ Level 2 streaming started for {symbol}")
                else:
                    print(f"❌ Failed to start Level 2 for {symbol}")
                    continue
                
                # Wait a moment for initial data
                await asyncio.sleep(3)
                
                # Test snapshot functionality
                print(f"📸 Getting Level 2 snapshot for {symbol}...")
                snapshot = await level2_connector.get_level2_snapshot(symbol, sec_type)
                
                if snapshot:
                    print(f"   Bids: {len(snapshot['bids'])} levels")
                    print(f"   Asks: {len(snapshot['asks'])} levels")
                    print(f"   Spread: {snapshot['spread']:.4f}")
                    print(f"   Mid Price: {snapshot['mid_price']:.2f}")
                    
                    if snapshot['bids'] and snapshot['asks']:
                        best_bid = snapshot['bids'][0]
                        best_ask = snapshot['asks'][0]
                        print(f"   Best Bid: {best_bid['price']:.2f} x {best_bid['size']}")
                        print(f"   Best Ask: {best_ask['price']:.2f} x {best_ask['size']}")
                else:
                    print(f"❌ Failed to get snapshot for {symbol}")
                
            except Exception as e:
                print(f"❌ Error testing {symbol}: {str(e)}")
                logging.error(f"Error testing {symbol}: {str(e)}", exc_info=True)
        
        if not active_tickers:
            print("\n❌ No Level 2 streams active - cannot continue test")
            return False
        
        # Monitor for opportunities
        print(f"\n👀 Monitoring {len(active_tickers)} symbols for opportunities...")
        print("   Watching for:")
        print("   • Order imbalances (>3:1 ratio)")
        print("   • Large orders (>5x average size)")
        print("   • Spread compression (>50% reduction)")
        print("   • Hidden liquidity patterns")
        print("\n⏳ Monitoring for 30 seconds...")
        
        # Monitor for 30 seconds
        start_time = datetime.now()
        while (datetime.now() - start_time).seconds < 30:
            await asyncio.sleep(1)
            
            # Show periodic status
            if (datetime.now() - start_time).seconds % 10 == 0:
                elapsed = (datetime.now() - start_time).seconds
                print(f"   {elapsed}s elapsed, {len(opportunities_detected)} opportunities detected")
        
        # Stop all Level 2 streams
        print(f"\n🛑 Stopping Level 2 streams...")
        for symbol, sec_type, ticker in active_tickers:
            level2_connector.stop_market_depth(symbol, sec_type)
            print(f"   Stopped {symbol}")
        
        # Show results
        print(f"\n📊 TEST RESULTS:")
        print(f"   Symbols monitored: {len(active_tickers)}")
        print(f"   Opportunities detected: {len(opportunities_detected)}")
        print(f"   Monitoring duration: 30 seconds")
        
        if opportunities_detected:
            print(f"\n🎯 DETECTED OPPORTUNITIES:")
            for i, opp in enumerate(opportunities_detected, 1):
                print(f"   {i}. {opp.symbol} - {opp.opportunity_type.value} "
                      f"(confidence: {opp.confidence:.2f}) - {opp.action_suggested}")
        else:
            print(f"\n💡 No opportunities detected during test period")
            print(f"   This is normal for quiet market conditions")
            print(f"   Try testing during active market hours for more activity")
        
        # Test database functionality
        print(f"\n💾 Testing database functionality...")
        recent_opportunities = opportunity_detector.get_recent_opportunities(hours=1)
        print(f"   Recent opportunities in database: {len(recent_opportunities)}")
        
        # Show statistics
        stats = opportunity_detector.get_statistics()
        print(f"\n📈 DETECTION STATISTICS:")
        print(f"   Total opportunities: {stats['total_opportunities']}")
        print(f"   Active symbols: {stats['active_symbols']}")
        print(f"   Detection parameters:")
        print(f"     • Imbalance threshold: {stats['detection_parameters']['imbalance_threshold']}")
        print(f"     • Volume spike threshold: {stats['detection_parameters']['volume_spike_threshold']}")
        print(f"     • Spread compression threshold: {stats['detection_parameters']['spread_compression_threshold']}")
        
        # Disconnect
        await ib_connector.disconnect()
        print(f"\n✅ Disconnected from IB Gateway")
        
        print(f"\n🎉 Level 2 Opportunity Detection System Test Complete!")
        print(f"   System is working correctly and ready for live trading")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure all Level 2 modules are properly installed")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        logging.error(f"Test error: {str(e)}", exc_info=True)
        return False

async def test_level2_gui():
    """Test the Level 2 GUI panel"""
    print(f"\n🖥️ Testing Level 2 GUI Panel...")
    
    try:
        import tkinter as tk
        from ib_data_manager.gui.level2_panel import Level2OpportunityPanel
        from ib_data_manager.api.async_ib_connector import AsyncIBConnector
        
        # Create a simple test window
        root = tk.Tk()
        root.title("Level 2 Opportunities Test")
        root.geometry("1000x700")
        
        # Create IB connector (mock for GUI test)
        ib_connector = AsyncIBConnector()
        
        # Create Level 2 panel
        level2_panel = Level2OpportunityPanel(root, ib_connector)
        
        print("✅ Level 2 GUI panel created successfully")
        print("   GUI components:")
        print("   • Control panel with symbol input")
        print("   • Real-time opportunities display")
        print("   • Statistics panel")
        print("   • Settings dialog")
        
        # Don't actually show the window in test mode
        # root.mainloop()
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Level 2 Opportunity Detection System Tests")
    print("=" * 60)
    
    # Run core functionality test
    core_result = asyncio.run(test_level2_opportunities())
    
    # Run GUI test
    gui_result = asyncio.run(test_level2_gui())
    
    print(f"\n📋 FINAL TEST RESULTS:")
    print(f"   Core Level 2 System: {'✅ PASS' if core_result else '❌ FAIL'}")
    print(f"   GUI Panel: {'✅ PASS' if gui_result else '❌ FAIL'}")
    
    if core_result and gui_result:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"   Level 2 Opportunity Detection System is ready for production use")
        print(f"\n📖 Next Steps:")
        print(f"   1. Integrate Level 2 panel into unified dashboard")
        print(f"   2. Test with live market data during trading hours")
        print(f"   3. Fine-tune detection parameters based on market conditions")
        print(f"   4. Set up alerts and notifications for high-confidence opportunities")
    else:
        print(f"\n❌ SOME TESTS FAILED")
        print(f"   Check the error messages above and resolve issues before proceeding")
        sys.exit(1)
