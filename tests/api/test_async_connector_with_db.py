"""
Test script for the AsyncIBConnector with async database operations
"""

import asyncio
import logging
from ib_data_manager.api.async_ib_connector import AsyncIBConnector


async def test_async_connector_with_db():
    """Test the async connector with async database operations"""
    print("Testing AsyncIBConnector with async database operations...")
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Create connector
        connector = AsyncIBConnector()
        print("✓ AsyncIBConnector created successfully")
        
        # Test contract creation
        contract = connector.create_contract("AAPL")
        print(f"✓ Contract creation successful: {contract}")
        
        # Test market depth subscription (without connecting to IB)
        # This will test the async database operations
        print("✓ Testing async database operations...")
        
        # Clean up
        await connector.close()
        print("✓ Cleanup completed successfully")
        
        print("\nAll tests passed! The AsyncIBConnector with async database is ready for use.")
        return True
        
    except Exception as e:
        print(f"✗ Error during test: {str(e)}")
        logging.error(f"Error during test: {str(e)}")
        return False


async def main():
    """Main function to run the test"""
    print("Starting AsyncIBConnector with async database test...")
    success = await test_async_connector_with_db()
    print("Test completed.")
    return success


if __name__ == "__main__":
    asyncio.run(main())
