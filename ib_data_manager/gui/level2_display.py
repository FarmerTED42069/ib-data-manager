"""
Professional Level 2 Order Book and Volume Profile Display
Real-time visualization for market microstructure analysis
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import logging
from typing import Dict, List, Optional, Callable
from collections import deque

from ..core.volume_profile import EnhancedTickCapture, VolumeProfile, OrderBookSnapshot, TickData
from .modern_theme import ModernTheme


class Level2Display:
    """Professional Level 2 order book display with volume profile"""
    
    def __init__(self, parent, ib_connector=None):
        self.parent = parent
        self.ib_connector = ib_connector
        self.tick_capture = EnhancedTickCapture()
        
        # Current data
        self.current_symbol = ""
        self.current_orderbook: Optional[OrderBookSnapshot] = None
        self.current_volume_profile: Optional[VolumeProfile] = None
        self.tick_history = deque(maxlen=1000)
        
        # Display settings
        self.depth_levels = 20
        self.price_precision = 2
        self.size_scale = 1000  # Display sizes in thousands
        
        # Create UI
        self.create_widgets()
        
        # Update timers
        self.update_interval = 100  # ms
        self.last_update = datetime.now()
        
    def create_widgets(self):
        """Create the Level 2 display interface"""
        # Main container
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control panel
        self.create_control_panel()
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Order Book tab
        self.create_order_book_tab()
        
        # Volume Profile tab
        self.create_volume_profile_tab()
        
        # Time & Sales tab
        self.create_time_sales_tab()
        
        # Market Statistics tab
        self.create_statistics_tab()
        
    def create_control_panel(self):
        """Create control panel for Level 2 display"""
        control_frame = ttk.LabelFrame(self.main_frame, text="Level 2 Controls", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Row 1: Symbol and connection
        row1 = ttk.Frame(control_frame)
        row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(row1, text="Symbol:").pack(side=tk.LEFT)
        self.symbol_var = tk.StringVar()
        self.symbol_entry = ttk.Entry(row1, textvariable=self.symbol_var, width=10)
        self.symbol_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        self.start_button = ttk.Button(row1, text="🚀 Start Level 2", 
                                      command=self.start_level2, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=2)
        
        self.stop_button = ttk.Button(row1, text="🛑 Stop", 
                                     command=self.stop_level2, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=2)
        
        # Status indicator
        self.status_label = ttk.Label(row1, text="● Disconnected", foreground="red")
        self.status_label.pack(side=tk.RIGHT)
        
        # Row 2: Display options
        row2 = ttk.Frame(control_frame)
        row2.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(row2, text="Depth Levels:").pack(side=tk.LEFT)
        self.depth_var = tk.StringVar(value="20")
        depth_combo = ttk.Combobox(row2, textvariable=self.depth_var, 
                                  values=["10", "20", "50"], width=5, state="readonly")
        depth_combo.pack(side=tk.LEFT, padx=(5, 10))
        depth_combo.bind('<<ComboboxSelected>>', self.on_depth_changed)
        
        ttk.Label(row2, text="Update Rate:").pack(side=tk.LEFT, padx=(10, 0))
        self.rate_var = tk.StringVar(value="Fast")
        rate_combo = ttk.Combobox(row2, textvariable=self.rate_var,
                                 values=["Slow", "Medium", "Fast"], width=8, state="readonly")
        rate_combo.pack(side=tk.LEFT, padx=(5, 10))
        rate_combo.bind('<<ComboboxSelected>>', self.on_rate_changed)
        
        # Statistics
        self.stats_label = ttk.Label(row2, text="Ticks: 0 | Updates: 0 | Spread: $0.00")
        self.stats_label.pack(side=tk.RIGHT)
        
    def create_order_book_tab(self):
        """Create order book visualization tab"""
        book_frame = ttk.Frame(self.notebook)
        self.notebook.add(book_frame, text="📊 Order Book")
        
        # Create matplotlib figure for order book
        self.book_figure = Figure(figsize=(12, 8), facecolor='white')
        self.book_canvas = FigureCanvasTkAgg(self.book_figure, book_frame)
        self.book_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Order book table
        table_frame = ttk.Frame(book_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for order book
        columns = ("Size", "Price", "Side", "MM")
        self.book_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        # Configure columns
        self.book_tree.heading("Size", text="Size")
        self.book_tree.heading("Price", text="Price")
        self.book_tree.heading("Side", text="Side")
        self.book_tree.heading("MM", text="Market Maker")
        
        self.book_tree.column("Size", width=100, anchor=tk.E)
        self.book_tree.column("Price", width=100, anchor=tk.E)
        self.book_tree.column("Side", width=60, anchor=tk.CENTER)
        self.book_tree.column("MM", width=100, anchor=tk.W)
        
        # Scrollbar
        book_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.book_tree.yview)
        self.book_tree.configure(yscrollcommand=book_scrollbar.set)
        
        self.book_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        book_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_volume_profile_tab(self):
        """Create volume profile visualization tab"""
        profile_frame = ttk.Frame(self.notebook)
        self.notebook.add(profile_frame, text="📈 Volume Profile")
        
        # Create matplotlib figure for volume profile
        self.profile_figure = Figure(figsize=(12, 8), facecolor='white')
        self.profile_canvas = FigureCanvasTkAgg(self.profile_figure, profile_frame)
        self.profile_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Volume profile controls
        controls_frame = ttk.LabelFrame(profile_frame, text="Volume Profile Controls", padding="5")
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(controls_frame, text="Time Period:").pack(side=tk.LEFT)
        self.period_var = tk.StringVar(value="Session")
        period_combo = ttk.Combobox(controls_frame, textvariable=self.period_var,
                                   values=["Last Hour", "Session", "Custom"], width=10, state="readonly")
        period_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(controls_frame, text="📊 Update Profile", 
                  command=self.update_volume_profile).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls_frame, text="💾 Export CSV", 
                  command=self.export_volume_profile).pack(side=tk.LEFT, padx=5)
        
        # Profile statistics
        self.profile_stats_label = ttk.Label(controls_frame, text="POC: $0.00 | VA: $0.00-$0.00 | Total Vol: 0")
        self.profile_stats_label.pack(side=tk.RIGHT)
        
    def create_time_sales_tab(self):
        """Create time & sales display tab"""
        sales_frame = ttk.Frame(self.notebook)
        self.notebook.add(sales_frame, text="⏰ Time & Sales")
        
        # Time & Sales table
        columns = ("Time", "Price", "Size", "Side", "Cumulative")
        self.sales_tree = ttk.Treeview(sales_frame, columns=columns, show='headings', height=25)
        
        # Configure columns
        self.sales_tree.heading("Time", text="Time")
        self.sales_tree.heading("Price", text="Price")
        self.sales_tree.heading("Size", text="Size")
        self.sales_tree.heading("Side", text="Side")
        self.sales_tree.heading("Cumulative", text="Cum. Vol")
        
        self.sales_tree.column("Time", width=100, anchor=tk.W)
        self.sales_tree.column("Price", width=80, anchor=tk.E)
        self.sales_tree.column("Size", width=80, anchor=tk.E)
        self.sales_tree.column("Side", width=60, anchor=tk.CENTER)
        self.sales_tree.column("Cumulative", width=100, anchor=tk.E)
        
        # Scrollbar for time & sales
        sales_scrollbar = ttk.Scrollbar(sales_frame, orient=tk.VERTICAL, command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=sales_scrollbar.set)
        
        self.sales_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        sales_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Configure row colors for buy/sell
        self.sales_tree.tag_configure('buy', background='#e8f5e8')
        self.sales_tree.tag_configure('sell', background='#ffe8e8')
        self.sales_tree.tag_configure('unknown', background='#f0f0f0')
        
    def create_statistics_tab(self):
        """Create market statistics tab"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📊 Statistics")
        
        # Create statistics display
        stats_container = ttk.Frame(stats_frame)
        stats_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Real-time metrics
        metrics_frame = ttk.LabelFrame(stats_container, text="Real-Time Metrics", padding="10")
        metrics_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create statistics labels
        self.create_statistics_labels(metrics_frame)
        
        # Performance chart
        perf_frame = ttk.LabelFrame(stats_container, text="Performance Chart", padding="10")
        perf_frame.pack(fill=tk.BOTH, expand=True)
        
        self.perf_figure = Figure(figsize=(10, 6), facecolor='white')
        self.perf_canvas = FigureCanvasTkAgg(self.perf_figure, perf_frame)
        self.perf_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_statistics_labels(self, parent):
        """Create statistics display labels"""
        # Row 1: Basic metrics
        row1 = ttk.Frame(parent)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(row1, text="Tick Count:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        self.tick_count_label = ttk.Label(row1, text="0")
        self.tick_count_label.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(row1, text="Updates/sec:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        self.update_rate_label = ttk.Label(row1, text="0.0")
        self.update_rate_label.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(row1, text="Spread:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        self.spread_label = ttk.Label(row1, text="$0.00")
        self.spread_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Row 2: Volume metrics
        row2 = ttk.Frame(parent)
        row2.pack(fill=tk.X, pady=2)
        
        ttk.Label(row2, text="Buy Volume:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        self.buy_volume_label = ttk.Label(row2, text="0", foreground="green")
        self.buy_volume_label.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(row2, text="Sell Volume:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        self.sell_volume_label = ttk.Label(row2, text="0", foreground="red")
        self.sell_volume_label.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(row2, text="Delta:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        self.delta_label = ttk.Label(row2, text="0")
        self.delta_label.pack(side=tk.LEFT, padx=(5, 0))
        
    async def start_level2(self):
        """Start Level 2 data capture"""
        print(f"🔍 DEBUG: start_level2 called for symbol: {self.symbol_var.get()}")
        
        if not self.ib_connector or not self.ib_connector.connected:
            print("❌ DEBUG: IB connector not connected")
            tk.messagebox.showwarning("Not Connected", "Please connect to IB Gateway first")
            return
        
        symbol = self.symbol_var.get().strip().upper()
        if not symbol:
            print("❌ DEBUG: No symbol provided")
            tk.messagebox.showwarning("No Symbol", "Please enter a symbol")
            return
        
        try:
            print(f"🚀 DEBUG: Starting Level 2 for {symbol}")
            self.current_symbol = symbol
            
            # Start tick capture with callbacks
            print("🔍 DEBUG: Calling start_tick_capture...")
            success = await self.tick_capture.start_tick_capture(
                symbol=symbol,
                ib_connector=self.ib_connector,
                tick_callback=self.on_tick_update,
                orderbook_callback=self.on_orderbook_update
            )
            print(f"🔍 DEBUG: start_tick_capture returned: {success}")
            
            if success:
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                self.status_label.config(text="● Connected", foreground="green")
                
                # Start update timer
                self.schedule_updates()
                
                logging.info(f"✅ Level 2 started for {symbol}")
            else:
                tk.messagebox.showerror("Error", f"Failed to start Level 2 for {symbol}")
                
        except Exception as e:
            logging.error(f"Error starting Level 2: {e}")
            tk.messagebox.showerror("Error", f"Error starting Level 2: {str(e)}")
    
    def stop_level2(self):
        """Stop Level 2 data capture"""
        if self.current_symbol:
            self.tick_capture.stop_tick_capture(self.current_symbol)
            
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="● Disconnected", foreground="red")
        
        # Clear displays
        self.clear_displays()
        
        logging.info("✅ Level 2 stopped")
    
    async def on_tick_update(self, tick: TickData):
        """Handle tick data updates"""
        print(f"📊 DEBUG: Tick update received: {tick}")
        self.tick_history.append(tick)
        
        # Update time & sales display
        self.parent.after(0, lambda: self.update_time_sales(tick))
    
    async def on_orderbook_update(self, orderbook: OrderBookSnapshot):
        """Handle order book updates"""
        print(f"📈 DEBUG: Order book update received: {orderbook}")
        self.current_orderbook = orderbook
        
        # Update order book display
        self.parent.after(0, lambda: self.update_order_book_display())
    
    def update_order_book_display(self):
        """Update the order book display"""
        if not self.current_orderbook:
            return
        
        try:
            # Clear existing items
            for item in self.book_tree.get_children():
                self.book_tree.delete(item)
            
            # Add asks (top to bottom, highest to lowest)
            for ask in reversed(self.current_orderbook.asks[:self.depth_levels//2]):
                size_display = f"{ask.size:,}" if ask.size >= 1000 else str(ask.size)
                self.book_tree.insert('', 0, values=(
                    size_display,
                    f"${ask.price:.{self.price_precision}f}",
                    "ASK",
                    ask.market_maker
                ), tags=('ask',))
            
            # Add separator
            self.book_tree.insert('', 'end', values=("---", "SPREAD", "---", "---"), tags=('spread',))
            
            # Add bids (top to bottom, highest to lowest)
            for bid in self.current_orderbook.bids[:self.depth_levels//2]:
                size_display = f"{bid.size:,}" if bid.size >= 1000 else str(bid.size)
                self.book_tree.insert('', 'end', values=(
                    size_display,
                    f"${bid.price:.{self.price_precision}f}",
                    "BID",
                    bid.market_maker
                ), tags=('bid',))
            
            # Configure row colors
            self.book_tree.tag_configure('ask', background='#ffe8e8')
            self.book_tree.tag_configure('bid', background='#e8f5e8')
            self.book_tree.tag_configure('spread', background='#f0f0f0', font=('Arial', 9, 'bold'))
            
            # Update spread display
            self.spread_label.config(text=f"${self.current_orderbook.spread:.{self.price_precision}f}")
            
        except Exception as e:
            logging.error(f"Error updating order book display: {e}")
    
    def update_time_sales(self, tick: TickData):
        """Update time & sales display"""
        try:
            # Add new tick to top of list
            time_str = tick.timestamp.strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
            cumulative = len(self.tick_history)
            
            tag = tick.side if tick.side in ['buy', 'sell'] else 'unknown'
            
            self.sales_tree.insert('', 0, values=(
                time_str,
                f"${tick.price:.{self.price_precision}f}",
                f"{tick.size:,}",
                tick.side.upper(),
                f"{cumulative:,}"
            ), tags=(tag,))
            
            # Limit number of displayed items
            children = self.sales_tree.get_children()
            if len(children) > 500:
                for item in children[500:]:
                    self.sales_tree.delete(item)
                    
        except Exception as e:
            logging.error(f"Error updating time & sales: {e}")
    
    def update_volume_profile(self):
        """Update volume profile display"""
        if not self.current_symbol:
            return
        
        try:
            profile = self.tick_capture.get_volume_profile(self.current_symbol)
            if not profile or not profile.levels:
                return
            
            self.current_volume_profile = profile
            profile.calculate_metrics()
            
            # Clear previous plot
            self.profile_figure.clear()
            ax = self.profile_figure.add_subplot(111)
            
            # Extract data for plotting
            prices = sorted(profile.levels.keys())
            volumes = [profile.levels[price].volume for price in prices]
            buy_volumes = [profile.levels[price].buy_volume for price in prices]
            sell_volumes = [profile.levels[price].sell_volume for price in prices]
            
            # Create horizontal bar chart
            y_pos = np.arange(len(prices))
            
            # Plot buy and sell volumes
            ax.barh(y_pos, buy_volumes, color='green', alpha=0.6, label='Buy Volume')
            ax.barh(y_pos, [-v for v in sell_volumes], color='red', alpha=0.6, label='Sell Volume')
            
            # Highlight POC
            if profile.poc_price in profile.levels:
                poc_index = prices.index(profile.poc_price)
                ax.barh(poc_index, volumes[poc_index], color='yellow', alpha=0.8, label='POC')
            
            # Highlight Value Area
            if profile.value_area_low and profile.value_area_high:
                va_indices = [i for i, p in enumerate(prices) 
                             if profile.value_area_low <= p <= profile.value_area_high]
                for i in va_indices:
                    ax.axhline(y=i, color='blue', alpha=0.3, linewidth=2)
            
            ax.set_yticks(y_pos)
            ax.set_yticklabels([f"${p:.2f}" for p in prices])
            ax.set_xlabel('Volume')
            ax.set_ylabel('Price')
            ax.set_title(f'{self.current_symbol} - Volume Profile')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            self.profile_canvas.draw()
            
            # Update statistics
            self.profile_stats_label.config(
                text=f"POC: ${profile.poc_price:.2f} | "
                     f"VA: ${profile.value_area_low:.2f}-${profile.value_area_high:.2f} | "
                     f"Total Vol: {profile.total_volume:,}"
            )
            
        except Exception as e:
            logging.error(f"Error updating volume profile: {e}")
    
    def schedule_updates(self):
        """Schedule regular updates"""
        if self.current_symbol and self.tick_capture.active_captures.get(self.current_symbol, False):
            # Update statistics
            self.update_statistics()
            
            # Update volume profile
            self.update_volume_profile()
            
            # Schedule next update
            self.parent.after(self.update_interval, self.schedule_updates)
    
    def update_statistics(self):
        """Update statistics display"""
        if not self.current_symbol:
            return
        
        try:
            stats = self.tick_capture.get_tick_statistics(self.current_symbol)
            
            # Update tick count
            self.tick_count_label.config(text=f"{stats['tick_count']:,}")
            
            # Calculate update rate
            now = datetime.now()
            time_diff = (now - self.last_update).total_seconds()
            if time_diff > 0:
                update_rate = 1.0 / time_diff
                self.update_rate_label.config(text=f"{update_rate:.1f}")
            self.last_update = now
            
            # Update volume statistics
            profile = self.tick_capture.get_volume_profile(self.current_symbol)
            if profile:
                total_buy = sum(level.buy_volume for level in profile.levels.values())
                total_sell = sum(level.sell_volume for level in profile.levels.values())
                delta = total_buy - total_sell
                
                self.buy_volume_label.config(text=f"{total_buy:,}")
                self.sell_volume_label.config(text=f"{total_sell:,}")
                self.delta_label.config(
                    text=f"{delta:+,}",
                    foreground="green" if delta > 0 else "red" if delta < 0 else "black"
                )
                
        except Exception as e:
            logging.error(f"Error updating statistics: {e}")
    
    def export_volume_profile(self):
        """Export volume profile to CSV"""
        if not self.current_volume_profile:
            tk.messagebox.showwarning("No Data", "No volume profile data to export")
            return
        
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Volume Profile"
            )
            
            if filename:
                from ..core.volume_profile import export_volume_profile_csv
                export_volume_profile_csv(self.current_volume_profile, filename)
                tk.messagebox.showinfo("Export Complete", f"Volume profile exported to {filename}")
                
        except Exception as e:
            logging.error(f"Error exporting volume profile: {e}")
            tk.messagebox.showerror("Export Error", f"Error exporting volume profile: {str(e)}")
    
    def on_depth_changed(self, event=None):
        """Handle depth level change"""
        self.depth_levels = int(self.depth_var.get())
        self.update_order_book_display()
    
    def on_rate_changed(self, event=None):
        """Handle update rate change"""
        rate_map = {"Slow": 500, "Medium": 250, "Fast": 100}
        self.update_interval = rate_map.get(self.rate_var.get(), 100)
    
    def clear_displays(self):
        """Clear all displays"""
        # Clear order book
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)
        
        # Clear time & sales
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        # Clear figures
        self.book_figure.clear()
        self.profile_figure.clear()
        self.perf_figure.clear()
        
        self.book_canvas.draw()
        self.profile_canvas.draw()
        self.perf_canvas.draw()
        
        # Reset labels
        self.tick_count_label.config(text="0")
        self.update_rate_label.config(text="0.0")
        self.spread_label.config(text="$0.00")
        self.buy_volume_label.config(text="0")
        self.sell_volume_label.config(text="0")
        self.delta_label.config(text="0")
        self.profile_stats_label.config(text="POC: $0.00 | VA: $0.00-$0.00 | Total Vol: 0")


def run_async_task(coro):
    """Helper function to run async tasks from tkinter"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, schedule the coroutine
            task = asyncio.create_task(coro)
            return task
        else:
            # If no loop is running, run the coroutine
            return loop.run_until_complete(coro)
    except RuntimeError:
        # Create new event loop if none exists
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
