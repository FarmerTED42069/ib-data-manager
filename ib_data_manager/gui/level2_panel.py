"""
Level 2 Opportunities GUI Panel
Real-time display of trading opportunities detected from Level 2 data
"""

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading

from ib_data_manager.core.level2_opportunities import Level2OpportunityDetector, OpportunityAlert, OpportunityType
from ib_data_manager.api.level2_connector import Level2Connector


class Level2OpportunityPanel:
    """GUI panel for Level 2 opportunity detection and monitoring"""
    
    def __init__(self, parent_frame, ib_connector):
        self.parent_frame = parent_frame
        self.ib_connector = ib_connector
        
        # Initialize Level 2 components
        self.level2_connector = Level2Connector(ib_connector)
        self.opportunity_detector = Level2OpportunityDetector()
        
        # GUI state
        self.active_symbols = {}
        self.opportunity_alerts = []
        
        # Create the GUI
        self.create_gui()
        
        # Set up opportunity callback
        self.opportunity_detector.add_opportunity_callback(self.on_opportunity_detected)
    
    def create_gui(self):
        """Create the Level 2 opportunities GUI"""
        # Main container
        self.main_frame = ttk.LabelFrame(self.parent_frame, text="🔍 Level 2 Opportunities", padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control panel
        self.create_control_panel()
        
        # Opportunities display
        self.create_opportunities_display()
        
        # Statistics panel
        self.create_statistics_panel()
    
    def create_control_panel(self):
        """Create the control panel for Level 2 monitoring"""
        control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding="5")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Symbol input
        input_frame = ttk.Frame(control_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Symbol:").pack(side=tk.LEFT)
        self.symbol_var = tk.StringVar(value="ES")
        symbol_entry = ttk.Entry(input_frame, textvariable=self.symbol_var, width=10)
        symbol_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        # Security type
        ttk.Label(input_frame, text="Type:").pack(side=tk.LEFT)
        self.sec_type_var = tk.StringVar(value="FUT")
        sec_type_combo = ttk.Combobox(input_frame, textvariable=self.sec_type_var, 
                                     values=["STK", "FUT", "OPT"], width=8, state="readonly")
        sec_type_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.start_button = ttk.Button(button_frame, text="🚀 Start Level 2", 
                                      command=self.start_level2_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="🛑 Stop", 
                                     command=self.stop_level2_monitoring, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_button = ttk.Button(button_frame, text="🗑️ Clear Alerts", 
                                      command=self.clear_alerts)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Settings button
        self.settings_button = ttk.Button(button_frame, text="⚙️ Settings", 
                                         command=self.show_settings)
        self.settings_button.pack(side=tk.RIGHT)
    
    def create_opportunities_display(self):
        """Create the opportunities display area"""
        display_frame = ttk.LabelFrame(self.main_frame, text="🚨 Live Opportunities", padding="5")
        display_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create treeview for opportunities
        columns = ("Time", "Symbol", "Type", "Confidence", "Price", "Action", "Description")
        self.opportunities_tree = ttk.Treeview(display_frame, columns=columns, show="headings", height=8)
        
        # Configure columns
        self.opportunities_tree.heading("Time", text="Time")
        self.opportunities_tree.heading("Symbol", text="Symbol")
        self.opportunities_tree.heading("Type", text="Opportunity")
        self.opportunities_tree.heading("Confidence", text="Confidence")
        self.opportunities_tree.heading("Price", text="Price")
        self.opportunities_tree.heading("Action", text="Action")
        self.opportunities_tree.heading("Description", text="Description")
        
        # Column widths
        self.opportunities_tree.column("Time", width=80)
        self.opportunities_tree.column("Symbol", width=60)
        self.opportunities_tree.column("Type", width=120)
        self.opportunities_tree.column("Confidence", width=80)
        self.opportunities_tree.column("Price", width=80)
        self.opportunities_tree.column("Action", width=60)
        self.opportunities_tree.column("Description", width=300)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.opportunities_tree.yview)
        self.opportunities_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.opportunities_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure row colors based on opportunity type
        self.opportunities_tree.tag_configure("BUY", background="#E8F5E8")
        self.opportunities_tree.tag_configure("SELL", background="#FFE8E8")
        self.opportunities_tree.tag_configure("WATCH", background="#FFF8DC")
    
    def create_statistics_panel(self):
        """Create the statistics display panel"""
        stats_frame = ttk.LabelFrame(self.main_frame, text="📊 Statistics", padding="5")
        stats_frame.pack(fill=tk.X)
        
        # Statistics labels
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        # Row 1
        ttk.Label(stats_grid, text="Active Symbols:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.active_symbols_label = ttk.Label(stats_grid, text="0", foreground="blue")
        self.active_symbols_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(stats_grid, text="Total Opportunities:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.total_opportunities_label = ttk.Label(stats_grid, text="0", foreground="green")
        self.total_opportunities_label.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        # Row 2
        ttk.Label(stats_grid, text="Last Detection:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.last_detection_label = ttk.Label(stats_grid, text="None", foreground="gray")
        self.last_detection_label.grid(row=1, column=1, sticky=tk.W, columnspan=3, padx=(0, 20))
    
    def start_level2_monitoring(self):
        """Start Level 2 monitoring for the selected symbol"""
        try:
            symbol = self.symbol_var.get().upper().strip()
            sec_type = self.sec_type_var.get()
            
            if not symbol:
                messagebox.showerror("Error", "Please enter a symbol")
                return
            
            # Start in a separate thread to avoid blocking GUI
            threading.Thread(target=self._start_monitoring_thread, 
                           args=(symbol, sec_type), daemon=True).start()
            
            # Update GUI state
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            self.show_status(f"Starting Level 2 monitoring for {symbol}...")
            
        except Exception as e:
            logging.error(f"Error starting Level 2 monitoring: {e}")
            messagebox.showerror("Error", f"Failed to start monitoring: {str(e)}")
    
    def _start_monitoring_thread(self, symbol: str, sec_type: str):
        """Start monitoring in async thread"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Start the monitoring
            loop.run_until_complete(self._start_monitoring_async(symbol, sec_type))
            
        except Exception as e:
            logging.error(f"Error in monitoring thread: {e}")
            self.show_status(f"Error: {str(e)}")
        finally:
            loop.close()
    
    async def _start_monitoring_async(self, symbol: str, sec_type: str):
        """Start async Level 2 monitoring"""
        try:
            # Create callback for Level 2 updates
            async def level2_callback(ticker):
                await self.opportunity_detector.process_level2_update(symbol, ticker)
            
            # Start market depth streaming
            ticker = await self.level2_connector.start_market_depth(
                symbol=symbol,
                sec_type=sec_type,
                callback=level2_callback
            )
            
            if ticker:
                self.active_symbols[symbol] = {
                    'sec_type': sec_type,
                    'ticker': ticker,
                    'start_time': datetime.now()
                }
                
                self.show_status(f"✅ Level 2 monitoring active for {symbol}")
                self.update_statistics()
            else:
                self.show_status(f"❌ Failed to start Level 2 for {symbol}")
                
        except Exception as e:
            logging.error(f"Error starting async monitoring: {e}")
            self.show_status(f"Error: {str(e)}")
    
    def stop_level2_monitoring(self):
        """Stop Level 2 monitoring"""
        try:
            # Stop all Level 2 streams
            self.level2_connector.stop_all_streams()
            
            # Clear active symbols
            self.active_symbols.clear()
            
            # Update GUI state
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
            self.show_status("🛑 Level 2 monitoring stopped")
            self.update_statistics()
            
        except Exception as e:
            logging.error(f"Error stopping Level 2 monitoring: {e}")
            messagebox.showerror("Error", f"Failed to stop monitoring: {str(e)}")
    
    def clear_alerts(self):
        """Clear all opportunity alerts"""
        try:
            # Clear the treeview
            for item in self.opportunities_tree.get_children():
                self.opportunities_tree.delete(item)
            
            # Clear the alerts list
            self.opportunity_alerts.clear()
            
            self.show_status("🗑️ Alerts cleared")
            
        except Exception as e:
            logging.error(f"Error clearing alerts: {e}")
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.parent_frame)
        settings_window.title("Level 2 Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.parent_frame)
        settings_window.grab_set()
        
        # Settings content
        ttk.Label(settings_window, text="Detection Thresholds", font=("Arial", 12, "bold")).pack(pady=10)
        
        settings_frame = ttk.Frame(settings_window)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Imbalance threshold
        ttk.Label(settings_frame, text="Order Imbalance Threshold:").grid(row=0, column=0, sticky=tk.W, pady=5)
        imbalance_var = tk.DoubleVar(value=self.opportunity_detector.imbalance_threshold)
        ttk.Scale(settings_frame, from_=1.5, to=10.0, variable=imbalance_var, 
                 orient=tk.HORIZONTAL, length=200).grid(row=0, column=1, padx=10, pady=5)
        ttk.Label(settings_frame, textvariable=imbalance_var).grid(row=0, column=2, pady=5)
        
        # Volume spike threshold
        ttk.Label(settings_frame, text="Volume Spike Threshold:").grid(row=1, column=0, sticky=tk.W, pady=5)
        volume_var = tk.DoubleVar(value=self.opportunity_detector.volume_spike_threshold)
        ttk.Scale(settings_frame, from_=2.0, to=20.0, variable=volume_var, 
                 orient=tk.HORIZONTAL, length=200).grid(row=1, column=1, padx=10, pady=5)
        ttk.Label(settings_frame, textvariable=volume_var).grid(row=1, column=2, pady=5)
        
        # Spread compression threshold
        ttk.Label(settings_frame, text="Spread Compression Threshold:").grid(row=2, column=0, sticky=tk.W, pady=5)
        spread_var = tk.DoubleVar(value=self.opportunity_detector.spread_compression_threshold)
        ttk.Scale(settings_frame, from_=0.1, to=1.0, variable=spread_var, 
                 orient=tk.HORIZONTAL, length=200).grid(row=2, column=1, padx=10, pady=5)
        ttk.Label(settings_frame, textvariable=spread_var).grid(row=2, column=2, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(pady=20)
        
        def apply_settings():
            self.opportunity_detector.imbalance_threshold = imbalance_var.get()
            self.opportunity_detector.volume_spike_threshold = volume_var.get()
            self.opportunity_detector.spread_compression_threshold = spread_var.get()
            settings_window.destroy()
            self.show_status("⚙️ Settings updated")
        
        ttk.Button(button_frame, text="Apply", command=apply_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.LEFT, padx=5)
    
    async def on_opportunity_detected(self, opportunity: OpportunityAlert):
        """Handle detected opportunity"""
        try:
            # Add to alerts list
            self.opportunity_alerts.append(opportunity)
            
            # Update GUI in main thread
            self.parent_frame.after(0, self._update_opportunity_display, opportunity)
            
        except Exception as e:
            logging.error(f"Error handling opportunity: {e}")
    
    def _update_opportunity_display(self, opportunity: OpportunityAlert):
        """Update the opportunity display (called in main thread)"""
        try:
            # Format the opportunity data
            time_str = opportunity.timestamp.strftime("%H:%M:%S")
            confidence_str = f"{opportunity.confidence:.2f}"
            price_str = f"{opportunity.price_level:.2f}"
            
            # Insert into treeview
            item = self.opportunities_tree.insert("", 0, values=(
                time_str,
                opportunity.symbol,
                opportunity.opportunity_type.value.replace("_", " ").title(),
                confidence_str,
                price_str,
                opportunity.action_suggested,
                opportunity.description
            ))
            
            # Apply color tag based on action
            if opportunity.action_suggested:
                self.opportunities_tree.set(item, tags=(opportunity.action_suggested,))
            
            # Keep only last 100 items
            children = self.opportunities_tree.get_children()
            if len(children) > 100:
                self.opportunities_tree.delete(children[-1])
            
            # Update statistics
            self.update_statistics()
            
            # Show status
            self.show_status(f"🚨 {opportunity.opportunity_type.value}: {opportunity.symbol} at {price_str}")
            
        except Exception as e:
            logging.error(f"Error updating opportunity display: {e}")
    
    def update_statistics(self):
        """Update the statistics display"""
        try:
            # Update active symbols count
            self.active_symbols_label.config(text=str(len(self.active_symbols)))
            
            # Update total opportunities
            self.total_opportunities_label.config(text=str(len(self.opportunity_alerts)))
            
            # Update last detection time
            if self.opportunity_alerts:
                last_time = self.opportunity_alerts[-1].timestamp.strftime("%H:%M:%S")
                self.last_detection_label.config(text=last_time, foreground="green")
            else:
                self.last_detection_label.config(text="None", foreground="gray")
                
        except Exception as e:
            logging.error(f"Error updating statistics: {e}")
    
    def show_status(self, message: str):
        """Show status message"""
        # This would typically update a status bar
        logging.info(f"Level 2 Status: {message}")
        print(f"Level 2 Status: {message}")  # For debugging
