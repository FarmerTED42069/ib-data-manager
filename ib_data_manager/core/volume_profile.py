"""
Enhanced Volume Profile and Level 2 Analysis System
Professional-grade market microstructure analysis for volume profile trading
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable
import sqlite3


@dataclass
class TickData:
    """Individual tick data point"""
    timestamp: datetime
    price: float
    size: int
    side: str  # 'buy', 'sell', 'unknown'
    exchange: str = ""
    conditions: str = ""


@dataclass
class DOMLevel:
    """Level 2 order book level"""
    price: float
    size: int
    market_maker: str = ""
    orders: int = 1


@dataclass
class OrderBookSnapshot:
    """Complete order book snapshot"""
    timestamp: datetime
    symbol: str
    bids: List[DOMLevel]
    asks: List[DOMLevel]
    spread: float = 0.0
    mid_price: float = 0.0
    
    def __post_init__(self):
        if self.bids and self.asks:
            self.spread = self.asks[0].price - self.bids[0].price
            self.mid_price = (self.asks[0].price + self.bids[0].price) / 2


@dataclass
class VolumeProfileLevel:
    """Volume profile price level"""
    price: float
    volume: int = 0
    buy_volume: int = 0
    sell_volume: int = 0
    tick_count: int = 0
    delta: int = 0  # buy_volume - sell_volume
    
    def __post_init__(self):
        self.delta = self.buy_volume - self.sell_volume


@dataclass
class VolumeProfile:
    """Complete volume profile for a time period"""
    symbol: str
    start_time: datetime
    end_time: datetime
    levels: Dict[float, VolumeProfileLevel] = field(default_factory=dict)
    total_volume: int = 0
    poc_price: float = 0.0  # Point of Control
    value_area_high: float = 0.0
    value_area_low: float = 0.0
    value_area_volume: int = 0
    
    def calculate_metrics(self):
        """Calculate volume profile metrics"""
        if not self.levels:
            return
            
        # Total volume
        self.total_volume = sum(level.volume for level in self.levels.values())
        
        # Point of Control (highest volume price)
        if self.levels:
            poc_level = max(self.levels.values(), key=lambda x: x.volume)
            self.poc_price = poc_level.price
        
        # Value Area (70% of volume around POC)
        self._calculate_value_area()
    
    def _calculate_value_area(self):
        """Calculate value area (70% of volume)"""
        if not self.levels:
            return
            
        target_volume = self.total_volume * 0.70
        sorted_levels = sorted(self.levels.items(), key=lambda x: x[1].volume, reverse=True)
        
        accumulated_volume = 0
        value_area_prices = []
        
        for price, level in sorted_levels:
            accumulated_volume += level.volume
            value_area_prices.append(price)
            if accumulated_volume >= target_volume:
                break
        
        if value_area_prices:
            self.value_area_high = max(value_area_prices)
            self.value_area_low = min(value_area_prices)
            self.value_area_volume = accumulated_volume


class EnhancedTickCapture:
    """Enhanced tick-by-tick data capture and analysis system"""
    
    def __init__(self, db_path: str = "ib_data.db"):
        self.db_path = db_path
        self.active_captures: Dict[str, bool] = {}
        self.tick_buffers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.order_books: Dict[str, OrderBookSnapshot] = {}
        self.volume_profiles: Dict[str, VolumeProfile] = {}
        self.callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        # Performance metrics
        self.tick_counts: Dict[str, int] = defaultdict(int)
        self.last_update: Dict[str, datetime] = {}
        
        # Initialize database
        self._init_enhanced_database()
    
    def _init_enhanced_database(self):
        """Initialize enhanced database schema for tick data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Enhanced tick data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tick_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    price REAL NOT NULL,
                    size INTEGER NOT NULL,
                    side TEXT NOT NULL,
                    exchange TEXT,
                    conditions TEXT,
                    microseconds INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Order book snapshots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_book_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    bid_prices TEXT NOT NULL,
                    bid_sizes TEXT NOT NULL,
                    ask_prices TEXT NOT NULL,
                    ask_sizes TEXT NOT NULL,
                    spread REAL,
                    mid_price REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Volume profile table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS volume_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME NOT NULL,
                    price REAL NOT NULL,
                    volume INTEGER NOT NULL,
                    buy_volume INTEGER NOT NULL,
                    sell_volume INTEGER NOT NULL,
                    tick_count INTEGER NOT NULL,
                    delta INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Time and sales table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS time_and_sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    price REAL NOT NULL,
                    size INTEGER NOT NULL,
                    side TEXT NOT NULL,
                    cumulative_volume INTEGER,
                    vwap REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create performance indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_tick_symbol_timestamp ON tick_data (symbol, timestamp);",
                "CREATE INDEX IF NOT EXISTS idx_tick_price ON tick_data (price);",
                "CREATE INDEX IF NOT EXISTS idx_orderbook_symbol_timestamp ON order_book_snapshots (symbol, timestamp);",
                "CREATE INDEX IF NOT EXISTS idx_volume_profile_symbol_time ON volume_profiles (symbol, start_time, end_time);",
                "CREATE INDEX IF NOT EXISTS idx_time_sales_symbol_timestamp ON time_and_sales (symbol, timestamp);"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            conn.commit()
            conn.close()
            logging.info("✅ Enhanced tick capture database initialized")
            
        except Exception as e:
            logging.error(f"❌ Error initializing enhanced database: {str(e)}")
    
    def _get_security_info(self, symbol: str) -> tuple:
        """Get security type and exchange for a symbol"""
        symbol = symbol.upper()
        
        # Futures mapping
        futures_map = {
            'ES': ('FUT', 'CME'),      # S&P 500 E-mini
            'NQ': ('FUT', 'CME'),      # NASDAQ 100 E-mini
            'YM': ('FUT', 'CBOT'),     # Dow Jones E-mini
            'RTY': ('FUT', 'CME'),     # Russell 2000 E-mini
            'CL': ('FUT', 'NYMEX'),    # Crude Oil
            'GC': ('FUT', 'COMEX'),    # Gold
            'SI': ('FUT', 'COMEX'),    # Silver
            'ZN': ('FUT', 'CBOT'),     # 10-Year Treasury Note
            'ZB': ('FUT', 'CBOT'),     # 30-Year Treasury Bond
            'ZF': ('FUT', 'CBOT'),     # 5-Year Treasury Note
            'ZS': ('FUT', 'CBOT'),     # Soybeans
            'ZC': ('FUT', 'CBOT'),     # Corn
            'ZW': ('FUT', 'CBOT'),     # Wheat
        }
        
        # Check if it's a known futures contract
        if symbol in futures_map:
            return futures_map[symbol]
        
        # Default to stock with SMART routing
        return ('STK', 'SMART')
    
    async def start_tick_capture(self, symbol: str, ib_connector, 
                                tick_callback: Optional[Callable] = None,
                                orderbook_callback: Optional[Callable] = None):
        """Start enhanced tick capture for a symbol"""
        try:
            print(f"🔍 DEBUG: EnhancedTickCapture.start_tick_capture called for {symbol}")
            
            if symbol in self.active_captures and self.active_captures[symbol]:
                print(f"⚠️ DEBUG: Tick capture already active for {symbol}")
                logging.warning(f"Tick capture already active for {symbol}")
                return True
            
            print(f"🔍 DEBUG: Registering callbacks for {symbol}")
            # Register callbacks
            if tick_callback:
                self.callbacks[f"{symbol}_tick"].append(tick_callback)
                print(f"✅ DEBUG: Tick callback registered for {symbol}")
            if orderbook_callback:
                self.callbacks[f"{symbol}_orderbook"].append(orderbook_callback)
                print(f"✅ DEBUG: Orderbook callback registered for {symbol}")
            
            # Determine security type and exchange based on symbol
            sec_type, exchange = self._get_security_info(symbol)
            print(f"🔍 DEBUG: Detected sec_type={sec_type}, exchange={exchange} for {symbol}")
            
            # Use the existing AsyncIBConnector methods that handle futures properly
            print(f"🔍 DEBUG: Using AsyncIBConnector.start_realtime_quotes for {symbol}")
            quote_ticker = await ib_connector.start_realtime_quotes(
                symbol=symbol,
                sec_type=sec_type,
                exchange=exchange,
                callback=lambda ticker: asyncio.create_task(self._process_quote_update(symbol, ticker))
            )
            print(f"🔍 DEBUG: start_realtime_quotes returned: {quote_ticker}")
            
            # Also try market depth
            print(f"🔍 DEBUG: Using AsyncIBConnector.start_market_depth for {symbol}")
            depth_ticker = await ib_connector.start_market_depth(
                symbol=symbol,
                sec_type=sec_type,
                exchange=exchange,
                callback=lambda ticker: asyncio.create_task(self._process_market_depth(symbol, ticker))
            )
            print(f"🔍 DEBUG: start_market_depth returned: {depth_ticker}")
            
            if depth_ticker:
                self.active_captures[symbol] = True
                self.last_update[symbol] = datetime.now()
                
                # Initialize volume profile for current session
                now = datetime.now()
                session_start = now.replace(hour=9, minute=30, second=0, microsecond=0)
                if now < session_start:
                    session_start -= timedelta(days=1)
                
                self.volume_profiles[symbol] = VolumeProfile(
                    symbol=symbol,
                    start_time=session_start,
                    end_time=session_start + timedelta(hours=6, minutes=30)
                )
                
                logging.info(f"✅ Enhanced tick capture started for {symbol}")
                return True
            else:
                logging.error(f"❌ Failed to start market depth for {symbol}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Error starting tick capture for {symbol}: {str(e)}")
            return False
    
    async def _process_market_depth(self, symbol: str, ticker):
        """Process market depth updates and extract tick data"""
        try:
            print(f"🔍 DEBUG: _process_market_depth called for {symbol}, ticker: {ticker}")
            now = datetime.now()
            self.last_update[symbol] = now
            
            # Extract order book data
            bids = []
            asks = []
            
            if hasattr(ticker, 'domBids') and ticker.domBids:
                for bid in ticker.domBids[:10]:  # Top 10 levels
                    bids.append(DOMLevel(
                        price=float(bid.price),
                        size=int(bid.size),
                        market_maker=getattr(bid, 'marketMaker', '')
                    ))
            
            if hasattr(ticker, 'domAsks') and ticker.domAsks:
                for ask in ticker.domAsks[:10]:  # Top 10 levels
                    asks.append(DOMLevel(
                        price=float(ask.price),
                        size=int(ask.size),
                        market_maker=getattr(ask, 'marketMaker', '')
                    ))
            
            # Create order book snapshot
            if bids and asks:
                snapshot = OrderBookSnapshot(
                    timestamp=now,
                    symbol=symbol,
                    bids=bids,
                    asks=asks
                )
                
                self.order_books[symbol] = snapshot
                
                # Save to database
                await self._save_order_book_snapshot(snapshot)
                
                # Trigger callbacks
                for callback in self.callbacks[f"{symbol}_orderbook"]:
                    try:
                        await callback(snapshot)
                    except Exception as e:
                        logging.error(f"Error in orderbook callback: {e}")
            
            # Process tick data from last trade
            if hasattr(ticker, 'last') and ticker.last and ticker.last > 0:
                tick = TickData(
                    timestamp=now,
                    price=float(ticker.last),
                    size=int(getattr(ticker, 'lastSize', 0)),
                    side=self._determine_trade_side(ticker, symbol)
                )
                
                # Add to buffer
                self.tick_buffers[symbol].append(tick)
                self.tick_counts[symbol] += 1
                
                # Update volume profile
                await self._update_volume_profile(symbol, tick)
                
                # Save tick data
                await self._save_tick_data(tick, symbol)
                
                # Trigger callbacks
                for callback in self.callbacks[f"{symbol}_tick"]:
                    try:
                        await callback(tick)
                    except Exception as e:
                        logging.error(f"Error in tick callback: {e}")
                        
        except Exception as e:
            logging.error(f"❌ Error processing market depth for {symbol}: {str(e)}")
    
    async def _process_quote_update(self, symbol: str, ticker):
        """Process regular quote updates for basic tick data"""
        try:
            print(f"📊 DEBUG: _process_quote_update called for {symbol}, ticker: {ticker}")
            
            # Extract basic tick data from ticker
            if hasattr(ticker, 'last') and ticker.last and ticker.last > 0:
                now = datetime.now()
                
                # Create tick data
                tick = TickData(
                    timestamp=now,
                    price=float(ticker.last),
                    size=int(getattr(ticker, 'lastSize', 0)),
                    side='unknown',  # We don't know buy/sell from basic quotes
                    exchange=getattr(ticker.contract, 'exchange', '')
                )
                
                print(f"📊 DEBUG: Created tick: {tick}")
                
                # Add to buffer
                self.tick_buffers[symbol].append(tick)
                self.tick_counts[symbol] += 1
                self.last_update[symbol] = now
                
                # Call tick callbacks
                for callback in self.callbacks.get(f"{symbol}_tick", []):
                    try:
                        await callback(tick)
                    except Exception as e:
                        logging.error(f"Error in tick callback: {e}")
                
                # Update volume profile
                await self._update_volume_profile(symbol, tick)
                
        except Exception as e:
            logging.error(f"❌ Error processing quote update for {symbol}: {str(e)}")
    
    def _determine_trade_side(self, ticker, symbol: str) -> str:
        """Determine if trade was buy or sell based on order book"""
        try:
            if not hasattr(ticker, 'last') or not ticker.last:
                return 'unknown'
            
            last_price = float(ticker.last)
            
            # Get current order book
            if symbol in self.order_books:
                snapshot = self.order_books[symbol]
                if snapshot.bids and snapshot.asks:
                    mid_price = snapshot.mid_price
                    
                    # Simple logic: above mid = buy, below mid = sell
                    if last_price >= mid_price:
                        return 'buy'
                    else:
                        return 'sell'
            
            return 'unknown'
            
        except Exception as e:
            logging.error(f"Error determining trade side: {e}")
            return 'unknown'
    
    async def _update_volume_profile(self, symbol: str, tick: TickData):
        """Update volume profile with new tick data"""
        try:
            if symbol not in self.volume_profiles:
                return
            
            profile = self.volume_profiles[symbol]
            price = tick.price
            
            # Round price to nearest tick (assuming 0.01 for stocks)
            rounded_price = round(price, 2)
            
            if rounded_price not in profile.levels:
                profile.levels[rounded_price] = VolumeProfileLevel(price=rounded_price)
            
            level = profile.levels[rounded_price]
            level.volume += tick.size
            level.tick_count += 1
            
            if tick.side == 'buy':
                level.buy_volume += tick.size
            elif tick.side == 'sell':
                level.sell_volume += tick.size
            
            level.delta = level.buy_volume - level.sell_volume
            
            # Recalculate profile metrics periodically
            if self.tick_counts[symbol] % 100 == 0:  # Every 100 ticks
                profile.calculate_metrics()
                
        except Exception as e:
            logging.error(f"Error updating volume profile: {e}")
    
    async def _save_tick_data(self, tick: TickData, symbol: str):
        """Save tick data to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO tick_data 
                (symbol, timestamp, price, size, side, exchange, conditions, microseconds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol,
                tick.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                tick.price,
                tick.size,
                tick.side,
                tick.exchange,
                tick.conditions,
                tick.timestamp.microsecond
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error saving tick data: {e}")
    
    async def _save_order_book_snapshot(self, snapshot: OrderBookSnapshot):
        """Save order book snapshot to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert order book to strings
            bid_prices = ','.join([str(bid.price) for bid in snapshot.bids])
            bid_sizes = ','.join([str(bid.size) for bid in snapshot.bids])
            ask_prices = ','.join([str(ask.price) for ask in snapshot.asks])
            ask_sizes = ','.join([str(ask.size) for ask in snapshot.asks])
            
            cursor.execute("""
                INSERT INTO order_book_snapshots 
                (symbol, timestamp, bid_prices, bid_sizes, ask_prices, ask_sizes, spread, mid_price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot.symbol,
                snapshot.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                bid_prices,
                bid_sizes,
                ask_prices,
                ask_sizes,
                snapshot.spread,
                snapshot.mid_price
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error saving order book snapshot: {e}")
    
    def get_volume_profile(self, symbol: str) -> Optional[VolumeProfile]:
        """Get current volume profile for symbol"""
        return self.volume_profiles.get(symbol)
    
    def get_tick_statistics(self, symbol: str) -> Dict:
        """Get tick capture statistics"""
        return {
            'tick_count': self.tick_counts.get(symbol, 0),
            'last_update': self.last_update.get(symbol),
            'buffer_size': len(self.tick_buffers.get(symbol, [])),
            'active': self.active_captures.get(symbol, False)
        }
    
    def stop_tick_capture(self, symbol: str):
        """Stop tick capture for symbol"""
        self.active_captures[symbol] = False
        logging.info(f"✅ Stopped tick capture for {symbol}")
    
    def get_recent_ticks(self, symbol: str, count: int = 100) -> List[TickData]:
        """Get recent tick data"""
        if symbol in self.tick_buffers:
            return list(self.tick_buffers[symbol])[-count:]
        return []


# Convenience functions for volume profile analysis
def calculate_session_volume_profile(symbol: str, date: str, db_path: str = "ib_data.db") -> Optional[VolumeProfile]:
    """Calculate volume profile for a trading session"""
    try:
        conn = sqlite3.connect(db_path)
        
        # Get tick data for the session
        query = """
            SELECT timestamp, price, size, side 
            FROM tick_data 
            WHERE symbol = ? AND date(timestamp) = ?
            ORDER BY timestamp
        """
        
        df = pd.read_sql_query(query, conn, params=(symbol, date))
        conn.close()
        
        if df.empty:
            return None
        
        # Create volume profile
        start_time = pd.to_datetime(df['timestamp'].iloc[0])
        end_time = pd.to_datetime(df['timestamp'].iloc[-1])
        
        profile = VolumeProfile(
            symbol=symbol,
            start_time=start_time,
            end_time=end_time
        )
        
        # Process each tick
        for _, row in df.iterrows():
            price = round(float(row['price']), 2)
            size = int(row['size'])
            side = row['side']
            
            if price not in profile.levels:
                profile.levels[price] = VolumeProfileLevel(price=price)
            
            level = profile.levels[price]
            level.volume += size
            level.tick_count += 1
            
            if side == 'buy':
                level.buy_volume += size
            elif side == 'sell':
                level.sell_volume += size
            
            level.delta = level.buy_volume - level.sell_volume
        
        # Calculate metrics
        profile.calculate_metrics()
        
        return profile
        
    except Exception as e:
        logging.error(f"Error calculating session volume profile: {e}")
        return None


def export_volume_profile_csv(profile: VolumeProfile, filename: str):
    """Export volume profile to CSV"""
    try:
        data = []
        for price, level in sorted(profile.levels.items()):
            data.append({
                'price': price,
                'volume': level.volume,
                'buy_volume': level.buy_volume,
                'sell_volume': level.sell_volume,
                'delta': level.delta,
                'tick_count': level.tick_count
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        logging.info(f"✅ Volume profile exported to {filename}")
        
    except Exception as e:
        logging.error(f"Error exporting volume profile: {e}")
