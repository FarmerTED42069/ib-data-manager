"""
Improved Interactive Brokers API Connector with better error handling
"""

from ib_insync import *
import logging
import pandas as pd
from datetime import datetime
import time

class IBConnectorImproved:
    def __init__(self):
        self.ib = IB()
        self.connected = False
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        
    def connect(self, host='127.0.0.1', port=4001, client_id=1):
        """Connect to IB Gateway with better error handling"""
        try:
            # Disconnect if already connected
            if self.ib.isConnected():
                self.ib.disconnect()
                
            self.ib.connect(host, port, client_id, timeout=15)
            self.connected = True
            
            # Wait for connection to stabilize
            time.sleep(1)
            
            # Verify connection
            if not self.ib.isConnected():
                raise ConnectionError("Connection established but immediately lost")
                
            self.logger.info(f"Connected to IB Gateway at {host}:{port}")
            
            # Set market data type to delayed if needed
            self.ib.reqMarketDataType(4)  # Use delayed data if live is not available
            
            return True
            
        except Exception as e:
            self.logger.error(f"Connection error: {str(e)}")
            self.connected = False
            return False
            
    def get_historical_data(self, symbol, sec_type="STK", exchange="SMART", 
                          currency="USD", duration="1 D", bar_size="1 min"):
        """Get historical data with improved error handling"""
        self.logger.debug(f"Requesting historical data for {symbol}")
        
        try:
            # Create contract
            if sec_type == "STK":
                contract = Stock(symbol, exchange, currency)
            elif sec_type == "FUT":
                contract = Future(symbol, exchange=exchange, currency=currency)
            elif sec_type == "CASH":
                contract = Forex(symbol)
            else:
                raise ValueError(f"Unsupported security type: {sec_type}")
            
            # Qualify the contract
            qualified_contracts = self.ib.qualifyContracts(contract)
            
            if not qualified_contracts:
                self.logger.error(f"Failed to qualify contract for {symbol}")
                return None
                
            qualified_contract = qualified_contracts[0]
            self.logger.debug(f"Contract qualified: {qualified_contract}")
            
            # Try different data types if TRADES fails
            data_types = ['TRADES', 'MIDPOINT', 'BID', 'ASK']
            
            for data_type in data_types:
                try:
                    self.logger.debug(f"Trying data type: {data_type}")
                    
                    # Request historical data
                    bars = self.ib.reqHistoricalData(
                        qualified_contract,
                        endDateTime='',
                        durationStr=duration,
                        barSizeSetting=bar_size,
                        whatToShow=data_type,
                        useRTH=True,
                        formatDate=1,
                        timeout=15
                    )
                    
                    if bars:
                        self.logger.info(f"Received {len(bars)} bars for {symbol} using {data_type}")
                        return bars
                    else:
                        self.logger.warning(f"No data received for {symbol} with {data_type}")
                        
                except Exception as e:
                    self.logger.warning(f"Failed to get {data_type} data: {str(e)}")
                    continue
            
            # If all data types fail, try with different settings
            try:
                self.logger.debug("Trying with useRTH=False")
                bars = self.ib.reqHistoricalData(
                    qualified_contract,
                    endDateTime='',
                    durationStr=duration,
                    barSizeSetting=bar_size,
                    whatToShow='TRADES',
                    useRTH=False,  # Include extended hours
                    formatDate=1,
                    timeout=15
                )
                
                if bars:
                    self.logger.info(f"Received {len(bars)} bars for {symbol} (including extended hours)")
                    return bars
                    
            except Exception as e:
                self.logger.error(f"Final attempt failed: {str(e)}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting historical data for {symbol}: {str(e)}")
            return None
            
    def test_connection(self):
        """Test the connection and market data access"""
        try:
            if not self.ib.isConnected():
                return False, "Not connected to IB Gateway"
                
            # Test server time
            server_time = self.ib.reqCurrentTime()
            self.logger.info(f"Server time: {datetime.fromtimestamp(server_time)}")
            
            # Test account access
            accounts = self.ib.managedAccounts()
            if not accounts:
                return False, "No managed accounts found"
                
            self.logger.info(f"Managed accounts: {accounts}")
            
            # Test market data
            test_contract = Stock('AAPL', 'SMART', 'USD')
            qualified = self.ib.qualifyContracts(test_contract)
            
            if not qualified:
                return False, "Failed to qualify test contract (AAPL)"
                
            return True, "Connection test successful"
            
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
            
    def get_market_data_type(self):
        """Get current market data type"""
        try:
            # 1 = Live, 2 = Frozen, 3 = Delayed, 4 = Delayed-Frozen
            data_type = self.ib.reqMarketDataType(3)  # Request delayed data
            return data_type
        except Exception as e:
            self.logger.error(f"Error getting market data type: {str(e)}")
            return None

# Test the improved connector
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    connector = IBConnectorImproved()
    
    if connector.connect():
        print("Connected successfully!")
        
        # Test connection
        success, message = connector.test_connection()
        print(f"Connection test: {message}")
        
        # Get market data type
        data_type = connector.get_market_data_type()
        print(f"Market data type: {data_type}")
        
        # Test historical data
        bars = connector.get_historical_data("SPY", duration="1 D", bar_size="30 mins")
        if bars:
            print(f"Received {len(bars)} bars")
            print(f"First bar: {bars[0].date} - {bars[0].close}")
            print(f"Last bar: {bars[-1].date} - {bars[-1].close}")
        else:
            print("No data received")
            
        connector.ib.disconnect()
    else:
        print("Connection failed!")
