"""
Enhanced Historical Data Acquisition Interface
Comprehensive data selection with multi-asset support and advanced timeframes
"""

import asyncio
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import logging
import json
import os
import csv
from typing import List, Dict, Any, Optional

from ib_data_manager.api.async_ib_connector import AsyncIBConnector

class AssetSelector:
    """Multi-asset selection interface"""
    
    def __init__(self, parent):
        self.parent = parent
        self.selected_assets = []
        
    def show_asset_selector(self):
        """Show asset selection dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Multi-Asset Selection")
        dialog.geometry("800x600")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Quick select buttons
        btn_frame = ttk.LabelFrame(main_frame, text="Quick Select", padding=10)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        buttons_row1 = ttk.Frame(btn_frame)
        buttons_row1.pack(fill=tk.X)
        ttk.Button(buttons_row1, text="Major Stocks", 
                  command=lambda: self.add_preset_assets("major_stocks")).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_row1, text="Tech Stocks", 
                  command=lambda: self.add_preset_assets("tech_stocks")).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_row1, text="Major ETFs", 
                  command=lambda: self.add_preset_assets("major_etfs")).pack(side=tk.LEFT, padx=5)
        
        buttons_row2 = ttk.Frame(btn_frame)
        buttons_row2.pack(fill=tk.X, pady=5)
        ttk.Button(buttons_row2, text="ES Futures", 
                  command=lambda: self.add_preset_assets("futures")).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_row2, text="Major Forex", 
                  command=lambda: self.add_preset_assets("forex")).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_row2, text="Crypto ETFs", 
                  command=lambda: self.add_preset_assets("crypto")).pack(side=tk.LEFT, padx=5)
        
        # Manual entry
        entry_frame = ttk.LabelFrame(main_frame, text="Manual Entry", padding=10)
        entry_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Single asset entry
        single_frame = ttk.Frame(entry_frame)
        single_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(single_frame, text="Symbol:").pack(side=tk.LEFT)
        self.symbol_entry = ttk.Entry(single_frame, width=10)
        self.symbol_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(single_frame, text="Type:").pack(side=tk.LEFT, padx=(10, 0))
        self.type_combo = ttk.Combobox(single_frame, values=["STK", "FUT", "OPT", "CASH"], width=8)
        self.type_combo.set("STK")
        self.type_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(single_frame, text="Add", command=self.add_single_asset).pack(side=tk.LEFT, padx=10)
        
        # Bulk entry
        ttk.Label(entry_frame, text="Bulk Entry (comma-separated):").pack(anchor=tk.W)
        self.bulk_entry = tk.Text(entry_frame, height=3, width=60)
        self.bulk_entry.pack(fill=tk.X, pady=5)
        self.bulk_entry.insert("1.0", "AAPL, MSFT, GOOGL, AMZN, TSLA")
        
        ttk.Button(entry_frame, text="Add Bulk", command=self.add_bulk_assets).pack()
        
        # Selected assets list
        selected_frame = ttk.LabelFrame(main_frame, text="Selected Assets", padding=10)
        selected_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview for selected assets
        columns = ("symbol", "type", "exchange")
        self.assets_tree = ttk.Treeview(selected_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.assets_tree.heading(col, text=col.title())
            self.assets_tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(selected_frame, orient="vertical", command=self.assets_tree.yview)
        self.assets_tree.configure(yscrollcommand=scrollbar.set)
        
        self.assets_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons
        control_frame = ttk.Frame(selected_frame)
        control_frame.pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Remove Selected", 
                  command=self.remove_selected_asset).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Clear All", 
                  command=self.clear_all_assets).pack(side=tk.LEFT, padx=5)
        
        # Dialog buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancel", 
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="OK", 
                  command=lambda: self.confirm_selection(dialog)).pack(side=tk.RIGHT)
        
        # Load existing assets
        self.refresh_assets_display()
        return dialog
        
    def add_preset_assets(self, category):
        """Add preset asset groups"""
        presets = {
            "major_stocks": [
                ("AAPL", "STK", "SMART"), ("MSFT", "STK", "SMART"), ("GOOGL", "STK", "SMART"),
                ("AMZN", "STK", "SMART"), ("TSLA", "STK", "SMART"), ("NVDA", "STK", "SMART"),
                ("META", "STK", "SMART"), ("JPM", "STK", "SMART"), ("JNJ", "STK", "SMART")
            ],
            "tech_stocks": [
                ("AAPL", "STK", "SMART"), ("MSFT", "STK", "SMART"), ("GOOGL", "STK", "SMART"),
                ("AMZN", "STK", "SMART"), ("TSLA", "STK", "SMART"), ("NVDA", "STK", "SMART"),
                ("META", "STK", "SMART"), ("NFLX", "STK", "SMART"), ("CRM", "STK", "SMART")
            ],
            "major_etfs": [
                ("SPY", "STK", "SMART"), ("QQQ", "STK", "SMART"), ("IWM", "STK", "SMART"),
                ("VTI", "STK", "SMART"), ("EFA", "STK", "SMART"), ("TLT", "STK", "SMART"),
                ("GLD", "STK", "SMART"), ("SLV", "STK", "SMART")
            ],
            "futures": [
                ("ES", "FUT", "CME"), ("NQ", "FUT", "CME"), ("YM", "FUT", "CBOT"),
                ("RTY", "FUT", "CME"), ("CL", "FUT", "NYMEX"), ("GC", "FUT", "COMEX")
            ],
            "forex": [
                ("EUR", "CASH", "IDEALPRO"), ("GBP", "CASH", "IDEALPRO"), 
                ("JPY", "CASH", "IDEALPRO"), ("AUD", "CASH", "IDEALPRO")
            ],
            "crypto": [
                ("BITO", "STK", "SMART"), ("ETHE", "STK", "SMART"), ("GBTC", "STK", "SMART")
            ]
        }
        
        if category in presets:
            for asset in presets[category]:
                if asset not in self.selected_assets:
                    self.selected_assets.append(asset)
            self.refresh_assets_display()
            
    def add_single_asset(self):
        """Add a single asset"""
        symbol = self.symbol_entry.get().strip().upper()
        asset_type = self.type_combo.get()
        exchange = "SMART" if asset_type == "STK" else "CME"
        
        if symbol:
            asset = (symbol, asset_type, exchange)
            if asset not in self.selected_assets:
                self.selected_assets.append(asset)
                self.refresh_assets_display()
                self.symbol_entry.delete(0, tk.END)
                
    def add_bulk_assets(self):
        """Add multiple assets from bulk entry"""
        bulk_text = self.bulk_entry.get("1.0", tk.END).strip()
        symbols = [s.strip().upper() for s in bulk_text.split(",") if s.strip()]
        
        for symbol in symbols:
            asset = (symbol, "STK", "SMART")
            if asset not in self.selected_assets:
                self.selected_assets.append(asset)
                
        self.refresh_assets_display()
        
    def remove_selected_asset(self):
        """Remove selected asset from list"""
        selection = self.assets_tree.selection()
        if selection:
            item = self.assets_tree.item(selection[0])
            values = item['values']
            asset = tuple(values)
            if asset in self.selected_assets:
                self.selected_assets.remove(asset)
                self.refresh_assets_display()
                
    def clear_all_assets(self):
        """Clear all selected assets"""
        self.selected_assets.clear()
        self.refresh_assets_display()
        
    def refresh_assets_display(self):
        """Refresh the assets treeview"""
        for item in self.assets_tree.get_children():
            self.assets_tree.delete(item)
            
        for asset in self.selected_assets:
            self.assets_tree.insert("", tk.END, values=asset)
            
    def confirm_selection(self, dialog):
        """Confirm asset selection and close dialog"""
        dialog.destroy()
        
    def get_selected_assets(self):
        """Get the list of selected assets"""
        return self.selected_assets.copy()

class TimeframeSelector:
    """Advanced timeframe selection"""
    
    def __init__(self):
        self.timeframe_presets = {
            "Intraday": {
                "1 Min - Last Hour": ("1 H", "1 min"),
                "5 Min - Last 4 Hours": ("4 H", "5 mins"),
                "15 Min - Last Day": ("1 D", "15 mins"),
                "1 Hour - Last Week": ("1 W", "1 hour")
            },
            "Daily": {
                "Daily - Last Month": ("1 M", "1 day"),
                "Daily - Last 3 Months": ("3 M", "1 day"),
                "Daily - Last Year": ("1 Y", "1 day"),
                "Daily - Last 2 Years": ("2 Y", "1 day")
            },
            "Weekly/Monthly": {
                "Weekly - Last Year": ("1 Y", "1 week"),
                "Monthly - Last 5 Years": ("5 Y", "1 month")
            }
        }
        
    def create_timeframe_widgets(self, parent):
        """Create timeframe selection widgets"""
        timeframe_frame = ttk.LabelFrame(parent, text="Timeframe Selection", padding=10)
        
        # Preset selection
        preset_frame = ttk.Frame(timeframe_frame)
        preset_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(preset_frame, text="Category:").pack(side=tk.LEFT)
        self.category_combo = ttk.Combobox(preset_frame, 
                                         values=list(self.timeframe_presets.keys()),
                                         state="readonly", width=15)
        self.category_combo.set("Daily")
        self.category_combo.pack(side=tk.LEFT, padx=5)
        self.category_combo.bind("<<ComboboxSelected>>", self.on_category_change)
        
        ttk.Label(preset_frame, text="Preset:").pack(side=tk.LEFT, padx=(20, 0))
        self.preset_combo = ttk.Combobox(preset_frame, state="readonly", width=25)
        self.preset_combo.pack(side=tk.LEFT, padx=5)
        
        # Custom selection
        custom_frame = ttk.Frame(timeframe_frame)
        custom_frame.pack(fill=tk.X)
        
        ttk.Label(custom_frame, text="Custom Duration:").pack(side=tk.LEFT)
        self.duration_entry = ttk.Entry(custom_frame, width=10)
        self.duration_entry.pack(side=tk.LEFT, padx=5)
        self.duration_entry.insert(0, "1 Y")
        
        ttk.Label(custom_frame, text="Bar Size:").pack(side=tk.LEFT, padx=(20, 0))
        self.bar_size_combo = ttk.Combobox(custom_frame, values=[
            "1 min", "5 mins", "15 mins", "30 mins", "1 hour", "1 day", "1 week", "1 month"
        ], state="readonly", width=12)
        self.bar_size_combo.set("1 day")
        self.bar_size_combo.pack(side=tk.LEFT, padx=5)
        
        # Initialize
        self.on_category_change()
        
        return timeframe_frame
        
    def on_category_change(self, event=None):
        """Handle category change"""
        category = self.category_combo.get()
        if category in self.timeframe_presets:
            presets = list(self.timeframe_presets[category].keys())
            self.preset_combo['values'] = presets
            if presets:
                self.preset_combo.set(presets[0])
                
    def get_timeframe_settings(self):
        """Get current timeframe settings"""
        # Try preset first
        category = self.category_combo.get()
        preset = self.preset_combo.get()
        if category in self.timeframe_presets and preset in self.timeframe_presets[category]:
            duration, bar_size = self.timeframe_presets[category][preset]
            return {"duration": duration, "bar_size": bar_size}
        
        # Fall back to custom
        return {
            "duration": self.duration_entry.get() or "1 Y",
            "bar_size": self.bar_size_combo.get() or "1 day"
        }

class EnhancedDataAcquisition:
    """Enhanced historical data acquisition interface"""
    
    def __init__(self, root, ib_connector):
        self.root = root
        self.ib_conn = ib_connector
        self.asset_selector = AssetSelector(root)
        self.timeframe_selector = TimeframeSelector()
        self.acquisition_results = {}
        self.is_acquiring = False
        
    def create_enhanced_interface(self, parent_frame):
        """Create the enhanced data acquisition interface"""
        main_container = ttk.Frame(parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_container, text="Enhanced Historical Data Acquisition", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Asset selection
        asset_frame = ttk.LabelFrame(main_container, text="Asset Selection", padding=10)
        asset_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.selected_assets_label = ttk.Label(asset_frame, text="No assets selected")
        self.selected_assets_label.pack(anchor=tk.W, pady=(0, 10))
        
        asset_btn_frame = ttk.Frame(asset_frame)
        asset_btn_frame.pack(fill=tk.X)
        
        ttk.Button(asset_btn_frame, text="Select Assets", 
                  command=self.show_asset_selector).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(asset_btn_frame, text="Clear Selection", 
                  command=self.clear_asset_selection).pack(side=tk.LEFT)
        
        # Timeframe selection
        timeframe_frame = self.timeframe_selector.create_timeframe_widgets(main_container)
        timeframe_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Connection status
        conn_frame = ttk.LabelFrame(main_container, text="Connection Status", padding=10)
        conn_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.conn_status_label = ttk.Label(conn_frame, text="Checking connection...", foreground="orange")
        self.conn_status_label.pack(side=tk.LEFT)
        
        ttk.Button(conn_frame, text="Refresh Status", 
                  command=self.update_connection_status).pack(side=tk.RIGHT)
        
        # Options
        options_frame = ttk.LabelFrame(main_container, text="Options", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        options_row = ttk.Frame(options_frame)
        options_row.pack(fill=tk.X)
        
        self.use_rth = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_row, text="Regular Trading Hours Only", 
                       variable=self.use_rth).pack(side=tk.LEFT)
        
        ttk.Label(options_row, text="Delay (sec):").pack(side=tk.LEFT, padx=(20, 0))
        self.delay_entry = ttk.Entry(options_row, width=5)
        self.delay_entry.insert(0, "1")
        self.delay_entry.pack(side=tk.LEFT, padx=5)
        
        # Update connection status initially
        self.root.after(1000, self.update_connection_status)
        
        # Progress
        progress_frame = ttk.LabelFrame(main_container, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="Ready")
        self.progress_label.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Action buttons
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_btn = ttk.Button(action_frame, text="Start Acquisition", 
                                  command=self.start_data_acquisition)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(action_frame, text="Stop", 
                                 command=self.stop_data_acquisition, state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(action_frame, text="Export All", 
                  command=self.export_all_results).pack(side=tk.LEFT, padx=(0, 10))
        
        # Results
        results_frame = ttk.LabelFrame(main_container, text="Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("asset", "bars", "timeframe", "status")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.results_tree.heading(col, text=col.title())
            self.results_tree.column(col, width=120)
        
        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return main_container
        
    def update_connection_status(self):
        """Update connection status display"""
        try:
            if hasattr(self.ib_conn, 'connected') and self.ib_conn.connected:
                if hasattr(self.ib_conn, 'ib') and self.ib_conn.ib.isConnected():
                    self.conn_status_label.config(text="✅ Connected to IB Gateway", foreground="green")
                else:
                    self.conn_status_label.config(text="⚠️ Connection unstable", foreground="orange")
            else:
                self.conn_status_label.config(text="❌ Not connected to IB Gateway", foreground="red")
        except Exception as e:
            self.conn_status_label.config(text=f"❌ Connection error: {e}", foreground="red")
        
    def show_asset_selector(self):
        """Show asset selector dialog"""
        dialog = self.asset_selector.show_asset_selector()
        self.root.wait_window(dialog)
        self.update_selected_assets_display()
        
    def clear_asset_selection(self):
        """Clear asset selection"""
        self.asset_selector.selected_assets.clear()
        self.update_selected_assets_display()
        
    def update_selected_assets_display(self):
        """Update selected assets display"""
        assets = self.asset_selector.get_selected_assets()
        if assets:
            asset_names = [f"{asset[0]}" for asset in assets[:5]]
            if len(assets) > 5:
                asset_names.append(f"... +{len(assets) - 5} more")
            self.selected_assets_label.config(text=f"Selected: {', '.join(asset_names)}")
        else:
            self.selected_assets_label.config(text="No assets selected")
            
    def start_data_acquisition(self):
        """Start data acquisition"""
        assets = self.asset_selector.get_selected_assets()
        if not assets:
            messagebox.showwarning("No Assets", "Please select at least one asset")
            return
            
        # Check connection
        if not hasattr(self.ib_conn, 'connected') or not self.ib_conn.connected:
            messagebox.showwarning("Not Connected", "Please connect to IB Gateway first")
            return
            
        # Validate timeframe settings
        timeframe_settings = self.timeframe_selector.get_timeframe_settings()
        if not timeframe_settings.get("duration") or not timeframe_settings.get("bar_size"):
            messagebox.showerror("Invalid Settings", "Please select valid duration and bar size")
            return
            
        print(f"Starting acquisition for {len(assets)} assets")
        print(f"Timeframe: {timeframe_settings}")
        print(f"Assets: {[f'{a[0]} ({a[1]})' for a in assets[:5]]}")  # Show first 5
            
        self.is_acquiring = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        # Clear previous results
        self.acquisition_results.clear()
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        # Start acquisition
        timeframe_settings = self.timeframe_selector.get_timeframe_settings()
        self.run_batch_acquisition(assets, timeframe_settings)
        
    def run_batch_acquisition(self, assets, timeframe_settings):
        """Run batch acquisition"""
        async def acquire_data():
            total = len(assets)
            delay = float(self.delay_entry.get() or "1")
            
            for i, (symbol, sec_type, exchange) in enumerate(assets):
                if not self.is_acquiring:
                    break
                    
                # Update progress - fix closure issue
                def update_progress_safe(idx=i, tot=total, sym=symbol):
                    self.update_progress(idx, tot, f"Fetching {sym}...")
                self.root.after(0, update_progress_safe)
                
                try:
                    # Debug output
                    print(f"Fetching {symbol} ({sec_type}) from {exchange}")
                    print(f"Duration: {timeframe_settings['duration']}, Bar size: {timeframe_settings['bar_size']}")
                    
                    # Fetch data using the correct method signature
                    data = await self.ib_conn.get_historical_data(
                        symbol=symbol,
                        sec_type=sec_type,
                        exchange=exchange,
                        currency="USD",
                        duration=timeframe_settings["duration"],
                        bar_size=timeframe_settings["bar_size"],
                        expiry=None if sec_type != "FUT" else None,  # Let connector handle futures
                        use_rth=self.use_rth.get()
                    )
                    
                    if data:
                        self.acquisition_results[symbol] = data
                        # Save to database
                        if hasattr(self.ib_conn, 'db') and self.ib_conn.db:
                            await self.ib_conn.db.save_historical_data(symbol, data)
                        status = f"✅ {len(data)} bars"
                        bar_count = len(data)
                    else:
                        status = "❌ No data"
                        bar_count = 0
                        
                    # Update results tree - fix closure issue
                    timeframe_str = f"{timeframe_settings['duration']} / {timeframe_settings['bar_size']}"
                    def update_results_safe(s=symbol, d=bar_count, t=timeframe_str, st=status):
                        self.results_tree.insert("", tk.END, values=(s, d, t, st))
                    self.root.after(0, update_results_safe)
                    
                except Exception as e:
                    print(f"Error fetching {symbol}: {e}")  # Debug output
                    status = f"❌ Error: {str(e)}"
                    timeframe_str = f"{timeframe_settings['duration']} / {timeframe_settings['bar_size']}"
                    def update_error_safe(s=symbol, t=timeframe_str, st=status):
                        self.results_tree.insert("", tk.END, values=(s, 0, t, st))
                    self.root.after(0, update_error_safe)
                
                # Delay between requests
                if i < total - 1 and self.is_acquiring:
                    await asyncio.sleep(delay)
                    
            # Finished
            self.root.after(0, self.acquisition_finished)
            
        # Use main GUI's async loop if available
        if hasattr(self, 'main_gui') and hasattr(self.main_gui, 'loop') and self.main_gui.loop:
            try:
                asyncio.run_coroutine_threadsafe(acquire_data(), self.main_gui.loop)
                return
            except Exception as e:
                print(f"Failed to use main GUI loop: {e}")
        
        # Try to get loop from IB connector
        elif hasattr(self.ib_conn, 'loop') and self.ib_conn.loop:
            try:
                asyncio.run_coroutine_threadsafe(acquire_data(), self.ib_conn.loop)
                return
            except Exception as e:
                print(f"Failed to use IB connector loop: {e}")
        
        # Fallback - create new event loop in thread
        def run_in_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(acquire_data())
            except Exception as e:
                print(f"Error in async acquisition: {e}")
                self.root.after(0, lambda: self.progress_label.config(text=f"Error: {e}"))
            finally:
                loop.close()
        
        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()
            
    def update_progress(self, current, total, message):
        """Update progress display"""
        self.progress_bar.config(maximum=total, value=current + 1)
        self.progress_label.config(text=f"{message} ({current + 1}/{total})")
        
    def stop_data_acquisition(self):
        """Stop data acquisition"""
        self.is_acquiring = False
        self.acquisition_finished()
        
    def acquisition_finished(self):
        """Handle acquisition completion"""
        self.is_acquiring = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.progress_label.config(text=f"Completed - {len(self.acquisition_results)} assets acquired")
        
    def export_all_results(self):
        """Export all acquisition results"""
        if not self.acquisition_results:
            messagebox.showinfo("No Data", "No data to export")
            return
            
        # Ask for export directory
        export_dir = filedialog.askdirectory(title="Select Export Directory")
        if not export_dir:
            return
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for symbol, data in self.acquisition_results.items():
                filename = os.path.join(export_dir, f"{symbol}_historical_{timestamp}.csv")
                
                with open(filename, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["date", "open", "high", "low", "close", "volume"])
                    for bar in data:
                        writer.writerow([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])
                        
            messagebox.showinfo("Export Complete", 
                              f"Exported {len(self.acquisition_results)} files to:\n{export_dir}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data:\n{str(e)}")

def main():
    """Test the enhanced data acquisition interface"""
    root = tk.Tk()
    root.title("Enhanced Data Acquisition Test")
    root.geometry("1000x800")
    
    # Mock connector for testing
    class MockConnector:
        def __init__(self):
            self.connected = True
            
    mock_conn = MockConnector()
    
    # Create interface
    enhanced_da = EnhancedDataAcquisition(root, mock_conn)
    interface = enhanced_da.create_enhanced_interface(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()
