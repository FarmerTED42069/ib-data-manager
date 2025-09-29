"""
Level 2 Market Depth Extension for AsyncIBConnector
Provides market depth and tick-by-tick data streaming capabilities
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Callable, Dict, Any


class Level2Connector:
    """Level 2 market depth extension for AsyncIBConnector"""
    
    def __init__(self, ib_connector):
        self.ib_connector = ib_connector
        self.ib = ib_connector.ib
        self.active_depth = {}
        self.active_tick_streams = {}
        self.depth_callbacks = {}
        
    async def start_market_depth(self, symbol: str, sec_type: str = "STK", 
                                exchange: str = None, currency: str = "USD", 
                                callback: Optional[Callable] = None, num_rows: int = 10):
        """Start Level 2 market depth streaming"""
        try:
            # Check if already streaming depth for this symbol
            depth_key = f"{symbol}_{sec_type}_depth"
            if depth_key in self.active_depth:
                logging.info(f"Already streaming market depth for {symbol}")
                return self.active_depth[depth_key]
            
            # Get qualified contract
            qualified_contract = await self._get_qualified_contract(symbol, sec_type, exchange, currency)
            if not qualified_contract:
                return None
            
            # Request market depth (Level 2 order book)
            ticker = self.ib.reqMktDepth(qualified_contract, numRows=num_rows, isSmartDepth=True)
            
            # Store the active depth ticker
            self.active_depth[depth_key] = ticker
            
            if callback:
                # Store callback and set up event handler
                self.depth_callbacks[depth_key] = callback
                ticker.updateEvent += lambda: asyncio.create_task(callback(ticker))
                
                logging.info(f"Level 2 market depth active for {symbol} with callback")
            else:
                logging.info(f"Level 2 market depth active for {symbol}")
            
            return ticker
            
        except Exception as e:
            logging.error(f"Error starting Level 2 market depth for {symbol}: {str(e)}")
            return None
    
    def stop_market_depth(self, symbol: str, sec_type: str = "STK"):
        """Stop Level 2 market depth streaming"""
        try:
            depth_key = f"{symbol}_{sec_type}_depth"
            
            if depth_key in self.active_depth:
                ticker = self.active_depth[depth_key]
                
                # Cancel market depth
                self.ib.cancelMktDepth(ticker.contract, isSmartDepth=True)
                
                # Clean up
                del self.active_depth[depth_key]
                if depth_key in self.depth_callbacks:
                    del self.depth_callbacks[depth_key]
                
                logging.info(f"Stopped Level 2 market depth for {symbol}")
                return True
            return False
        except Exception as e:
            logging.error(f"Error stopping Level 2 market depth: {str(e)}")
            return False
    
    async def start_tick_by_tick(self, symbol: str, sec_type: str = "STK", 
                                exchange: str = None, currency: str = "USD",
                                tick_type: str = "Last", callback: Optional[Callable] = None):
        """Start tick-by-tick data streaming"""
        try:
            tick_key = f"{symbol}_{sec_type}_{tick_type}_tick"
            if tick_key in self.active_tick_streams:
                logging.info(f"Already streaming tick data for {symbol}")
                return self.active_tick_streams[tick_key]
            
            # Get qualified contract
            qualified_contract = await self._get_qualified_contract(symbol, sec_type, exchange, currency)
            if not qualified_contract:
                return None
            
            # Request tick-by-tick data
            # tick_type options: "Last", "AllLast", "BidAsk", "MidPoint"
            ticker = self.ib.reqTickByTickData(qualified_contract, tick_type, 0, False)
            
            # Store the active ticker
            self.active_tick_streams[tick_key] = ticker
            
            if callback:
                ticker.updateEvent += lambda: asyncio.create_task(callback(ticker))
                logging.info(f"Tick-by-tick data active for {symbol} ({tick_type}) with callback")
            else:
                logging.info(f"Tick-by-tick data active for {symbol} ({tick_type})")
            
            return ticker
            
        except Exception as e:
            logging.error(f"Error starting tick-by-tick data for {symbol}: {str(e)}")
            return None
    
    def stop_tick_by_tick(self, symbol: str, sec_type: str = "STK", tick_type: str = "Last"):
        """Stop tick-by-tick data streaming"""
        try:
            tick_key = f"{symbol}_{sec_type}_{tick_type}_tick"
            
            if tick_key in self.active_tick_streams:
                ticker = self.active_tick_streams[tick_key]
                
                # Cancel tick-by-tick data
                self.ib.cancelTickByTickData(ticker.contract, tick_type)
                
                # Clean up
                del self.active_tick_streams[tick_key]
                
                logging.info(f"Stopped tick-by-tick data for {symbol}")
                return True
            return False
        except Exception as e:
            logging.error(f"Error stopping tick-by-tick data: {str(e)}")
            return False
    
    async def get_level2_snapshot(self, symbol: str, sec_type: str = "STK", 
                                 exchange: str = None, currency: str = "USD") -> Optional[Dict[str, Any]]:
        """Get a one-time Level 2 order book snapshot"""
        try:
            # Start market depth temporarily
            ticker = await self.start_market_depth(symbol, sec_type, exchange, currency)
            if not ticker:
                return None
            
            # Wait for initial data
            await asyncio.sleep(2)
            
            # Extract order book data
            snapshot = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'bids': [],
                'asks': [],
                'spread': 0.0,
                'mid_price': 0.0
            }
            
            # Get bid data
            if hasattr(ticker, 'domBids') and ticker.domBids:
                for bid in ticker.domBids[:10]:
                    snapshot['bids'].append({
                        'price': float(bid.price),
                        'size': int(bid.size),
                        'market_maker': getattr(bid, 'marketMaker', ''),
                        'orders': getattr(bid, 'orders', 1)
                    })
            
            # Get ask data
            if hasattr(ticker, 'domAsks') and ticker.domAsks:
                for ask in ticker.domAsks[:10]:
                    snapshot['asks'].append({
                        'price': float(ask.price),
                        'size': int(ask.size),
                        'market_maker': getattr(ask, 'marketMaker', ''),
                        'orders': getattr(ask, 'orders', 1)
                    })
            
            # Calculate spread and mid price
            if snapshot['bids'] and snapshot['asks']:
                best_bid = snapshot['bids'][0]['price']
                best_ask = snapshot['asks'][0]['price']
                snapshot['spread'] = best_ask - best_bid
                snapshot['mid_price'] = (best_ask + best_bid) / 2
            
            # Stop the temporary depth stream
            self.stop_market_depth(symbol, sec_type)
            
            return snapshot
            
        except Exception as e:
            logging.error(f"Error getting Level 2 snapshot for {symbol}: {str(e)}")
            return None
    
    async def _get_qualified_contract(self, symbol: str, sec_type: str, exchange: str, currency: str):
        """Get qualified contract for Level 2 data"""
        try:
            if sec_type == "FUT":
                # For futures, get the front month contract
                base_contract = self.ib_connector.create_contract(symbol, sec_type, exchange, currency)
                contracts = await self.ib.reqContractDetailsAsync(base_contract)
                if contracts:
                    qualified_contract = contracts[0].contract
                    logging.info(f"Using futures contract for Level 2: {qualified_contract}")
                    return qualified_contract
                else:
                    logging.error(f"No futures contracts found for Level 2 on {symbol}")
                    return None
            else:
                # For non-futures, qualify the contract
                contract = self.ib_connector.create_contract(symbol, sec_type, exchange, currency)
                qualified_contracts = await self.ib.qualifyContractsAsync(contract)
                if qualified_contracts:
                    return qualified_contracts[0]
                else:
                    logging.error(f"Failed to qualify contract for Level 2 on {symbol}")
                    return None
        except Exception as e:
            logging.error(f"Error qualifying contract for Level 2: {e}")
            return None
    
    def get_active_streams(self) -> Dict[str, Any]:
        """Get information about active Level 2 streams"""
        return {
            'market_depth_streams': list(self.active_depth.keys()),
            'tick_streams': list(self.active_tick_streams.keys()),
            'total_streams': len(self.active_depth) + len(self.active_tick_streams)
        }
    
    def stop_all_streams(self):
        """Stop all Level 2 streams"""
        try:
            # Stop all market depth streams
            for depth_key in list(self.active_depth.keys()):
                symbol, sec_type = depth_key.split('_')[:2]
                self.stop_market_depth(symbol, sec_type)
            
            # Stop all tick streams
            for tick_key in list(self.active_tick_streams.keys()):
                parts = tick_key.split('_')
                symbol, sec_type, tick_type = parts[0], parts[1], parts[2]
                self.stop_tick_by_tick(symbol, sec_type, tick_type)
            
            logging.info("Stopped all Level 2 streams")
            return True
        except Exception as e:
            logging.error(f"Error stopping all Level 2 streams: {e}")
            return False
