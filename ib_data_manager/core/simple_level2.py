"""
Simple Level 2 Market Depth Integration
Minimal, practical Level 2 functionality that integrates with existing AsyncIBConnector
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable
import pandas as pd


class SimpleLevel2Manager:
    """Simple Level 2 manager that works with existing AsyncIBConnector"""
    
    def __init__(self, ib_connector):
        self.ib_connector = ib_connector
        self.ib = ib_connector.ib
        self.active_depth_tickers = {}
        self.level2_callbacks = {}
        self.current_order_books = {}
        
    async def start_level2_stream(self, symbol: str, sec_type: str = "STK", 
                                 exchange: str = None, currency: str = "USD",
                                 callback: Optional[Callable] = None):
        """Start Level 2 market depth streaming - simple version"""
        try:
            # Use existing contract creation logic
            if sec_type == "FUT":
                # For futures, get front month contract
                base_contract = self.ib_connector.create_contract(symbol, sec_type, exchange, currency)
                contracts = await self.ib.reqContractDetailsAsync(base_contract)
                if contracts:
                    contract = contracts[0].contract
                else:
                    logging.error(f"No futures contracts found for {symbol}")
                    return None
            else:
                # For stocks, use existing logic
                contract = self.ib_connector.create_contract(symbol, sec_type, exchange, currency)
                qualified_contracts = await self.ib.qualifyContractsAsync(contract)
                if qualified_contracts:
                    contract = qualified_contracts[0]
                else:
                    logging.error(f"Failed to qualify contract for {symbol}")
                    return None
            
            # Request market depth
            ticker = self.ib.reqMktDepth(contract, numRows=10, isSmartDepth=True)
            
            # Store ticker
            key = f"{symbol}_{sec_type}"
            self.active_depth_tickers[key] = ticker
            
            # Set up callback if provided
            if callback:
                self.level2_callbacks[key] = callback
                ticker.updateEvent += lambda: self._process_level2_update(symbol, sec_type, ticker, callback)
            
            logging.info(f"Started Level 2 streaming for {symbol}")
            return ticker
            
        except Exception as e:
            logging.error(f"Error starting Level 2 for {symbol}: {str(e)}")
            return None
    
    def stop_level2_stream(self, symbol: str, sec_type: str = "STK"):
        """Stop Level 2 streaming"""
        try:
            key = f"{symbol}_{sec_type}"
            
            if key in self.active_depth_tickers:
                ticker = self.active_depth_tickers[key]
                self.ib.cancelMktDepth(ticker.contract, isSmartDepth=True)
                
                # Clean up
                del self.active_depth_tickers[key]
                if key in self.level2_callbacks:
                    del self.level2_callbacks[key]
                if key in self.current_order_books:
                    del self.current_order_books[key]
                
                logging.info(f"Stopped Level 2 streaming for {symbol}")
                return True
            return False
            
        except Exception as e:
            logging.error(f"Error stopping Level 2 for {symbol}: {str(e)}")
            return False
    
    def _process_level2_update(self, symbol: str, sec_type: str, ticker, callback):
        """Process Level 2 updates"""
        try:
            # Extract order book data
            order_book = self._extract_order_book(symbol, ticker)
            
            if order_book:
                # Store current order book
                key = f"{symbol}_{sec_type}"
                self.current_order_books[key] = order_book
                
                # Call callback
                if callback:
                    asyncio.create_task(callback(order_book))
                    
        except Exception as e:
            logging.error(f"Error processing Level 2 update: {str(e)}")
    
    def _extract_order_book(self, symbol: str, ticker) -> Optional[Dict]:
        """Extract order book data from ticker"""
        try:
            bids = []
            asks = []
            
            # Extract bids
            if hasattr(ticker, 'domBids') and ticker.domBids:
                for bid in ticker.domBids[:10]:
                    if bid.price > 0 and bid.size > 0:
                        bids.append({
                            'price': float(bid.price),
                            'size': int(bid.size),
                            'market_maker': getattr(bid, 'marketMaker', '')
                        })
            
            # Extract asks
            if hasattr(ticker, 'domAsks') and ticker.domAsks:
                for ask in ticker.domAsks[:10]:
                    if ask.price > 0 and ask.size > 0:
                        asks.append({
                            'price': float(ask.price),
                            'size': int(ask.size),
                            'market_maker': getattr(ask, 'marketMaker', '')
                        })
            
            if not bids or not asks:
                return None
            
            # Calculate basic metrics
            spread = asks[0]['price'] - bids[0]['price']
            mid_price = (asks[0]['price'] + bids[0]['price']) / 2
            
            return {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'bids': bids,
                'asks': asks,
                'spread': spread,
                'mid_price': mid_price,
                'best_bid': bids[0]['price'],
                'best_ask': asks[0]['price'],
                'bid_size': bids[0]['size'],
                'ask_size': asks[0]['size']
            }
            
        except Exception as e:
            logging.error(f"Error extracting order book: {str(e)}")
            return None
    
    def get_current_order_book(self, symbol: str, sec_type: str = "STK") -> Optional[Dict]:
        """Get current order book for symbol"""
        key = f"{symbol}_{sec_type}"
        return self.current_order_books.get(key)
    
    def get_active_streams(self) -> List[str]:
        """Get list of active Level 2 streams"""
        return list(self.active_depth_tickers.keys())
    
    def stop_all_streams(self):
        """Stop all Level 2 streams"""
        for key in list(self.active_depth_tickers.keys()):
            symbol, sec_type = key.split('_', 1)
            self.stop_level2_stream(symbol, sec_type)
    
    def format_order_book_for_display(self, order_book: Dict) -> str:
        """Format order book data for simple text display"""
        if not order_book:
            return "No Level 2 data available"
        
        lines = []
        lines.append(f"Level 2 Data for {order_book['symbol']}")
        lines.append(f"Time: {order_book['timestamp'].strftime('%H:%M:%S')}")
        lines.append(f"Spread: {order_book['spread']:.4f}")
        lines.append(f"Mid Price: {order_book['mid_price']:.2f}")
        lines.append("")
        
        # Format asks (highest first)
        lines.append("ASKS (Sell Orders):")
        for i, ask in enumerate(reversed(order_book['asks'][:5])):
            lines.append(f"  {ask['price']:.2f} x {ask['size']:,}")
        
        lines.append("")
        lines.append(f"--- SPREAD: {order_book['spread']:.4f} ---")
        lines.append("")
        
        # Format bids (highest first)
        lines.append("BIDS (Buy Orders):")
        for bid in order_book['bids'][:5]:
            lines.append(f"  {bid['price']:.2f} x {bid['size']:,}")
        
        return "\n".join(lines)
    
    def create_level2_dataframe(self, order_book: Dict) -> Optional[pd.DataFrame]:
        """Create pandas DataFrame from order book for analysis"""
        if not order_book:
            return None
        
        try:
            # Combine bids and asks
            data = []
            
            # Add asks
            for ask in order_book['asks']:
                data.append({
                    'side': 'ASK',
                    'price': ask['price'],
                    'size': ask['size'],
                    'market_maker': ask.get('market_maker', '')
                })
            
            # Add bids
            for bid in order_book['bids']:
                data.append({
                    'side': 'BID',
                    'price': bid['price'],
                    'size': bid['size'],
                    'market_maker': bid.get('market_maker', '')
                })
            
            df = pd.DataFrame(data)
            df['timestamp'] = order_book['timestamp']
            df['symbol'] = order_book['symbol']
            
            return df
            
        except Exception as e:
            logging.error(f"Error creating Level 2 DataFrame: {str(e)}")
            return None
