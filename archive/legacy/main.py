"""
Interactive Brokers Data Manager
A clean interface to pull data from IB Gateway and store it in a database
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
from datetime import datetime
from ib_data_manager.db import database
from ib_data_manager.api import ib_connector
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ib_data_manager.log'),
        logging.StreamHandler()
    ]
)

class IBDataManager:
    def __init__(self, root):
        self.root = root
        self.root.title("IB Data Manager")
        self.root.geometry("800x600")

        # Initialize IB connector
        self.ib_conn = ib_connector.IBConnector()

        # Initialize database
        self.db = database.DataManager()

        # Create GUI
        self.create_widgets()

    def on_futures_details_change(self, event=None):
        contract_type = self.contract_type.get()
        if contract_type == "FUT":
            self.update_futures_expiries()

    def update_futures_expiries(self):
        symbol = self.symbol_entry.get().strip().upper()
        exchange = self.exchange_entry.get().strip().upper()
        if not symbol or not exchange:
            self.expiry_combo.set("")
            self.expiry_combo.configure(state="disabled")
            return
        self.expiry_combo.set("Loading...")
        self.expiry_combo.configure(state="disabled")
        def fetch_expiries():
            try:
                from ib_insync import Future
                contract = Future(symbol, exchange=exchange)
                contracts = self.ib_conn.ib.reqContractDetails(contract)
                expiries = sorted({c.contract.lastTradeDateOrContractMonth[:6] for c in contracts if hasattr(c.contract, 'lastTradeDateOrContractMonth')})
                self.root.after(0, lambda: self._set_expiry_combo(expiries))
            except Exception as e:
                self.root.after(0, lambda: self._set_expiry_combo([], error=str(e)))
        import threading
        threading.Thread(target=fetch_expiries, daemon=True).start()

    def _set_expiry_combo(self, expiries, error=None):
        if error:
            self.expiry_combo['values'] = []
            self.expiry_combo.set("Error")
            self.expiry_combo.configure(state="disabled")
            self.log_message(f"Error fetching expiries: {error}")
        elif expiries:
            self.expiry_combo['values'] = expiries
            self.expiry_combo.set(expiries[0])
            self.expiry_combo.configure(state="readonly")
        else:
            self.expiry_combo['values'] = []
            self.expiry_combo.set("")
            self.expiry_combo.configure(state="disabled")

    def on_contract_type_change(self, event=None):
        contract_type = self.contract_type.get()
        if contract_type == "FUT":
            self.expiry_combo.configure(state="readonly")
            self.exchange_entry.delete(0, tk.END)
            self.exchange_entry.insert(0, "CME")
            self.update_futures_expiries()
        else:
            self.expiry_combo.set("")
            self.expiry_combo.configure(state="disabled")
            self.exchange_entry.delete(0, tk.END)
            self.exchange_entry.insert(0, "SMART")
        
    def create_widgets(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

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

        # Date range
        ttk.Label(request_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.start_date_entry = ttk.Entry(request_frame, width=12)
        self.start_date_entry.grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(request_frame, text="End Date (YYYY-MM-DD):").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.end_date_entry = ttk.Entry(request_frame, width=12)
        self.end_date_entry.grid(row=0, column=5, padx=5, pady=5)

        # Bar size selection
        ttk.Label(request_frame, text="Bar Size:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.bar_size_var = tk.StringVar()
        self.bar_size_combo = ttk.Combobox(request_frame, textvariable=self.bar_size_var, width=12, state="readonly")
        self.bar_size_combo['values'] = ("1 min", "5 mins", "10 mins", "15 mins", "30 mins", "1 hour", "1 day")
        self.bar_size_combo.current(0)
        self.bar_size_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(request_frame, text="Symbol:").grid(row=0, column=0, padx=5, pady=5)
        self.symbol_entry = ttk.Entry(request_frame)
        self.symbol_entry.insert(0, "AAPL")
        self.symbol_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Contract type
        ttk.Label(request_frame, text="Type:").grid(row=0, column=2, padx=5, pady=5)
        self.contract_type = ttk.Combobox(request_frame, values=["STK", "FUT", "OPT", "CASH", "BOND"])
        self.contract_type.set("STK")
        self.contract_type.grid(row=0, column=3, padx=5, pady=5)
        self.contract_type.bind("<<ComboboxSelected>>", self.on_contract_type_change)
        # Bind expiry update for futures
        self.symbol_entry.bind('<FocusOut>', self.on_futures_details_change)
        self.exchange_entry.bind('<FocusOut>', self.on_futures_details_change)

        # Expiry (for futures)
        ttk.Label(request_frame, text="Expiry (YYYYMM):").grid(row=0, column=4, padx=5, pady=5)
        self.expiry_var = tk.StringVar()
        self.expiry_combo = ttk.Combobox(request_frame, textvariable=self.expiry_var, width=10, state="disabled")
        self.expiry_combo.grid(row=0, column=5, padx=5, pady=5)

        # Exchange
        ttk.Label(request_frame, text="Exchange:").grid(row=1, column=0, padx=5, pady=5)
        self.exchange_entry = ttk.Entry(request_frame)
        self.exchange_entry.insert(0, "SMART")
        self.exchange_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Currency
        ttk.Label(request_frame, text="Currency:").grid(row=1, column=2, padx=5, pady=5)
        self.currency_entry = ttk.Entry(request_frame)
        self.currency_entry.insert(0, "USD")
        self.currency_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Date range
        ttk.Label(request_frame, text="Start Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
        self.start_date_entry = ttk.Entry(request_frame, width=12)
        self.start_date_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(request_frame, text="End Date (YYYY-MM-DD):").grid(row=2, column=2, padx=5, pady=5)
        self.end_date_entry = ttk.Entry(request_frame, width=12)
        self.end_date_entry.grid(row=2, column=3, padx=5, pady=5)

        # Bar size selection
        ttk.Label(request_frame, text="Bar Size:").grid(row=3, column=0, padx=5, pady=5)
        self.bar_size_var = tk.StringVar()
        self.bar_size_combo = ttk.Combobox(request_frame, textvariable=self.bar_size_var, width=12, state="readonly")
        self.bar_size_combo['values'] = ("1 min", "5 mins", "10 mins", "15 mins", "30 mins", "1 hour", "1 day")
        self.bar_size_combo.current(0)
        self.bar_size_combo.grid(row=3, column=1, padx=5, pady=5)

        # Fetch button
        ttk.Button(request_frame, text="Fetch Historical Data", command=self.fetch_historical_data).grid(row=3, column=3, padx=5, pady=5)

        # Status label
        self.hist_status_label = ttk.Label(request_frame, text="", foreground="blue")
        self.hist_status_label.grid(row=3, column=4, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Data type selection
        data_type_frame = ttk.LabelFrame(main_frame, text="Data Type", padding="5")
        data_type_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.data_type = tk.StringVar(value="historical")
        ttk.Radiobutton(data_type_frame, text="Historical Data", variable=self.data_type, value="historical").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(data_type_frame, text="Real-time Quotes", variable=self.data_type, value="realtime").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(data_type_frame, text="Account Info", variable=self.data_type, value="account").grid(row=0, column=2, padx=5)
        ttk.Radiobutton(data_type_frame, text="Market Depth (Level 2)", variable=self.data_type, value="market_depth").grid(row=0, column=3, padx=5)
        
        # Historical data settings
        self.hist_frame = ttk.LabelFrame(main_frame, text="Historical Data Settings", padding="5")
        self.hist_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Duration
        ttk.Label(self.hist_frame, text="Duration:").grid(row=0, column=0, padx=5, pady=5)
        self.duration_entry = ttk.Entry(self.hist_frame)
        self.duration_entry.insert(0, "1 D")
        self.duration_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Bar size
        ttk.Label(self.hist_frame, text="Bar Size:").grid(row=0, column=2, padx=5, pady=5)
        self.bar_size = ttk.Combobox(self.hist_frame, values=["1 min", "5 mins", "15 mins", "30 mins", "1 hour", "1 day"])
        self.bar_size.set("1 min")
        self.bar_size.grid(row=0, column=3, padx=5, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Fetch Data", command=self.fetch_data).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="View Database", command=self.view_database).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Export CSV", command=self.export_csv).grid(row=0, column=2, padx=5)
        
        # Output text area
        self.output_text = tk.Text(main_frame, height=15, width=80)
        self.output_text.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Scrollbar for text area
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.output_text.yview)
        scrollbar.grid(row=5, column=2, sticky=(tk.N, tk.S))
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
    def connect_ib(self):
        """Connect to IB Gateway"""
        try:
            if self.ib_conn.connect():
                self.status_label.config(text="Connected", foreground="green")
                self.log_message("Successfully connected to IB Gateway")
            else:
                self.status_label.config(text="Failed to Connect", foreground="red")
                self.log_message("Failed to connect to IB Gateway")
        except Exception as e:
            self.log_message(f"Connection error: {str(e)}")
            messagebox.showerror("Connection Error", str(e))
            
    def disconnect_ib(self):
        """Disconnect from IB Gateway"""
        try:
            self.ib_conn.disconnect()
            self.status_label.config(text="Disconnected", foreground="red")
            self.log_message("Disconnected from IB Gateway")
        except Exception as e:
            self.log_message(f"Disconnection error: {str(e)}")
            
    def fetch_data(self):
        """Fetch data based on user selection"""
        if not self.ib_conn.is_connected():
            messagebox.showwarning("Warning", "Please connect to IB Gateway first")
            return

        # Get contract details
        symbol = self.symbol_entry.get()
        contract_type = self.contract_type.get()
        exchange = self.exchange_entry.get()
        currency = self.currency_entry.get()
        expiry = self.expiry_entry.get() if contract_type == "FUT" else None

        # Create thread to fetch data
        thread = threading.Thread(target=self._fetch_data_thread, 
                                args=(symbol, contract_type, exchange, currency, expiry))
        thread.daemon = True
        thread.start()
        
    def _fetch_data_thread(self, symbol, contract_type, exchange, currency, expiry=None):
        """Thread function to fetch data"""
        # Ensure event loop is started for ib_insync in this thread
        from ib_insync import util
        util.startLoop()
        try:
            data_type = self.data_type.get()
            
            if data_type == "historical":
                duration = self.duration_entry.get()
                bar_size = self.bar_size.get()
                self.log_message(f"Fetching historical data for {symbol}...")
                
                data = self.ib_conn.get_historical_data(symbol, contract_type, exchange, 
                                                      currency, duration, bar_size, expiry)
                                                      
                if data:
                    # Save to database
                    self.db.save_historical_data(symbol, data)
                    self.log_message(f"Saved {len(data)} bars for {symbol}")
                    
                    # Display data
                    self.display_historical_data(data)
                else:
                    self.log_message("No data received")
                    
            elif data_type == "realtime":
                self.log_message(f"Starting real-time quotes for {symbol}...")
                self.ib_conn.start_realtime_quotes(symbol, contract_type, exchange, 
                                                 currency, self.on_realtime_update, expiry)
                                                 
            elif data_type == "account":
                self.log_message("Fetching account information...")
                account_info = self.ib_conn.get_account_info()
                if account_info:
                    self.display_account_info(account_info)
                    
            elif data_type == "market_depth":
                self.log_message(f"Starting Level 2 (market depth) for {symbol}...")
                self.ib_conn.start_market_depth(symbol, contract_type, exchange, currency, num_rows=5, callback=self.on_market_depth_update, expiry=expiry)
                self.log_message("Subscribed to market depth updates. Watch this area for order book changes.")
                
        except Exception as e:
            self.log_message(f"Error fetching data: {str(e)}")
            logging.error(f"Fetch data error: {str(e)}")
            
    def on_realtime_update(self, ticker):
        """Callback for real-time updates"""
        try:
            # Save to database
            self.db.save_realtime_quote(ticker.contract.symbol, ticker)
            
            # Display update
            self.log_message(f"{ticker.contract.symbol} - Bid: {ticker.bid}, Ask: {ticker.ask}, Last: {ticker.last}")
        except Exception as e:
            logging.error(f"Real-time update error: {str(e)}")

    def on_market_depth_update(self, ticker):
        """Callback for Level 2 (market depth) updates"""
        try:
            # Format order book for display
            bids = [(d.price, d.size) for d in ticker.domBids]
            asks = [(d.price, d.size) for d in ticker.domAsks]
            symbol = ticker.contract.symbol if hasattr(ticker.contract, 'symbol') else str(ticker.contract)
            msg = f"{symbol} Market Depth\nBids: {bids}\nAsks: {asks}"
            self.log_message(msg)
        except Exception as e:
            logging.error(f"Market depth update error: {str(e)}")

            
    def display_historical_data(self, data):
        """Display historical data in the output area"""
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Time\t\tOpen\tHigh\tLow\tClose\tVolume\n")
        self.output_text.insert(tk.END, "-" * 70 + "\n")
        
        for bar in data:
            self.output_text.insert(tk.END, 
                f"{bar.date}\t{bar.open}\t{bar.high}\t{bar.low}\t{bar.close}\t{bar.volume}\n")
                
    def display_account_info(self, account_info):
        """Display account information"""
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Account Information\n")
        self.output_text.insert(tk.END, "-" * 40 + "\n")
        
        for key, value in account_info.items():
            self.output_text.insert(tk.END, f"{key}: {value}\n")
            
    def view_database(self):
        """Open database viewer window"""
        db_window = tk.Toplevel(self.root)
        db_window.title("Database Viewer")
        db_window.geometry("800x600")
        
        # Create notebook for different tables
        notebook = ttk.Notebook(db_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Historical data tab
        hist_frame = ttk.Frame(notebook)
        notebook.add(hist_frame, text="Historical Data")
        
        # Create treeview for historical data
        columns = ("ID", "Symbol", "Date", "Open", "High", "Low", "Close", "Volume")
        tree = ttk.Treeview(hist_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
            
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Load data from database
        data = self.db.get_all_historical_data()
        for row in data:
            tree.insert("", tk.END, values=row)
            
        # Real-time quotes tab
        rt_frame = ttk.Frame(notebook)
        notebook.add(rt_frame, text="Real-time Quotes")
        
        # Create treeview for real-time data
        rt_columns = ("ID", "Symbol", "Time", "Bid", "Ask", "Last", "Volume")
        rt_tree = ttk.Treeview(rt_frame, columns=rt_columns, show="headings")
        
        for col in rt_columns:
            rt_tree.heading(col, text=col)
            rt_tree.column(col, width=100)
            
        rt_tree.pack(fill=tk.BOTH, expand=True)
        
        # Load real-time data from database
        rt_data = self.db.get_all_realtime_quotes()
        for row in rt_data:
            rt_tree.insert("", tk.END, values=row)

        # Market Depth (Level 2) tab
        depth_frame = ttk.Frame(notebook)
        notebook.add(depth_frame, text="Market Depth (Level 2)")

        # Controls for Level 2 collection
        ttk.Label(depth_frame, text="Symbols (comma-separated):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.depth_symbols_entry = ttk.Entry(depth_frame, width=40)
        self.depth_symbols_entry.grid(row=0, column=1, padx=5, pady=5)
        self.depth_status_label = ttk.Label(depth_frame, text="Status: Idle", foreground="blue")
        self.depth_status_label.grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(depth_frame, text="Start Collection", command=self.start_depth_collection).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Button(depth_frame, text="Stop Collection", command=self.stop_depth_collection).grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)

        # Treeview for recent market depth data
        depth_columns = ("ID", "Symbol", "Timestamp", "Side", "Position", "Price", "Size", "Market Maker", "Operation")
        self.depth_tree = ttk.Treeview(depth_frame, columns=depth_columns, show="headings", height=12)
        for col in depth_columns:
            self.depth_tree.heading(col, text=col)
            self.depth_tree.column(col, width=90)
        self.depth_tree.grid(row=2, column=0, columnspan=3, padx=5, pady=10, sticky=(tk.W, tk.E))
        ttk.Button(depth_frame, text="Refresh Data", command=self.refresh_depth_table).grid(row=3, column=2, padx=5, pady=5, sticky=tk.E)

    def export_csv(self):
        """Export data to CSV"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.db.export_to_csv(filename)
                self.log_message(f"Data exported to {filename}")
                messagebox.showinfo("Success", "Data exported successfully!")
            except Exception as e:
                self.log_message(f"Export error: {str(e)}")
                messagebox.showerror("Export Error", str(e))
                
    def log_message(self, message):
        """Add message to output text area"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if hasattr(self, 'output_text'):
            self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.output_text.see(tk.END)
        logging.info(message)

    def fetch_historical_data(self):
        symbol = self.symbol_entry.get().strip().upper()
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        bar_size = self.bar_size_var.get()
        contract_type = self.contract_type.get()
        exchange = self.exchange_entry.get().strip()
        currency = self.currency_entry.get().strip()
        expiry = self.expiry_var.get().strip() if contract_type == "FUT" else None
        duration = self.duration_entry.get().strip() if hasattr(self, 'duration_entry') else "1 D"
        if not symbol:
            self.log_message("No symbol entered for historical data fetch.")
            messagebox.showerror("Input Error", "Please enter a symbol.")
            return
        if not start_date or not end_date:
            self.log_message("Start or end date missing.")
            messagebox.showerror("Input Error", "Please enter both start and end dates.")
            return
        try:
            self.hist_status_label.config(text="Fetching data...", foreground="orange")
            self.root.update_idletasks()
            # Add progress bar if not present
            if not hasattr(self, 'hist_progress'):
                self.hist_progress = ttk.Progressbar(self.hist_frame, orient="horizontal", length=200, mode="determinate")
                self.hist_progress.grid(row=2, column=0, columnspan=4, pady=5)
            self.hist_progress['value'] = 0
            self.hist_progress.update()
            # Run in a thread to avoid GUI freeze
            threading.Thread(
                target=self._fetch_historical_data_thread_with_progress,
                args=(symbol, start_date, end_date, bar_size, contract_type, exchange, currency, expiry, duration),
                daemon=True
            ).start()

        except Exception as e:
            self.hist_status_label.config(text="Error", foreground="red")
            self.log_message(f"Error starting historical fetch: {str(e)}")
            messagebox.showerror("Error", str(e))

    def _fetch_historical_data_thread_with_progress(self, symbol, start_date, end_date, bar_size, contract_type=None, exchange=None, currency=None, expiry=None, duration="1 D"):
        try:
            from ib_insync import util
            util.startLoop()
            bar_size_map = {
                "1 min": "1 min",
                "5 mins": "5 mins",
                "10 mins": "10 mins",
                "15 mins": "15 mins",
                "30 mins": "30 mins",
                "1 hour": "1 hour",
                "1 day": "1 day"
            }
            ib_bar_size = bar_size_map.get(bar_size, "1 min")
            from dateutil import parser
            dt_start = parser.parse(start_date)
            dt_end = parser.parse(end_date)
            total_days = max((dt_end - dt_start).days, 1)
            if hasattr(self, 'hist_progress'):
                self.hist_progress['maximum'] = total_days
                self.hist_progress['value'] = 0
                self.hist_progress.update()
            bars_all = []
            dt_cursor = dt_end
            steps = 0
            error_occurred = False
            while dt_cursor > dt_start:
                try:
                    end_str = dt_cursor.strftime("%Y%m%d %H:%M:%S")
                    bars = self.ib_conn.get_historical_data(
                        symbol,
                        contract_type or "STK",
                        exchange or "SMART",
                        currency or "USD",
                        duration,
                        ib_bar_size,
                        expiry
                    )
                    if not bars:
                        break
                    for bar in bars:
                        self.db.insert_historical_data(
                            symbol=symbol,
                            date=bar.date,
                            open=bar.open,
                            high=bar.high,
                            low=bar.low,
                            close=bar.close,
                            volume=bar.volume,
                            average=getattr(bar, 'average', None),
                            bar_count=getattr(bar, 'barCount', None)
                        )
                    bars_all.extend(bars)
                    dt_cursor = parser.parse(bars[0].date)
                    steps += 1
                    if hasattr(self, 'hist_progress'):
                        self.hist_progress['value'] = steps
                        self.hist_progress.update()
                    self.hist_status_label.config(text=f"Progress: {steps}/{total_days} days", foreground="orange")
                except Exception as e:
                    error_occurred = True
                    self.hist_status_label.config(text="Error fetching data", foreground="red")
                    self.log_message(f"Error fetching chunk: {str(e)}")
                    break
            if bars_all and not error_occurred:
                self.hist_status_label.config(text="Fetch complete!", foreground="green")
                self.log_message(f"Fetched {len(bars_all)} bars for {symbol} [{ib_bar_size}] from {start_date} to {end_date}")
            elif not bars_all and not error_occurred:
                self.hist_status_label.config(text="No data found.", foreground="red")
                self.log_message(f"No data returned for {symbol} [{ib_bar_size}] from {start_date} to {end_date}")
            if hasattr(self, 'hist_progress'):
                self.hist_progress['value'] = 0
                self.hist_progress.update()
        except Exception as e:
            self.hist_status_label.config(text="Error", foreground="red")
            self.log_message(f"Error fetching historical data: {str(e)}")

    def start_depth_collection(self):
        symbols_str = self.depth_symbols_entry.get()
        symbols = [s.strip().upper() for s in symbols_str.split(',') if s.strip()]
        if not symbols:
            self.log_message("No symbols entered for Level 2 collection.")
            messagebox.showerror("Input Error", "Please enter at least one symbol.")
            return
        try:
            self.ib_conn.automate_market_depth_collection(symbols)
            self.depth_status_label.config(text=f"Status: Collecting ({', '.join(symbols)})", foreground="green")
            self.log_message(f"Started Level 2 collection for: {', '.join(symbols)}")
        except Exception as e:
            self.log_message(f"Error starting Level 2 collection: {str(e)}")
            messagebox.showerror("Error", str(e))

    def stop_depth_collection(self):
        try:
            self.ib_conn.stop_automated_market_depth()
            self.depth_status_label.config(text="Status: Idle", foreground="blue")
            self.log_message("Stopped Level 2 collection.")
        except Exception as e:
            self.log_message(f"Error stopping Level 2 collection: {str(e)}")
            messagebox.showerror("Error", str(e))

    def refresh_depth_table(self):
        # Show recent market depth data for entered symbols
        symbols_str = self.depth_symbols_entry.get()
        symbols = [s.strip().upper() for s in symbols_str.split(',') if s.strip()]
        try:
            with self.db:
                with self.db:
                    self.depth_tree.delete(*self.depth_tree.get_children())
                    for symbol in symbols:
                        query = """
                        SELECT id, symbol, timestamp, side, position, price, size, market_maker, operation
                        FROM market_depth
                        WHERE symbol = ?
                        ORDER BY timestamp DESC
                        LIMIT 25
                        """
                        conn = self.db
                        import sqlite3
                        with sqlite3.connect(conn.db_path) as c:
                            cur = c.cursor()
                            cur.execute(query, (symbol,))
                            rows = cur.fetchall()
                            for row in rows:
                                self.depth_tree.insert("", tk.END, values=row)
            self.log_message(f"Refreshed Level 2 data table for: {', '.join(symbols)}")
        except Exception as e:
            self.log_message(f"Error refreshing Level 2 table: {str(e)}")
            messagebox.showerror("Error", str(e))

    def on_closing(self):
        """Handle window closing"""
        if self.ib_conn.is_connected():
            self.ib_conn.disconnect()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = IBDataManager(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
