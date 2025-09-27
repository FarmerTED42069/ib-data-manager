"""
Async Interactive Brokers Data Manager
A clean interface to pull data from IB Gateway and store it in a database using async operations
"""

import asyncio
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
import logging
from ib_data_manager.api.async_ib_connector import AsyncIBConnector
import os
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ib_data_manager_async.log'),
        logging.StreamHandler()
    ]
)

class AsyncIBDataManager:
    """Async version of the IB Data Manager GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("IB Data Manager (Async)")
        self.root.geometry("800x600")

        # Async connector
        self.ib_conn = AsyncIBConnector()

        # Async loop (run in separate thread)
        self.loop = None
        self.thread = None

        # Track last fetched historical data for CSV export
        self.last_historical_data = None
        self.last_historical_symbol = None

        # Create GUI
        self.create_widgets()

        # Start the async loop
        self.start_async_loop()
        
        # Load settings
        self.load_settings()
        
    def create_widgets(self):
        """Create GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Connection status frame
        status_frame = ttk.LabelFrame(main_frame, text="Connection Status", padding="5")
        status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Not Connected", foreground="red")
        self.status_label.grid(row=0, column=0, padx=5)
        
        ttk.Button(status_frame, text="Connect", command=self.connect_ib).grid(row=0, column=1, padx=5)
        ttk.Button(status_frame, text="Disconnect", command=self.disconnect_ib).grid(row=0, column=2, padx=5)
        
        # Data request frame
        request_frame = ttk.LabelFrame(main_frame, text="Data Request", padding="5")
        request_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Symbol entry
        ttk.Label(request_frame, text="Symbol:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.symbol_entry = ttk.Entry(request_frame, width=15)
        self.symbol_entry.grid(row=0, column=1, padx=5, pady=5)
        self.symbol_entry.insert(0, "AAPL")
        
        # Contract type
        ttk.Label(request_frame, text="Type:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.contract_type = ttk.Combobox(request_frame, values=["STK", "FUT", "OPT", "CASH", "BOND"])
        self.contract_type.set("STK")
        self.contract_type.grid(row=0, column=3, padx=5, pady=5)
        self.contract_type.bind("<<ComboboxSelected>>", self.on_contract_type_change)
        
        # Exchange and currency
        ttk.Label(request_frame, text="Exchange:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.exchange_entry = ttk.Entry(request_frame, width=15)
        self.exchange_entry.grid(row=1, column=1, padx=5, pady=5)
        self.exchange_entry.insert(0, "SMART")
        
        ttk.Label(request_frame, text="Currency:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.currency_entry = ttk.Entry(request_frame, width=15)
        self.currency_entry.grid(row=1, column=3, padx=5, pady=5)
        self.currency_entry.insert(0, "USD")
        
        # Expiry (for futures/options) with enhanced futures selection
        ttk.Label(request_frame, text="Expiry:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        expiry_frame = ttk.Frame(request_frame)
        expiry_frame.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        self.expiry_entry = ttk.Entry(expiry_frame, width=12)
        self.expiry_entry.grid(row=0, column=0, padx=(0, 5))
        
        # Futures contract selection buttons
        self.front_contract_btn = ttk.Button(expiry_frame, text="Front Contract", 
                                           command=self.select_front_contract, width=12)
        self.front_contract_btn.grid(row=0, column=1, padx=2)
        
        self.browse_contracts_btn = ttk.Button(expiry_frame, text="Browse Contracts", 
                                             command=self.browse_futures_contracts, width=14)
        self.browse_contracts_btn.grid(row=0, column=2, padx=2)
        
        # Data type selection
        data_type_frame = ttk.LabelFrame(main_frame, text="Data Type", padding="5")
        data_type_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.data_type = tk.StringVar(value="historical")
        ttk.Radiobutton(data_type_frame, text="Historical Data", variable=self.data_type, 
                       value="historical", command=self.on_data_type_change).grid(row=0, column=0, padx=5, pady=5)
        ttk.Radiobutton(data_type_frame, text="Real-time Quotes", variable=self.data_type, 
                       value="realtime", command=self.on_data_type_change).grid(row=0, column=1, padx=5, pady=5)
        ttk.Radiobutton(data_type_frame, text="Account Info", variable=self.data_type, 
                       value="account", command=self.on_data_type_change).grid(row=0, column=2, padx=5, pady=5)
        ttk.Radiobutton(data_type_frame, text="Market Depth (Level 2)", variable=self.data_type, 
                       value="market_depth", command=self.on_data_type_change).grid(row=0, column=3, padx=5, pady=5)
        
        # Historical data settings with enhanced date range selection
        self.historical_frame = ttk.LabelFrame(main_frame, text="Historical Data Settings", padding="5")
        self.historical_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Date range selection mode
        date_mode_frame = ttk.Frame(self.historical_frame)
        date_mode_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        self.date_mode = tk.StringVar(value="duration")
        ttk.Radiobutton(date_mode_frame, text="Duration (e.g., 1 Y, 6 M)", 
                       variable=self.date_mode, value="duration", 
                       command=self.on_date_mode_change).grid(row=0, column=0, padx=5)
        ttk.Radiobutton(date_mode_frame, text="Specific Date Range", 
                       variable=self.date_mode, value="daterange", 
                       command=self.on_date_mode_change).grid(row=0, column=1, padx=5)
        
        # Duration settings (existing)
        self.duration_frame = ttk.Frame(self.historical_frame)
        self.duration_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.duration_frame, text="Duration:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.duration_entry = ttk.Entry(self.duration_frame, width=15)
        self.duration_entry.grid(row=0, column=1, padx=5, pady=5)
        self.duration_entry.insert(0, "1 Y")
        
        ttk.Label(self.duration_frame, text="Bar Size:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.bar_size = ttk.Combobox(self.duration_frame, values=[
            "1 sec", "5 secs", "10 secs", "15 secs", "30 secs", 
            "1 min", "2 mins", "3 mins", "5 mins", "10 mins", "15 mins", "30 mins", 
            "1 hour", "1 day", "1 week", "1 month"
        ], width=12)
        self.bar_size.set("1 hour")
        self.bar_size.grid(row=0, column=3, padx=5, pady=5)
        self.bar_size.bind("<<ComboboxSelected>>", self.update_max_duration_label)
        
        # Date range settings (new)
        self.daterange_frame = ttk.Frame(self.historical_frame)
        self.daterange_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.daterange_frame, text="Start Date:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.start_date_entry = ttk.Entry(self.daterange_frame, width=12)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.start_date_entry.insert(0, "2024-06-12")
        
        ttk.Button(self.daterange_frame, text="", width=3, 
                  command=lambda: self.pick_date(self.start_date_entry)).grid(row=0, column=2, padx=2)
        
        ttk.Label(self.daterange_frame, text="End Date:").grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        self.end_date_entry = ttk.Entry(self.daterange_frame, width=12)
        self.end_date_entry.grid(row=0, column=4, padx=5, pady=5)
        self.end_date_entry.insert(0, "2024-07-12")
        
        ttk.Button(self.daterange_frame, text="", width=3, 
                  command=lambda: self.pick_date(self.end_date_entry)).grid(row=0, column=5, padx=2)
        
        # Bar size for date range mode
        ttk.Label(self.daterange_frame, text="Bar Size:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.daterange_bar_size = ttk.Combobox(self.daterange_frame, values=[
            "30 secs", "1 min", "2 mins", "3 mins", "5 mins", "10 mins", "15 mins", "30 mins", 
            "1 hour", "1 day", "1 week", "1 month"
        ], width=12)
        self.daterange_bar_size.set("1 min")
        self.daterange_bar_size.grid(row=1, column=1, padx=5, pady=5)
        
        # Batch processing settings for high-frequency data
        batch_frame = ttk.Frame(self.daterange_frame)
        batch_frame.grid(row=1, column=2, columnspan=4, padx=10, pady=5, sticky=(tk.W, tk.E))
        
        self.enable_batching = tk.BooleanVar(value=True)
        ttk.Checkbutton(batch_frame, text="Enable Batch Processing", 
                       variable=self.enable_batching).grid(row=0, column=0, padx=5)
        
        ttk.Label(batch_frame, text="Batch Size (days):").grid(row=0, column=1, padx=5)
        self.batch_size_entry = ttk.Entry(batch_frame, width=8)
        self.batch_size_entry.grid(row=0, column=2, padx=5)
        self.batch_size_entry.insert(0, "7")  # 7-day batches by default
        
        # Duration limits info
        self.duration_info_label = ttk.Label(self.duration_frame, text="e.g. 1 D, 6 M, 2 Y, 3 W, 30 S", 
                                           foreground="gray")
        self.duration_info_label.grid(row=1, column=0, columnspan=2, padx=5, sticky=tk.W)
        
        self.max_duration_label = ttk.Label(self.duration_frame, text="Max allowed: 1 M for 1 hour bars", 
                                          foreground="blue")
        self.max_duration_label.grid(row=1, column=2, columnspan=2, padx=5, sticky=tk.W)
        
        # Initially hide date range frame
        self.daterange_frame.grid_remove()
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Fetch Data", command=self.fetch_data).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="View Database", command=self.view_database).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Export CSV", command=self.export_csv).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Quick Export", command=self.quick_export).grid(row=0, column=3, padx=5)
        
        # Output text area
        self.output_text = tk.Text(main_frame, height=15, width=80)
        self.output_text.grid(row=5, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for text area
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.output_text.yview)
        scrollbar.grid(row=5, column=2, sticky=(tk.N, tk.S))
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
    def on_contract_type_change(self, event=None):
        """Handle contract type change"""
        contract_type = self.contract_type.get()
        if contract_type == "FUT":
            self.expiry_entry.configure(state="normal")
        else:
            self.expiry_entry.configure(state="disabled")
            self.expiry_entry.delete(0, tk.END)
            
    def start_async_loop(self):
        """Start the asyncio event loop in a separate thread"""
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
            
        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()
        
    def run_async_task(self, coro):
        """Schedule an async task to run in the async loop"""
        if self.loop and self.thread and self.thread.is_alive():
            future = asyncio.run_coroutine_threadsafe(coro, self.loop)
            return future
        else:
            self.log_message("Error: Async loop not running")
            return None
            
    def connect_ib(self):
        """Connect to IB Gateway"""
        def update_ui(success):
            if success:
                self.status_label.config(text="Connected", foreground="green")
                self.log_message("Successfully connected to IB Gateway")
            else:
                self.status_label.config(text="Failed to Connect", foreground="red")
                self.log_message("Failed to connect to IB Gateway")
                
        # Run the async connect operation
        future = self.run_async_task(self.ib_conn.connect())
        if future:
            future.add_done_callback(lambda f: self.root.after(0, update_ui, f.result()))
            
    def disconnect_ib(self):
        """Disconnect from IB Gateway"""
        def update_ui(success):
            if success:
                self.status_label.config(text="Disconnected", foreground="red")
                self.log_message("Disconnected from IB Gateway")
            else:
                self.log_message("Error disconnecting from IB Gateway")
                
        # Run the async disconnect operation
        future = self.run_async_task(self.ib_conn.disconnect())
        if future:
            future.add_done_callback(lambda f: self.root.after(0, update_ui, f.result()))
            
    def validate_duration(self, duration):
        """Validate duration string for IBKR (e.g. 1 D, 6 M, 2 Y, 3 W, 30 S)"""
        import re
        pattern = r"^\s*([1-9][0-9]*)\s*([SMWDYsmwdy])\s*$"
        match = re.match(pattern, duration.strip())
        if not match:
            return False
        num, unit = match.groups()
        return unit.upper() in ["S", "D", "W", "M", "Y"]

    def validate_bar_size(self, bar_size):
        """Validate bar size string for IBKR"""
        valid_sizes = [
            "1 sec", "5 secs", "10 secs", "15 secs", "30 secs", "1 min", "2 mins", "3 mins", "5 mins", "10 mins", "15 mins", "30 mins", "1 hour", "1 day", "1 week", "1 month"
        ]
        return bar_size in valid_sizes

    def fetch_data(self):
        """Fetch data based on user selection (with validation)"""
        if not self.ib_conn.connected:
            messagebox.showwarning("Warning", "Please connect to IB Gateway first")
            return

        # Get contract details
        symbol = self.symbol_entry.get()
        contract_type = self.contract_type.get()
        exchange = self.exchange_entry.get()
        currency = self.currency_entry.get()
        expiry = self.expiry_entry.get() if contract_type == "FUT" else None
        data_type = self.data_type.get()

        if data_type == "historical":
            if self.date_mode.get() == "duration":
                duration = self.duration_entry.get()
                bar_size = self.bar_size.get()

                # --- Validation ---
                if not self.validate_duration(duration):
                    messagebox.showerror("Invalid Duration", "Duration must be in the form: <number> <unit>, e.g. 1 D, 6 M, 2 Y, 3 W, 30 S. Supported units: S=seconds, D=days, W=weeks, M=months, Y=years.")
                    return
                if not self.validate_bar_size(bar_size):
                    messagebox.showerror("Invalid Bar Size", "Bar size must be one of the supported IBKR intervals.")
                    return

                self.log_message(f"Fetching historical data for {symbol}...")
                def update_ui(result):
                    if result:
                        self.log_message(f"Fetched {len(result)} bars for {symbol}")
                        self.display_historical_data(result)
                        # --- AUTOMATED DATABASE SAVE ---
                        async def save_to_db():
                            try:
                                await self.ib_conn.db.save_historical_data(symbol, result)
                                self.log_message(f"Saved {len(result)} bars for {symbol} to database.")
                            except Exception as e:
                                self.log_message(f"Failed to save {symbol} data to database: {e}")
                        self.run_async_task(save_to_db())
                    else:
                        self.log_message(f"Failed to fetch historical data for {symbol}")
                # Run the async operation
                future = self.run_async_task(
                    self.ib_conn.get_historical_data(symbol, contract_type, exchange, currency, duration, bar_size, expiry)
                )
                if future:
                    future.add_done_callback(lambda f: self.root.after(0, update_ui, f.result()))
            elif self.date_mode.get() == "daterange":
                start_date = self.start_date_entry.get()
                end_date = self.end_date_entry.get()
                bar_size = self.daterange_bar_size.get()

                # --- Validation ---
                if not self.validate_bar_size(bar_size):
                    messagebox.showerror("Invalid Bar Size", "Bar size must be one of the supported IBKR intervals.")
                    return

                self.log_message(f"Fetching historical data for {symbol}...")
                def update_ui(result):
                    if result:
                        self.log_message(f"Fetched {len(result)} bars for {symbol}")
                        self.display_historical_data(result)
                        # --- AUTOMATED DATABASE SAVE ---
                        async def save_to_db():
                            try:
                                await self.ib_conn.db.save_historical_data(symbol, result)
                                self.log_message(f"Saved {len(result)} bars for {symbol} to database.")
                            except Exception as e:
                                self.log_message(f"Failed to save {symbol} data to database: {e}")
                        self.run_async_task(save_to_db())
                    else:
                        self.log_message(f"Failed to fetch historical data for {symbol}")
                # Run the async operation
                future = self.run_async_task(
                    self.ib_conn.get_historical_data(symbol, contract_type, exchange, currency, start_date=start_date, end_date=end_date, bar_size=bar_size, expiry=expiry)
                )
                if future:
                    future.add_done_callback(lambda f: self.root.after(0, update_ui, f.result()))
        elif data_type == "account":
            self.log_message("Fetching account information...")
            def update_ui(result):
                if result:
                    self.display_account_info(result)
                else:
                    self.log_message("Failed to fetch account information")
            future = self.run_async_task(self.ib_conn.get_account_info())
            if future:
                future.add_done_callback(lambda f: self.root.after(0, update_ui, f.result()))
        elif data_type == "realtime":
            # Start real-time quote subscription for the selected symbol/contract
            self.log_message(f"Starting real-time quote subscription for {symbol}...")
            self.realtime_active = True
            self.realtime_symbol = symbol
            self.realtime_ticker = None

            def on_tick(ticker):
                # Display tick data in output area
                msg = f"[Tick] {datetime.now().strftime('%H:%M:%S')} {symbol} Last: {ticker.last}, Bid: {ticker.bid}, Ask: {ticker.ask}, Vol: {ticker.volume}"
                self.output_text.insert(tk.END, msg + "\n")
                self.output_text.see(tk.END)
                # Save tick to database asynchronously
                async def save_tick():
                    try:
                        await self.ib_conn.db.save_realtime_quote(symbol, ticker)
                    except Exception as e:
                        self.log_message(f"Failed to save real-time tick: {e}")
                self.run_async_task(save_tick())

            async def start_realtime():
                ticker = await self.ib_conn.start_realtime_quotes(
                    symbol, sec_type=contract_type, exchange=exchange, currency=currency, callback=on_tick
                )
                self.realtime_ticker = ticker
                if ticker is not None:
                    self.log_message(f"Real-time subscription started for {symbol}. Click 'Stop Realtime' to end.")
                else:
                    self.log_message(f"Failed to start real-time subscription for {symbol}.")
                    self.realtime_active = False

            self.run_async_task(start_realtime())

        # Add/enable Stop Realtime button
        if not hasattr(self, 'stop_realtime_button'):
            self.stop_realtime_button = ttk.Button(self.root, text="Stop Realtime", command=self.stop_realtime)
            self.stop_realtime_button.place(x=650, y=35)
        self.stop_realtime_button.config(state="normal")

    def stop_realtime(self):
        """Stop real-time quote subscription"""
        if hasattr(self, 'realtime_ticker') and self.realtime_ticker:
            try:
                self.ib_conn.ib.cancelMktData(self.realtime_ticker.contract)
                self.log_message(f"Stopped real-time subscription for {self.realtime_symbol}")
            except Exception as e:
                self.log_message(f"Error stopping real-time: {e}")
        self.realtime_active = False
        if hasattr(self, 'stop_realtime_button'):
            self.stop_realtime_button.config(state="disabled")

            
        elif data_type == "market_depth":
            self.log_message("Starting market depth collection...")
            
            def update_ui(result):
                if result:
                    self.log_message(f"Subscribed to market depth for {symbol}")
                else:
                    self.log_message(f"Failed to subscribe to market depth for {symbol}")
                    
            # Run the async operation
            future = self.run_async_task(
                self.ib_conn.subscribe_market_depth(symbol, contract_type, exchange, currency)
            )
            if future:
                future.add_done_callback(lambda f: self.root.after(0, update_ui, f.result()))
                
    def display_historical_data(self, data):
        """Display historical data in the output area and save for CSV export"""
        self.last_historical_data = data
        self.last_historical_symbol = self.symbol_entry.get()
        self.output_text.insert(tk.END, f"\nHistorical Data ({len(data)} bars):\n")
        self.output_text.insert(tk.END, f"{'Date':<20} {'Open':<10} {'High':<10} {'Low':<10} {'Close':<10} {'Volume':<10}\n")
        self.output_text.insert(tk.END, "-" * 80 + "\n")
        for bar in data[:20]:  # Show first 20 bars
            self.output_text.insert(tk.END, f"{bar.date:<20} {bar.open:<10.2f} {bar.high:<10.2f} {bar.low:<10.2f} {bar.close:<10.2f} {bar.volume:<10}\n")
        if len(data) > 20:
            self.output_text.insert(tk.END, f"... and {len(data) - 20} more bars\n")
        self.output_text.see(tk.END)
        
    def display_account_info(self, account_info):
        """Display account information"""
        self.output_text.insert(tk.END, f"\nAccount Information ({len(account_info)} items):\n")
        self.output_text.insert(tk.END, "-" * 50 + "\n")
        
        for key, value in list(account_info.items())[:30]:  # Show first 30 items
            self.output_text.insert(tk.END, f"{key}: {value}\n")
            
        if len(account_info) > 30:
            self.output_text.insert(tk.END, f"... and {len(account_info) - 30} more items\n")
            
        self.output_text.see(tk.END)
        
    def view_database(self):
        """Open database viewer window (async)"""
        import tkinter as tk
        from tkinter import ttk, simpledialog
        # Ask user for symbol
        symbol = simpledialog.askstring("Database Viewer", "Enter symbol to view (e.g. AAPL):", parent=self.root)
        if not symbol:
            self.log_message("Database viewer cancelled.")
            return
        # Inner async fetch
        def show_data(result):
            if not result:
                self.log_message(f"No data found for {symbol} in database.")
                return
            # Create window
            win = tk.Toplevel(self.root)
            win.title(f"Database Viewer: {symbol}")
            win.geometry("800x400")
            tree = ttk.Treeview(win, columns=("date","open","high","low","close","volume"), show="headings")
            for col in ["date","open","high","low","close","volume"]:
                tree.heading(col, text=col.title())
                tree.column(col, width=100)
            for bar in result:
                tree.insert("", tk.END, values=(bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume))
            tree.pack(fill=tk.BOTH, expand=True)
            # Add scrollbar
            scrollbar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Async DB fetch stub
        async def fetch_from_db():
            # If the connector/db exposes a method for this, use it; otherwise, return []
            if hasattr(self.ib_conn, "get_historical_data_from_db"):
                return await self.ib_conn.get_historical_data_from_db(symbol, limit=500)
            elif hasattr(self.ib_conn, "db") and hasattr(self.ib_conn.db, "get_historical_data"):
                return await self.ib_conn.db.get_historical_data(symbol, limit=500)
            else:
                return []
        future = self.run_async_task(fetch_from_db())
        if future:
            future.add_done_callback(lambda f: self.root.after(0, show_data, f.result()))
        
    def export_csv(self):
        """Export last fetched historical data to CSV and optionally create Jupyter notebook"""
        import csv
        import os
        from tkinter import filedialog, messagebox
        from ib_data_manager.utils.jupyter_generator import create_notebook_for_csv
        
        if not self.last_historical_data:
            self.log_message("No historical data to export. Please fetch data first.")
            return
        
        # Ask user to select export directory
        export_dir = filedialog.askdirectory(
            title="Select Export Directory",
            initialdir=self.settings.get("export_dir", os.path.expanduser("~/Documents"))
        )
        if not export_dir:
            self.log_message("Export cancelled.")
            return
        
        # Create organized folder structure
        symbol = self.last_historical_symbol or "unknown"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_folder = os.path.join(export_dir, f"{symbol}_export_{timestamp}")
        
        try:
            # Create export folder
            os.makedirs(export_folder, exist_ok=True)
            
            # Export CSV
            csv_filename = f"{symbol}_historical_data.csv"
            csv_path = os.path.join(export_folder, csv_filename)
            
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["date", "open", "high", "low", "close", "volume"])
                for bar in self.last_historical_data:
                    writer.writerow([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])
            
            self.log_message(f"CSV exported: {csv_path}")
            
            # Ask user if they want to create a Jupyter notebook
            create_notebook = messagebox.askyesno(
                "Create Analysis Notebook",
                f"CSV export successful!\n\nWould you like to create a Jupyter notebook for data analysis?\n\nThis will generate a ready-to-use notebook with:\n• Pre-loaded data as pandas DataFrame\n• Basic visualizations\n• Statistical analysis\n• Analysis templates",
                parent=self.root
            )
            
            if create_notebook:
                try:
                    # Create notebooks subfolder
                    notebooks_dir = os.path.join(export_folder, "notebooks")
                    
                    # Generate notebook
                    notebook_path = create_notebook_for_csv(
                        csv_path, 
                        symbol, 
                        output_dir=notebooks_dir
                    )
                    
                    self.log_message(f"Jupyter notebook created: {notebook_path}")
                    
                    # Ask if user wants to open the notebook
                    open_notebook = messagebox.askyesno(
                        "Open Notebook",
                        f"Notebook created successfully!\n\nWould you like to open it now?\n\nPath: {notebook_path}",
                        parent=self.root
                    )
                    
                    if open_notebook:
                        self._open_jupyter_notebook(notebook_path)
                        
                except Exception as e:
                    self.log_message(f"Failed to create Jupyter notebook: {e}")
                    messagebox.showerror(
                        "Notebook Creation Failed",
                        f"CSV export was successful, but notebook creation failed:\n\n{str(e)}",
                        parent=self.root
                    )
            
            # Show export summary
            self._show_export_summary(export_folder, csv_path, create_notebook)
            
        except Exception as e:
            self.log_message(f"Export failed: {e}")
            messagebox.showerror(
                "Export Failed",
                f"Failed to export data:\n\n{str(e)}",
                parent=self.root
            )
    
    def quick_export(self):
        """Quick export last fetched historical data to CSV"""
        import csv
        import os
        
        if not self.last_historical_data:
            self.log_message("No historical data to export. Please fetch data first.")
            return
        
        # Get export directory from settings
        export_dir = self.settings.get("export_dir", os.path.expanduser("~/Documents"))
        
        # Create organized folder structure
        symbol = self.last_historical_symbol or "unknown"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_folder = os.path.join(export_dir, f"{symbol}_export_{timestamp}")
        
        try:
            # Create export folder
            os.makedirs(export_folder, exist_ok=True)
            
            # Export CSV
            csv_filename = f"{symbol}_historical_data.csv"
            csv_path = os.path.join(export_folder, csv_filename)
            
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["date", "open", "high", "low", "close", "volume"])
                for bar in self.last_historical_data:
                    writer.writerow([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])
            
            self.log_message(f"CSV exported: {csv_path}")
            
        except Exception as e:
            self.log_message(f"Export failed: {e}")
    
    def _open_jupyter_notebook(self, notebook_path: str):
        """Open Jupyter notebook in default application"""
        import subprocess
        import sys
        import os
        
        try:
            if sys.platform.startswith('win'):
                # Windows
                os.startfile(notebook_path)
            elif sys.platform.startswith('darwin'):
                # macOS
                subprocess.run(['open', notebook_path])
            else:
                # Linux
                subprocess.run(['xdg-open', notebook_path])
                
            self.log_message("Opening notebook in default application...")
            
        except Exception as e:
            self.log_message(f"Could not open notebook automatically: {e}")
            messagebox.showinfo(
                "Notebook Created",
                f"Notebook created successfully but could not be opened automatically.\n\nPath: {notebook_path}\n\nYou can open it manually with Jupyter Lab/Notebook.",
                parent=self.root
            )
    
    def _show_export_summary(self, export_folder: str, csv_path: str, notebook_created: bool):
        """Show export summary dialog"""
        from tkinter import messagebox
        
        summary = f"Export completed successfully!\n\n"
        summary += f"Export folder: {export_folder}\n"
        summary += f"CSV file: {os.path.basename(csv_path)}\n"
        
        if notebook_created:
            summary += f"Jupyter notebook: Created in notebooks/ subfolder\n"
        
        summary += f"\nData exported: {len(self.last_historical_data)} bars for {self.last_historical_symbol}"
        
        messagebox.showinfo(
            "Export Summary",
            summary,
            parent=self.root
        )
        
    def log_message(self, message):
        """Add message to output text area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
        self.output_text.update_idletasks()
        
    def on_closing(self):
        """Handle window closing"""
        # Clean up async resources
        if self.loop and self.thread and self.thread.is_alive():
            self.loop.call_soon_threadsafe(self.loop.stop)
        self.root.destroy()
        
    def load_settings(self):
        """Load settings from file"""
        try:
            with open("settings.json", "r") as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {}
            
    def save_settings(self):
        """Save settings to file"""
        with open("settings.json", "w") as f:
            json.dump(self.settings, f)

    def update_max_duration_label(self, event=None):
        """Update max allowed duration helper label based on selected bar size"""
        bar_size = self.bar_size.get()
        if bar_size == "1 sec":
            max_duration = "1 D"
        elif bar_size in ["5 secs", "10 secs", "15 secs", "30 secs"]:
            max_duration = "2 D"
        elif bar_size in ["1 min", "2 mins", "3 mins", "5 mins", "10 mins", "15 mins", "30 mins"]:
            max_duration = "1 W"
        elif bar_size in ["1 hour", "1 day"]:
            max_duration = "1 M"
        elif bar_size in ["1 week", "1 month"]:
            max_duration = "1 Y"
        else:
            max_duration = "Unknown"
        self.max_duration_label.config(text=f"Max allowed: {max_duration} for {bar_size} bars", foreground="blue")

    def on_data_type_change(self):
        """Handle data type change"""
        data_type = self.data_type.get()
        if data_type == "historical":
            self.historical_frame.grid()
        else:
            self.historical_frame.grid_remove()

    def on_date_mode_change(self):
        """Handle date mode change"""
        date_mode = self.date_mode.get()
        if date_mode == "duration":
            self.duration_frame.grid()
            self.daterange_frame.grid_remove()
        elif date_mode == "daterange":
            self.duration_frame.grid_remove()
            self.daterange_frame.grid()

    def pick_date(self, entry):
        """Pick date using calendar dialog"""
        import calendar
        import tkinter as tk
        from tkinter import ttk
        from datetime import datetime
        
        def select_date():
            try:
                year_val = int(year.get())
                month_val = int(month.get())
                day_val = int(day.get())
                date = f"{year_val}-{month_val:02d}-{day_val:02d}"
                entry.delete(0, tk.END)
                entry.insert(0, date)
                win.destroy()
            except ValueError as e:
                messagebox.showerror("Invalid Date", f"Please enter valid numbers for year, month, and day.\nError: {e}", parent=win)
        
        win = tk.Toplevel(self.root)
        win.title("Select Date")
        
        year = tk.StringVar(value=datetime.now().strftime("%Y"))
        month = tk.StringVar(value=datetime.now().strftime("%m"))
        day = tk.StringVar(value=datetime.now().strftime("%d"))
        
        ttk.Label(win, text="Year:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(win, textvariable=year, width=5).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(win, text="Month:").grid(row=0, column=2, padx=5, pady=5)
        ttk.Entry(win, textvariable=month, width=3).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(win, text="Day:").grid(row=0, column=4, padx=5, pady=5)
        ttk.Entry(win, textvariable=day, width=3).grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Button(win, text="Select", command=select_date).grid(row=1, column=0, columnspan=6, padx=5, pady=5)

    def select_front_contract(self):
        """Select front contract for futures"""
        symbol = self.symbol_entry.get()
        if not symbol:
            messagebox.showwarning("Warning", "Please enter a symbol first")
            return
            
        if not self.ib_conn.connected:
            messagebox.showwarning("Warning", "Please connect to IB Gateway first")
            return
            
        # Set contract type to FUT if not already
        self.contract_type.set("FUT")
        self.on_contract_type_change()
        
        # Set exchange to CME for MES (based on debug results)
        if symbol.upper() == "MES":
            self.exchange_entry.delete(0, tk.END)
            self.exchange_entry.insert(0, "CME")
            
        self.log_message(f"Finding front contract for {symbol}...")
        
        async def get_front_contract():
            try:
                # Get front contract for the symbol
                exchange = self.exchange_entry.get() or "SMART"
                currency = self.currency_entry.get() or "USD"
                
                front_contract = await self.ib_conn.get_front_contract(symbol, exchange, currency)
                if front_contract:
                    expiry = front_contract.lastTradeDateOrContractMonth
                    self.expiry_entry.delete(0, tk.END)
                    self.expiry_entry.insert(0, expiry)
                    self.log_message(f"✅ Front contract expiry set to: {expiry}")
                    
                    # Also update exchange to match the found contract
                    if front_contract.exchange != exchange:
                        self.exchange_entry.delete(0, tk.END)
                        self.exchange_entry.insert(0, front_contract.exchange)
                        self.log_message(f"📍 Exchange updated to: {front_contract.exchange}")
                    
                    return expiry
                else:
                    self.log_message(f"❌ No futures contracts found for {symbol}")
                    return None
            except Exception as e:
                self.log_message(f"❌ Error finding front contract: {str(e)}")
                return None
                
        future = self.run_async_task(get_front_contract())
        if future:
            future.add_done_callback(lambda f: None)  # Result already handled in async function

    def browse_futures_contracts(self):
        """Browse and select from available futures contracts"""
        symbol = self.symbol_entry.get()
        if not symbol:
            messagebox.showwarning("Warning", "Please enter a symbol first")
            return
            
        if not self.ib_conn.connected:
            messagebox.showwarning("Warning", "Please connect to IB Gateway first")
            return
            
        # Set contract type to FUT if not already
        self.contract_type.set("FUT")
        self.on_contract_type_change()
        
        # Set exchange to CME for MES (based on debug results)
        if symbol.upper() == "MES":
            self.exchange_entry.delete(0, tk.END)
            self.exchange_entry.insert(0, "CME")
            
        self.log_message(f"Browsing contracts for {symbol}...")
        
        async def get_contracts():
            try:
                exchange = self.exchange_entry.get() or "SMART"
                currency = self.currency_entry.get() or "USD"
                
                contracts = await self.ib_conn.get_futures_contracts(symbol, exchange, currency)
                if contracts:
                    # Update exchange to match found contracts
                    if contracts and contracts[0].exchange != exchange:
                        self.exchange_entry.delete(0, tk.END)
                        self.exchange_entry.insert(0, contracts[0].exchange)
                        self.log_message(f"📍 Exchange updated to: {contracts[0].exchange}")
                    
                    # Create selection dialog on UI thread
                    self.root.after(0, lambda: self.show_contract_selection_dialog(contracts))
                else:
                    self.log_message(f"❌ No futures contracts found for {symbol}")
            except Exception as e:
                self.log_message(f"❌ Error browsing contracts: {str(e)}")
                
        future = self.run_async_task(get_contracts())
        if future:
            future.add_done_callback(lambda f: None)
            
    def show_contract_selection_dialog(self, contracts):
        """Show dialog to select from available contracts"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Futures Contract")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"Available Contracts for {self.symbol_entry.get()}:", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Add info about front contract
        info_frame = ttk.Frame(dialog)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(info_frame, text="💡 Front contract (nearest expiry) is highlighted", 
                 foreground="blue", font=("Arial", 9)).pack()
        
        # Create frame for listbox and scrollbar
        list_frame = ttk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create listbox with contracts
        listbox = tk.Listbox(list_frame, height=15, font=("Courier", 10))
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        contract_map = {}
        for i, contract in enumerate(contracts):
            expiry = contract.lastTradeDateOrContractMonth
            local_symbol = getattr(contract, 'localSymbol', 'N/A')
            front_indicator = " ← FRONT" if i == 0 else ""
            display_text = f"{contract.symbol:<6} {expiry:<10} {local_symbol:<8} ({contract.exchange}){front_indicator}"
            listbox.insert(tk.END, display_text)
            contract_map[i] = expiry
            
        # Select front contract by default and highlight it
        if contracts:
            listbox.selection_set(0)  # Select first (front) contract by default
            listbox.activate(0)
            
        def select_contract():
            selection = listbox.curselection()
            if selection:
                selected_index = selection[0]
                expiry = contract_map[selected_index]
                selected_contract = contracts[selected_index]
                
                self.expiry_entry.delete(0, tk.END)
                self.expiry_entry.insert(0, expiry)
                
                # Update exchange to match selected contract
                self.exchange_entry.delete(0, tk.END)
                self.exchange_entry.insert(0, selected_contract.exchange)
                
                front_info = " (FRONT CONTRACT)" if selected_index == 0 else ""
                self.log_message(f"✅ Selected contract: {expiry}{front_info}")
                dialog.destroy()
            else:
                messagebox.showwarning("Warning", "Please select a contract", parent=dialog)
                
        # Button frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Select Contract", command=select_contract).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Add double-click support
        listbox.bind("<Double-Button-1>", lambda e: select_contract())
        
def main():
    """Main function"""
    root = tk.Tk()
    app = AsyncIBDataManager(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
