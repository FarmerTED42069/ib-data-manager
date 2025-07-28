"""
Interactive Brokers Trading Module - Enhanced with Dynamic Expiry and Improved Connection Handling

This module handles connections to Interactive Brokers TWS or IB Gateway
and executes futures trades based on webhook alert signals.
"""

import logging
import time
from typing import Dict, Optional, Union
from datetime import datetime
from ib_insync import IB, Future, MarketOrder, Contract, OrderStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# IBKR connection settings - adjust as needed
TWS_HOST = '127.0.0.1'
TWS_PORT = 4002  # 4002 for IB Gateway paper trading
TWS_CLIENT_ID = 54321  # Changed to a different unique client ID
CONNECTION_TIMEOUT = 20  # Increased timeout

def get_current_expiry() -> str:
    """
    Determine the current front-month futures expiry.
    
    Returns:
        str: Expiry in format YYYYMM
    """
    now = datetime.utcnow()
    month = now.month
    year = now.year
    
    # For simplicity, assume contracts expire in current or next month
    if month in [3, 6, 9, 12]:
        # Quarterly roll
        expiry = f"{year}{month:02}"
    else:
        # Round up to next quarter
        quarter = ((month - 1) // 3 + 1) * 3
        if quarter > month:
            # Next quarter this year
            expiry = f"{year}{quarter:02}"
        else:
            # First quarter next year
            expiry = f"{year + 1}03"
            
    logger.info(f"Calculated current expiry: {expiry}")
    return expiry

def check_api_settings():
    """
    Check IB Gateway API settings and connectivity.
    
    Returns:
        bool: True if the connection is operational, False otherwise
    """
    ib = IB()
    try:
        logger.info(f"Testing API connection to {TWS_HOST}:{TWS_PORT}...")
        ib.connect(TWS_HOST, TWS_PORT, clientId=TWS_CLIENT_ID, readonly=True, timeout=10)
        
        if ib.isConnected():
            logger.info("API connection test successful!")
            connected = True
        else:
            logger.error("API connection test failed - could not establish connection")
            connected = False
            
        return connected
    except Exception as e:
        logger.error(f"API connection test error: {type(e).__name__}: {e}")
        return False
    finally:
        if ib and ib.isConnected():
            ib.disconnect()
            logger.info("Test connection disconnected")

def connect_to_ibkr() -> IB:
    """
    Establish connection to Interactive Brokers TWS/Gateway with retry.
    
    Returns:
        IB: Connected IB instance
    
    Raises:
        ConnectionError: If connection to TWS/Gateway fails after retries
    """
    ib = IB()
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Connecting to IBKR at {TWS_HOST}:{TWS_PORT} (attempt {attempt}/{max_retries})...")
            ib.connect(TWS_HOST, TWS_PORT, clientId=TWS_CLIENT_ID, timeout=CONNECTION_TIMEOUT)
            
            if ib.isConnected():
                logger.info(f"Successfully connected to IBKR")
                # Test the connection with a simple command
                try:
                    server_time = ib.reqCurrentTime()
                    logger.info(f"Server time: {server_time}")
                    return ib
                except Exception as cmd_error:
                    logger.error(f"Connected but command failed: {cmd_error}")
                    ib.disconnect()
                    # Continue to retry
                
            logger.warning("Initial connection established but not fully connected")
            
        except Exception as e:
            logger.error(f"Connection attempt {attempt} failed: {e}")
            
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("All connection attempts failed")
                raise ConnectionError(f"Could not connect to Interactive Brokers after {max_retries} attempts: {e}")
                
    # If we get here, all attempts failed
    raise ConnectionError("Could not establish a working connection to Interactive Brokers")

def create_futures_contract(symbol: str, expiry: Optional[str] = None, exchange: str = "CME") -> Future:
    """
    Create a futures contract object.
    
    Args:
        symbol: Futures symbol (e.g. 'MES', 'MNQ')
        expiry: Contract expiration in format YYYYMM, or None to use auto-detection
        exchange: Exchange name (default: 'CME')
    
    Returns:
        Future: IB Future contract object
    """
    # Use auto-detection if expiry not provided
    if not expiry:
        expiry = get_current_expiry()
    
    contract = Future(symbol=symbol, lastTradeDateOrContractMonth=expiry, exchange=exchange)
    logger.info(f"Created futures contract: {symbol} {expiry} on {exchange}")
    return contract

def execute_trade(symbol: str, direction: str, price: float, expiry: Optional[str] = None) -> Dict[str, Union[str, float]]:
    """
    Execute a futures trade on Interactive Brokers.
    
    Args:
        symbol: Futures symbol (e.g. 'MES', 'MNQ')
        direction: Trade direction ('BUY' or 'SELL')
        price: Alert price (for logging purposes)
        expiry: Optional contract expiration in format YYYYMM
    
    Returns:
        Dict containing order status information
    
    Raises:
        ValueError: If direction is invalid
        ConnectionError: If IBKR connection fails
        RuntimeError: If order placement fails
    """
    # Validate direction
    if direction not in ["BUY", "SELL"]:
        error_msg = f"Invalid trade direction: {direction}. Must be 'BUY' or 'SELL'."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Quantity - always positive, action determines direction
    quantity = 1
    
    # Initialize results
    result = {
        "symbol": symbol,
        "direction": direction,
        "price": price,
        "expiry": expiry if expiry else get_current_expiry(),
        "status": "FAILED",
        "message": ""
    }
    
    ib = None
    try:
        # First verify API settings are correct
        if not check_api_settings():
            raise ConnectionError("API settings check failed. Please verify IB Gateway configuration.")
        
        # Connect to Interactive Brokers
        ib = connect_to_ibkr()
        
        # Create the futures contract with optional custom expiry
        contract = create_futures_contract(symbol, expiry)
        
        # Qualify the contract to ensure all details are resolved
        qualified_contract = ib.qualifyContracts(contract)
        if not qualified_contract:
            raise ValueError(f"Could not qualify contract: {symbol}")
        
        contract = qualified_contract[0]
        
        # Create market order
        order = MarketOrder(
            action=direction,
            totalQuantity=quantity
        )
        
        # Submit the order
        trade = ib.placeOrder(contract, order)
        
        # Log the order submission
        logger.info(f"Order placed: {direction} {quantity} {symbol} {result['expiry']} at market")
        
        # Wait for order status update (timeout after 10 seconds)
        for _ in range(10):
            ib.sleep(1)
            if trade.orderStatus.status in ['Filled', 'Submitted', 'PreSubmitted', 'Cancelled']:
                break
        
        # Check order status
        if trade.orderStatus.status in ['Filled', 'Submitted', 'PreSubmitted']:
            result["status"] = trade.orderStatus.status
            result["message"] = f"Order {trade.orderStatus.status}. Filled: {trade.orderStatus.filled}"
            logger.info(f"Order successful: {result['message']}")
        else:
            result["message"] = f"Order status: {trade.orderStatus.status}"
            logger.warning(f"Order may have issues: {result['message']}")
        
        return result
        
    except Exception as e:
        error_msg = f"Trade execution error: {str(e)}"
        logger.error(error_msg)
        result["message"] = error_msg
        raise RuntimeError(error_msg)
    
    finally:
        # Disconnect from IBKR
        if ib and ib.isConnected():
            ib.disconnect()
            logger.info("Disconnected from IBKR")

# This allows for testing the module directly
if __name__ == "__main__":
    # Test execution - will only run when this file is executed directly
    try:
        print("Testing IBKR connection and API settings...")
        if check_api_settings():
            print("API settings verified - connection is operational.")
            print(f"Current front-month expiry: {get_current_expiry()}")
            
            print("\nConnection test successful!")
            print("Ready to execute trades.")
        else:
            print("\nAPI settings check failed.")
            print("Please make sure:")
            print("1. IB Gateway is running")
            print("2. API settings are configured correctly")
            print("3. API client shows 'connected' in IB Gateway status")
    except Exception as e:
        print(f"Test failed: {e}")
