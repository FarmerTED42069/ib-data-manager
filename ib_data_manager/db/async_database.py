"""
Async Database Manager
Handles asynchronous SQLite database operations for storing IB data
"""

import aiosqlite
import asyncio
import logging
from datetime import datetime
from contextlib import asynccontextmanager


class AsyncDataManager:
    """Async database manager with connection pooling"""
    
    def __init__(self, db_path="ib_data.db", pool_size=5):
        self.db_path = db_path
        self.pool_size = pool_size
        self._connection_pool = asyncio.Queue(maxsize=pool_size)
        self._initialized = False
        
    async def initialize(self):
        """Initialize the database and connection pool"""
        if self._initialized:
            return
            
        # Create database tables with a temporary connection
        conn = await aiosqlite.connect(self.db_path)
        try:
            # Historical data table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS historical_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date DATETIME NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    average REAL,
                    bar_count INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Real-time quotes table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS realtime_quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    bid REAL,
                    bid_size INTEGER,
                    ask REAL,
                    ask_size INTEGER,
                    last REAL,
                    last_size INTEGER,
                    volume INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Account information table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS account_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id TEXT,
                    key TEXT NOT NULL,
                    value TEXT,
                    currency TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Market depth (Level 2) data table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS market_depth (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    side TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    price REAL NOT NULL,
                    size INTEGER NOT NULL,
                    market_maker TEXT,
                    operation TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create indexes for better performance
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_historical_symbol_date 
                ON historical_data (symbol, date);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_realtime_symbol_timestamp 
                ON realtime_quotes (symbol, timestamp);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_market_depth_symbol_timestamp 
                ON market_depth (symbol, timestamp);
            """)
            
            await conn.commit()
        finally:
            await conn.close()
        
        # Initialize connection pool
        for _ in range(self.pool_size):
            conn = await aiosqlite.connect(self.db_path)
            await self._connection_pool.put(conn)
            
        self._initialized = True
        logging.info("Async database manager initialized")
            
    @asynccontextmanager
    async def _get_connection(self):
        """Get a connection from the pool"""
        if not self._initialized:
            await self.initialize()
            
        conn = await self._connection_pool.get()
        try:
            yield conn
        finally:
            await self._connection_pool.put(conn)
            
    async def save_historical_data(self, symbol, bars):
        """Save historical data to database using batch operations for better performance"""
        if not bars:
            return
            
        try:
            async with self._get_connection() as conn:
                data = []
                for bar in bars:
                    data.append((
                        symbol,
                        bar.date,
                        bar.open,
                        bar.high,
                        bar.low,
                        bar.close,
                        bar.volume,
                        getattr(bar, 'average', None),
                        getattr(bar, 'barCount', None)
                    ))
                    
                await conn.executemany("""
                    INSERT INTO historical_data 
                    (symbol, date, open, high, low, close, volume, average, bar_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, data)
                await conn.commit()
                logging.info(f"Saved {len(bars)} historical data points for {symbol}")
                
        except Exception as e:
            logging.error(f"Error saving historical data for {symbol}: {str(e)}")
            
    async def save_realtime_quote(self, symbol, ticker):
        """Save real-time quote to database"""
        try:
            async with self._get_connection() as conn:
                await conn.execute("""
                    INSERT INTO realtime_quotes 
                    (symbol, timestamp, bid, bid_size, ask, ask_size, last, last_size, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ticker.bid,
                    ticker.bidSize,
                    ticker.ask,
                    ticker.askSize,
                    ticker.last,
                    ticker.lastSize,
                    ticker.volume
                ))
                await conn.commit()
                
        except Exception as e:
            logging.error(f"Error saving real-time quote for {symbol}: {str(e)}")
            
    async def save_account_info(self, account_info):
        """Save account information to database"""
        try:
            async with self._get_connection() as conn:
                # Clear existing account info
                await conn.execute("DELETE FROM account_info")
                
                # Insert new account info
                data = []
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                for key, value in account_info.items():
                    # Handle different value types
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            data.append((
                                None,  # account_id
                                f"{key}.{sub_key}",
                                str(sub_value),
                                None,  # currency
                                timestamp
                            ))
                    else:
                        data.append((
                            None,  # account_id
                            key,
                            str(value),
                            None,  # currency
                            timestamp
                        ))
                        
                await conn.executemany("""
                    INSERT INTO account_info (account_id, key, value, currency, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, data)
                await conn.commit()
                logging.info(f"Saved {len(data)} account info records")
                
        except Exception as e:
            logging.error(f"Error saving account info: {str(e)}")
            
    async def insert_market_depth(self, symbol, timestamp, side, position, price, size, market_maker, operation):
        """Insert a market depth (Level 2) record asynchronously"""
        try:
            async with self._get_connection() as conn:
                await conn.execute("""
                    INSERT INTO market_depth 
                    (symbol, timestamp, side, position, price, size, market_maker, operation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, timestamp, side, position, price, size, market_maker, operation))
                await conn.commit()
        except Exception as e:
            logging.error(f"Error inserting market depth: {str(e)}")
            
    async def close(self):
        """Close all connections in the pool"""
        while not self._connection_pool.empty():
            try:
                conn = self._connection_pool.get_nowait()
                await conn.close()
            except asyncio.QueueEmpty:
                break
        self._initialized = False
        logging.info("Async database manager closed")
