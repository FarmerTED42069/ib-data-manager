"""
Example of how to integrate the AsyncIBConnector with a GUI application
This shows the pattern for properly handling async operations in a GUI context
"""

import asyncio
import threading
import tkinter as tk
from tkinter import ttk, filedialog
import logging
from ib_data_manager.api.async_ib_connector import AsyncIBConnector
from datetime import datetime
import pandas as pd
import pandas_ta as ta

class AsyncGUIExample:
    """Example GUI application showing async integration"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Async IB Connector Example")
        self.root.geometry("600x400")
        
        # Async connector
        self.ib_connector = AsyncIBConnector()
        
        # Async loop (run in separate thread)
        self.loop = None
        self.thread = None
        
        # Create GUI
        self.create_widgets()
        
        # Start the async loop
        self.start_async_loop()
        
    def create_widgets(self):
        """Create GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Connection controls
        conn_frame = ttk.LabelFrame(main_frame, text="Connection", padding="5")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(conn_frame, text="Connect", command=self.connect).grid(row=0, column=0, padx=5)
        ttk.Button(conn_frame, text="Disconnect", command=self.disconnect).grid(row=0, column=1, padx=5)
        
        self.status_label = ttk.Label(conn_frame, text="Disconnected", foreground="red")
        self.status_label.grid(row=0, column=2, padx=10)
        
        # Data controls
        data_frame = ttk.LabelFrame(main_frame, text="Data Operations", padding="5")
        data_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(data_frame, text="Get Account Info", command=self.get_account_info).grid(row=0, column=0, padx=5)
        ttk.Button(data_frame, text="Get Positions", command=self.get_positions).grid(row=0, column=1, padx=5)
        
        # Symbol input
        ttk.Label(data_frame, text="Symbol:").grid(row=1, column=0, padx=5, pady=5)
        self.symbol_entry = ttk.Entry(data_frame, width=10)
        self.symbol_entry.insert(0, "AAPL")
        self.symbol_entry.grid(row=1, column=1, padx=5, pady=5)

        # Duration input
        ttk.Label(data_frame, text="Duration:").grid(row=2, column=0, padx=5, pady=5)
        self.duration_entry = ttk.Entry(data_frame, width=10)
        self.duration_entry.insert(0, "1 D")
        self.duration_entry.grid(row=2, column=1, padx=5, pady=5)

        # Bar-size input
        ttk.Label(data_frame, text="Bar Size:").grid(row=2, column=2, padx=5, pady=5)
        self.bar_size_combo = ttk.Combobox(
            data_frame,
            width=10,
            values=[
                "1 min",
                "5 mins",
                "15 mins",
                "30 mins",
                "1 hour",
                "4 hours",
                "1 day",
            ],
            state="readonly",
        )
        self.bar_size_combo.set("1 hour")
        self.bar_size_combo.grid(row=2, column=3, padx=5, pady=5)
        
        ttk.Button(data_frame, text="Get Historical Data", command=self.get_historical_data).grid(row=1, column=2, padx=5)
        
        # Output text area
        self.output_text = tk.Text(main_frame, height=15, width=70)
        self.output_text.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Export CSV button (initially disabled until data is loaded)
        self.export_button = ttk.Button(main_frame, text="Export to CSV", command=self.export_csv, state=tk.DISABLED)
        self.export_button.grid(row=3, column=0, pady=5)
        
        # Indicator controls
        indicator_frame = ttk.LabelFrame(main_frame, text="Indicators", padding="5")
        indicator_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Label(indicator_frame, text="Indicator:").grid(row=0, column=0, padx=5)
        self.indicator_combo = ttk.Combobox(
            indicator_frame,
            width=10,
            values=["SMA", "EMA", "RSI", "MACD"],
            state="readonly",
        )
        self.indicator_combo.set("SMA")
        self.indicator_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(indicator_frame, text="Length:").grid(row=0, column=2, padx=5)
        self.length_entry = ttk.Entry(indicator_frame, width=5)
        self.length_entry.insert(0, "20")
        self.length_entry.grid(row=0, column=3, padx=5)
        
        ttk.Button(indicator_frame, text="Add", command=self.add_indicator).grid(row=0, column=4, padx=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.output_text.yview)
        scrollbar.grid(row=2, column=2, sticky=(tk.N, tk.S))
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        # Placeholder for last retrieved DataFrame
        self.last_df = None
        
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
            
    def connect(self):
        """Connect to IB Gateway"""
        def update_ui(success):
            if success:
                self.status_label.config(text="Connected", foreground="green")
                self.log_message("Successfully connected to IB Gateway")
            else:
                self.status_label.config(text="Connection Failed", foreground="red")
                self.log_message("Failed to connect to IB Gateway")
                
        # Run the async connect operation
        future = self.run_async_task(self.ib_connector.connect())
        if future:
            future.add_done_callback(lambda f: self.root.after(0, update_ui, f.result()))
            
    def disconnect(self):
        """Disconnect from IB Gateway"""
        def update_ui(success):
            if success:
                self.status_label.config(text="Disconnected", foreground="red")
                self.log_message("Disconnected from IB Gateway")
            else:
                self.log_message("Error disconnecting from IB Gateway")
                
        # Run the async disconnect operation
        future = self.run_async_task(self.ib_connector.disconnect())
        if future:
            future.add_done_callback(lambda f: self.root.after(0, update_ui, f.result()))
            
    def get_account_info(self):
        """Get account information"""
        def update_ui(account_info):
            if account_info:
                self.log_message(f"Account Info ({len(account_info)} items):")
                for key, value in list(account_info.items())[:10]:  # Show first 10 items
                    self.log_message(f"  {key}: {value}")
            else:
                self.log_message("Failed to get account information")
                
        # Run the async operation
        future = self.run_async_task(self.ib_connector.get_account_info())
        if future:
            future.add_done_callback(lambda f: self.root.after(0, update_ui, f.result()))
            
    def get_positions(self):
        """Get current positions"""
        def update_ui(positions):
            if positions is not None:
                self.log_message(f"Positions ({len(positions)} items):")
                for pos in positions:
                    self.log_message(f"  {pos.contract.symbol}: {pos.position} @ {pos.avgCost}")
            else:
                self.log_message("Failed to get positions")
                
        # Run the async operation
        future = self.run_async_task(self.ib_connector.get_positions())
        if future:
            future.add_done_callback(lambda f: self.root.after(0, update_ui, f.result()))
            
    def get_historical_data(self):
        """Get historical data for a symbol"""
        symbol = self.symbol_entry.get().strip()
        duration = self.duration_entry.get().strip() or "1 D"
        bar_size = self.bar_size_combo.get().strip() or "1 hour"
        if not symbol:
            self.log_message("Please enter a symbol")
            return
            
        def update_ui(bars):
            if bars:
                self.log_message(f"Historical Data for {symbol} ({len(bars)} bars):")
                for bar in bars[:5]:  # Show first 5 bars
                    self.log_message(f"  {bar.date}: O={bar.open}, H={bar.high}, L={bar.low}, C={bar.close}, V={bar.volume}")
                
                # Convert to pandas DataFrame and store
                try:
                    from ib_insync import util as ib_util
                    df = ib_util.df(bars)
                    df.set_index("date", inplace=True)
                    self.last_df = df
                    self.export_button.config(state=tk.NORMAL)
                    self.log_message("DataFrame created – ready to export.")
                except Exception as e:
                    self.log_message(f"Error converting to DataFrame: {e}")
            else:
                self.log_message(f"Failed to get historical data for {symbol}")
                
        # Run the async operation
        future = self.run_async_task(
            self.ib_connector.get_historical_data(
                symbol,
                duration=duration,
                bar_size=bar_size,
            )
        )
        if future:
            future.add_done_callback(lambda f: self.root.after(0, update_ui, f.result()))
            
    def log_message(self, message):
        """Add message to output text area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
        
    def on_closing(self):
        """Handle window closing"""
        # Stop the async loop
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        self.root.destroy()
        
    def export_csv(self):
        """Export the last retrieved DataFrame to a CSV file"""
        if self.last_df is None or self.last_df.empty:
            self.log_message("No data available to export. Fetch data first.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save as",
        )
        if file_path:
            try:
                self.last_df.to_csv(file_path)
                self.log_message(f"Data exported to {file_path}")
            except Exception as e:
                self.log_message(f"Error exporting CSV: {e}")
                
    def add_indicator(self):
        """Compute selected indicator and append to DataFrame"""
        if self.last_df is None or self.last_df.empty:
            self.log_message("Fetch data first before adding indicators.")
            return

        ind = self.indicator_combo.get()
        try:
            length = int(self.length_entry.get())
        except ValueError:
            length = 20

        try:
            if ind == "SMA":
                self.last_df[f"SMA_{length}"] = ta.sma(self.last_df["close"], length=length)
            elif ind == "EMA":
                self.last_df[f"EMA_{length}"] = ta.ema(self.last_df["close"], length=length)
            elif ind == "RSI":
                self.last_df[f"RSI_{length}"] = ta.rsi(self.last_df["close"], length=length)
            elif ind == "MACD":
                macd = ta.macd(self.last_df["close"], fast=12, slow=26, signal=9)
                # macd returns 3 columns; merge them
                self.last_df = pd.concat([self.last_df, macd], axis=1)
            else:
                self.log_message(f"Indicator {ind} not implemented.")
                return

            self.log_message(f"Indicator {ind} added to DataFrame.")
        except Exception as e:
            self.log_message(f"Error computing indicator: {e}")


def main():
    """Main function"""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    root = tk.Tk()
    app = AsyncGUIExample(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
