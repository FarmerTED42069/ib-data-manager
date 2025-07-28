"""
Database Manager
Handles SQLite database operations for storing IB data
"""

import sqlite3
import pandas as pd
from datetime import datetime
import logging
import os

class DataManager:
    def __init__(self, db_path="ib_data.db"):
        self.db_path = db_path
        self.setup_database()
        
    def setup_database(self):
        """Create database tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Historical data table
                cursor.execute("""
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
                cursor.execute("""
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
                
                # Market depth (Level 2) table
                cursor.execute("""
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
                
                # Account info table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS account_info (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        account_id TEXT,
                        key TEXT NOT NULL,
                        value TEXT,
                        currency TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Positions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS positions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        account TEXT,
                        symbol TEXT NOT NULL,
                        position REAL,
                        avg_cost REAL,
                        market_price REAL,
                        market_value REAL,
                        unrealized_pnl REAL,
                        realized_pnl REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Orders table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_id INTEGER,
                        symbol TEXT NOT NULL,
                        action TEXT,
                        quantity REAL,
                        order_type TEXT,
                        limit_price REAL,
                        stop_price REAL,
                        status TEXT,
                        filled REAL,
                        remaining REAL,
                        avg_fill_price REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Create comprehensive indexes for better query performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_historical_symbol_date ON historical_data(symbol, date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_realtime_symbol_time ON realtime_quotes(symbol, timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_depth_symbol_time ON market_depth(symbol, timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol, timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_symbol_status ON orders(symbol, status, timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_account_key ON account_info(key, timestamp)")
                
                # Create unique constraints to prevent duplicate data
                cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS unique_historical_symbol_date ON historical_data(symbol, date)")
                cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS unique_order_id ON orders(order_id) WHERE order_id IS NOT NULL")
                
                conn.commit()
                logging.info("Database setup completed")
                
        except Exception as e:
            logging.error(f"Database setup error: {str(e)}")
            
    def save_historical_data(self, symbol, bars):
        """Save historical data to database using batch operations for better performance"""
        if not bars:
            return
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Prepare data for batch insert
                data_rows = [
                    (
                        symbol,
                        bar.date,
                        bar.open,
                        bar.high,
                        bar.low,
                        bar.close,
                        bar.volume,
                        bar.average,
                        bar.barCount
                    )
                    for bar in bars
                ]
                
                # Use executemany for batch insert - much faster than individual inserts
                cursor.executemany("""
                    INSERT INTO historical_data 
                    (symbol, date, open, high, low, close, volume, average, bar_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, data_rows)
                    
                conn.commit()
                logging.info(f"Batch saved {len(bars)} historical bars for {symbol}")
                
        except Exception as e:
            logging.error(f"Error saving historical data: {str(e)}")
            
    def save_realtime_quote(self, symbol, ticker):
        """Save real-time quote to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO realtime_quotes 
                    (symbol, timestamp, bid, bid_size, ask, ask_size, last, last_size, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol,
                    datetime.now(),
                    ticker.bid,
                    ticker.bidSize,
                    ticker.ask,
                    ticker.askSize,
                    ticker.last,
                    ticker.lastSize,
                    ticker.volume
                ))
                
                conn.commit()
                
        except Exception as e:
            logging.error(f"Error saving real-time quote: {str(e)}")
            
    def save_account_info(self, account_info):
        """Save account information to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for key, value in account_info.items():
                    cursor.execute("""
                        INSERT INTO account_info (key, value)
                        VALUES (?, ?)
                    """, (key, value))
                    
                conn.commit()
                logging.info("Saved account information")
                
        except Exception as e:
            logging.error(f"Error saving account info: {str(e)}")
            
    def get_historical_data(self, symbol, start_date=None, end_date=None):
        """Retrieve historical data from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM historical_data WHERE symbol = ?"
                params = [symbol]
                
                if start_date:
                    query += " AND date >= ?"
                    params.append(start_date)
                    
                if end_date:
                    query += " AND date <= ?"
                    params.append(end_date)
                    
                query += " ORDER BY date"
                
                df = pd.read_sql_query(query, conn, params=params)
                return df
                
        except Exception as e:
            logging.error(f"Error retrieving historical data: {str(e)}")
            return None
            
    def get_all_symbols(self):
        """Get list of all symbols in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT symbol FROM historical_data")
                symbols = [row[0] for row in cursor.fetchall()]
                return symbols
                
        except Exception as e:
            logging.error(f"Error getting symbols: {str(e)}")
            return []
            
    def get_all_historical_data(self):
        """Get all historical data for database viewer"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, symbol, date, open, high, low, close, volume 
                    FROM historical_data 
                    ORDER BY symbol, date DESC 
                    LIMIT 1000
                """)
                return cursor.fetchall()
                
        except Exception as e:
            logging.error(f"Error getting all historical data: {str(e)}")
            return []
            
    def get_all_realtime_quotes(self):
        """Get all real-time quotes for database viewer"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, symbol, timestamp, bid, ask, last, volume 
                    FROM realtime_quotes 
                    ORDER BY timestamp DESC 
                    LIMIT 1000
                """)
                return cursor.fetchall()
                
        except Exception as e:
            logging.error(f"Error getting all real-time quotes: {str(e)}")
            return []
            
    def export_to_csv(self, filename, table="historical_data"):
        """Export data to CSV file"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if table == "historical_data":
                    df = pd.read_sql_query("SELECT * FROM historical_data ORDER BY symbol, date", conn)
                elif table == "realtime_quotes":
                    df = pd.read_sql_query("SELECT * FROM realtime_quotes ORDER BY symbol, timestamp", conn)
                else:
                    raise ValueError(f"Unknown table: {table}")
                    
                df.to_csv(filename, index=False)
                logging.info(f"Exported {table} to {filename}")
                
        except Exception as e:
            logging.error(f"Error exporting to CSV: {str(e)}")
            raise
            
    def get_latest_price(self, symbol):
        """Get latest price for a symbol"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Try real-time quotes first
                cursor.execute("""
                    SELECT last FROM realtime_quotes 
                    WHERE symbol = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """, (symbol,))
                
                result = cursor.fetchone()
                if result:
                    return result[0]
                    
                # Fall back to historical data
                cursor.execute("""
                    SELECT close FROM historical_data 
                    WHERE symbol = ? 
                    ORDER BY date DESC 
                    LIMIT 1
                """, (symbol,))
                
                result = cursor.fetchone()
                if result:
                    return result[0]
                    
                return None
                
        except Exception as e:
            logging.error(f"Error getting latest price: {str(e)}")
            return None
            
    def get_price_range(self, symbol, days=30):
        """Get price range for a symbol over specified days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT MIN(low) as min_price, MAX(high) as max_price 
                    FROM historical_data 
                    WHERE symbol = ? 
                    AND date >= datetime('now', ?) 
                """, (symbol, f'-{days} days'))
                
                result = cursor.fetchone()
                if result:
                    return {'min': result[0], 'max': result[1]}
                    
                return None
                
        except Exception as e:
            logging.error(f"Error getting price range: {str(e)}")
            return None
            
    def cleanup_old_data(self, days_to_keep=30):
        """Clean up old data from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clean up old real-time quotes
                cursor.execute("""
                    DELETE FROM realtime_quotes 
                    WHERE timestamp < datetime('now', ?)
                """, (f'-{days_to_keep} days',))
                
                # Clean up old account info
                cursor.execute("""
                    DELETE FROM account_info 
                    WHERE timestamp < datetime('now', ?)
                """, (f'-{days_to_keep} days',))
                
                conn.commit()
                logging.info(f"Cleaned up data older than {days_to_keep} days")
                
        except Exception as e:
            logging.error(f"Error cleaning up old data: {str(e)}")

    def insert_market_depth(self, symbol, timestamp, side, position, price, size, market_maker, operation):
        """Insert a market depth (Level 2) record"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO market_depth (symbol, timestamp, side, position, price, size, market_maker, operation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, timestamp, side, position, price, size, market_maker, operation))
                conn.commit()
        except Exception as e:
            logging.error(f"Error inserting market depth: {str(e)}")

    def get_symbol_statistics(self, symbol):
        """Get statistics for a symbol"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query("""
                    SELECT date, open, high, low, close, volume 
                    FROM historical_data 
                    WHERE symbol = ? 
                    ORDER BY date
                """, conn, params=(symbol,))
                
                if df.empty:
                    return None
                    
                stats = {
                    'count': len(df),
                    'first_date': df['date'].min(),
                    'last_date': df['date'].max(),
                    'min_price': df['low'].min(),
                    'max_price': df['high'].max(),
                    'avg_price': df['close'].mean(),
                    'avg_volume': df['volume'].mean(),
                    'total_volume': df['volume'].sum()
                }
                
                return stats
                
        except Exception as e:
            logging.error(f"Error getting symbol statistics: {str(e)}")
            return None

# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create database manager
    db = DataManager()
    
    # Test database operations
    print("Database setup completed")
    print(f"Database file: {db.db_path}")
    
    # Example: Get all symbols
    symbols = db.get_all_symbols()
    print(f"Symbols in database: {symbols}")
    
    # Example: Get latest price
    if symbols:
        symbol = symbols[0]
        price = db.get_latest_price(symbol)
        print(f"Latest price for {symbol}: {price}")
        
        # Get statistics
        stats = db.get_symbol_statistics(symbol)
        if stats:
            print(f"Statistics for {symbol}:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
