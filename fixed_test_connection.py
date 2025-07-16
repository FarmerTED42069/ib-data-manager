"""
Test connection to Interactive Brokers Gateway

This script verifies that your IB Gateway connection is properly configured
and that the ib_insync library can connect using the settings in ibkr_trader.py.
"""

from ib_insync import IB, util
import sys
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_connection():
    """Test connection to IB Gateway and retrieve account information."""
    ib = IB()
    
    try:
        # Connection settings
        host = '127.0.0.1'
        port = 4002  # Using IB Gateway Paper Trading port (as shown in test_ports.py)
        client_id = random.randint(10000, 99999)  # Use random client ID to avoid conflicts
        
        logger.info(f"Attempting to connect to IB Gateway at {host}:{port} with client ID {client_id}...")
        ib.connect(host, port, clientId=client_id)
        
        # Check if connected
        if ib.isConnected():
            logger.info("✓ Successfully connected to IB Gateway!")
            
            # Get account summary
            account = ib.accountSummary()
            logger.info("\nAccount Summary:")
            for item in account:
                if item.tag in ['NetLiquidation', 'AvailableFunds', 'BuyingPower']:
                    logger.info(f"  {item.tag}: {item.value} {item.currency}")
            
            # Get current positions
            positions = ib.positions()
            if positions:
                logger.info("\nCurrent Positions:")
                for position in positions:
                    logger.info(f"  {position.contract.symbol}: {position.position} contracts")
            else:
                logger.info("\nNo open positions")
            
            # Get calculated front-month expiry
            current_month = 6  # June
            current_year = 2025  
            logger.info(f"\nExpected front-month futures expiry: {current_year}{current_month:02}")
            
            logger.info("\nConnection test completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Failed to connect to IB Gateway: {e}")
        logger.error("\nPlease check:")
        logger.error("  1. IB Gateway is running")
        logger.error("  2. API settings match your configuration (port 4002)")
        logger.error("  3. There are no other active API connections")
        return False
        
    finally:
        # Always disconnect
        if ib and ib.isConnected():
            ib.disconnect()
            logger.info("Disconnected from IB Gateway")

if __name__ == "__main__":
    print("\n===== IB Gateway Connection Test =====\n")
    success = test_connection()
    
    if not success:
        sys.exit(1)  # Exit with error code
