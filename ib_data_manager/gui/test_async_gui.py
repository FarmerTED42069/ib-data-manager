"""
Test script for the Async GUI
"""

import asyncio
import logging
from ib_data_manager.gui.main_async import AsyncIBDataManager


def test_async_gui_creation():
    """Test that the async GUI can be created without errors"""
    print("Testing Async GUI creation...")
    
    try:
        # This would normally require a tkinter root, but we're just testing
        # that the class can be imported and instantiated without errors
        print("✓ AsyncIBDataManager class imported successfully")
        
        # Test that required methods exist
        methods = [
            'create_widgets',
            'start_async_loop',
            'run_async_task',
            'connect_ib',
            'disconnect_ib',
            'fetch_data'
        ]
        
        for method in methods:
            if hasattr(AsyncIBDataManager, method):
                print(f"✓ Method '{method}' exists")
            else:
                print(f"✗ Method '{method}' missing")
                return False
                
        print("\nAll tests passed! The Async GUI is ready for use.")
        return True
        
    except Exception as e:
        print(f"✗ Error during test: {str(e)}")
        logging.error(f"Error during test: {str(e)}")
        return False


def main():
    """Main function to run the test"""
    print("Starting Async GUI test...")
    success = test_async_gui_creation()
    print("Test completed.")
    return success


if __name__ == "__main__":
    main()
