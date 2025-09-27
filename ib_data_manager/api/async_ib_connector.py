"""
Async Interactive Brokers API Connector
Handles connection and data retrieval from IB Gateway using native async patterns
"""

import asyncio
import logging
import pandas as pd
from datetime import datetime
from ib_insync import IB, util, Contract, Stock, Future, Option, Forex, Index, CFD, Bond, Commodity, Crypto, MutualFund, Warrant, Bag
from ib_data_manager.db.async_database import AsyncDataManager
from ib_data_manager.config import config


class AsyncIBConnector:
    """Async-native IB connector using ib_insync's asyncio patterns"""
    
    def __init__(self):
        """Initialize the async IB connector"""
        self.ib = None
        self.connected = False
        self.depth_subscriptions = {}  # symbol: handler
        self.db = AsyncDataManager()
        self.config = config.config
        
        # Async queue for market depth data
        self.depth_queue = None
        self.depth_task = None
        
    async def connect(self, host='127.0.0.1', port=4002, client_id=None, timeout=30, max_retries=3):
        """Async connection to IB Gateway with retry logic"""
        import random
        
        # Auto-generate client_id to avoid conflicts
        if client_id is None:
            client_id = random.randint(1000, 9999)
            
        logging.info(f"Attempting to connect to IB Gateway at {host}:{port} with client_id {client_id}")
        
        # Initialize IB instance if not already done
        if self.ib is None:
            self.ib = IB()
        
        # Initialize async database
        await self.db.initialize()
        
        for attempt in range(max_retries):
            try:
                # Ensure we're disconnected first
                if self.ib.isConnected():
                    logging.info("Already connected, disconnecting first...")
                    await self.disconnect()
                    await asyncio.sleep(2)  # Give IB time to clean up
                
                # Attempt connection with timeout
                logging.info(f"Connection attempt {attempt + 1}/{max_retries}...")
                await asyncio.wait_for(
                    self.ib.connectAsync(host, port, client_id, timeout=timeout),
                    timeout=timeout
                )
                
                self.connected = True
                logging.info("Successfully connected to IB Gateway")
                return True
                
            except asyncio.TimeoutError:
                logging.warning(f"Connection attempt {attempt + 1} timed out")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
                
            except Exception as e:
                logging.error(f"Connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
        
        logging.error("Failed to connect to IB Gateway after all retries")
        return False
        
    async def disconnect(self):
        """Async disconnect from IB Gateway"""
        try:
            if self.ib and self.ib.isConnected():
                # Stop any running tasks
                await self.stop_automated_market_depth()
                
                # Disconnect
                await self.ib.disconnectAsync()
                self.connected = False
                logging.info("Disconnected from IB Gateway")
                return True
            return True
        except Exception as e:
            logging.error(f"Error disconnecting from IB Gateway: {str(e)}")
            return False
            
    def is_connected(self):
        """Check if connected to IB Gateway"""
        return self.connected and self.ib and self.ib.isConnected()
        
    async def auto_reconnect(self, max_attempts=5):
        """Automatic reconnection with exponential backoff"""
        host = self.config.get('ib_gateway', 'host', '127.0.0.1')
        port = self.config.get('ib_gateway', 'port', 4002)
        client_id = self.config.get('ib_gateway', 'client_id', 1)
        
        for attempt in range(max_attempts):
            try:
                logging.info(f"Auto-reconnect attempt {attempt + 1}/{max_attempts}")
                if await self.connect(host, port, client_id):
                    logging.info("Auto-reconnect successful")
                    return True
                
                # Exponential backoff
                delay = min(2 ** attempt, 60)  # Cap at 60 seconds
                logging.info(f"Waiting {delay} seconds before next reconnect attempt")
                await asyncio.sleep(delay)
                
            except Exception as e:
                logging.error(f"Auto-reconnect attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_attempts - 1:
                    delay = min(2 ** attempt, 60)
                    await asyncio.sleep(delay)
                continue
        
        logging.error("Auto-reconnect failed after all attempts")
        return False
        
    def create_contract(self, symbol, sec_type="STK", exchange="SMART", currency="USD", expiry=None):
        """Create a contract object"""
        from ib_insync import Stock, Future, Option, Forex, Index, CFD, Bond, Commodity, Crypto, MutualFund, Warrant, Bag, Contract
        
        contract_map = {
            "STK": Stock,
            "FUT": Future,
            "OPT": Option,
            "CASH": Forex,
            "IND": Index,
            "CFD": CFD,
            "BOND": Bond,
            "CMDTY": Commodity,
            "CRYPTO": Crypto,
            "FUND": MutualFund,
            "WAR": Warrant,
            "BAG": Bag
        }
        
        contract_class = contract_map.get(sec_type, Contract)
        
        try:
            if sec_type == "FUT":
                # For futures, always include expiry if provided
                if expiry:
                    return contract_class(symbol=symbol, exchange=exchange, currency=currency, 
                                        lastTradeDateOrContractMonth=expiry)
                else:
                    # For futures without expiry (used in contract search)
                    return contract_class(symbol=symbol, exchange=exchange, currency=currency)
            elif sec_type in ["STK", "CASH", "IND", "CFD", "BOND", "CMDTY", "CRYPTO", "FUND", "WAR"]:
                return contract_class(symbol=symbol, exchange=exchange, currency=currency)
            elif sec_type == "OPT" and expiry:
                # For options, we need more parameters - this is a simplified version
                return contract_class(symbol=symbol, exchange=exchange, currency=currency, 
                                    lastTradeDateOrContractMonth=expiry)
            else:
                # Fallback to generic contract
                return Contract(symbol=symbol, secType=sec_type, exchange=exchange, currency=currency)
        except Exception as e:
            logging.error(f"Error creating {sec_type} contract for {symbol}: {str(e)}")
            # Fallback to generic contract
            return Contract(symbol=symbol, secType=sec_type, exchange=exchange, currency=currency)
            
    async def get_historical_data(self, symbol, sec_type="STK", exchange="SMART", 
                                currency="USD", duration="1 D", bar_size="1 min", expiry=None,
                                start_date=None, end_date=None):
        """
        Get historical data for a contract. Supports both duration and date range modes.
        Duration mode: <number> <unit> (e.g. 1 D, 6 M, 2 Y, 3 W, 30 S), unit in S/D/W/M/Y
        Date range mode: start_date and end_date in YYYY-MM-DD format
        Bar Size: IBKR supported intervals (e.g. 1 min, 5 mins, 1 day, 1 week, 1 month, etc.)
        """
        def validate_duration(duration):
            import re
            pattern = r"^\s*([1-9][0-9]*)\s*([SMWDYsmwdy])\s*$"
            match = re.match(pattern, duration.strip())
            if not match:
                return False
            num, unit = match.groups()
            return unit.upper() in ["S", "D", "W", "M", "Y"]
            
        def validate_bar_size(bar_size):
            valid_sizes = [
                "1 sec", "5 secs", "10 secs", "15 secs", "30 secs", "1 min", "2 mins", "3 mins", "5 mins", "10 mins", "15 mins", "30 mins", "1 hour", "1 day", "1 week", "1 month"
            ]
            return bar_size in valid_sizes
            
        # Validate bar size
        if not validate_bar_size(bar_size):
            logging.error(f"Invalid bar size: {bar_size}. Must be one of IBKR supported intervals.")
            return None
            
        try:
            contract = self.create_contract(symbol, sec_type, exchange, currency, expiry)
            
            # Qualify the contract
            qualified_contracts = await self.ib.qualifyContractsAsync(contract)
            if not qualified_contracts:
                logging.error(f"Failed to qualify contract for {symbol}")
                return None
            qualified_contract = qualified_contracts[0]
            
            # Handle date range mode with batch processing
            if start_date and end_date:
                return await self._get_historical_data_date_range(
                    qualified_contract, start_date, end_date, bar_size
                )
            else:
                # Duration mode validation
                if not validate_duration(duration):
                    logging.error(f"Invalid duration string: {duration}. Must be <number> <unit> (S/D/W/M/Y). Example: 1 D, 6 M, 2 Y, 3 W, 30 S.")
                    return None
                    
                # Request historical data using duration
                bars = await self.ib.reqHistoricalDataAsync(
                    qualified_contract,
                    endDateTime='',
                    durationStr=duration,
                    barSizeSetting=bar_size,
                    whatToShow='TRADES',
                    useRTH=False,
                    formatDate=1
                )
                return bars
                
        except Exception as e:
            logging.error(f"Error getting historical data for {symbol}: {str(e)}")
            return None
            
    async def _get_historical_data_date_range(self, contract, start_date, end_date, bar_size):
        """
        Get historical data for a specific date range with automatic batch processing
        to handle IBKR API limitations and prevent throttling
        """
        from datetime import datetime, timedelta
        import asyncio
        
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Calculate optimal batch size based on bar size to avoid API limits
            batch_days = self._calculate_batch_size(bar_size)
            
            all_bars = []
            current_end = end_dt
            batch_count = 0
            
            logging.info(f"Fetching data from {start_date} to {end_date} in {batch_days}-day batches")
            
            while current_end > start_dt:
                batch_count += 1
                current_start = max(start_dt, current_end - timedelta(days=batch_days))
                
                # Calculate duration string for this batch
                duration_days = (current_end - current_start).days + 1
                duration_str = f"{duration_days} D"
                
                logging.info(f"Batch {batch_count}: Fetching {duration_str} ending {current_end.strftime('%Y-%m-%d')}")
                
                try:
                    # Request this batch
                    bars = await self.ib.reqHistoricalDataAsync(
                        contract,
                        endDateTime=current_end.strftime('%Y%m%d %H:%M:%S'),
                        durationStr=duration_str,
                        barSizeSetting=bar_size,
                        whatToShow='TRADES',
                        useRTH=False,
                        formatDate=1
                    )
                    
                    if bars:
                        # Filter bars to exact date range and add to collection
                        filtered_bars = [
                            bar for bar in bars 
                            if start_dt <= bar.date.replace(tzinfo=None) <= end_dt
                        ]
                        all_bars.extend(filtered_bars)
                        logging.info(f"Batch {batch_count}: Retrieved {len(filtered_bars)} bars")
                    
                    # Rate limiting - wait between requests to avoid throttling
                    if current_end > start_dt:  # Don't wait after last batch
                        await asyncio.sleep(1.1)  # IBKR allows ~1 request per second
                        
                except Exception as e:
                    logging.error(f"Error in batch {batch_count}: {str(e)}")
                    # Continue with next batch on error
                    
                # Move to next batch
                current_end = current_start - timedelta(days=1)
            
            # Sort bars by date (oldest first)
            all_bars.sort(key=lambda x: x.date)
            
            logging.info(f"Date range fetch complete: {len(all_bars)} total bars from {batch_count} batches")
            return all_bars
            
        except Exception as e:
            logging.error(f"Error in date range fetch: {str(e)}")
            return None
            
    def _calculate_batch_size(self, bar_size):
        """
        Calculate optimal batch size in days based on bar size to avoid API limits
        IBKR has limits on how much data can be requested at once
        """
        # Conservative batch sizes to avoid hitting API limits
        batch_sizes = {
            "1 sec": 1,      # 1 day max for 1-second bars
            "5 secs": 2,     # 2 days max for 5-second bars  
            "10 secs": 3,    # 3 days max for 10-second bars
            "15 secs": 5,    # 5 days max for 15-second bars
            "30 secs": 7,    # 1 week max for 30-second bars
            "1 min": 14,     # 2 weeks max for 1-minute bars
            "2 mins": 21,    # 3 weeks max for 2-minute bars
            "3 mins": 30,    # 1 month max for 3-minute bars
            "5 mins": 45,    # 1.5 months max for 5-minute bars
            "10 mins": 60,   # 2 months max for 10-minute bars
            "15 mins": 90,   # 3 months max for 15-minute bars
            "30 mins": 180,  # 6 months max for 30-minute bars
            "1 hour": 365,   # 1 year max for 1-hour bars
            "1 day": 1825,   # 5 years max for daily bars
            "1 week": 3650,  # 10 years max for weekly bars
            "1 month": 7300  # 20 years max for monthly bars
        }
        
        return batch_sizes.get(bar_size, 30)  # Default to 30 days if unknown
        
    async def get_futures_contracts(self, symbol, exchange="SMART", currency="USD"):
        """
        Get available futures contracts for a symbol
        Returns list of qualified contracts sorted by expiry
        """
        try:
            logging.info(f"Searching for futures contracts for {symbol}")
            
            # Create a generic futures contract for contract search
            from ib_insync import Future
            
            # Try multiple exchanges for common futures symbols
            exchanges_to_try = [exchange]
            if exchange == "SMART":
                # Add common futures exchanges for well-known symbols
                # Based on debug results: CME works for MES, GLOBEX doesn't
                symbol_exchanges = {
                    "ES": ["CME", "GLOBEX"],
                    "MES": ["CME"],  # MES works on CME, not GLOBEX
                    "NQ": ["CME", "GLOBEX"],
                    "MNQ": ["CME", "GLOBEX"],
                    "YM": ["ECBOT", "CBOT", "CME"],
                    "MYM": ["ECBOT", "CBOT", "CME"],
                    "RTY": ["CME", "GLOBEX"],
                    "M2K": ["CME", "GLOBEX"],
                    "CL": ["NYMEX"],
                    "GC": ["COMEX"],
                    "SI": ["COMEX"],
                    "ZN": ["ECBOT", "CBOT"],
                    "ZB": ["ECBOT", "CBOT"]
                }
                if symbol in symbol_exchanges:
                    exchanges_to_try = symbol_exchanges[symbol]
                else:
                    exchanges_to_try = ["CME", "GLOBEX", "NYMEX", "COMEX", "ECBOT", "CBOT"]
            
            all_contracts = []
            
            for exch in exchanges_to_try:
                try:
                    contract = Future(symbol, exchange=exch, currency=currency)
                    logging.info(f"Requesting contract details for: {contract}")
                    
                    contract_details = await self.ib.reqContractDetailsAsync(contract)
                    
                    if contract_details:
                        logging.info(f"Found {len(contract_details)} contracts on {exch}")
                        all_contracts.extend(contract_details)
                        break  # Found contracts, no need to try other exchanges
                    else:
                        logging.info(f"No contracts found on {exch}")
                        
                except Exception as e:
                    logging.warning(f"Error searching {exch} for {symbol}: {str(e)}")
                    continue
            
            if not all_contracts:
                logging.warning(f"No futures contracts found for {symbol} on any exchange")
                return []
                
            # Extract contracts and sort by expiry
            contracts = [cd.contract for cd in all_contracts]
            
            # Filter out contracts without expiry dates and sort
            valid_contracts = [c for c in contracts if c.lastTradeDateOrContractMonth]
            valid_contracts.sort(key=lambda c: c.lastTradeDateOrContractMonth)
            
            logging.info(f"Found {len(valid_contracts)} futures contracts for {symbol}")
            for contract in valid_contracts:
                logging.info(f"  - {contract.symbol} {contract.lastTradeDateOrContractMonth} ({contract.exchange})")
                
            return valid_contracts
            
        except Exception as e:
            logging.error(f"Error getting futures contracts for {symbol}: {str(e)}")
            return []
            
    async def get_front_contract(self, symbol, exchange="SMART", currency="USD"):
        """
        Get the front (nearest expiry) futures contract for a symbol
        """
        try:
            contracts = await self.get_futures_contracts(symbol, exchange, currency)
            if contracts:
                front_contract = contracts[0]  # Already sorted by expiry
                logging.info(f"Front contract for {symbol}: {front_contract.lastTradeDateOrContractMonth}")
                return front_contract
            else:
                logging.warning(f"No front contract found for {symbol}")
                return None
        except Exception as e:
            logging.error(f"Error getting front contract for {symbol}: {str(e)}")
            return None
            
    async def qualify_contract_with_expiry(self, symbol, sec_type="FUT", exchange="CME", currency="USD", expiry=None):
        """
        Qualify a specific futures contract with expiry to avoid ambiguous contract errors
        """
        try:
            if not expiry:
                # If no expiry specified, get the front contract
                front_contract = await self.get_front_contract(symbol, exchange, currency)
                if front_contract:
                    expiry = front_contract.lastTradeDateOrContractMonth
                else:
                    logging.error(f"No expiry specified and no front contract found for {symbol}")
                    return None
            
            # Create contract with specific expiry
            contract = self.create_contract(symbol, sec_type, exchange, currency, expiry)
            logging.info(f"Qualifying specific contract: {contract}")
            
            # Qualify the specific contract
            qualified_contracts = await self.ib.qualifyContractsAsync(contract)
            if qualified_contracts:
                qualified_contract = qualified_contracts[0]
                logging.info(f"✅ Successfully qualified: {qualified_contract}")
                return qualified_contract
            else:
                logging.error(f"Failed to qualify specific contract: {contract}")
                return None
                
        except Exception as e:
            logging.error(f"Error qualifying contract with expiry: {str(e)}")
            return None
            
    async def start_realtime_quotes(self, symbol, sec_type="STK", exchange="SMART", 
                                  currency="USD", callback=None):
        """Start real-time market data"""
        try:
            contract = self.create_contract(symbol, sec_type, exchange, currency)
            
            # Qualify the contract
            logging.info(f"Qualifying contract: {contract}")
            qualified_contracts = await self.ib.qualifyContractsAsync(contract)
            if not qualified_contracts:
                logging.error(f"Failed to qualify contract for {symbol}")
                return None
                
            qualified_contract = qualified_contracts[0]
            logging.info(f"Qualification result: {qualified_contracts}")
            
            # Request market data
            ticker = self.ib.reqMktData(qualified_contract, '', False, False)
            
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
            
    async def start_market_depth(self, symbol, sec_type="STK", exchange="SMART", 
                               currency="USD", num_rows=5, callback=None):
        """Start Level 2 (market depth) data feed"""
        try:
            contract = self.create_contract(symbol, sec_type, exchange, currency)
            logging.info(f"Qualifying contract for market depth: {contract}")
            qualified_contracts = await self.ib.qualifyContractsAsync(contract)
            if not qualified_contracts:
                logging.error(f"Failed to qualify contract for {symbol}")
                return None
                
            qualified_contract = qualified_contracts[0]
            logging.info(f"Qualification result: {qualified_contracts}")
            
            ticker = self.ib.reqMktDepth(qualified_contract, numRows=num_rows)
            
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
            
    async def get_account_info(self):
        """Get account information"""
        try:
            # Request account summary
            account_values = await self.ib.accountSummaryAsync()
            
            # Convert to dictionary
            account_info = {}
            for av in account_values:
                account_info[av.tag] = av.value
                
            return account_info
            
        except Exception as e:
            logging.error(f"Error getting account info: {str(e)}")
            return None
            
    async def get_positions(self):
        """Get current positions"""
        try:
            positions = await self.ib.positionsAsync()
            return positions
        except Exception as e:
            logging.error(f"Error getting positions: {str(e)}")
            return None
            
    async def get_orders(self):
        """Get open orders"""
        try:
            orders = await self.ib.ordersAsync()
            return orders
        except Exception as e:
            logging.error(f"Error getting orders: {str(e)}")
            return None
            
    async def place_order(self, contract, order):
        """Place an order"""
        try:
            trade = await self.ib.placeOrderAsync(contract, order)
            return trade
        except Exception as e:
            logging.error(f"Error placing order: {str(e)}")
            return None
            
    async def cancel_order(self, order):
        """Cancel an order"""
        try:
            await self.ib.cancelOrderAsync(order)
            return True
        except Exception as e:
            logging.error(f"Error canceling order: {str(e)}")
            return False
            
    async def subscribe_market_depth(self, symbol, sec_type="STK", exchange="SMART", 
                                   currency="USD", num_rows=10):
        """Subscribe to Level 2 (market depth) for a symbol and record updates to the database."""
        contract = self.create_contract(symbol, sec_type, exchange, currency)
        qualified_contracts = await self.ib.qualifyContractsAsync(contract)
        if not qualified_contracts:
            logging.error(f"Failed to qualify contract for {symbol}")
            return None
            
        qualified_contract = qualified_contracts[0]
        depth = self.ib.reqMktDepth(qualified_contract, numRows=num_rows)
        
        def handle_depth_update(md, rows):
            # Schedule the database insert as a task
            asyncio.create_task(self._insert_market_depth_data(
                symbol, md, rows
            ))
            
        depth.updateEvent += handle_depth_update
        self.depth_subscriptions[symbol] = depth
        logging.info(f"Subscribed to market depth for {symbol}")
        return depth
        
    async def _insert_market_depth_data(self, symbol, md, rows):
        """Insert market depth data into database asynchronously"""
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for row in rows:
                # row.operation: 0=insert, 1=update, 2=delete
                op_map = {0: 'insert', 1: 'update', 2: 'delete'}
                operation = op_map.get(row.operation, 'unknown')
                side = 'bid' if row.side == 0 else 'ask'
                await self.db.insert_market_depth(
                    symbol=symbol,
                    timestamp=now,
                    side=side,
                    position=row.position,
                    price=row.price,
                    size=row.size,
                    market_maker=row.marketMaker,
                    operation=operation
                )
        except Exception as e:
            logging.error(f"Error inserting market depth data: {str(e)}")
            
    async def close(self):
        """Clean up resources"""
        await self.db.close()
        if self.connected:
            await self.disconnect()
            
    def unsubscribe_market_depth(self, symbol):
        """Unsubscribe from market depth for a symbol."""
        depth = self.depth_subscriptions.get(symbol)
        if depth:
            self.ib.cancelMktDepth(depth.contract)
            del self.depth_subscriptions[symbol]
            logging.info(f"Unsubscribed from market depth for {symbol}")
            
    async def automate_market_depth_collection(self, symbols, sec_type="STK", 
                                             exchange="SMART", currency="USD", 
                                             num_rows=10):
        """Automate Level 2 data collection for a list of symbols using async event-driven approach."""
        try:
            # Subscribe to all symbols
            for symbol in symbols:
                await self.subscribe_market_depth(symbol, sec_type, exchange, currency, num_rows)
                
            logging.info(f"Started automated market depth collection for: {symbols}")
            return True
            
        except Exception as e:
            logging.error(f"Error in automated market depth collection: {str(e)}")
            return False
            
    async def stop_automated_market_depth(self):
        """Stop all automated market depth collection."""
        try:
            for symbol in list(self.depth_subscriptions.keys()):
                self.unsubscribe_market_depth(symbol)
                
            logging.info("Stopped all market depth collection.")
            return True
            
        except Exception as e:
            logging.error(f"Error stopping market depth collection: {str(e)}")
            return False


# Test connection
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        # Create connector
        connector = AsyncIBConnector()
        
        # Connect to IB Gateway
        if await connector.connect():
            print("Connected successfully!")
            
            # Test historical data
            bars = await connector.get_historical_data("AAPL", "1 D", "1 hour")
            if bars:
                print(f"Received {len(bars)} bars")
                for bar in bars[:5]:
                    print(f"{bar.date}: {bar.close}")
                    
            # Disconnect
            await connector.disconnect()
        else:
            print("Connection failed!")
    
    # Run the async main function
    asyncio.run(main())
