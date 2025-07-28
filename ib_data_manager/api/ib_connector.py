"""
Interactive Brokers API Connector
Handles connection and data retrieval from IB Gateway
"""

from ib_insync import *
import logging
import pandas as pd
from datetime import datetime
import threading
import time
from ib_data_manager.db import database

class IBConnector:
    def __init__(self):
        self.ib = IB()
        self.connected = False
        self.depth_subscriptions = {}  # symbol: handler
        self.db = database.DataManager()
        self.depth_threads = []
        self._depth_stop_event = threading.Event()
        # Runtime check for directory
        import os, logging
        expected_dir = r'D:\projects\trading-bots\ib_data_manager'
        cwd = os.path.abspath(os.getcwd())
        if not cwd.lower().startswith(expected_dir.lower()):
            logging.warning(f"Running from unexpected directory: {cwd}. Expected: {expected_dir}")
        
    def connect(self, host='127.0.0.1', port=4002, client_id=None, timeout=30, max_retries=3):
        """Robust connection to IB Gateway with retry logic and proper error handling"""
        import random
        import time
        
        # Auto-generate client_id to avoid conflicts (common IB issue)
        if client_id is None:
            client_id = random.randint(1000, 9999)
            
        logging.info(f"Attempting to connect to IB Gateway at {host}:{port} with client_id {client_id}")
        
        for attempt in range(max_retries):
            try:
                # Ensure we're disconnected first
                if self.ib.isConnected():
                    logging.info("Already connected, disconnecting first...")
                    self.ib.disconnect()
                    time.sleep(2)  # Give IB time to clean up
                
                # Attempt connection with timeout
                logging.info(f"Connection attempt {attempt + 1}/{max_retries}...")
                self.ib.connect(host, port, client_id, timeout=timeout)
                
                # Verify connection is actually working
                if self.ib.isConnected():
                    # Test the connection with a simple request
                    try:
                        account_summary = self.ib.accountSummary()
                        logging.info(f"Connection verified - found {len(account_summary)} account items")
                        self.connected = True
                        logging.info(f"✅ Successfully connected to IB Gateway at {host}:{port} (client_id: {client_id})")
                        return True
                    except Exception as test_error:
                        logging.warning(f"Connection established but API test failed: {test_error}")
                        # Connection might still be usable, so continue
                        self.connected = True
                        return True
                else:
                    raise ConnectionError("Connection established but isConnected() returns False")
                    
            except Exception as e:
                error_msg = str(e).lower()
                logging.error(f"Connection attempt {attempt + 1} failed: {str(e)}")
                
                # Handle specific IB error cases
                if "already connected" in error_msg:
                    logging.info("Client ID conflict detected, trying new ID...")
                    client_id = random.randint(1000, 9999)
                elif "connection refused" in error_msg:
                    logging.error("❌ IB Gateway/TWS is not running or not accepting connections")
                    logging.error("   Please ensure IB Gateway is running and API is enabled")
                elif "timeout" in error_msg:
                    logging.error("❌ Connection timeout - IB Gateway may be overloaded")
                elif "permission denied" in error_msg:
                    logging.error("❌ API access denied - check IB Gateway API settings")
                
                self.connected = False
                
                # Wait before retry (except on last attempt)
                if attempt < max_retries - 1:
                    retry_delay = (attempt + 1) * 2  # Increasing delay: 2, 4, 6 seconds
                    logging.info(f"Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                    
        # All attempts failed
        logging.error(f"❌ Failed to connect after {max_retries} attempts")
        self._log_connection_troubleshooting(host, port)
        return False
            
    def disconnect(self):
        """Disconnect from IB Gateway"""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            logging.info("Disconnected from IB Gateway")
            
    def is_connected(self):
        """Check if connected with health verification"""
        if not self.connected or not self.ib.isConnected():
            return False
            
        # Additional health check - try a simple API call
        try:
            # Quick health check that doesn't consume data
            self.ib.reqCurrentTime()
            return True
        except Exception as e:
            logging.warning(f"Connection health check failed: {e}")
            self.connected = False
            return False
            
    def _log_connection_troubleshooting(self, host, port):
        """Log detailed troubleshooting information for connection failures"""
        logging.error("\n" + "="*60)
        logging.error("🔧 CONNECTION TROUBLESHOOTING GUIDE")
        logging.error("="*60)
        logging.error(f"Target: {host}:{port}")
        logging.error("")
        logging.error("Common solutions:")
        logging.error("1. ✅ Ensure IB Gateway/TWS is running")
        logging.error("2. ✅ Check API settings in IB Gateway:")
        logging.error("   - Go to Configure > Settings > API > Settings")
        logging.error("   - Enable 'Enable ActiveX and Socket Clients'")
        logging.error("   - Check 'Read-Only API' if you only need data")
        logging.error("   - Verify Socket Port matches your port")
        logging.error("3. ✅ Verify port numbers:")
        logging.error("   - Paper Trading: 4002")
        logging.error("   - Live Trading: 4001")
        logging.error("4. ✅ Check Windows Firewall/Antivirus")
        logging.error("5. ✅ Try restarting IB Gateway")
        logging.error("6. ✅ Check if another application is using the same client_id")
        logging.error("="*60)
        
    def auto_reconnect(self, max_attempts=5):
        """Automatic reconnection with exponential backoff"""
        if self.is_connected():
            return True
            
        logging.info("🔄 Starting auto-reconnection process...")
        
        for attempt in range(max_attempts):
            logging.info(f"Auto-reconnect attempt {attempt + 1}/{max_attempts}")
            
            if self.connect():
                logging.info("✅ Auto-reconnection successful!")
                return True
                
            # Exponential backoff: 5, 10, 20, 40, 80 seconds
            if attempt < max_attempts - 1:
                delay = 5 * (2 ** attempt)
                logging.info(f"Waiting {delay} seconds before next attempt...")
                import time
                time.sleep(delay)
                
        logging.error("❌ Auto-reconnection failed after all attempts")
        return False
        
    def diagnose_connection(self, host='127.0.0.1', port=4002):
        """Comprehensive connection diagnostics to identify specific issues"""
        import socket
        import platform
        
        logging.info("\n" + "="*60)
        logging.info("🔍 RUNNING CONNECTION DIAGNOSTICS")
        logging.info("="*60)
        
        # 1. Basic system info
        logging.info(f"System: {platform.system()} {platform.release()}")
        logging.info(f"Python: {platform.python_version()}")
        
        # 2. Test network connectivity
        logging.info(f"\n🌐 Testing network connectivity to {host}:{port}...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                logging.info("✅ Network connection successful - IB Gateway is reachable")
            else:
                logging.error("❌ Network connection failed - IB Gateway not reachable")
                logging.error("   Check if IB Gateway is running and port is correct")
                return False
        except Exception as e:
            logging.error(f"❌ Network test failed: {e}")
            return False
            
        # 3. Test IB API connection
        logging.info(f"\n🔗 Testing IB API connection...")
        test_ib = IB()
        try:
            import random
            test_client_id = random.randint(5000, 9999)
            test_ib.connect(host, port, test_client_id, timeout=10)
            
            if test_ib.isConnected():
                logging.info("✅ IB API connection successful")
                
                # 4. Test API permissions
                logging.info("\n🔐 Testing API permissions...")
                try:
                    account_summary = test_ib.accountSummary()
                    logging.info(f"✅ Account data access: {len(account_summary)} items retrieved")
                except Exception as perm_error:
                    logging.warning(f"⚠️ Limited API permissions: {perm_error}")
                    logging.warning("   Consider enabling 'Read-Only API' in IB Gateway settings")
                    
                # 5. Test market data permissions
                try:
                    from ib_insync import Stock
                    test_contract = Stock('AAPL', 'SMART', 'USD')
                    test_ib.qualifyContracts(test_contract)
                    ticker = test_ib.reqMktData(test_contract)
                    test_ib.sleep(2)  # Wait for data
                    test_ib.cancelMktData(test_contract)
                    logging.info("✅ Market data access confirmed")
                except Exception as market_error:
                    logging.warning(f"⚠️ Market data access limited: {market_error}")
                    logging.warning("   You may need market data subscriptions")
                    
                test_ib.disconnect()
                logging.info("✅ All diagnostic tests completed successfully")
                return True
                
            else:
                logging.error("❌ IB API connection failed - connected but not responding")
                return False
                
        except Exception as api_error:
            error_msg = str(api_error).lower()
            logging.error(f"❌ IB API connection failed: {api_error}")
            
            if "already connected" in error_msg:
                logging.error("   Another application may be using this client ID")
            elif "timeout" in error_msg:
                logging.error("   IB Gateway may be overloaded or not responding")
            elif "permission" in error_msg:
                logging.error("   API access is disabled in IB Gateway settings")
                
            return False
        finally:
            if test_ib.isConnected():
                test_ib.disconnect()
                
        logging.info("="*60)
        
    def create_contract(self, symbol, sec_type="STK", exchange="SMART", currency="USD", expiry=None):
        """Create a contract object"""
        if sec_type == "STK":
            contract = Stock(symbol, exchange, currency)
        elif sec_type == "FUT":
            if expiry:
                contract = Future(symbol, lastTradeDateOrContractMonth=expiry, exchange=exchange, currency=currency)
            else:
                contract = Future(symbol, exchange=exchange, currency=currency)
        elif sec_type == "OPT":
            contract = Option(symbol, exchange=exchange, currency=currency)
        elif sec_type == "CASH":
            contract = Forex(symbol, exchange=exchange, currency=currency)
        elif sec_type == "BOND":
            contract = Bond(symbol, exchange=exchange, currency=currency)
        else:
            raise ValueError(f"Unsupported security type: {sec_type}")
        return contract
        
    def get_historical_data(self, symbol, sec_type="STK", exchange="SMART", 
                          currency="USD", duration="1 D", bar_size="1 min", expiry=None):
        """Get historical data for a contract"""
        try:
            contract = self.create_contract(symbol, sec_type, exchange, currency, expiry)
            # Qualify the contract
            import logging
            logging.info(f"Qualifying contract: {contract}")
            result = self.ib.qualifyContracts(contract)
            logging.info(f"Qualification result: {result}")
            # Request historical data
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr=duration,
                barSizeSetting=bar_size,
                whatToShow='TRADES',
                useRTH=True,
                formatDate=1
            )
            return bars
        except Exception as e:
            logging.error(f"Error getting historical data: {str(e)}")
            return None
            
    def start_realtime_quotes(self, symbol, sec_type="STK", exchange="SMART", 
                            currency="USD", callback=None):
        """Start real-time market data"""
        try:
            contract = self.create_contract(symbol, sec_type, exchange, currency)
            
            # Qualify the contract
            import logging
            logging.info(f"Qualifying contract: {contract}")
            result = self.ib.qualifyContracts(contract)
            logging.info(f"Qualification result: {result}")
            
            # Request market data
            ticker = self.ib.reqMktData(contract, '', False, False)
            
            if callback:
                # Set up callback for updates
                ticker.updateEvent += callback
                
            return ticker
            
        except Exception as e:
            logging.error(f"Error starting real-time quotes: {str(e)}")
            return None
            
    def stop_realtime_quotes(self, ticker):
        """Stop real-time market data"""
        try:
            self.ib.cancelMktData(ticker.contract)
        except Exception as e:
            logging.error(f"Error stopping real-time quotes: {str(e)}")

    def start_market_depth(self, symbol, sec_type="STK", exchange="SMART", currency="USD", num_rows=5, callback=None):
        """Start Level 2 (market depth) data feed"""
        try:
            contract = self.create_contract(symbol, sec_type, exchange, currency)
            logging.info(f"Qualifying contract for market depth: {contract}")
            result = self.ib.qualifyContracts(contract)
            logging.info(f"Qualification result: {result}")
            ticker = self.ib.reqMktDepth(contract, numRows=num_rows)
            if callback:
                ticker.updateEvent += callback
            return ticker
        except Exception as e:
            logging.error(f"Error starting market depth: {str(e)}")
            return None

    def stop_market_depth(self, ticker):
        """Stop Level 2 (market depth) data feed"""
        try:
            self.ib.cancelMktDepth(ticker.contract)
        except Exception as e:
            logging.error(f"Error stopping market depth: {str(e)}")
            
    def get_account_info(self):
        """Get account information"""
        try:
            # Request account summary
            account_values = self.ib.accountSummary()
            
            # Convert to dictionary
            account_info = {}
            for av in account_values:
                account_info[av.tag] = av.value
                
            return account_info
            
        except Exception as e:
            logging.error(f"Error getting account info: {str(e)}")
            return None
            
    def get_positions(self):
        """Get current positions"""
        try:
            positions = self.ib.positions()
            return positions
        except Exception as e:
            logging.error(f"Error getting positions: {str(e)}")
            return None
            
    def get_orders(self):
        """Get open orders"""
        try:
            orders = self.ib.orders()
            return orders
        except Exception as e:
            logging.error(f"Error getting orders: {str(e)}")
            return None
            
    def place_order(self, contract, order):
        """Place an order"""
        try:
            trade = self.ib.placeOrder(contract, order)
            return trade
        except Exception as e:
            logging.error(f"Error placing order: {str(e)}")
            return None
            
    def cancel_order(self, order):
        """Cancel an order"""
        try:
            self.ib.cancelOrder(order)
            return True
        except Exception as e:
            logging.error(f"Error canceling order: {str(e)}")
            return False

    def subscribe_market_depth(self, symbol, sec_type="STK", exchange="SMART", currency="USD", num_rows=10):
        """Subscribe to Level 2 (market depth) for a symbol and record updates to the database."""
        contract = self.create_contract(symbol, sec_type, exchange, currency)
        self.ib.qualifyContracts(contract)
        depth = self.ib.reqMktDepth(contract, numRows=num_rows)
        
        def handle_depth_update(md, rows):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for row in rows:
                # row.operation: 0=insert, 1=update, 2=delete
                op_map = {0: 'insert', 1: 'update', 2: 'delete'}
                operation = op_map.get(row.operation, 'unknown')
                side = 'bid' if row.side == 0 else 'ask'
                self.db.insert_market_depth(
                    symbol=symbol,
                    timestamp=now,
                    side=side,
                    position=row.position,
                    price=row.price,
                    size=row.size,
                    market_maker=row.marketMaker,
                    operation=operation
                )
        depth.updateEvent += handle_depth_update
        self.depth_subscriptions[symbol] = depth
        logging.info(f"Subscribed to market depth for {symbol}")
        return depth

    def unsubscribe_market_depth(self, symbol):
        """Unsubscribe from market depth for a symbol."""
        depth = self.depth_subscriptions.get(symbol)
        if depth:
            self.ib.cancelMktDepth(depth.contract)
            del self.depth_subscriptions[symbol]
            logging.info(f"Unsubscribed from market depth for {symbol}")

    def automate_market_depth_collection(self, symbols, sec_type="STK", exchange="SMART", currency="USD", num_rows=10, poll_interval=1):
        """Automate Level 2 data collection for a list of symbols in background threads."""
        def collector(symbol):
            try:
                self.subscribe_market_depth(symbol, sec_type, exchange, currency, num_rows)
                while not self._depth_stop_event.is_set():
                    time.sleep(poll_interval)
            except Exception as e:
                logging.error(f"Error in market depth collection for {symbol}: {str(e)}")
            finally:
                self.unsubscribe_market_depth(symbol)
        self._depth_stop_event.clear()
        for symbol in symbols:
            t = threading.Thread(target=collector, args=(symbol,), daemon=True)
            t.start()
            self.depth_threads.append(t)
        logging.info(f"Started automated market depth collection for: {symbols}")

    def stop_automated_market_depth(self):
        """Stop all automated market depth collection threads."""
        self._depth_stop_event.set()
        for t in self.depth_threads:
            t.join(timeout=3)
        self.depth_threads.clear()
        for symbol in list(self.depth_subscriptions.keys()):
            self.unsubscribe_market_depth(symbol)
        logging.info("Stopped all market depth collection threads.")

    def get_historical_data(self, symbol, start_date, end_date, bar_size, sec_type="STK", exchange="SMART", currency="USD"):
        """
        Fetch historical data for a symbol between start_date and end_date at the given bar_size.
        Stores results in the database and returns the list of bars.
        """
        from dateutil import parser
        import time as time_module

        contract = self.create_contract(symbol, sec_type, exchange, currency)
        self.ib.qualifyContracts(contract)

        # IBKR has limits: max duration per request depends on bar_size
        duration_map = {
            "1 min": "1 D",
            "5 mins": "1 W",
            "10 mins": "1 W",
            "15 mins": "2 W",
            "30 mins": "1 M",
            "1 hour": "1 M",
            "1 day": "1 Y"
        }
        duration_str = duration_map.get(bar_size, "1 D")
        bar_size_str = bar_size

        # Date handling
        dt_start = parser.parse(start_date)
        dt_end = parser.parse(end_date)
        bars_all = []
        dt_cursor = dt_end
        while dt_cursor > dt_start:
            # IBKR expects endDateTime as string YYYYMMDD HH:MM:SS in US/Eastern
            end_str = dt_cursor.strftime("%Y%m%d %H:%M:%S")
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime=end_str,
                durationStr=duration_str,
                barSizeSetting=bar_size_str,
                whatToShow="TRADES",
                useRTH=False,
                formatDate=1
            )
            if not bars:
                break
            for bar in bars:
                self.db.insert_historical_data(
                    symbol=symbol,
                    date=bar.date,
                    open=bar.open,
                    high=bar.high,
                    low=bar.low,
                    close=bar.close,
                    volume=bar.volume,
                    average=getattr(bar, 'average', None),
                    bar_count=getattr(bar, 'barCount', None)
                )
            bars_all.extend(bars)
            # Move the cursor back by the duration (avoid overlap)
            dt_cursor = parser.parse(bars[0].date)
            # Avoid rate limits
            time_module.sleep(1)
        return bars_all

# Test connection
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create connector
    connector = IBConnector()
    
    # Connect to IB Gateway
    if connector.connect():
        print("Connected successfully!")
        
        # Test historical data
        bars = connector.get_historical_data("AAPL", "2024-01-01", "2024-01-05", "1 hour")
        if bars:
            print(f"Received {len(bars)} bars")
            for bar in bars[:5]:
                print(f"{bar.date}: {bar.close}")
                
        # Disconnect
        connector.disconnect()
    else:
        print("Connection failed!")
