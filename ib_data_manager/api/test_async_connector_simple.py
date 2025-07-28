"""
Simple test script for the AsyncIBConnector (no IB connection required)
"""

import asyncio
import logging
from ib_data_manager.api.async_ib_connector import AsyncIBConnector


def test_import_and_initialization():
    """Test that we can import and initialize the connector"""
    print("Testing AsyncIBConnector import and initialization...")
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Create connector
        connector = AsyncIBConnector()
        print("✓ AsyncIBConnector created successfully")
        
        # Test contract creation
        contract = connector.create_contract("AAPL")
        print(f"✓ Contract creation successful: {contract}")
        
        # Test contract creation with different types
        fut_contract = connector.create_contract("ES", "FUT", "CME", "USD", "202503")
        print(f"✓ Future contract creation successful: {fut_contract}")
        
        print("\nAll tests passed! The AsyncIBConnector is ready for use.")
        return True
        
    except Exception as e:
        print(f"✗ Error during test: {str(e)}")
        logging.error(f"Error during test: {str(e)}")
        return False


def main():
    """Main function to run the test"""
    print("Starting AsyncIBConnector simple test...")
    success = test_import_and_initialization()
    print("Test completed.")
    return success


if __name__ == "__main__":
    main()
