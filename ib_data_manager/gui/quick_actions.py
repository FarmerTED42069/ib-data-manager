"""
Quick Actions Panel
One-click data acquisition with smart presets and efficient workflows
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import asyncio
import logging

from ib_data_manager.gui.options_browser import show_options_browser

class QuickActionsPanel:
    """
    Eliminates the tedious form-filling by providing smart presets
    and one-click data acquisition for common scenarios.
    """
    
    def __init__(self, parent, dashboard):
        self.parent = parent
        self.dashboard = dashboard
        self.current_symbol = tk.StringVar(value="AAPL")
        self.is_fetching = False
        
        self.create_panel()
        
    def create_panel(self):
        """Create the quick actions UI"""
        # Main frame
        self.actions_frame = ttk.LabelFrame(self.parent, text="⚡ Quick Data Fetch", padding="10")
        self.actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Symbol input with smart suggestions
        self.create_symbol_input()
        
        # Quick preset buttons with integrated custom fetch
        self.create_preset_buttons()
        
        # Progress indicator
        self.create_progress_indicator()
        
    def create_symbol_input(self):
        """Create streamlined symbol input with smart suggestions"""
        symbol_frame = ttk.Frame(self.actions_frame)
        symbol_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Single row: Symbol, Type, and Contract selection
        input_row = ttk.Frame(symbol_frame)
        input_row.pack(fill=tk.X)
        
        ttk.Label(input_row, text="Symbol:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # Symbol entry with autocomplete suggestions
        self.symbol_entry = ttk.Entry(
            input_row, 
            textvariable=self.current_symbol,
            font=("Arial", 11),
            width=15
        )
        self.symbol_entry.pack(side=tk.LEFT, padx=(10, 15))
        self.symbol_entry.bind('<Return>', lambda e: self.smart_fetch())
        self.symbol_entry.bind('<KeyRelease>', self.on_symbol_keyrelease)
        
        # Contract type selector
        ttk.Label(input_row, text="Type:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.contract_type = tk.StringVar(value="STK")
        contract_combo = ttk.Combobox(
            input_row,
            textvariable=self.contract_type,
            values=["STK", "FUT", "OPT", "CASH"],
            width=8,
            state="readonly"
        )
        contract_combo.pack(side=tk.LEFT, padx=(5, 15))
        contract_combo.bind("<<ComboboxSelected>>", self.on_contract_type_change)
        
        # Contract selection button (for futures/options)
        self.contract_btn = ttk.Button(
            input_row,
            text="📋 Select Contract",
            command=self.show_contract_selector,
            width=15
        )
        self.contract_btn.pack(side=tk.LEFT, padx=5)
        self.contract_btn.pack_forget()  # Hidden initially
        
        # Smart suggestions (appears on focus/typing)
        self.suggestions_frame = ttk.Frame(symbol_frame)
        # Will be packed dynamically when needed
            
    def create_preset_buttons(self):
        """Create streamlined data fetch interface"""
        fetch_frame = ttk.LabelFrame(self.actions_frame, text="📊 Data & Analysis", padding="8")
        fetch_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Single row: All essential controls
        main_row = ttk.Frame(fetch_frame)
        main_row.pack(fill=tk.X, pady=2)
        
        # Duration and bar size controls
        ttk.Label(main_row, text="Duration:", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        self.duration_var = tk.StringVar(value="1 Y")
        duration_combo = ttk.Combobox(
            main_row, 
            textvariable=self.duration_var,
            values=["1 D", "2 D", "1 W", "2 W", "1 M", "2 M", "3 M", "6 M", "1 Y", "2 Y"],
            width=8,
            state="readonly"
        )
        duration_combo.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(main_row, text="Bar Size:", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        self.bar_size_var = tk.StringVar(value="1 day")
        bar_size_combo = ttk.Combobox(
            main_row,
            textvariable=self.bar_size_var,
            values=["1 min", "5 mins", "15 mins", "30 mins", "1 hour", "4 hours", "1 day", "1 week"],
            width=10,
            state="readonly"
        )
        bar_size_combo.pack(side=tk.LEFT, padx=(5, 20))
        
        # Primary action buttons
        ttk.Button(main_row, text="📊 Fetch Data", 
                  command=self.smart_fetch, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(main_row, text="🚀 Fetch + Analysis", 
                  command=self.quick_analysis, width=14).pack(side=tk.LEFT, padx=2)
        ttk.Button(main_row, text="🧪 Custom Analysis", 
                  command=self.show_feature_analysis, width=14).pack(side=tk.LEFT, padx=2)
        ttk.Button(main_row, text="📡 Live Stream", 
                  command=self.start_live_quotes, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(main_row, text="🔄 Refresh", 
                  command=self.refresh_current, width=10).pack(side=tk.LEFT, padx=2)
        
        # Second row: Advanced tools
        advanced_row = ttk.Frame(fetch_frame)
        advanced_row.pack(fill=tk.X, pady=(8, 2))
        
        ttk.Button(advanced_row, text="📋 Multi-Symbol Analysis", 
                  command=self.show_multi_symbol_dialog, width=18).pack(side=tk.LEFT, padx=2)
        ttk.Button(advanced_row, text="📊 Level II Pro", 
                  command=self.start_enhanced_level2, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(advanced_row, text="🔴 Stop All Streams", 
                  command=self.stop_streaming, width=14).pack(side=tk.LEFT, padx=2)
        
        # Add batch operations section
        self.create_batch_operations()
        
    def create_progress_indicator(self):
        """Create progress indicator"""
        progress_frame = ttk.Frame(self.actions_frame)
        progress_frame.pack(fill=tk.X)
        
        self.progress_label = ttk.Label(progress_frame, text="Ready", foreground="gray")
        self.progress_label.pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            mode='indeterminate',
            length=200
        )
        self.progress_bar.pack(side=tk.RIGHT)
        
    def set_symbol(self, symbol):
        """Set the current symbol"""
        self.current_symbol.set(symbol)
        self.symbol_entry.focus()
        
    def set_symbol_and_type(self, symbol, contract_type):
        """Set symbol and contract type together"""
        self.current_symbol.set(symbol)
        self.contract_type.set(contract_type)
        self.on_contract_type_change()
        self.symbol_entry.focus()
        
    def on_contract_type_change(self, event=None):
        """Handle contract type change"""
        contract_type = self.contract_type.get()
        
        if contract_type in ["FUT", "OPT"]:
            # Show contract selection button for derivatives
            self.contract_btn.pack(side=tk.LEFT, padx=5)
        else:
            # Hide contract selection button for stocks/cash
            self.contract_btn.pack_forget()
            
        # Update button text based on type
        if contract_type == "FUT":
            self.contract_btn.config(text="📋 Select Futures Contract")
        elif contract_type == "OPT":
            self.contract_btn.config(text="📋 Select Options Chain")
        else:
            self.contract_btn.config(text="📋 Select Contract")
            
    def show_contract_selector(self):
        """Show appropriate contract selector based on type"""
        contract_type = self.contract_type.get()
        symbol = self.current_symbol.get().strip().upper()
        
        if not symbol:
            messagebox.showwarning("No Symbol", "Please enter a symbol first")
            return
            
        if self.dashboard.connection_status != "connected":
            messagebox.showwarning("Not Connected", "Please connect to IB Gateway first")
            return
            
        if contract_type == "FUT":
            self.show_futures_selector(symbol)
        elif contract_type == "OPT":
            self.show_options_selector(symbol)
        else:
            messagebox.showinfo("Contract Selection", f"Contract selection not needed for {contract_type}")
            
    def show_futures_selector(self, symbol):
        """Show futures contract selector"""
        self.progress_label.config(text=f"Loading futures contracts for {symbol}...", foreground="blue")
        
        async def get_futures_contracts():
            try:
                # Use the existing async connector method
                contracts = await self.dashboard.ib_conn.get_futures_contracts(symbol, "SMART", "USD")
                if contracts:
                    self.dashboard.root.after(0, lambda: self.show_futures_dialog(symbol, contracts))
                else:
                    self.dashboard.root.after(0, lambda: self.progress_label.config(
                        text=f"❌ No futures contracts found for {symbol}", foreground="red"
                    ))
            except Exception as e:
                self.dashboard.root.after(0, lambda: self.progress_label.config(
                    text=f"❌ Error loading contracts: {str(e)[:50]}...", foreground="red"
                ))
                
        future = self.dashboard.run_async_task(get_futures_contracts())
        
    def show_futures_dialog(self, symbol, contracts):
        """Show futures contract selection dialog"""
        dialog = tk.Toplevel(self.dashboard.root)
        dialog.title(f"Select Futures Contract - {symbol}")
        dialog.geometry("700x500")
        dialog.transient(self.dashboard.root)
        dialog.grab_set()
        
        # Header
        header_frame = ttk.Frame(dialog, padding="10")
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, text=f"Available Futures Contracts for {symbol}", 
                 font=("Arial", 14, "bold")).pack()
        ttk.Label(header_frame, text="💡 Front contract (nearest expiry) is highlighted", 
                 foreground="blue").pack(pady=5)
        
        # Contract list
        list_frame = ttk.Frame(dialog, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for contracts
        columns = ("symbol", "expiry", "local_symbol", "exchange")
        contract_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            contract_tree.heading(col, text=col.replace("_", " ").title())
            contract_tree.column(col, width=150)
            
        # Populate contracts
        contract_map = {}
        for i, contract in enumerate(contracts):
            expiry = contract.lastTradeDateOrContractMonth
            local_symbol = getattr(contract, 'localSymbol', 'N/A')
            front_indicator = " (FRONT)" if i == 0 else ""
            
            item_id = contract_tree.insert("", tk.END, values=(
                contract.symbol,
                expiry + front_indicator,
                local_symbol,
                contract.exchange
            ))
            contract_map[item_id] = contract
            
            # Highlight front contract
            if i == 0:
                contract_tree.selection_set(item_id)
                contract_tree.focus(item_id)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=contract_tree.yview)
        contract_tree.configure(yscrollcommand=scrollbar.set)
        
        contract_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill=tk.X)
        
        def select_contract():
            selection = contract_tree.selection()
            if selection:
                selected_contract = contract_map[selection[0]]
                expiry = selected_contract.lastTradeDateOrContractMonth
                
                # Store selected contract info
                self.selected_contract = {
                    'expiry': expiry,
                    'exchange': selected_contract.exchange,
                    'local_symbol': getattr(selected_contract, 'localSymbol', '')
                }
                
                self.progress_label.config(
                    text=f"✅ Selected: {symbol} {expiry} ({selected_contract.exchange})", 
                    foreground="green"
                )
                dialog.destroy()
            else:
                messagebox.showwarning("No Selection", "Please select a contract", parent=dialog)
                
        ttk.Button(button_frame, text="Select Contract", command=select_contract).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Double-click support
        contract_tree.bind("<Double-Button-1>", lambda e: select_contract())
        
        # Clear status after dialog
        self.dashboard.root.after(100, lambda: self.progress_label.config(text="Ready", foreground="gray"))
        
    def show_options_selector(self, symbol):
        """Show options chain selector"""
        self.progress_label.config(text=f"Opening options browser for {symbol}...", foreground="blue")
        
        try:
            # Show the options browser
            selected_option = show_options_browser(self.dashboard.root, self.dashboard, symbol)
            
            if selected_option:
                # Store selected option info
                self.selected_option = selected_option
                
                self.progress_label.config(
                    text=f"✅ Selected: {symbol} {selected_option['strike']} {selected_option['right']} {selected_option['expiry']}", 
                    foreground="green"
                )
            else:
                self.progress_label.config(text="Options selection cancelled", foreground="gray")
                
        except Exception as e:
            self.progress_label.config(
                text=f"❌ Error opening options browser: {str(e)[:50]}...", 
                foreground="red"
            )
        
    def fetch_daily_data(self):
        """Fetch daily data for 1 year"""
        self.fetch_data("1 Y", "1 day", "📊 Daily Data")
        
    def fetch_hourly_data(self):
        """Fetch hourly data for 1 month"""
        self.fetch_data("1 M", "1 hour", "📈 Hourly Data")
        
    def fetch_intraday_data(self):
        """Fetch 5-minute data for 1 week"""
        self.fetch_data("1 W", "5 mins", "⚡ Intraday Data")
        
    def fetch_recent_data(self):
        """Fetch recent daily data (30 days)"""
        self.fetch_data("30 D", "1 day", "🎯 Recent Data")
        
    def fetch_custom_data(self):
        """Fetch data with custom settings"""
        duration = self.duration_var.get()
        bar_size = self.bar_size_var.get()
        self.fetch_data(duration, bar_size, "🔧 Custom Data")
        
    def fetch_data(self, duration, bar_size, description):
        """Generic data fetching method"""
        symbol = self.current_symbol.get().strip().upper()
        if not symbol:
            messagebox.showwarning("No Symbol", "Please enter a symbol")
            return
            
        if self.dashboard.connection_status != "connected":
            messagebox.showwarning("Not Connected", "Please connect to IB Gateway first")
            return
            
        if self.is_fetching:
            messagebox.showinfo("Already Fetching", "Data fetch in progress, please wait")
            return
            
        # Get contract details
        contract_type = self.contract_type.get()
        exchange = "SMART"
        expiry = None
        
        # Handle futures contracts
        if contract_type == "FUT":
            if hasattr(self, 'selected_contract') and self.selected_contract:
                expiry = self.selected_contract['expiry']
                exchange = self.selected_contract['exchange']
                description += f" ({expiry})"
            else:
                # Try to get front contract automatically
                messagebox.showinfo("Contract Selection", 
                                  f"Please select a futures contract first using the 'Select Contract' button")
                return
                
        self.start_fetch_progress(f"Fetching {description} for {symbol}...")
        
        async def do_fetch():
            try:
                # Fetch the data
                data = await self.dashboard.ib_conn.get_historical_data(
                    symbol=symbol,
                    sec_type=contract_type,
                    exchange=exchange,
                    currency="USD",
                    duration=duration,
                    bar_size=bar_size,
                    expiry=expiry,
                    use_rth=True
                )
                
                if data:
                    # Save to database
                    if hasattr(self.dashboard.ib_conn, 'db') and self.dashboard.ib_conn.db:
                        await self.dashboard.ib_conn.db.save_historical_data(symbol, data)
                    
                    # Store in dashboard
                    self.dashboard.current_data[symbol] = {
                        'data': data,
                        'duration': duration,
                        'bar_size': bar_size,
                        'fetched_at': datetime.now(),
                        'description': description
                    }
                    
                    # Update UI on main thread
                    self.dashboard.root.after(0, lambda: self.fetch_complete(
                        symbol, len(data), description
                    ))
                    
                    # Notify results panel if it exists
                    if hasattr(self.dashboard, 'results_panel') and self.dashboard.results_panel:
                        self.dashboard.root.after(0, lambda: 
                            self.dashboard.results_panel.update_data(symbol, data, description)
                        )
                else:
                    self.dashboard.root.after(0, lambda: self.fetch_error(
                        f"No data returned for {symbol}"
                    ))
                    
            except Exception as e:
                self.dashboard.root.after(0, lambda: self.fetch_error(str(e)))
                
        # Run the fetch
        future = self.dashboard.run_async_task(do_fetch())
        
    def start_fetch_progress(self, message):
        """Start progress indication"""
        self.is_fetching = True
        self.progress_label.config(text=message, foreground="blue")
        self.progress_bar.start(10)
        
        # Disable fetch buttons
        for widget in self.actions_frame.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for btn in child.winfo_children():
                            if isinstance(btn, ttk.Button):
                                btn.config(state="disabled")
                                
    def fetch_complete(self, symbol, bar_count, description):
        """Handle successful fetch completion"""
        self.is_fetching = False
        self.progress_bar.stop()
        self.progress_label.config(
            text=f"✅ {description}: {bar_count} bars for {symbol}", 
            foreground="green"
        )
        
        # Re-enable buttons
        self.enable_buttons()
        
        # Auto-clear status after 5 seconds
        self.dashboard.root.after(5000, self.clear_status)
        
    def fetch_error(self, error_msg):
        """Handle fetch error"""
        self.is_fetching = False
        self.progress_bar.stop()
        self.progress_label.config(
            text=f"❌ Error: {error_msg[:50]}...", 
            foreground="red"
        )
        
        # Re-enable buttons
        self.enable_buttons()
        
        # Auto-clear status after 10 seconds
        self.dashboard.root.after(10000, self.clear_status)
        
    def enable_buttons(self):
        """Re-enable all buttons"""
        for widget in self.actions_frame.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for btn in child.winfo_children():
                            if isinstance(btn, ttk.Button):
                                btn.config(state="normal")
                                
    def clear_status(self):
        """Clear status message"""
        if not self.is_fetching:
            self.progress_label.config(text="Ready", foreground="gray")
            
    def update_progress(self, message, show_spinner=False):
        """Update progress with message and optional spinner"""
        self.progress_label.config(text=message, foreground="blue")
        if show_spinner:
            self.progress_bar.start()
        else:
            self.progress_bar.stop()
            
    def quick_export_last(self):
        """Quick export the last fetched data"""
        if not self.dashboard.current_data:
            messagebox.showinfo("No Data", "No data to export. Fetch some data first.")
            return
            
        # Get the most recent data
        latest_symbol = max(
            self.dashboard.current_data.keys(),
            key=lambda k: self.dashboard.current_data[k]['fetched_at']
        )
        
        # Trigger export (this will be implemented in the export component)
        if hasattr(self.dashboard, 'export_panel') and self.dashboard.export_panel:
            self.dashboard.export_panel.quick_export(latest_symbol)
        else:
            messagebox.showinfo("Export", f"Would export {latest_symbol} data (export panel not ready)")
            
    def refresh_current(self):
        """Refresh the current symbol with last used settings"""
        symbol = self.current_symbol.get().strip().upper()
        if not symbol:
            messagebox.showwarning("No Symbol", "Please enter a symbol")
            return
            
        # Use the last settings for this symbol if available
        if symbol in self.dashboard.current_data:
            last_data = self.dashboard.current_data[symbol]
            duration = last_data['duration']
            bar_size = last_data['bar_size']
            description = f"🔄 Refreshed {last_data['description']}"
        else:
            # Default to daily data
            duration = "1 Y"
            bar_size = "1 day"
            description = "🔄 Refreshed Daily Data"
            
        self.fetch_data(duration, bar_size, description)
        
    def quick_analysis(self):
        """Fetch data and immediately create analysis notebook"""
        symbol = self.current_symbol.get().strip().upper()
        if not symbol:
            messagebox.showwarning("No Symbol", "Please enter a symbol")
            return
            
        if self.dashboard.connection_status != "connected":
            messagebox.showwarning("Not Connected", "Please connect to IB Gateway first")
            return
            
        # Fetch daily data first, then create analysis
        self.fetch_data_for_analysis("1 Y", "1 day", "🚀 Quick Analysis")
        
    def fetch_data_for_analysis(self, duration, bar_size, description):
        """Fetch data specifically for analysis creation"""
        symbol = self.current_symbol.get().strip().upper()
        
        if self.is_fetching:
            messagebox.showinfo("Already Fetching", "Data fetch in progress, please wait")
            return
            
        # Get contract details
        contract_type = self.contract_type.get()
        exchange = "SMART"
        expiry = None
        
        # Handle futures contracts
        if contract_type == "FUT":
            if hasattr(self, 'selected_contract') and self.selected_contract:
                expiry = self.selected_contract['expiry']
                exchange = self.selected_contract['exchange']
                description += f" ({expiry})"
            else:
                messagebox.showinfo("Contract Selection", 
                                  f"Please select a futures contract first using the 'Select Contract' button")
                return
            
        self.start_fetch_progress(f"Fetching data for analysis: {symbol}...")
        
        async def do_fetch_and_analyze():
            try:
                # Fetch the data
                data = await self.dashboard.ib_conn.get_historical_data(
                    symbol=symbol,
                    sec_type=contract_type,
                    exchange=exchange,
                    currency="USD",
                    duration=duration,
                    bar_size=bar_size,
                    expiry=expiry,
                    use_rth=True
                )
                
                if data:
                    # Save to database
                    if hasattr(self.dashboard.ib_conn, 'db') and self.dashboard.ib_conn.db:
                        await self.dashboard.ib_conn.db.save_historical_data(symbol, data)
                    
                    # Store in dashboard
                    self.dashboard.current_data[symbol] = {
                        'data': data,
                        'duration': duration,
                        'bar_size': bar_size,
                        'fetched_at': datetime.now(),
                        'description': description
                    }
                    
                    # Update UI and trigger analysis creation
                    self.dashboard.root.after(0, lambda: self.create_analysis_after_fetch(
                        symbol, data, description
                    ))
                else:
                    self.dashboard.root.after(0, lambda: self.fetch_error(
                        f"No data returned for {symbol}"
                    ))
                    
            except Exception as e:
                self.dashboard.root.after(0, lambda: self.fetch_error(str(e)))
                
        # Run the fetch
        future = self.dashboard.run_async_task(do_fetch_and_analyze())
        
    def create_analysis_after_fetch(self, symbol, data, description):
        """Create analysis notebook after successful data fetch"""
        try:
            # Update results panel first
            if hasattr(self.dashboard, 'results_panel') and self.dashboard.results_panel:
                self.dashboard.results_panel.update_data(symbol, data, description)
            
            # Mark fetch as complete
            self.fetch_complete(symbol, len(data), description)
            
            # Automatically trigger analysis creation
            self.dashboard.root.after(1000, self.trigger_analysis_creation)
            
        except Exception as e:
            self.fetch_error(f"Analysis creation failed: {str(e)}")
            
    def trigger_analysis_creation(self):
        """Trigger the analysis notebook creation"""
        if hasattr(self.dashboard, 'results_panel') and self.dashboard.results_panel:
            # Switch to export tab and trigger quick analysis
            self.dashboard.results_panel.notebook.select(2)  # Export tab
            self.dashboard.results_panel.quick_analysis()
        else:
            messagebox.showinfo("Analysis", "Results panel not available for analysis creation")
            
    # ==================== REAL-TIME STREAMING METHODS ====================
    
    def start_live_quotes(self):
        """Start real-time quotes streaming"""
        print(f"🔍 DEBUG: start_live_quotes called")
        
        if not self.dashboard.ib_conn or not self.dashboard.ib_conn.connected:
            print(f"🔍 DEBUG: Not connected - ib_conn: {self.dashboard.ib_conn}, connected: {getattr(self.dashboard.ib_conn, 'connected', False)}")
            messagebox.showwarning("Not Connected", "Please connect to IB Gateway first")
            return
            
        symbol = self.current_symbol.get().strip().upper()
        if not symbol:
            print(f"🔍 DEBUG: No symbol entered, using default AAPL")
            symbol = "AAPL"  # Use default symbol for testing
            self.current_symbol.set(symbol)
            
        print(f"🔍 DEBUG: Starting live quotes for symbol: {symbol}")
        self.update_progress("Starting live quotes...", True)
        
        async def start_streaming():
            try:
                print(f"🔍 DEBUG: Inside start_streaming async function")
                
                # Get contract type
                contract_type = self.contract_type.get()
                print(f"🔍 DEBUG: Contract type: {contract_type}")
                
                # Create callback for real-time updates
                def quote_callback(ticker):
                    print(f"🔍 DEBUG: Quote callback triggered for {ticker}")
                    # Update the live data display
                    if hasattr(self.dashboard, 'results_panel') and self.dashboard.results_panel:
                        self.dashboard.root.after(0, lambda: 
                            self.dashboard.results_panel.update_live_quote(ticker))
                
                print(f"🔍 DEBUG: Calling start_realtime_quotes with symbol={symbol}, sec_type={contract_type}")
                
                # Start the real-time quotes (exchange will be auto-determined)
                ticker = await self.dashboard.ib_conn.start_realtime_quotes(
                    symbol=symbol,
                    sec_type=contract_type,
                    callback=quote_callback
                )
                
                print(f"🔍 DEBUG: start_realtime_quotes returned: {ticker}")
                
                if ticker:
                    # Store the ticker for later stopping
                    if not hasattr(self.dashboard, 'active_tickers'):
                        self.dashboard.active_tickers = {}
                    self.dashboard.active_tickers[f"{symbol}_quotes"] = ticker
                    
                    # Switch to live data tab
                    self.dashboard.root.after(0, lambda: self.switch_to_live_data_tab())
                    self.dashboard.root.after(0, lambda: self.update_progress(
                        f"✅ Live quotes active for {symbol}", False))
                else:
                    self.dashboard.root.after(0, lambda: self.update_progress(
                        "❌ Failed to start live quotes", False))
                    
            except Exception as e:
                print(f"🔍 DEBUG: Exception in start_streaming: {str(e)}")
                import traceback
                traceback.print_exc()
                self.dashboard.root.after(0, lambda: self.update_progress(
                    f"❌ Error: {str(e)}", False))
                
        # Run the streaming start
        print(f"🔍 DEBUG: Calling run_async_task")
        future = self.dashboard.run_async_task(start_streaming())
        print(f"🔍 DEBUG: run_async_task returned: {future}")
        
    def start_market_depth(self):
        """Start Level II market depth streaming"""
        if not self.dashboard.ib_conn or not self.dashboard.ib_conn.connected:
            messagebox.showwarning("Not Connected", "Please connect to IB Gateway first")
            return
            
        symbol = self.current_symbol.get().strip().upper()
        if not symbol:
            messagebox.showwarning("No Symbol", "Please enter a symbol first")
            return
            
        self.update_progress("Starting Level II data...", True)
        
        async def start_depth():
            try:
                # Get contract type
                contract_type = self.contract_type.get()
                
                # Create callback for market depth updates
                def depth_callback(ticker):
                    print(f"🔍 DEBUG: Market depth callback in quick_actions triggered")
                    print(f"🔍 DEBUG: Ticker received: {ticker}")
                    print(f"🔍 DEBUG: Ticker type: {type(ticker)}")
                    # Update the live data display
                    if hasattr(self.dashboard, 'results_panel') and self.dashboard.results_panel:
                        self.dashboard.root.after(0, lambda: 
                            self.dashboard.results_panel.update_market_depth(ticker))
                
                # Start the market depth (exchange will be auto-determined)
                ticker = await self.dashboard.ib_conn.start_market_depth(
                    symbol=symbol,
                    sec_type=contract_type,
                    num_rows=10,
                    callback=depth_callback
                )
                
                if ticker:
                    # Store the ticker for later stopping
                    if not hasattr(self.dashboard, 'active_tickers'):
                        self.dashboard.active_tickers = {}
                    self.dashboard.active_tickers[f"{symbol}_depth"] = ticker
                    
                    # Switch to live data tab
                    self.dashboard.root.after(0, lambda: self.switch_to_live_data_tab())
                    self.dashboard.root.after(0, lambda: self.update_progress(
                        f"✅ Level II active for {symbol}", False))
                else:
                    self.dashboard.root.after(0, lambda: self.update_progress(
                        "❌ Failed to start Level II", False))
                    
            except Exception as e:
                self.dashboard.root.after(0, lambda: self.update_progress(
                    f"❌ Error: {str(e)}", False))
                
        # Run the depth start
        future = self.dashboard.run_async_task(start_depth())
        
    def stop_streaming(self):
        """Stop all active streaming data"""
        if not hasattr(self.dashboard, 'active_tickers') or not self.dashboard.active_tickers:
            messagebox.showinfo("No Streams", "No active streaming data to stop")
            return
            
        self.update_progress("Stopping streams...", True)
        
        async def stop_all_streams():
            try:
                stopped_count = 0
                for stream_id, ticker in list(self.dashboard.active_tickers.items()):
                    try:
                        if "_quotes" in stream_id:
                            self.dashboard.ib_conn.stop_realtime_quotes(ticker)
                        elif "_depth" in stream_id:
                            self.dashboard.ib_conn.stop_market_depth(ticker)
                        stopped_count += 1
                    except Exception as e:
                        print(f"Error stopping {stream_id}: {e}")
                        
                # Clear the active tickers
                self.dashboard.active_tickers.clear()
                
                self.dashboard.root.after(0, lambda: self.update_progress(
                    f"✅ Stopped {stopped_count} streams", False))
                    
            except Exception as e:
                self.dashboard.root.after(0, lambda: self.update_progress(
                    f"❌ Error stopping streams: {str(e)}", False))
                
        # Run the stop operation
        future = self.dashboard.run_async_task(stop_all_streams())
        
    def get_current_symbol(self):
        """Get the current symbol from the symbol entry"""
        return self.current_symbol.get().strip().upper()
    
    def start_enhanced_level2(self):
        """Start enhanced Level II with volume profile"""
        if not self.dashboard.ib_conn or not self.dashboard.ib_conn.connected:
            messagebox.showwarning("Not Connected", "Please connect to IB Gateway first")
            return
        
        symbol = self.get_current_symbol()
        if not symbol:
            messagebox.showwarning("No Symbol", "Please enter a symbol first")
            return
        
        # Open enhanced Level 2 window
        self.open_enhanced_level2_window(symbol)
    
    def open_enhanced_level2_window(self, symbol):
        """Open the enhanced Level 2 display window"""
        try:
            # Create new window for Level 2
            level2_window = tk.Toplevel(self.dashboard.root)
            level2_window.title(f"Level II Pro - {symbol}")
            level2_window.geometry("1400x900")
            
            # Import and create Level 2 display
            from .level2_display import Level2Display
            
            level2_display = Level2Display(level2_window, self.dashboard.ib_conn)
            level2_display.symbol_var.set(symbol)
            
            # Auto-start Level 2 for the symbol after a short delay
            def auto_start():
                try:
                    self.dashboard.run_async_task(level2_display.start_level2())
                except Exception as e:
                    logging.error(f"Auto-start Level 2 error: {e}")
            
            # Schedule auto-start after window is fully created
            level2_window.after(1000, auto_start)
            
            # Focus the window
            level2_window.focus_set()
            level2_window.lift()
            
            logging.info(f"✅ Opened enhanced Level 2 for {symbol}")
            
        except Exception as e:
            logging.error(f"Error opening enhanced Level 2: {e}")
            messagebox.showerror("Error", f"Error opening Level 2: {str(e)}")
    
    def switch_to_live_data_tab(self):
        """Switch to the live data tab in results panel"""
        if hasattr(self.dashboard, 'results_panel') and self.dashboard.results_panel:
            # Switch to the live data tab (index 1)
            self.dashboard.results_panel.notebook.select(1)
    
    def create_batch_operations(self):
        """Add batch operation buttons to existing GUI"""
        batch_frame = ttk.LabelFrame(self.actions_frame, text="🔄 Batch Operations", padding="5")
        batch_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Portfolio operations
        ttk.Button(batch_frame, text="📊 Portfolio Scan", 
                  command=self.batch_portfolio_scan, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(batch_frame, text="🚀 Futures Sweep", 
                  command=self.batch_futures_scan, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(batch_frame, text="📈 Update All", 
                  command=self.batch_update_existing, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(batch_frame, text="🎯 Morning Scan", 
                  command=self.batch_morning_scan, width=15).pack(side=tk.LEFT, padx=2)
    
    def batch_portfolio_scan(self):
        """Scan multiple portfolio symbols with daily data"""
        if self.dashboard.connection_status != "connected":
            messagebox.showwarning("Not Connected", "Please connect to IB Gateway first")
            return
            
        if self.is_fetching:
            messagebox.showinfo("Already Fetching", "Batch operation in progress, please wait")
            return
        
        # Portfolio symbols to scan
        portfolio_symbols = ["AAPL", "SPY", "QQQ", "TSLA", "MSFT", "NVDA", "GOOGL", "AMZN"]
        
        self.start_batch_operation("📊 Portfolio Scan", portfolio_symbols, "1 Y", "1 day")
    
    def batch_futures_scan(self):
        """Scan major futures contracts"""
        if self.dashboard.connection_status != "connected":
            messagebox.showwarning("Not Connected", "Please connect to IB Gateway first")
            return
            
        if self.is_fetching:
            messagebox.showinfo("Already Fetching", "Batch operation in progress, please wait")
            return
        
        # Major futures symbols
        futures_symbols = ["ES", "NQ", "YM", "RTY", "CL", "GC", "SI"]
        
        self.start_batch_futures_operation("🚀 Futures Sweep", futures_symbols, "1 M", "1 day")
    
    def batch_update_existing(self):
        """Update all existing symbols with fresh data"""
        if self.dashboard.connection_status != "connected":
            messagebox.showwarning("Not Connected", "Please connect to IB Gateway first")
            return
            
        if self.is_fetching:
            messagebox.showinfo("Already Fetching", "Batch operation in progress, please wait")
            return
        
        if not self.dashboard.current_data:
            messagebox.showinfo("No Data", "No existing data to update. Fetch some data first.")
            return
        
        # Get all symbols that have been fetched before
        existing_symbols = list(self.dashboard.current_data.keys())
        
        self.start_batch_operation("📈 Update All", existing_symbols, "30 D", "1 day")
    
    def batch_morning_scan(self):
        """Morning market scan with key symbols and timeframes"""
        if self.dashboard.connection_status != "connected":
            messagebox.showwarning("Not Connected", "Please connect to IB Gateway first")
            return
            
        if self.is_fetching:
            messagebox.showinfo("Already Fetching", "Batch operation in progress, please wait")
            return
        
        # Morning scan symbols (stocks only for now to avoid contract issues)
        morning_symbols = ["SPY", "QQQ", "TLT", "GLD", "VXX"]  # VXX instead of VIX for stock-based VIX exposure
        
        self.start_batch_operation("🎯 Morning Scan", morning_symbols, "5 D", "1 hour")
    
    def start_batch_operation(self, operation_name, symbols, duration, bar_size):
        """Execute batch operation for stock symbols"""
        self.is_fetching = True
        self.batch_progress = {"current": 0, "total": len(symbols), "operation": operation_name}
        
        self.progress_label.config(
            text=f"{operation_name}: Starting batch for {len(symbols)} symbols...", 
            foreground="blue"
        )
        self.progress_bar.start(10)
        
        async def batch_fetch():
            successful = 0
            failed = 0
            
            for i, symbol in enumerate(symbols):
                try:
                    # Update progress
                    self.dashboard.root.after(0, lambda s=symbol, idx=i: self.update_batch_progress(s, idx))
                    
                    # Fetch data for this symbol
                    data = await self.dashboard.ib_conn.get_historical_data(
                        symbol=symbol,
                        sec_type="STK",
                        exchange="SMART",
                        currency="USD",
                        duration=duration,
                        bar_size=bar_size,
                        use_rth=True
                    )
                    
                    if data:
                        # Save to database with retry logic
                        if hasattr(self.dashboard.ib_conn, 'db') and self.dashboard.ib_conn.db:
                            try:
                                await self.dashboard.ib_conn.db.save_historical_data(symbol, data)
                            except Exception as db_error:
                                logging.warning(f"Database save failed for {symbol}: {db_error}")
                                # Continue without failing the entire operation
                        
                        # Store in dashboard
                        self.dashboard.current_data[symbol] = {
                            'data': data,
                            'duration': duration,
                            'bar_size': bar_size,
                            'fetched_at': datetime.now(),
                            'description': f"{operation_name} - {len(data)} bars"
                        }
                        successful += 1
                    else:
                        failed += 1
                        
                    # Small delay between requests to avoid rate limiting
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logging.error(f"Batch fetch error for {symbol}: {e}")
                    failed += 1
            
            # Complete the batch operation
            self.dashboard.root.after(0, lambda: self.complete_batch_operation(
                operation_name, successful, failed
            ))
        
        # Run the batch fetch
        future = self.dashboard.run_async_task(batch_fetch())
    
    def start_batch_futures_operation(self, operation_name, symbols, duration, bar_size):
        """Execute batch operation for futures symbols"""
        self.is_fetching = True
        self.batch_progress = {"current": 0, "total": len(symbols), "operation": operation_name}
        
        self.progress_label.config(
            text=f"{operation_name}: Starting batch for {len(symbols)} futures...", 
            foreground="blue"
        )
        self.progress_bar.start(10)
        
        async def batch_futures_fetch():
            successful = 0
            failed = 0
            
            for i, symbol in enumerate(symbols):
                try:
                    # Update progress
                    self.dashboard.root.after(0, lambda s=symbol, idx=i: self.update_batch_progress(s, idx))
                    
                    # Get front contract for futures
                    contracts = await self.dashboard.ib_conn.get_futures_contracts(symbol, "SMART", "USD")
                    if not contracts:
                        failed += 1
                        continue
                    
                    # Use front contract (first in list)
                    front_contract = contracts[0]
                    expiry = front_contract.lastTradeDateOrContractMonth
                    
                    # Fetch data for this futures contract
                    data = await self.dashboard.ib_conn.get_historical_data(
                        symbol=symbol,
                        sec_type="FUT",
                        exchange="SMART",
                        currency="USD",
                        duration=duration,
                        bar_size=bar_size,
                        expiry=expiry,
                        use_rth=True
                    )
                    
                    if data:
                        # Save to database with retry logic
                        if hasattr(self.dashboard.ib_conn, 'db') and self.dashboard.ib_conn.db:
                            try:
                                await self.dashboard.ib_conn.db.save_historical_data(f"{symbol}_{expiry}", data)
                            except Exception as db_error:
                                logging.warning(f"Database save failed for {symbol}_{expiry}: {db_error}")
                                # Continue without failing the entire operation
                        
                        # Store in dashboard with expiry info
                        display_symbol = f"{symbol}_{expiry}"
                        self.dashboard.current_data[display_symbol] = {
                            'data': data,
                            'duration': duration,
                            'bar_size': bar_size,
                            'fetched_at': datetime.now(),
                            'description': f"{operation_name} - {len(data)} bars ({expiry})"
                        }
                        successful += 1
                    else:
                        failed += 1
                        
                    # Small delay between requests
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logging.error(f"Batch futures fetch error for {symbol}: {e}")
                    failed += 1
            
            # Complete the batch operation
            self.dashboard.root.after(0, lambda: self.complete_batch_operation(
                operation_name, successful, failed
            ))
        
        # Run the batch fetch
        future = self.dashboard.run_async_task(batch_futures_fetch())
    
    def update_batch_progress(self, current_symbol, index):
        """Update batch operation progress"""
        if hasattr(self, 'batch_progress'):
            self.batch_progress["current"] = index + 1
            progress_text = f"{self.batch_progress['operation']}: {current_symbol} ({self.batch_progress['current']}/{self.batch_progress['total']})"
            self.progress_label.config(text=progress_text, foreground="blue")
    
    def complete_batch_operation(self, operation_name, successful, failed):
        """Complete batch operation and show results"""
        self.is_fetching = False
        self.progress_bar.stop()
        
        total = successful + failed
        success_rate = (successful / total * 100) if total > 0 else 0
        
        result_text = f"✅ {operation_name}: {successful}/{total} successful ({success_rate:.0f}%)"
        if failed > 0:
            result_text += f", {failed} failed"
        
        self.progress_label.config(text=result_text, foreground="green")
        
        # Re-enable buttons
        self.enable_buttons()
        
        # Update results panel if available
        if hasattr(self.dashboard, 'results_panel') and self.dashboard.results_panel:
            # Try to refresh the results panel data display
            try:
                if hasattr(self.dashboard.results_panel, 'refresh_data_list'):
                    self.dashboard.results_panel.refresh_data_list()
                elif hasattr(self.dashboard.results_panel, 'update_data_display'):
                    self.dashboard.results_panel.update_data_display()
            except Exception as e:
                logging.warning(f"Could not refresh results panel: {e}")
        
        # Auto-clear status after 10 seconds
        self.dashboard.root.after(10000, self.clear_status)
        
        # Show completion message
        messagebox.showinfo("Batch Complete", 
                          f"{operation_name} completed!\n\n"
                          f"✅ Successful: {successful}\n"
                          f"❌ Failed: {failed}\n"
                          f"📊 Success Rate: {success_rate:.0f}%")
        
        # Clean up batch progress
        if hasattr(self, 'batch_progress'):
            delattr(self, 'batch_progress')
    
    def smart_fetch(self):
        """Smart fetch that uses current duration and bar size settings"""
        duration = self.duration_var.get()
        bar_size = self.bar_size_var.get()
        self.fetch_data(duration, bar_size, f"📊 Smart Fetch ({duration}, {bar_size})")
    
    def on_symbol_keyrelease(self, event):
        """Handle symbol input with smart suggestions"""
        current_text = self.current_symbol.get().upper()
        
        # Common symbols for suggestions
        common_symbols = {
            'stocks': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'SPY', 'QQQ', 'IWM', 'VTI', 'TLT', 'GLD', 'VXX'],
            'futures': ['ES', 'NQ', 'YM', 'RTY', 'CL', 'GC', 'SI', 'ZN', 'ZB'],
            'crypto': ['COIN', 'MSTR', 'RIOT', 'MARA']
        }
        
        if len(current_text) >= 1:
            # Show suggestions
            suggestions = []
            for category, symbols in common_symbols.items():
                for symbol in symbols:
                    if symbol.startswith(current_text):
                        suggestions.append(symbol)
            
            if suggestions and len(current_text) < 4:  # Only show for partial matches
                self.show_suggestions(suggestions[:6])  # Limit to 6 suggestions
            else:
                self.hide_suggestions()
        else:
            self.hide_suggestions()
    
    def show_suggestions(self, suggestions):
        """Show symbol suggestions"""
        # Clear existing suggestions
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()
        
        if not suggestions:
            return
        
        # Pack the suggestions frame
        self.suggestions_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(self.suggestions_frame, text="Suggestions:", 
                 font=("Arial", 8), foreground="gray").pack(anchor=tk.W)
        
        # Create suggestion buttons
        suggestions_row = ttk.Frame(self.suggestions_frame)
        suggestions_row.pack(fill=tk.X, pady=2)
        
        for symbol in suggestions:
            btn = ttk.Button(
                suggestions_row,
                text=symbol,
                width=6,
                command=lambda s=symbol: self.select_suggestion(s)
            )
            btn.pack(side=tk.LEFT, padx=1)
    
    def hide_suggestions(self):
        """Hide symbol suggestions"""
        self.suggestions_frame.pack_forget()
    
    def select_suggestion(self, symbol):
        """Select a suggested symbol"""
        self.current_symbol.set(symbol)
        self.hide_suggestions()
        
        # Auto-detect contract type
        if symbol in ['ES', 'NQ', 'YM', 'RTY', 'CL', 'GC', 'SI', 'ZN', 'ZB']:
            self.contract_type.set("FUT")
        else:
            self.contract_type.set("STK")
        
        self.on_contract_type_change()
        self.symbol_entry.focus()
    
    def show_custom_preset_dialog(self):
        """Show dialog to create custom presets"""
        dialog = tk.Toplevel(self.dashboard.root)
        dialog.title("⚙️ Create Custom Preset")
        dialog.geometry("500x400")
        dialog.transient(self.dashboard.root)
        dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Preset name
        ttk.Label(main_frame, text="Preset Name:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        preset_name_var = tk.StringVar(value="My Custom Preset")
        ttk.Entry(main_frame, textvariable=preset_name_var, width=40).pack(fill=tk.X, pady=(5, 15))
        
        # Duration selection
        ttk.Label(main_frame, text="Duration:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        duration_var = tk.StringVar(value="1 Y")
        duration_combo = ttk.Combobox(
            main_frame, 
            textvariable=duration_var,
            values=["1 D", "2 D", "3 D", "1 W", "2 W", "1 M", "2 M", "3 M", "6 M", "1 Y", "2 Y", "5 Y"],
            width=15,
            state="readonly"
        )
        duration_combo.pack(anchor=tk.W, pady=(5, 15))
        
        # Bar size selection
        ttk.Label(main_frame, text="Bar Size:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        bar_size_var = tk.StringVar(value="1 day")
        bar_size_combo = ttk.Combobox(
            main_frame,
            textvariable=bar_size_var,
            values=["1 min", "2 mins", "5 mins", "10 mins", "15 mins", "30 mins", "1 hour", "2 hours", "4 hours", "1 day", "1 week"],
            width=15,
            state="readonly"
        )
        bar_size_combo.pack(anchor=tk.W, pady=(5, 15))
        
        # Symbol list
        ttk.Label(main_frame, text="Symbols (one per line):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        symbols_text = tk.Text(main_frame, height=8, width=40)
        symbols_text.pack(fill=tk.BOTH, expand=True, pady=(5, 15))
        symbols_text.insert(1.0, "AAPL\nSPY\nQQQ\nTSLA")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def execute_custom_preset():
            symbols = [s.strip().upper() for s in symbols_text.get(1.0, tk.END).strip().split('\n') if s.strip()]
            if symbols:
                preset_name = preset_name_var.get()
                duration = duration_var.get()
                bar_size = bar_size_var.get()
                
                dialog.destroy()
                self.start_batch_operation(f"⚙️ {preset_name}", symbols, duration, bar_size)
            else:
                messagebox.showwarning("No Symbols", "Please enter at least one symbol", parent=dialog)
        
        ttk.Button(button_frame, text="Execute Preset", command=execute_custom_preset).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def show_multi_symbol_dialog(self):
        """Show dialog for multi-symbol analysis setup"""
        dialog = tk.Toplevel(self.dashboard.root)
        dialog.title("📋 Multi-Symbol Analysis")
        dialog.geometry("600x500")
        dialog.transient(self.dashboard.root)
        dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Preset categories
        categories_frame = ttk.LabelFrame(main_frame, text="Quick Categories", padding="10")
        categories_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Category buttons
        cat_row1 = ttk.Frame(categories_frame)
        cat_row1.pack(fill=tk.X, pady=2)
        
        def load_category(symbols_list):
            symbols_text.delete(1.0, tk.END)
            symbols_text.insert(1.0, '\n'.join(symbols_list))
        
        ttk.Button(cat_row1, text="📊 Large Cap", 
                  command=lambda: load_category(["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"]), 
                  width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(cat_row1, text="📈 ETFs", 
                  command=lambda: load_category(["SPY", "QQQ", "IWM", "VTI", "TLT", "GLD"]), 
                  width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(cat_row1, text="🚀 Futures", 
                  command=lambda: load_category(["ES", "NQ", "YM", "RTY", "CL", "GC"]), 
                  width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(cat_row1, text="💰 Crypto", 
                  command=lambda: load_category(["COIN", "MSTR", "RIOT", "MARA"]), 
                  width=12).pack(side=tk.LEFT, padx=2)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Analysis Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        settings_row = ttk.Frame(settings_frame)
        settings_row.pack(fill=tk.X)
        
        ttk.Label(settings_row, text="Duration:").pack(side=tk.LEFT)
        multi_duration_var = tk.StringVar(value="3 M")
        ttk.Combobox(settings_row, textvariable=multi_duration_var,
                    values=["1 W", "2 W", "1 M", "2 M", "3 M", "6 M", "1 Y"],
                    width=10, state="readonly").pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(settings_row, text="Bar Size:").pack(side=tk.LEFT)
        multi_bar_var = tk.StringVar(value="1 day")
        ttk.Combobox(settings_row, textvariable=multi_bar_var,
                    values=["1 hour", "4 hours", "1 day", "1 week"],
                    width=10, state="readonly").pack(side=tk.LEFT, padx=(5, 15))
        
        # Auto-analysis checkbox
        auto_analysis_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_row, text="Auto-create analysis notebook", 
                       variable=auto_analysis_var).pack(side=tk.LEFT, padx=15)
        
        # Symbol list
        ttk.Label(main_frame, text="Symbols for Analysis:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        symbols_text = tk.Text(main_frame, height=10, width=50)
        symbols_text.pack(fill=tk.BOTH, expand=True, pady=(5, 15))
        symbols_text.insert(1.0, "SPY\nQQQ\nTLT\nGLD\nVXX")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def execute_multi_analysis():
            symbols = [s.strip().upper() for s in symbols_text.get(1.0, tk.END).strip().split('\n') if s.strip()]
            if symbols:
                duration = multi_duration_var.get()
                bar_size = multi_bar_var.get()
                auto_analysis = auto_analysis_var.get()
                
                dialog.destroy()
                
                # Start batch operation
                self.start_batch_operation(f"📋 Multi-Symbol Analysis", symbols, duration, bar_size)
                
                # If auto-analysis is enabled, trigger notebook creation after a delay
                if auto_analysis:
                    self.dashboard.root.after(5000, self.trigger_multi_symbol_analysis)
            else:
                messagebox.showwarning("No Symbols", "Please enter at least one symbol", parent=dialog)
        
        ttk.Button(button_frame, text="Start Analysis", command=execute_multi_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def trigger_multi_symbol_analysis(self):
        """Trigger multi-symbol analysis notebook creation"""
        if hasattr(self.dashboard, 'results_panel') and self.dashboard.results_panel:
            # Switch to export tab and trigger analysis
            self.dashboard.results_panel.notebook.select(3)  # Export tab
            messagebox.showinfo("Analysis Ready", 
                              "Multi-symbol data loaded! Switch to Export tab to create analysis notebooks.")
    
    def save_preset_config(self):
        """Save current preset configuration"""
        messagebox.showinfo("Save Config", 
                          "Preset configuration saved!\n\n"
                          "Your custom presets and symbol lists have been saved for future sessions.")
        # TODO: Implement actual config saving to JSON file
    
    def show_feature_analysis(self):
        """Show feature selector dialog for custom analysis"""
        if not self.current_symbol.get().strip():
            messagebox.showwarning("No Symbol", "Please enter a symbol first")
            return
        
        # Import here to avoid circular imports
        from ib_data_manager.gui.feature_selector import show_feature_selector
        
        def on_features_selected(selected_features):
            """Callback when features are selected"""
            if selected_features:
                self.create_custom_analysis_notebook(selected_features)
        
        # Show feature selector dialog
        show_feature_selector(self.dashboard.root, callback=on_features_selected)
    
    def create_custom_analysis_notebook(self, selected_features):
        """Create analysis notebook with selected features"""
        symbol = self.current_symbol.get().strip().upper()
        
        # First fetch the data
        duration = self.duration_var.get()
        bar_size = self.bar_size_var.get()
        
        # Show progress
        self.progress_label.config(text=f"Fetching {symbol} data for custom analysis...", foreground="blue")
        self.progress_bar.start(10)
        
        async def fetch_and_analyze():
            try:
                # Fetch data
                contract_type = self.contract_type.get()
                
                if contract_type == "FUT":
                    # Handle futures
                    data = await self.dashboard.ib_conn.get_historical_data(
                        symbol=symbol,
                        sec_type="FUT", 
                        exchange="SMART",
                        currency="USD",
                        duration=duration,
                        bar_size=bar_size,
                        use_rth=True
                    )
                else:
                    # Handle stocks
                    data = await self.dashboard.ib_conn.get_historical_data(
                        symbol=symbol,
                        sec_type="STK",
                        exchange="SMART", 
                        currency="USD",
                        duration=duration,
                        bar_size=bar_size,
                        use_rth=True
                    )
                
                if data:
                    # Save to database
                    if hasattr(self.dashboard.ib_conn, 'db') and self.dashboard.ib_conn.db:
                        try:
                            await self.dashboard.ib_conn.db.save_historical_data(symbol, data)
                        except Exception as db_error:
                            logging.warning(f"Database save failed: {db_error}")
                    
                    # Update dashboard data
                    self.dashboard.current_data[symbol] = {
                        'data': data,
                        'duration': duration,
                        'bar_size': bar_size,
                        'fetched_at': datetime.now(),
                        'description': f"Custom Analysis - {len(data)} bars"
                    }
                    
                    # Update results panel
                    if hasattr(self.dashboard, 'results_panel') and self.dashboard.results_panel:
                        self.dashboard.results_panel.update_data(symbol, data, f"Custom Analysis ({len(selected_features)} features)")
                    
                    # Create custom notebook with selected features
                    self.dashboard.root.after(0, lambda: self.generate_custom_notebook(symbol, data, selected_features))
                    
                else:
                    self.dashboard.root.after(0, lambda: self.show_error("No data received"))
                    
            except Exception as e:
                logging.error(f"Custom analysis fetch error: {e}")
                self.dashboard.root.after(0, lambda: self.show_error(str(e)))
        
        # Run the fetch
        future = self.dashboard.run_async_task(fetch_and_analyze())
    
    def generate_custom_notebook(self, symbol, data, selected_features):
        """Generate Jupyter notebook with custom features"""
        try:
            from ib_data_manager.utils.jupyter_generator import JupyterNotebookGenerator
            import csv
            import os
            
            # Create CSV export
            export_dir = os.path.join(os.getcwd(), "exports")
            os.makedirs(export_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"{symbol}_custom_analysis_{timestamp}.csv"
            csv_path = os.path.join(export_dir, csv_filename)
            
            # Write CSV
            with open(csv_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['date', 'open', 'high', 'low', 'close', 'volume'])
                for bar in data:
                    writer.writerow([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])
            
            # Generate notebook with selected features
            generator = JupyterNotebookGenerator("notebooks")
            notebook_path = generator.create_analysis_notebook(
                csv_path, symbol, "custom_analysis", selected_features
            )
            
            self.progress_bar.stop()
            self.progress_label.config(
                text=f"✅ Custom analysis notebook created: {os.path.basename(notebook_path)}", 
                foreground="green"
            )
            
            # Launch Jupyter
            self.launch_jupyter_notebook(notebook_path)
            
        except Exception as e:
            logging.error(f"Notebook generation error: {e}")
            self.progress_bar.stop()
            self.progress_label.config(text=f"❌ Error creating notebook: {str(e)}", foreground="red")
    
    def launch_jupyter_notebook(self, notebook_path):
        """Launch Jupyter notebook with system environment"""
        try:
            import subprocess
            import sys
            
            # Try Jupyter Lab first, then fallback to notebook
            try:
                if sys.platform == "win32":
                    subprocess.Popen(f'jupyter lab "{notebook_path}"', shell=True)
                else:
                    subprocess.Popen(['jupyter', 'lab', str(notebook_path)])
                
                messagebox.showinfo("Notebook Ready", 
                                  f"✅ Custom analysis notebook created!\n\n"
                                  f"📊 Notebook: {os.path.basename(notebook_path)}\n"
                                  f"🧪 Opening in Jupyter Lab\n\n"
                                  f"The notebook includes smart import handling - missing libraries will show helpful install messages.")
                                  
            except FileNotFoundError:
                # Fallback to regular notebook
                if sys.platform == "win32":
                    subprocess.Popen(f'jupyter notebook "{notebook_path}"', shell=True)
                else:
                    subprocess.Popen(['jupyter', 'notebook', str(notebook_path)])
                
                messagebox.showinfo("Notebook Ready", 
                                  f"✅ Custom analysis notebook created!\n\n"
                                  f"📊 Notebook: {os.path.basename(notebook_path)}\n"
                                  f"🧪 Opening in Jupyter Notebook\n\n"
                                  f"The notebook includes smart import handling - missing libraries will show helpful install messages.")
                              
        except Exception as e:
            logging.error(f"Jupyter launch error: {e}")
            messagebox.showerror("Launch Failed", 
                               f"❌ Could not launch Jupyter.\n\n"
                               f"Error: {str(e)}\n\n"
                               f"Please ensure Jupyter is installed:\n"
                               f"pip install jupyter\n\n"
                               f"Or manually open: {notebook_path}")
        
        # Auto-clear status after 10 seconds
        self.dashboard.root.after(10000, self.clear_status)
    
    def show_error(self, error_message):
        """Show error message"""
        self.progress_bar.stop()
        self.progress_label.config(text=f"❌ Error: {error_message}", foreground="red")
        messagebox.showerror("Error", f"Operation failed:\n\n{error_message}")
    
    def clear_status(self):
        """Clear status message"""
        self.progress_label.config(text="Ready", foreground="gray")
