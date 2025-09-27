"""
Unified IB Data Manager Dashboard
A streamlined, efficient interface that eliminates GUI fragmentation
"""

import asyncio
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import logging
import json
import os
from typing import Dict, List, Any, Optional

from ib_data_manager.api.async_ib_connector import AsyncIBConnector
from ib_data_manager.gui.connection_panel import ConnectionPanel
from ib_data_manager.gui.quick_actions import QuickActionsPanel
from ib_data_manager.gui.results_panel import ResultsPanel

class UnifiedDashboard:
    """
    Unified dashboard that brings all functionality into one efficient interface.
    No more navigating between tabs or scattered controls.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("IB Data Manager - Unified Dashboard")
        self.root.geometry("1400x900")
        
        # Core components
        self.ib_conn = AsyncIBConnector()
        self.loop = None
        self.thread = None
        
        # Data storage
        self.current_data = {}
        self.connection_status = "disconnected"
        
        # UI Components
        self.connection_panel = None
        self.quick_actions = None
        self.results_panel = None
        
        # Settings and preferences
        self.settings = self.load_settings()
        
        # Initialize async loop
        self.start_async_loop()
        
        # Create the unified interface
        self.create_dashboard()
        
        # Auto-connect if configured
        self.root.after(1000, self.auto_connect_if_configured)
        
    def create_dashboard(self):
        """Create the main dashboard layout"""
        # Main container with padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for responsive layout
        main_container.columnconfigure(0, weight=2)  # Left panel
        main_container.columnconfigure(1, weight=3)  # Right panel
        main_container.rowconfigure(0, weight=1)
        
        # Create left and right panels
        self.create_left_panel(main_container)
        self.create_right_panel(main_container)
        
    def create_left_panel(self, parent):
        """Create the left control panel"""
        left_frame = ttk.Frame(parent)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        left_frame.columnconfigure(0, weight=1)
        
        # Connection Panel - Always visible at the top
        self.connection_panel = ConnectionPanel(left_frame, self)
        
        # Quick Actions Panel - Main data acquisition interface
        self.quick_actions = QuickActionsPanel(left_frame, self)
        
        # Placeholder for additional panels (Settings, etc.)
        # These will be added in subsequent steps
        
    def create_right_panel(self, parent):
        """Create the right results panel"""
        right_frame = ttk.Frame(parent)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        # Results Panel - Integrated data display and export
        self.results_panel = ResultsPanel(right_frame, self)
        
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
            print("Error: Async loop not running")
            return None
            
    def load_settings(self):
        """Load user settings and preferences"""
        try:
            with open("dashboard_settings.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Default settings
            # Check if quantitative analysis environment exists
            quant_analysis_dir = r"C:\Users\tnova\quant_analysis\data\exports"
            if os.path.exists(r"C:\Users\tnova\quant_analysis"):
                default_export_dir = quant_analysis_dir
            else:
                default_export_dir = os.path.expanduser("~/Documents/IB_Data")
                
            return {
                "auto_connect": False,
                "default_symbols": ["AAPL", "SPY", "QQQ"],
                "default_timeframe": "1 Y",
                "default_bar_size": "1 day",
                "export_dir": default_export_dir,
                "theme": "default"
            }
            
    def save_settings(self):
        """Save current settings"""
        try:
            with open("dashboard_settings.json", "w") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")
            
    def auto_connect_if_configured(self):
        """Auto-connect to IB Gateway if configured"""
        if self.settings.get("auto_connect", False) and self.connection_panel:
            self.connection_panel.connect()
        
    def on_closing(self):
        """Handle application closing"""
        self.save_settings()
        if self.loop and self.thread and self.thread.is_alive():
            self.loop.call_soon_threadsafe(self.loop.stop)
        self.root.destroy()

def main():
    """Launch the unified dashboard"""
    root = tk.Tk()
    dashboard = UnifiedDashboard(root)
    root.protocol("WM_DELETE_WINDOW", dashboard.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
