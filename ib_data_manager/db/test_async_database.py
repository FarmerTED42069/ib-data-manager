"""
Test script for the AsyncDataManager
"""

import asyncio
import logging
from datetime import datetime
from ib_data_manager.db.async_database import AsyncDataManager


async def test_async_database():
    """Test the async database manager"""
    print("Testing AsyncDataManager...")
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Create async database manager
        db = AsyncDataManager()
        
        # Initialize the database
        await db.initialize()
        print("✓ Database initialized successfully")
        
        # Test market depth insertion
        await db.insert_market_depth(
            symbol="AAPL",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            side="bid",
            position=0,
            price=150.00,
            size=100,
            market_maker="NASDAQ",
            operation="insert"
        )
        print("✓ Market depth data inserted successfully")
        
        # Test account info saving
        account_info = {
            "CashBalance": 10000.00,
            "NetLiquidation": 15000.00,
            "TotalCashBalance": 10000.00
        }
        await db.save_account_info(account_info)
        print("✓ Account info saved successfully")
        
        # Close the database
        await db.close()
        print("✓ Database closed successfully")
        
        print("\nAll tests passed! The AsyncDataManager is ready for use.")
        return True
        
    except Exception as e:
        print(f"✗ Error during test: {str(e)}")
        logging.error(f"Error during test: {str(e)}")
        return False


async def main():
    """Main function to run the test"""
    print("Starting AsyncDataManager test...")
    success = await test_async_database()
    print("Test completed.")
    return success


if __name__ == "__main__":
    asyncio.run(main())
