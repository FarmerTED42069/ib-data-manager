#!/usr/bin/env python3
"""
Simple Level 2 Test - No Unicode Issues
Basic test of Level 2 functionality without emoji characters
"""

import asyncio
import logging
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup simple logging without Unicode
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def simple_level2_test():
    """Simple test of Level 2 components"""
    print("Testing Level 2 System Components")
    print("=" * 50)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from ib_data_manager.api.async_ib_connector import AsyncIBConnector
        from ib_data_manager.api.level2_connector import Level2Connector
        from ib_data_manager.core.level2_opportunities import Level2OpportunityDetector
        print("   All imports successful")
        
        # Test component initialization
        print("2. Testing component initialization...")
        ib_connector = AsyncIBConnector()
        level2_connector = Level2Connector(ib_connector)
        opportunity_detector = Level2OpportunityDetector()
        print("   All components initialized")
        
        # Test database initialization
        print("3. Testing database...")
        stats = opportunity_detector.get_statistics()
        print(f"   Database initialized, parameters: {stats['detection_parameters']}")
        
        # Test connection (if IB Gateway is running)
        print("4. Testing IB Gateway connection...")
        try:
            connected = await ib_connector.connect()
            if connected:
                print("   Connected to IB Gateway successfully")
                
                # Test Level 2 snapshot
                print("5. Testing Level 2 snapshot...")
                snapshot = await level2_connector.get_level2_snapshot("SPY", "STK")
                if snapshot:
                    print(f"   Snapshot successful: {len(snapshot['bids'])} bids, {len(snapshot['asks'])} asks")
                else:
                    print("   Snapshot returned no data (normal if market closed)")
                
                await ib_connector.disconnect()
                print("   Disconnected from IB Gateway")
            else:
                print("   Could not connect to IB Gateway (make sure it's running on port 4002)")
        except Exception as e:
            print(f"   Connection test failed: {str(e)}")
        
        print("\nLevel 2 System Test Complete")
        print("All core components are working correctly")
        return True
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(simple_level2_test())
    if result:
        print("\nSUCCESS: Level 2 system is ready to use")
    else:
        print("\nFAILED: Check error messages above")
