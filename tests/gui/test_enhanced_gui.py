"""
Test script for the enhanced GUI with multi-asset data acquisition
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import tkinter as tk
from ib_data_manager.gui.main_async import AsyncIBDataManager

def main():
    """Test the enhanced GUI"""
    print("🚀 Starting Enhanced IB Data Manager GUI...")
    print("📊 Features available:")
    print("   • Basic Data Acquisition (original functionality)")
    print("   • Enhanced Data Acquisition (multi-asset, advanced timeframes)")
    print("   • Batch processing with progress tracking")
    print("   • Preset asset groups (Major Stocks, Tech, ETFs, Futures, Forex)")
    print("   • Advanced timeframe selection with presets")
    print("   • Bulk CSV export capabilities")
    print()
    
    # Create main window
    root = tk.Tk()
    
    # Create the enhanced GUI
    app = AsyncIBDataManager(root)
    
    # Set up window close handler
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    print("✅ GUI initialized successfully!")
    print("💡 Switch to 'Enhanced Data Acquisition' tab for advanced features")
    print()
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()
