#!/usr/bin/env python3
"""
Debug script to understand market depth data structure
"""

import sys
import os
import asyncio
import logging

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_market_depth_structure():
    """Test market depth data structure"""
    print("🔍 Testing Market Depth Data Structure...")
    print("=" * 60)
    
    try:
        from ib_insync import IB, Stock, Future
        
        # Create IB instance
        ib = IB()
        
        print("📡 This test shows what market depth data looks like...")
        print("🔍 Market depth data typically comes in these forms:")
        print()
        
        print("1. **domBids/domAsks** - Most common structure:")
        print("   ticker.domBids = [DOMLevel(price=100.50, size=10, marketMaker=''), ...]")
        print("   ticker.domAsks = [DOMLevel(price=100.51, size=5, marketMaker=''), ...]")
        print()
        
        print("2. **updateEvent** - Triggered when depth changes:")
        print("   - ticker.updateEvent fires when domBids/domAsks change")
        print("   - Contains the full ticker object with updated depth")
        print()
        
        print("3. **Possible attributes to check:**")
        depth_attrs = [
            'domBids', 'domAsks', 'domBidsEvent', 'domAsksEvent',
            'updateEvent', 'bids', 'asks', 'marketDepth',
            'bidSize', 'askSize', 'bidPrice', 'askPrice'
        ]
        for attr in depth_attrs:
            print(f"   - {attr}")
        print()
        
        print("4. **DOMLevel structure:**")
        print("   - price: float (e.g., 100.50)")
        print("   - size: int (e.g., 10)")
        print("   - marketMaker: str (usually empty)")
        print()
        
        print("🚀 **Next Steps for Debugging:**")
        print("1. Run the dashboard")
        print("2. Click 'Level II' button")
        print("3. Check console output for:")
        print("   - 'Market depth callback triggered'")
        print("   - 'Ticker attributes: [...]'")
        print("   - 'Depth-related attributes: [...]'")
        print("   - 'Found domBids/domAsks - Bids: X, Asks: Y'")
        print()
        
        print("🔧 **Common Issues & Solutions:**")
        print("1. **No callback triggered**: Event subscription issue")
        print("   - Check if updateEvent, domBidsEvent, domAsksEvent exist")
        print("   - Try subscribing to multiple events")
        print()
        
        print("2. **Callback triggered but no data**: Data structure issue")
        print("   - Check if domBids/domAsks are populated")
        print("   - Look for alternative attributes (bids/asks)")
        print()
        
        print("3. **Data exists but display fails**: Parsing issue")
        print("   - Check DOMLevel object structure")
        print("   - Verify price/size attribute access")
        print()
        
        print("✅ Debug information prepared!")
        print("Now test Level II in the dashboard and check console output.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in debug test: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_market_depth_structure())
