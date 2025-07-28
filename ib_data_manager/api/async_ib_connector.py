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
        
        if sec_type == "FUT" and expiry:
            return contract_class(symbol, exchange=exchange, currency=currency, lastTradeDateOrContractMonth=expiry)
        elif sec_type in ["STK", "CASH", "IND", "CFD", "BOND", "CMDTY", "CRYPTO", "FUND", "WAR"]:
            return contract_class(symbol, exchange=exchange, currency=currency)
        elif sec_type == "OPT" and expiry:
            # For options, we need more parameters - this is a simplified version
            return contract_class(symbol, exchange=exchange, currency=currency, lastTradeDateOrContractMonth=expiry)
        else:
            return Contract(symbol, secType=sec_type, exchange=exchange, currency=currency)
            
    async def get_historical_data(self, symbol, sec_type="STK", exchange="SMART", 
                                currency="USD", duration="1 D", bar_size="1 min", expiry=None):
        """Get historical data for a contract"""
        try:
            contract = self.create_contract(symbol, sec_type, exchange, currency, expiry)
            
            # Qualify the contract
            qualified_contracts = await self.ib.qualifyContractsAsync(contract)
            if not qualified_contracts:
                logging.error(f"Failed to qualify contract for {symbol}")
                return None
                
            qualified_contract = qualified_contracts[0]
            
            # Request historical data
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
