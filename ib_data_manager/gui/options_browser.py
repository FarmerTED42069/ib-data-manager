"""
Options Chain Browser Component
Advanced options chain selection and data acquisition
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import asyncio
from typing import List, Dict, Any, Optional

class OptionsBrowser:
    """
    Comprehensive options chain browser with strike selection,
    expiry management, and options data acquisition.
    """
    
    def __init__(self, parent, dashboard, symbol):
        self.parent = parent
        self.dashboard = dashboard
        self.symbol = symbol
        self.selected_option = None
        self.chain_data = {}
        
        self.create_browser()
        
    def create_browser(self):
        """Create the options browser interface"""
        # Main window
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"Options Chain - {self.symbol}")
        self.window.geometry("1000x700")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Header
        self.create_header()
        
        # Control panel
        self.create_controls()
        
        # Options chain display
        self.create_chain_display()
        
        # Action buttons
        self.create_action_buttons()
        
        # Load initial data
        self.load_options_chain()
        
    def create_header(self):
        """Create header with symbol info"""
        header_frame = ttk.Frame(self.window, padding="10")
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, text=f"📊 Options Chain for {self.symbol}", 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(header_frame, text="Loading...", foreground="blue")
        self.status_label.pack(side=tk.RIGHT)
        
    def create_controls(self):
        """Create control panel for filtering options"""
        controls_frame = ttk.LabelFrame(self.window, text="Chain Filters", padding="10")
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Row 1: Expiry and option type
        row1 = ttk.Frame(controls_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1, text="Expiry:").pack(side=tk.LEFT)
        self.expiry_var = tk.StringVar()
        self.expiry_combo = ttk.Combobox(row1, textvariable=self.expiry_var, 
                                        width=15, state="readonly")
        self.expiry_combo.pack(side=tk.LEFT, padx=(5, 20))
        self.expiry_combo.bind("<<ComboboxSelected>>", self.on_expiry_change)
        
        ttk.Label(row1, text="Type:").pack(side=tk.LEFT)
        self.option_type = tk.StringVar(value="CALL")
        type_frame = ttk.Frame(row1)
        type_frame.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Radiobutton(type_frame, text="Calls", variable=self.option_type, 
                       value="CALL", command=self.filter_chain).pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="Puts", variable=self.option_type, 
                       value="PUT", command=self.filter_chain).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(type_frame, text="Both", variable=self.option_type, 
                       value="BOTH", command=self.filter_chain).pack(side=tk.LEFT, padx=(10, 0))
        
        # Row 2: Strike range
        row2 = ttk.Frame(controls_frame)
        row2.pack(fill=tk.X, pady=5)
        
        ttk.Label(row2, text="Strike Range:").pack(side=tk.LEFT)
        self.strike_range = tk.StringVar(value="ATM ±10")
        range_combo = ttk.Combobox(row2, textvariable=self.strike_range,
                                  values=["All", "ATM ±5", "ATM ±10", "ATM ±20", "ITM Only", "OTM Only"],
                                  width=12, state="readonly")
        range_combo.pack(side=tk.LEFT, padx=(5, 20))
        range_combo.bind("<<ComboboxSelected>>", self.filter_chain)
        
        ttk.Button(row2, text="🔄 Refresh Chain", 
                  command=self.load_options_chain).pack(side=tk.RIGHT)
        
    def create_chain_display(self):
        """Create options chain display"""
        display_frame = ttk.Frame(self.window, padding="10")
        display_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(display_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Chain view
        self.create_chain_view()
        
        # Greeks view (placeholder)
        self.create_greeks_view()
        
    def create_chain_view(self):
        """Create main options chain view"""
        chain_frame = ttk.Frame(self.notebook)
        self.notebook.add(chain_frame, text="📊 Options Chain")
        
        # Treeview for options data
        columns = ("strike", "call_bid", "call_ask", "call_last", "call_vol", 
                  "put_bid", "put_ask", "put_last", "put_vol", "expiry")
        
        self.chain_tree = ttk.Treeview(chain_frame, columns=columns, show="headings", height=20)
        
        # Configure columns
        column_config = {
            "strike": {"text": "Strike", "width": 80},
            "call_bid": {"text": "Call Bid", "width": 70},
            "call_ask": {"text": "Call Ask", "width": 70},
            "call_last": {"text": "Call Last", "width": 70},
            "call_vol": {"text": "Call Vol", "width": 70},
            "put_bid": {"text": "Put Bid", "width": 70},
            "put_ask": {"text": "Put Ask", "width": 70},
            "put_last": {"text": "Put Last", "width": 70},
            "put_vol": {"text": "Put Vol", "width": 70},
            "expiry": {"text": "Expiry", "width": 100}
        }
        
        for col, config in column_config.items():
            self.chain_tree.heading(col, text=config["text"])
            self.chain_tree.column(col, width=config["width"], anchor="center")
            
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(chain_frame, orient="vertical", command=self.chain_tree.yview)
        h_scrollbar = ttk.Scrollbar(chain_frame, orient="horizontal", command=self.chain_tree.xview)
        self.chain_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack components
        self.chain_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind selection
        self.chain_tree.bind("<<TreeviewSelect>>", self.on_option_select)
        self.chain_tree.bind("<Double-Button-1>", self.on_option_double_click)
        
    def create_greeks_view(self):
        """Create Greeks analysis view (placeholder)"""
        greeks_frame = ttk.Frame(self.notebook)
        self.notebook.add(greeks_frame, text="🔢 Greeks")
        
        ttk.Label(greeks_frame, text="📈 Options Greeks Analysis", 
                 font=("Arial", 14, "bold")).pack(pady=20)
        ttk.Label(greeks_frame, text="Coming soon:\n• Delta, Gamma, Theta, Vega\n• Risk analysis\n• Volatility surface", 
                 font=("Arial", 12), justify=tk.CENTER).pack()
        
    def create_action_buttons(self):
        """Create action buttons"""
        button_frame = ttk.Frame(self.window, padding="10")
        button_frame.pack(fill=tk.X)
        
        # Selection info
        self.selection_label = ttk.Label(button_frame, text="No option selected", 
                                        foreground="gray")
        self.selection_label.pack(side=tk.LEFT)
        
        # Action buttons
        ttk.Button(button_frame, text="📊 Get Option Data", 
                  command=self.fetch_option_data).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Select Option", 
                  command=self.select_option).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        
    def load_options_chain(self):
        """Load options chain data"""
        self.status_label.config(text="Loading options chain...", foreground="blue")
        
        async def get_chain():
            try:
                # This would use the IB API to get options chain
                # For now, we'll create sample data
                await asyncio.sleep(1)  # Simulate API call
                
                # Sample expiry dates
                expiries = [
                    (datetime.now() + timedelta(days=7)).strftime("%Y%m%d"),
                    (datetime.now() + timedelta(days=14)).strftime("%Y%m%d"),
                    (datetime.now() + timedelta(days=30)).strftime("%Y%m%d"),
                    (datetime.now() + timedelta(days=60)).strftime("%Y%m%d")
                ]
                
                self.dashboard.root.after(0, lambda: self.populate_chain_data(expiries))
                
            except Exception as e:
                self.dashboard.root.after(0, lambda: self.status_label.config(
                    text=f"❌ Error loading chain: {str(e)}", foreground="red"
                ))
                
        future = self.dashboard.run_async_task(get_chain())
        
    def populate_chain_data(self, expiries):
        """Populate the chain with sample data"""
        # Update expiry dropdown
        self.expiry_combo['values'] = expiries
        if expiries:
            self.expiry_combo.set(expiries[0])
            
        # Generate sample options data
        self.generate_sample_chain_data()
        self.filter_chain()
        
        self.status_label.config(text="✅ Options chain loaded", foreground="green")
        
    def generate_sample_chain_data(self):
        """Generate sample options chain data"""
        # This would normally come from IB API
        base_price = 440.0  # Sample underlying price
        
        self.chain_data = {}
        for expiry in self.expiry_combo['values']:
            strikes = []
            for i in range(-10, 11):  # ±10 strikes around ATM
                strike = base_price + (i * 5)  # $5 intervals
                strikes.append({
                    'strike': strike,
                    'call_bid': max(0, base_price - strike - 2),
                    'call_ask': max(0, base_price - strike + 2),
                    'call_last': max(0, base_price - strike),
                    'call_vol': 100 + abs(i) * 10,
                    'put_bid': max(0, strike - base_price - 2),
                    'put_ask': max(0, strike - base_price + 2),
                    'put_last': max(0, strike - base_price),
                    'put_vol': 80 + abs(i) * 8,
                    'expiry': expiry
                })
            self.chain_data[expiry] = strikes
            
    def filter_chain(self, event=None):
        """Filter and display options chain"""
        # Clear current display
        for item in self.chain_tree.get_children():
            self.chain_tree.delete(item)
            
        expiry = self.expiry_var.get()
        if not expiry or expiry not in self.chain_data:
            return
            
        option_type = self.option_type.get()
        strike_range = self.strike_range.get()
        
        strikes = self.chain_data[expiry]
        
        # Apply strike range filter
        if strike_range != "All":
            # This would implement actual filtering logic
            pass
            
        # Populate tree
        for strike_data in strikes:
            if option_type == "CALL":
                values = (
                    f"{strike_data['strike']:.0f}",
                    f"{strike_data['call_bid']:.2f}",
                    f"{strike_data['call_ask']:.2f}",
                    f"{strike_data['call_last']:.2f}",
                    f"{strike_data['call_vol']:.0f}",
                    "-", "-", "-", "-",
                    expiry
                )
            elif option_type == "PUT":
                values = (
                    f"{strike_data['strike']:.0f}",
                    "-", "-", "-", "-",
                    f"{strike_data['put_bid']:.2f}",
                    f"{strike_data['put_ask']:.2f}",
                    f"{strike_data['put_last']:.2f}",
                    f"{strike_data['put_vol']:.0f}",
                    expiry
                )
            else:  # BOTH
                values = (
                    f"{strike_data['strike']:.0f}",
                    f"{strike_data['call_bid']:.2f}",
                    f"{strike_data['call_ask']:.2f}",
                    f"{strike_data['call_last']:.2f}",
                    f"{strike_data['call_vol']:.0f}",
                    f"{strike_data['put_bid']:.2f}",
                    f"{strike_data['put_ask']:.2f}",
                    f"{strike_data['put_last']:.2f}",
                    f"{strike_data['put_vol']:.0f}",
                    expiry
                )
                
            self.chain_tree.insert("", tk.END, values=values)
            
    def on_expiry_change(self, event=None):
        """Handle expiry selection change"""
        self.filter_chain()
        
    def on_option_select(self, event):
        """Handle option selection"""
        selection = self.chain_tree.selection()
        if selection:
            item = self.chain_tree.item(selection[0])
            values = item['values']
            strike = values[0]
            expiry = values[-1]
            
            option_type = "CALL" if self.option_type.get() in ["CALL", "BOTH"] else "PUT"
            self.selection_label.config(
                text=f"Selected: {self.symbol} {strike} {option_type} {expiry}",
                foreground="blue"
            )
            
    def on_option_double_click(self, event):
        """Handle double-click to select option"""
        self.select_option()
        
    def select_option(self):
        """Select the current option and close dialog"""
        selection = self.chain_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an option contract")
            return
            
        item = self.chain_tree.item(selection[0])
        values = item['values']
        
        self.selected_option = {
            'symbol': self.symbol,
            'strike': values[0],
            'expiry': values[-1],
            'right': "CALL" if self.option_type.get() in ["CALL", "BOTH"] else "PUT"
        }
        
        messagebox.showinfo("Option Selected", 
                           f"Selected: {self.symbol} {values[0]} {self.selected_option['right']} {values[-1]}")
        self.window.destroy()
        
    def fetch_option_data(self):
        """Fetch historical data for selected option"""
        selection = self.chain_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an option contract")
            return
            
        messagebox.showinfo("Option Data", 
                           "Option historical data fetching will be integrated with the main dashboard")


def show_options_browser(parent, dashboard, symbol):
    """Show options browser for a symbol"""
    browser = OptionsBrowser(parent, dashboard, symbol)
    return browser.selected_option
