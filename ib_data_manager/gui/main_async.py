"""
Async Interactive Brokers Data Manager
A clean interface to pull data from IB Gateway and store it in a database using async operations
"""

import asyncio
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import logging
from ib_data_manager.api.async_ib_connector import AsyncIBConnector

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
        
        # Expiry (for futures)
        ttk.Label(request_frame, text="Expiry:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.expiry_entry = ttk.Entry(request_frame, width=15)
        self.expiry_entry.grid(row=2, column=1, padx=5, pady=5)
        self.expiry_entry.configure(state="disabled")
        
        # Data type selection
        self.data_type = tk.StringVar(value="historical")
        data_type_frame = ttk.LabelFrame(request_frame, text="Data Type", padding="5")
        data_type_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Radiobutton(data_type_frame, text="Historical Data", variable=self.data_type, value="historical").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(data_type_frame, text="Real-time Quotes", variable=self.data_type, value="realtime").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(data_type_frame, text="Account Info", variable=self.data_type, value="account").grid(row=0, column=2, padx=5)
        ttk.Radiobutton(data_type_frame, text="Market Depth (Level 2)", variable=self.data_type, value="market_depth").grid(row=0, column=3, padx=5)
        
        # --- Historical Data Settings ---
        self.hist_frame = ttk.LabelFrame(main_frame, text="Historical Data Settings", padding="5")
        self.hist_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Duration
        ttk.Label(self.hist_frame, text="Duration:").grid(row=0, column=0, padx=5, pady=5)
        self.duration_entry = ttk.Entry(self.hist_frame, width=15)
        self.duration_entry.insert(0, "1 D")
        self.duration_entry.grid(row=0, column=1, padx=5, pady=5)
        self.duration_entry_tooltip = ttk.Label(self.hist_frame, text="e.g. 1 D, 6 M, 2 Y, 3 W", foreground="gray")
        self.duration_entry_tooltip.grid(row=1, column=0, columnspan=2, padx=5, sticky=tk.W)

        # Bar size (expanded to all IBKR-supported options)
        ttk.Label(self.hist_frame, text="Bar Size:").grid(row=0, column=2, padx=5, pady=5)
        self.bar_size = ttk.Combobox(
            self.hist_frame,
            values=[
                "1 sec", "5 secs", "10 secs", "15 secs", "30 secs", "1 min", "2 mins", "3 mins", "5 mins", "10 mins", "15 mins", "30 mins", "1 hour", "1 day", "1 week", "1 month"
            ],
            width=10
        )
        self.bar_size.set("1 min")
        self.bar_size.grid(row=0, column=3, padx=5, pady=5)
        self.bar_size_tooltip = ttk.Label(self.hist_frame, text="e.g. 1 min, 1 day, 1 week", foreground="gray")
        self.bar_size_tooltip.grid(row=1, column=2, columnspan=2, padx=5, sticky=tk.W)

        # Max allowed duration helper label (updates with bar size)
        self.max_duration_label = ttk.Label(self.hist_frame, text="Max allowed: 1 week for 1 min bars", foreground="blue")
        self.max_duration_label.grid(row=2, column=0, columnspan=4, padx=5, sticky=tk.W)
        self.bar_size.bind("<<ComboboxSelected>>", self.update_max_duration_label)

        self.update_max_duration_label()
        # --- End Historical Data Settings ---

        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Fetch Data", command=self.fetch_data).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="View Database", command=self.view_database).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Export CSV", command=self.export_csv).grid(row=0, column=2, padx=5)
        
        # Output text area
        self.output_text = tk.Text(main_frame, height=15, width=80)
        self.output_text.grid(row=4, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for text area
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.output_text.yview)
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
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
        """Export last fetched historical data to CSV"""
        import csv
        from tkinter import filedialog
        if not self.last_historical_data:
            self.log_message("No historical data to export. Please fetch data first.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save CSV file"
        )
        if not file_path:
            self.log_message("CSV export cancelled.")
            return
        try:
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["date", "open", "high", "low", "close", "volume"])
                for bar in self.last_historical_data:
                    writer.writerow([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])
            self.log_message(f"CSV exported: {file_path}")
        except Exception as e:
            self.log_message(f"CSV export failed: {e}")
        
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


def main():
    """Main function"""
    root = tk.Tk()
    app = AsyncIBDataManager(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
