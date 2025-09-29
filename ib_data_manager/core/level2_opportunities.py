"""
Level 2 Market Depth and Tick Data Opportunity Detection System
Focused on identifying actionable trading opportunities from order book and tick data
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Any
import sqlite3
from enum import Enum


class OpportunityType(Enum):
    """Types of trading opportunities detected"""
    LARGE_ORDER_IMBALANCE = "large_order_imbalance"
    ICEBERG_ORDER = "iceberg_order"
    SWEEP_ACTIVITY = "sweep_activity"
    VOLUME_SPIKE = "volume_spike"
    SPREAD_COMPRESSION = "spread_compression"
    HIDDEN_LIQUIDITY = "hidden_liquidity"
    MOMENTUM_SHIFT = "momentum_shift"
    SUPPORT_RESISTANCE = "support_resistance"


@dataclass
class OpportunityAlert:
    """Trading opportunity alert"""
    timestamp: datetime
    symbol: str
    opportunity_type: OpportunityType
    confidence: float  # 0.0 to 1.0
    price_level: float
    description: str
    data: Dict[str, Any] = field(default_factory=dict)
    action_suggested: str = ""  # "BUY", "SELL", "WATCH"


@dataclass
class Level2Snapshot:
    """Enhanced Level 2 order book snapshot"""
    timestamp: datetime
    symbol: str
    bids: List[Dict[str, Any]]
    asks: List[Dict[str, Any]]
    spread: float
    mid_price: float
    total_bid_size: int
    total_ask_size: int
    imbalance_ratio: float  # bid_size / ask_size
    
    def __post_init__(self):
        if self.bids and self.asks:
            self.total_bid_size = sum(bid['size'] for bid in self.bids)
            self.total_ask_size = sum(ask['size'] for ask in self.asks)
            self.imbalance_ratio = self.total_bid_size / max(self.total_ask_size, 1)


class Level2OpportunityDetector:
    """Advanced Level 2 opportunity detection system"""
    
    def __init__(self, db_path: str = "ib_data.db"):
        self.db_path = db_path
        self.active_symbols: Dict[str, bool] = {}
        self.order_book_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.tick_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.opportunity_callbacks: List[Callable] = []
        
        # Detection parameters
        self.imbalance_threshold = 3.0  # 3:1 ratio triggers alert
        self.volume_spike_threshold = 5.0  # 5x average volume
        self.spread_compression_threshold = 0.5  # 50% spread reduction
        
        # Performance tracking
        self.opportunities_detected = 0
        self.last_detection_time = {}
        
        self._init_database()
    
    def _init_database(self):
        """Initialize opportunity tracking database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS level2_opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    symbol TEXT NOT NULL,
                    opportunity_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    price_level REAL NOT NULL,
                    description TEXT NOT NULL,
                    action_suggested TEXT,
                    data_json TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_opportunities_symbol_time 
                ON level2_opportunities (symbol, timestamp);
            """)
            
            conn.commit()
            conn.close()
            logging.info("Level 2 opportunities database initialized")
            
        except Exception as e:
            logging.error(f"Error initializing opportunities database: {str(e)}")
    
    def add_opportunity_callback(self, callback: Callable):
        """Add callback for opportunity alerts"""
        self.opportunity_callbacks.append(callback)
    
    async def process_level2_update(self, symbol: str, ticker):
        """Process Level 2 market depth updates for opportunity detection"""
        try:
            # Create Level 2 snapshot
            snapshot = self._create_level2_snapshot(symbol, ticker)
            if not snapshot:
                return
            
            # Store in history
            self.order_book_history[symbol].append(snapshot)
            
            # Run opportunity detection algorithms
            opportunities = await self._detect_opportunities(symbol, snapshot)
            
            # Process any detected opportunities
            for opportunity in opportunities:
                await self._handle_opportunity(opportunity)
                
        except Exception as e:
            logging.error(f"Error processing Level 2 update for {symbol}: {str(e)}")
    
    def _create_level2_snapshot(self, symbol: str, ticker) -> Optional[Level2Snapshot]:
        """Create Level 2 snapshot from ticker data"""
        try:
            bids = []
            asks = []
            
            # Extract bid data
            if hasattr(ticker, 'domBids') and ticker.domBids:
                for bid in ticker.domBids[:10]:
                    bids.append({
                        'price': float(bid.price),
                        'size': int(bid.size),
                        'market_maker': getattr(bid, 'marketMaker', ''),
                        'orders': getattr(bid, 'orders', 1)
                    })
            
            # Extract ask data
            if hasattr(ticker, 'domAsks') and ticker.domAsks:
                for ask in ticker.domAsks[:10]:
                    asks.append({
                        'price': float(ask.price),
                        'size': int(ask.size),
                        'market_maker': getattr(ask, 'marketMaker', ''),
                        'orders': getattr(ask, 'orders', 1)
                    })
            
            if not bids or not asks:
                return None
            
            # Calculate metrics
            spread = asks[0]['price'] - bids[0]['price']
            mid_price = (asks[0]['price'] + bids[0]['price']) / 2
            
            return Level2Snapshot(
                timestamp=datetime.now(),
                symbol=symbol,
                bids=bids,
                asks=asks,
                spread=spread,
                mid_price=mid_price,
                total_bid_size=0,  # Will be calculated in __post_init__
                total_ask_size=0,
                imbalance_ratio=0.0
            )
            
        except Exception as e:
            logging.error(f"Error creating Level 2 snapshot: {e}")
            return None
    
    async def _detect_opportunities(self, symbol: str, snapshot: Level2Snapshot) -> List[OpportunityAlert]:
        """Run all opportunity detection algorithms"""
        opportunities = []
        
        # 1. Order Imbalance Detection
        imbalance_opp = self._detect_order_imbalance(symbol, snapshot)
        if imbalance_opp:
            opportunities.append(imbalance_opp)
        
        # 2. Spread Compression Detection
        spread_opp = self._detect_spread_compression(symbol, snapshot)
        if spread_opp:
            opportunities.append(spread_opp)
        
        # 3. Large Order Detection
        large_order_opp = self._detect_large_orders(symbol, snapshot)
        if large_order_opp:
            opportunities.append(large_order_opp)
        
        # 4. Hidden Liquidity Detection
        hidden_liq_opp = self._detect_hidden_liquidity(symbol, snapshot)
        if hidden_liq_opp:
            opportunities.append(hidden_liq_opp)
        
        return opportunities
    
    def _detect_order_imbalance(self, symbol: str, snapshot: Level2Snapshot) -> Optional[OpportunityAlert]:
        """Detect significant order book imbalances"""
        try:
            if snapshot.imbalance_ratio > self.imbalance_threshold:
                # Heavy bid side - potential upward pressure
                return OpportunityAlert(
                    timestamp=snapshot.timestamp,
                    symbol=symbol,
                    opportunity_type=OpportunityType.LARGE_ORDER_IMBALANCE,
                    confidence=min(snapshot.imbalance_ratio / 10.0, 1.0),
                    price_level=snapshot.mid_price,
                    description=f"Heavy bid imbalance: {snapshot.imbalance_ratio:.2f}:1 ratio",
                    action_suggested="BUY",
                    data={
                        'bid_size': snapshot.total_bid_size,
                        'ask_size': snapshot.total_ask_size,
                        'imbalance_ratio': snapshot.imbalance_ratio
                    }
                )
            elif snapshot.imbalance_ratio < (1.0 / self.imbalance_threshold):
                # Heavy ask side - potential downward pressure
                return OpportunityAlert(
                    timestamp=snapshot.timestamp,
                    symbol=symbol,
                    opportunity_type=OpportunityType.LARGE_ORDER_IMBALANCE,
                    confidence=min((1.0 / snapshot.imbalance_ratio) / 10.0, 1.0),
                    price_level=snapshot.mid_price,
                    description=f"Heavy ask imbalance: 1:{1/snapshot.imbalance_ratio:.2f} ratio",
                    action_suggested="SELL",
                    data={
                        'bid_size': snapshot.total_bid_size,
                        'ask_size': snapshot.total_ask_size,
                        'imbalance_ratio': snapshot.imbalance_ratio
                    }
                )
            return None
        except Exception as e:
            logging.error(f"Error detecting order imbalance: {e}")
            return None
    
    def _detect_spread_compression(self, symbol: str, snapshot: Level2Snapshot) -> Optional[OpportunityAlert]:
        """Detect spread compression indicating potential breakout"""
        try:
            history = self.order_book_history[symbol]
            if len(history) < 10:
                return None
            
            # Calculate average spread over last 10 snapshots
            recent_spreads = [s.spread for s in list(history)[-10:]]
            avg_spread = np.mean(recent_spreads)
            
            if avg_spread > 0 and snapshot.spread < (avg_spread * self.spread_compression_threshold):
                return OpportunityAlert(
                    timestamp=snapshot.timestamp,
                    symbol=symbol,
                    opportunity_type=OpportunityType.SPREAD_COMPRESSION,
                    confidence=1.0 - (snapshot.spread / avg_spread),
                    price_level=snapshot.mid_price,
                    description=f"Spread compressed {((1 - snapshot.spread/avg_spread)*100):.1f}%",
                    action_suggested="WATCH",
                    data={
                        'current_spread': snapshot.spread,
                        'average_spread': avg_spread,
                        'compression_ratio': snapshot.spread / avg_spread
                    }
                )
            return None
        except Exception as e:
            logging.error(f"Error detecting spread compression: {e}")
            return None
    
    def _detect_large_orders(self, symbol: str, snapshot: Level2Snapshot) -> Optional[OpportunityAlert]:
        """Detect unusually large orders in the book"""
        try:
            # Calculate average order size
            all_sizes = [bid['size'] for bid in snapshot.bids] + [ask['size'] for ask in snapshot.asks]
            if not all_sizes:
                return None
            
            avg_size = np.mean(all_sizes)
            max_size = max(all_sizes)
            
            # Look for orders 5x larger than average
            if max_size > (avg_size * 5):
                # Find which side has the large order
                large_bid = max((bid['size'] for bid in snapshot.bids), default=0)
                large_ask = max((ask['size'] for ask in snapshot.asks), default=0)
                
                if large_bid > large_ask:
                    side = "BID"
                    action = "BUY"
                    price = snapshot.bids[0]['price']
                else:
                    side = "ASK"
                    action = "SELL"
                    price = snapshot.asks[0]['price']
                
                return OpportunityAlert(
                    timestamp=snapshot.timestamp,
                    symbol=symbol,
                    opportunity_type=OpportunityType.ICEBERG_ORDER,
                    confidence=min(max_size / (avg_size * 10), 1.0),
                    price_level=price,
                    description=f"Large {side} order: {max_size:,} vs avg {avg_size:.0f}",
                    action_suggested=action,
                    data={
                        'large_order_size': max_size,
                        'average_size': avg_size,
                        'size_ratio': max_size / avg_size,
                        'side': side
                    }
                )
            return None
        except Exception as e:
            logging.error(f"Error detecting large orders: {e}")
            return None
    
    def _detect_hidden_liquidity(self, symbol: str, snapshot: Level2Snapshot) -> Optional[OpportunityAlert]:
        """Detect potential hidden liquidity based on order patterns"""
        try:
            # Look for consistent order sizes at multiple levels (potential iceberg)
            bid_sizes = [bid['size'] for bid in snapshot.bids[:5]]
            ask_sizes = [ask['size'] for ask in snapshot.asks[:5]]
            
            # Check for repeated sizes (iceberg pattern)
            from collections import Counter
            bid_counts = Counter(bid_sizes)
            ask_counts = Counter(ask_sizes)
            
            # Find most common size
            most_common_bid = bid_counts.most_common(1)[0] if bid_counts else (0, 0)
            most_common_ask = ask_counts.most_common(1)[0] if ask_counts else (0, 0)
            
            # If same size appears 3+ times, might be iceberg
            if most_common_bid[1] >= 3 or most_common_ask[1] >= 3:
                if most_common_bid[1] > most_common_ask[1]:
                    side = "BID"
                    size = most_common_bid[0]
                    count = most_common_bid[1]
                    action = "BUY"
                else:
                    side = "ASK"
                    size = most_common_ask[0]
                    count = most_common_ask[1]
                    action = "SELL"
                
                return OpportunityAlert(
                    timestamp=snapshot.timestamp,
                    symbol=symbol,
                    opportunity_type=OpportunityType.HIDDEN_LIQUIDITY,
                    confidence=min(count / 5.0, 1.0),
                    price_level=snapshot.mid_price,
                    description=f"Potential iceberg: {size:,} size repeated {count}x on {side}",
                    action_suggested=action,
                    data={
                        'repeated_size': size,
                        'repetition_count': count,
                        'side': side
                    }
                )
            return None
        except Exception as e:
            logging.error(f"Error detecting hidden liquidity: {e}")
            return None
    
    async def _handle_opportunity(self, opportunity: OpportunityAlert):
        """Handle detected opportunity"""
        try:
            # Save to database
            await self._save_opportunity(opportunity)
            
            # Update counters
            self.opportunities_detected += 1
            self.last_detection_time[opportunity.symbol] = opportunity.timestamp
            
            # Trigger callbacks
            for callback in self.opportunity_callbacks:
                try:
                    await callback(opportunity)
                except Exception as e:
                    logging.error(f"Error in opportunity callback: {e}")
            
            logging.info(f"OPPORTUNITY: {opportunity.opportunity_type.value} for {opportunity.symbol} "
                        f"at {opportunity.price_level:.2f} (confidence: {opportunity.confidence:.2f})")
                        
        except Exception as e:
            logging.error(f"Error handling opportunity: {e}")
    
    async def _save_opportunity(self, opportunity: OpportunityAlert):
        """Save opportunity to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            import json
            cursor.execute("""
                INSERT INTO level2_opportunities 
                (timestamp, symbol, opportunity_type, confidence, price_level, 
                 description, action_suggested, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                opportunity.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
                opportunity.symbol,
                opportunity.opportunity_type.value,
                opportunity.confidence,
                opportunity.price_level,
                opportunity.description,
                opportunity.action_suggested,
                json.dumps(opportunity.data)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error saving opportunity: {e}")
    
    def get_recent_opportunities(self, symbol: str = None, hours: int = 24) -> List[Dict]:
        """Get recent opportunities from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            since_time = datetime.now() - timedelta(hours=hours)
            
            if symbol:
                query = """
                    SELECT * FROM level2_opportunities 
                    WHERE symbol = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                """
                params = (symbol, since_time.strftime("%Y-%m-%d %H:%M:%S"))
            else:
                query = """
                    SELECT * FROM level2_opportunities 
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                """
                params = (since_time.strftime("%Y-%m-%d %H:%M:%S"),)
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            logging.error(f"Error getting recent opportunities: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detection statistics"""
        return {
            'total_opportunities': self.opportunities_detected,
            'active_symbols': len(self.active_symbols),
            'last_detections': dict(self.last_detection_time),
            'detection_parameters': {
                'imbalance_threshold': self.imbalance_threshold,
                'volume_spike_threshold': self.volume_spike_threshold,
                'spread_compression_threshold': self.spread_compression_threshold
            }
        }
