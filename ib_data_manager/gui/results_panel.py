"""
Results Panel Component
Integrated data display with charts and export options
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import csv
import os
import subprocess
import sys
from typing import List, Dict, Any, Optional

from ib_data_manager.utils.jupyter_generator import create_notebook_for_csv

class ResultsPanel:
    """
    Unified results display that shows data immediately after fetching.
    No more hunting for your data - it's right here with charts and export options.
    """
    
    def __init__(self, parent, dashboard):
        self.parent = parent
        self.dashboard = dashboard
        self.current_symbol = None
        self.current_data = None
        
        self.create_panel()
        
    def create_panel(self):
        """Create the results panel UI"""
        # Main results frame
        self.results_frame = ttk.Frame(self.parent)
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(self.results_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Data view tab
        self.create_data_view()
        
        # Live data tab
        self.create_live_data_view()
        
        # Summary view tab
        self.create_summary_view()
        
        # Export tab
        self.create_export_view()
        
    def create_data_view(self):
        """Create the data table view"""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="📊 Data Table")
        
        # Create paned window for symbol list and data view
        paned_window = ttk.PanedWindow(data_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel: Symbol list
        symbols_frame = ttk.LabelFrame(paned_window, text="📋 Loaded Symbols", padding="5")
        paned_window.add(symbols_frame, weight=1)
        
        # Symbol listbox
        self.symbols_listbox = tk.Listbox(symbols_frame, height=15, font=("Arial", 10))
        self.symbols_listbox.pack(fill=tk.BOTH, expand=True)
        self.symbols_listbox.bind("<<ListboxSelect>>", self.on_symbol_select)
        
        # Right panel: Data display
        data_display_frame = ttk.Frame(paned_window)
        paned_window.add(data_display_frame, weight=3)
        
        # Header with symbol info
        header_frame = ttk.Frame(data_display_frame)
        header_frame.pack(fill=tk.X, pady=5)
        
        self.symbol_label = ttk.Label(
            header_frame, 
            text="Select a symbol to view data", 
            font=("Arial", 14, "bold")
        )
        self.symbol_label.pack(side=tk.LEFT)
        
        self.data_info_label = ttk.Label(
            header_frame, 
            text="", 
            font=("Arial", 10),
            foreground="gray"
        )
        self.data_info_label.pack(side=tk.RIGHT)
        
        # Data table
        table_frame = ttk.Frame(data_display_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview for data display
        columns = ("date", "open", "high", "low", "close", "volume")
        self.data_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        column_widths = {"date": 150, "open": 80, "high": 80, "low": 80, "close": 80, "volume": 100}
        for col in columns:
            self.data_tree.heading(col, text=col.title())
            self.data_tree.column(col, width=column_widths[col], anchor="center")
            
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.data_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_live_data_view(self):
        """Create the live data streaming view"""
        live_frame = ttk.Frame(self.notebook)
        self.notebook.add(live_frame, text="📡 Live Data")
        
        # Header with streaming status
        header_frame = ttk.Frame(live_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.live_symbol_label = ttk.Label(
            header_frame, 
            text="No live data streaming", 
            font=("Arial", 14, "bold")
        )
        self.live_symbol_label.pack(side=tk.LEFT)
        
        self.stream_status_label = ttk.Label(
            header_frame, 
            text="● Disconnected", 
            font=("Arial", 10),
            foreground="red"
        )
        self.stream_status_label.pack(side=tk.RIGHT)
        
        # Create notebook for different live data types
        self.live_notebook = ttk.Notebook(live_frame)
        self.live_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Live quotes tab
        self.create_live_quotes_tab()
        
        # Market depth tab
        self.create_market_depth_tab()
        
        # Live chart placeholder (for future implementation)
        self.create_live_chart_tab()
        
    def create_live_quotes_tab(self):
        """Create live quotes display"""
        quotes_frame = ttk.Frame(self.live_notebook)
        self.live_notebook.add(quotes_frame, text="💹 Live Quotes")
        
        # Current quote display
        quote_display_frame = ttk.LabelFrame(quotes_frame, text="Current Quote", padding="15")
        quote_display_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Price display grid
        price_grid = ttk.Frame(quote_display_frame)
        price_grid.pack(fill=tk.X)
        
        # Bid/Ask display
        bid_ask_frame = ttk.Frame(price_grid)
        bid_ask_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(bid_ask_frame, text="Bid:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.bid_label = ttk.Label(bid_ask_frame, text="--", font=("Arial", 16), foreground="red")
        self.bid_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(bid_ask_frame, text="Ask:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.ask_label = ttk.Label(bid_ask_frame, text="--", font=("Arial", 16), foreground="blue")
        self.ask_label.grid(row=1, column=1, sticky=tk.W)
        
        # Last trade display
        last_frame = ttk.Frame(price_grid)
        last_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        ttk.Label(last_frame, text="Last:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.last_label = ttk.Label(last_frame, text="--", font=("Arial", 20, "bold"), foreground="green")
        self.last_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(last_frame, text="Volume:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.volume_label = ttk.Label(last_frame, text="--", font=("Arial", 14))
        self.volume_label.grid(row=1, column=1, sticky=tk.W)
        
        # Additional quote data
        details_frame = ttk.LabelFrame(quotes_frame, text="Quote Details", padding="15")
        details_frame.pack(fill=tk.X, padx=10, pady=10)
        
        details_grid = ttk.Frame(details_frame)
        details_grid.pack(fill=tk.X)
        
        # Left column
        left_col = ttk.Frame(details_grid)
        left_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(left_col, text="Open:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.open_label = ttk.Label(left_col, text="--", font=("Arial", 10))
        self.open_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(left_col, text="High:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.high_label = ttk.Label(left_col, text="--", font=("Arial", 10))
        self.high_label.grid(row=1, column=1, sticky=tk.W)
        
        # Right column
        right_col = ttk.Frame(details_grid)
        right_col.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        ttk.Label(right_col, text="Low:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.low_label = ttk.Label(right_col, text="--", font=("Arial", 10))
        self.low_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(right_col, text="Close:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.close_label = ttk.Label(right_col, text="--", font=("Arial", 10))
        self.close_label.grid(row=1, column=1, sticky=tk.W)
        
    def create_market_depth_tab(self):
        """Create market depth (Level II) display"""
        depth_frame = ttk.Frame(self.live_notebook)
        self.live_notebook.add(depth_frame, text="📊 Level II")
        
        # Market depth table
        depth_table_frame = ttk.LabelFrame(depth_frame, text="Market Depth", padding="10")
        depth_table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for market depth
        depth_columns = ("bid_size", "bid_price", "ask_price", "ask_size")
        self.depth_tree = ttk.Treeview(depth_table_frame, columns=depth_columns, show="headings", height=15)
        
        # Configure columns
        self.depth_tree.heading("bid_size", text="Bid Size")
        self.depth_tree.heading("bid_price", text="Bid Price")
        self.depth_tree.heading("ask_price", text="Ask Price")
        self.depth_tree.heading("ask_size", text="Ask Size")
        
        self.depth_tree.column("bid_size", width=100, anchor="center")
        self.depth_tree.column("bid_price", width=100, anchor="center")
        self.depth_tree.column("ask_price", width=100, anchor="center")
        self.depth_tree.column("ask_size", width=100, anchor="center")
        
        # Scrollbars for depth table
        depth_v_scrollbar = ttk.Scrollbar(depth_table_frame, orient="vertical", command=self.depth_tree.yview)
        self.depth_tree.configure(yscrollcommand=depth_v_scrollbar.set)
        
        # Pack depth table
        self.depth_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        depth_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_live_chart_tab(self):
        """Create live chart placeholder"""
        chart_frame = ttk.Frame(self.live_notebook)
        self.live_notebook.add(chart_frame, text="📈 Live Chart")
        
        # Placeholder for live chart
        chart_placeholder = ttk.Label(
            chart_frame, 
            text="📈 Live Chart\n\nComing Soon:\n• Real-time price chart\n• Volume indicators\n• Technical overlays", 
            font=("Arial", 14),
            justify=tk.CENTER
        )
        chart_placeholder.pack(expand=True)
        
    def create_summary_view(self):
        """Create the summary statistics view"""
        summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(summary_frame, text="📈 Summary")
        
        # Summary content
        summary_content = ttk.Frame(summary_frame, padding="20")
        summary_content.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(summary_content, text="Data Summary", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Statistics grid
        stats_frame = ttk.Frame(summary_content)
        stats_frame.pack(fill=tk.X)
        
        # Left column - Basic stats
        left_stats = ttk.LabelFrame(stats_frame, text="Basic Statistics", padding="10")
        left_stats.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.basic_stats_text = tk.Text(left_stats, height=10, width=30, font=("Courier", 10))
        self.basic_stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Right column - Price stats
        right_stats = ttk.LabelFrame(stats_frame, text="Price Analysis", padding="10")
        right_stats.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.price_stats_text = tk.Text(right_stats, height=10, width=30, font=("Courier", 10))
        self.price_stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Chart placeholder (for future enhancement)
        chart_frame = ttk.LabelFrame(summary_content, text="Price Chart", padding="10")
        chart_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.chart_placeholder = ttk.Label(
            chart_frame, 
            text="📊 Chart visualization will be added in future update",
            font=("Arial", 12),
            foreground="gray"
        )
        self.chart_placeholder.pack(pady=20)
        
    def create_export_view(self):
        """Create the export options view"""
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="💾 Export")
        
        export_content = ttk.Frame(export_frame, padding="20")
        export_content.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(export_content, text="Export Options", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Quick export section
        quick_frame = ttk.LabelFrame(export_content, text="Quick Export", padding="15")
        quick_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Export buttons row
        buttons_frame = ttk.Frame(quick_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="📄 Export CSV", 
                  command=self.export_csv, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="📊 Create Analysis Notebook", 
                  command=self.export_with_analysis, width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="🚀 Quick Analysis", 
                  command=self.quick_analysis, width=15).pack(side=tk.LEFT)
        
        # Export settings
        settings_frame = ttk.LabelFrame(export_content, text="Export Settings", padding="15")
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Export directory
        dir_frame = ttk.Frame(settings_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dir_frame, text="Export Directory:").pack(side=tk.LEFT)
        self.export_dir_var = tk.StringVar(value=self.dashboard.settings.get("export_dir", ""))
        self.export_dir_entry = ttk.Entry(dir_frame, textvariable=self.export_dir_var, width=40)
        self.export_dir_entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="Browse", command=self.browse_export_dir).pack(side=tk.RIGHT)
        
        # Export format options
        format_frame = ttk.Frame(settings_frame)
        format_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(format_frame, text="Include:").pack(side=tk.LEFT)
        
        self.include_headers = tk.BooleanVar(value=True)
        ttk.Checkbutton(format_frame, text="Headers", variable=self.include_headers).pack(side=tk.LEFT, padx=10)
        
        self.include_metadata = tk.BooleanVar(value=True)
        ttk.Checkbutton(format_frame, text="Metadata", variable=self.include_metadata).pack(side=tk.LEFT, padx=10)
        
        # Export status
        self.export_status_label = ttk.Label(export_content, text="Ready to export", foreground="gray")
        self.export_status_label.pack(pady=10)
        
    def update_data(self, symbol, data, description=""):
        """Update the display with new data"""
        self.current_symbol = symbol
        self.current_data = data
        
        # Update header
        self.symbol_label.config(text=f"{symbol} - {description}")
        self.data_info_label.config(text=f"{len(data)} bars • Last updated: {datetime.now().strftime('%H:%M:%S')}")
        
        # Clear and populate data table
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
            
        for bar in data:
            self.data_tree.insert("", tk.END, values=(
                bar.date,
                f"{bar.open:.2f}",
                f"{bar.high:.2f}",
                f"{bar.low:.2f}",
                f"{bar.close:.2f}",
                f"{bar.volume:,}"
            ))
            
        # Update summary statistics
        self.update_summary_stats(data)
        
        # Update symbol list and switch to data view
        self.refresh_symbol_list()
        self.notebook.select(0)
        
    def update_summary_stats(self, data):
        """Update summary statistics"""
        if not data:
            return
            
        # Calculate basic statistics
        closes = [float(bar.close) for bar in data]
        volumes = [int(bar.volume) for bar in data]
        highs = [float(bar.high) for bar in data]
        lows = [float(bar.low) for bar in data]
        
        # Basic stats
        basic_stats = f"""Data Points: {len(data):,}
Date Range: {data[0].date} to {data[-1].date}

Price Statistics:
Current Price: ${closes[-1]:.2f}
Highest: ${max(highs):.2f}
Lowest: ${min(lows):.2f}
Average: ${sum(closes)/len(closes):.2f}

Volume Statistics:
Total Volume: {sum(volumes):,}
Average Volume: {sum(volumes)//len(volumes):,}
Max Volume: {max(volumes):,}"""
        
        # Price analysis
        price_change = closes[-1] - closes[0]
        price_change_pct = (price_change / closes[0]) * 100
        
        price_analysis = f"""Price Movement:
Start Price: ${closes[0]:.2f}
End Price: ${closes[-1]:.2f}
Change: ${price_change:+.2f}
Change %: {price_change_pct:+.2f}%

Volatility:
Price Range: ${max(highs) - min(lows):.2f}
Avg Daily Range: ${sum(h-l for h,l in zip(highs,lows))/len(data):.2f}

Recent Trend:
Last 5 bars avg: ${sum(closes[-5:])/5:.2f}
vs Overall avg: {((sum(closes[-5:])/5) / (sum(closes)/len(closes)) - 1) * 100:+.1f}%"""
        
        # Update text widgets
        self.basic_stats_text.delete(1.0, tk.END)
        self.basic_stats_text.insert(1.0, basic_stats)
        
        self.price_stats_text.delete(1.0, tk.END)
        self.price_stats_text.insert(1.0, price_analysis)
        
    def export_csv(self):
        """Export data to CSV file"""
        if not self.current_data:
            messagebox.showinfo("No Data", "No data to export")
            return
            
        # Get export directory
        export_dir = self.export_dir_var.get() or filedialog.askdirectory(title="Select Export Directory")
        if not export_dir:
            return
            
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.current_symbol}_data_{timestamp}.csv"
        filepath = os.path.join(export_dir, filename)
        
        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write headers if requested
                if self.include_headers.get():
                    writer.writerow(["date", "open", "high", "low", "close", "volume"])
                    
                # Write data
                for bar in self.current_data:
                    writer.writerow([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])
                    
            self.export_status_label.config(text=f"✅ Exported to: {filename}", foreground="green")
            
            # Update settings
            self.dashboard.settings["export_dir"] = export_dir
            self.dashboard.save_settings()
            
        except Exception as e:
            self.export_status_label.config(text=f"❌ Export failed: {str(e)}", foreground="red")
            
    def export_with_analysis(self):
        """Export data with comprehensive analysis notebook"""
        if not self.current_data:
            messagebox.showinfo("No Data", "No data to export")
            return
            
        # Get export directory
        export_dir = self.export_dir_var.get() or filedialog.askdirectory(title="Select Export Directory")
        if not export_dir:
            return
            
        try:
            # Create organized folder structure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            analysis_folder = os.path.join(export_dir, f"{self.current_symbol}_analysis_{timestamp}")
            os.makedirs(analysis_folder, exist_ok=True)
            
            # Create data subfolder
            data_folder = os.path.join(analysis_folder, "data")
            os.makedirs(data_folder, exist_ok=True)
            
            # Export CSV first
            csv_filename = f"{self.current_symbol}_data.csv"
            csv_path = os.path.join(data_folder, csv_filename)
            
            with open(csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                if self.include_headers.get():
                    writer.writerow(["date", "open", "high", "low", "close", "volume"])
                for bar in self.current_data:
                    writer.writerow([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])
            
            # Create notebooks subfolder
            notebooks_folder = os.path.join(analysis_folder, "notebooks")
            
            # Generate comprehensive analysis notebook
            notebook_path = create_notebook_for_csv(csv_path, self.current_symbol, notebooks_folder)
            
            self.export_status_label.config(
                text=f"✅ Analysis created: {os.path.basename(analysis_folder)}", 
                foreground="green"
            )
            
            # Update settings
            self.dashboard.settings["export_dir"] = export_dir
            self.dashboard.save_settings()
            
            # Ask if user wants to open the notebook
            open_notebook = messagebox.askyesno(
                "Analysis Ready!",
                f"📊 Complete analysis package created!\n\n"
                f"📁 Folder: {os.path.basename(analysis_folder)}\n"
                f"📄 Data: {csv_filename}\n"
                f"📓 Notebook: {os.path.basename(notebook_path)}\n\n"
                f"The notebook includes:\n"
                f"• Pre-loaded data with automatic cleaning\n"
                f"• Price charts and volume analysis\n"
                f"• Statistical analysis and risk metrics\n"
                f"• Technical indicator templates\n"
                f"• Ready-to-run analysis code\n\n"
                f"Would you like to open the notebook now?",
                parent=self.dashboard.root
            )
            
            if open_notebook:
                self._open_notebook(notebook_path)
                
        except Exception as e:
            self.export_status_label.config(
                text=f"❌ Analysis creation failed: {str(e)}", 
                foreground="red"
            )
        
    def quick_export(self):
        """Quick export to default location"""
        if not self.current_data:
            messagebox.showinfo("No Data", "No data to export")
            return
            
        # Use default export directory
        export_dir = self.dashboard.settings.get("export_dir", os.path.expanduser("~/Documents"))
        self.export_dir_var.set(export_dir)
        self.export_csv()
        
    def quick_analysis(self):
        """One-click analysis - export CSV and create notebook in default location"""
        if not self.current_data:
            messagebox.showinfo("No Data", "No data to export")
            return
            
        # Use default export directory or ask user
        export_dir = self.dashboard.settings.get("export_dir")
        if not export_dir:
            export_dir = filedialog.askdirectory(title="Select Analysis Directory")
            if not export_dir:
                return
            self.dashboard.settings["export_dir"] = export_dir
            self.dashboard.save_settings()
            
        self.export_dir_var.set(export_dir)
        
        # Show progress
        self.export_status_label.config(text="🚀 Creating quick analysis...", foreground="blue")
        self.dashboard.root.update()
        
        # Create analysis
        self.export_with_analysis()
        
    def _open_notebook(self, notebook_path):
        """Open Jupyter notebook in default application or Jupyter"""
        try:
            # Try to open with Jupyter first
            if self._try_jupyter_lab(notebook_path):
                return
            elif self._try_jupyter_notebook(notebook_path):
                return
            else:
                # Fall back to system default
                self._open_with_system_default(notebook_path)
                
        except Exception as e:
            messagebox.showerror(
                "Cannot Open Notebook",
                f"Could not open the notebook automatically.\n\n"
                f"Path: {notebook_path}\n\n"
                f"Error: {str(e)}\n\n"
                f"You can open it manually with Jupyter Lab/Notebook.",
                parent=self.dashboard.root
            )
            
    def _try_jupyter_lab(self, notebook_path):
        """Try to open with Jupyter Lab"""
        try:
            subprocess.Popen(['jupyter', 'lab', notebook_path], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            self.export_status_label.config(
                text="✅ Opening in Jupyter Lab...", 
                foreground="green"
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
            
    def _try_jupyter_notebook(self, notebook_path):
        """Try to open with Jupyter Notebook"""
        try:
            subprocess.Popen(['jupyter', 'notebook', notebook_path], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            self.export_status_label.config(
                text="✅ Opening in Jupyter Notebook...", 
                foreground="green"
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
            
    def _open_with_system_default(self, notebook_path):
        """Open with system default application"""
        if sys.platform.startswith('win'):
            os.startfile(notebook_path)
        elif sys.platform.startswith('darwin'):
            subprocess.run(['open', notebook_path])
        else:
            subprocess.run(['xdg-open', notebook_path])
            
        self.export_status_label.config(
            text="✅ Opening with system default...", 
            foreground="green"
        )
        
    def browse_export_dir(self):
        """Browse for export directory"""
        directory = filedialog.askdirectory(
            title="Select Export Directory",
            initialdir=self.export_dir_var.get()
        )
        if directory:
            self.export_dir_var.set(directory)
            
    def clear_data(self):
        """Clear current data display"""
        self.current_symbol = None
        self.current_data = None
        
        # Clear table
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
            
        # Reset labels
        self.symbol_label.config(text="No data loaded")
        self.data_info_label.config(text="")
        
        # Clear summary
        self.basic_stats_text.delete(1.0, tk.END)
        self.price_stats_text.delete(1.0, tk.END)
        
    # ==================== LIVE DATA UPDATE METHODS ====================
    
    def update_live_quote(self, ticker):
        """Update live quote display with new ticker data"""
        try:
            # Update symbol and status
            symbol = ticker.contract.symbol if hasattr(ticker, 'contract') else "Unknown"
            self.live_symbol_label.config(text=f"Live Data: {symbol}")
            self.stream_status_label.config(text="● Streaming", foreground="green")
            
            # Update bid/ask
            if hasattr(ticker, 'bid') and ticker.bid and ticker.bid > 0:
                self.bid_label.config(text=f"{ticker.bid:.2f}")
            if hasattr(ticker, 'ask') and ticker.ask and ticker.ask > 0:
                self.ask_label.config(text=f"{ticker.ask:.2f}")
                
            # Update last trade
            if hasattr(ticker, 'last') and ticker.last and ticker.last > 0:
                self.last_label.config(text=f"{ticker.last:.2f}")
            if hasattr(ticker, 'lastSize') and ticker.lastSize:
                self.volume_label.config(text=f"{ticker.lastSize:,}")
                
            # Update OHLC if available
            if hasattr(ticker, 'open') and ticker.open and ticker.open > 0:
                self.open_label.config(text=f"{ticker.open:.2f}")
            if hasattr(ticker, 'high') and ticker.high and ticker.high > 0:
                self.high_label.config(text=f"{ticker.high:.2f}")
            if hasattr(ticker, 'low') and ticker.low and ticker.low > 0:
                self.low_label.config(text=f"{ticker.low:.2f}")
            if hasattr(ticker, 'close') and ticker.close and ticker.close > 0:
                self.close_label.config(text=f"{ticker.close:.2f}")
                
        except Exception as e:
            print(f"Error updating live quote: {e}")
            
    def update_market_depth(self, ticker):
        """Update market depth display with new depth data"""
        try:
            print(f"🔍 DEBUG: Market depth callback triggered")
            print(f"🔍 DEBUG: Ticker type: {type(ticker)}")
            print(f"🔍 DEBUG: Ticker attributes: {dir(ticker)}")
            
            # Update symbol and status
            symbol = ticker.contract.symbol if hasattr(ticker, 'contract') else "Unknown"
            self.live_symbol_label.config(text=f"Level II: {symbol}")
            self.stream_status_label.config(text="● Streaming", foreground="green")
            
            # Debug: Check what depth attributes are available
            depth_attrs = [attr for attr in dir(ticker) if 'dom' in attr.lower() or 'depth' in attr.lower() or 'bid' in attr.lower() or 'ask' in attr.lower()]
            print(f"🔍 DEBUG: Depth-related attributes: {depth_attrs}")
            
            # Clear existing depth data
            for item in self.depth_tree.get_children():
                self.depth_tree.delete(item)
                
            # Try different ways to access market depth data
            bids = []
            asks = []
            
            # Method 1: domBids/domAsks (most common)
            if hasattr(ticker, 'domBids') and hasattr(ticker, 'domAsks'):
                bids = ticker.domBids if ticker.domBids else []
                asks = ticker.domAsks if ticker.domAsks else []
                print(f"🔍 DEBUG: Found domBids/domAsks - Bids: {len(bids)}, Asks: {len(asks)}")
                
            # Method 2: Check for other depth attributes
            elif hasattr(ticker, 'marketDepth'):
                print(f"🔍 DEBUG: Found marketDepth attribute")
                depth_data = ticker.marketDepth
                print(f"🔍 DEBUG: Market depth data: {depth_data}")
                
            # Method 3: Check for bid/ask arrays
            elif hasattr(ticker, 'bids') and hasattr(ticker, 'asks'):
                bids = ticker.bids if ticker.bids else []
                asks = ticker.asks if ticker.asks else []
                print(f"🔍 DEBUG: Found bids/asks arrays - Bids: {len(bids)}, Asks: {len(asks)}")
                
            else:
                print(f"🔍 DEBUG: No recognized depth data structure found")
                # Show a placeholder message
                self.depth_tree.insert("", tk.END, values=("--", "No depth data", "No depth data", "--"))
                return
                
            # Display the depth data
            if bids or asks:
                max_levels = min(10, max(len(bids), len(asks)))
                print(f"🔍 DEBUG: Displaying {max_levels} levels")
                
                for i in range(max_levels):
                    try:
                        # Handle bid side
                        if i < len(bids):
                            bid_item = bids[i]
                            print(f"🔍 DEBUG: Bid {i}: {bid_item} (type: {type(bid_item)})")
                            
                            # Try different ways to access bid data
                            if hasattr(bid_item, 'size') and hasattr(bid_item, 'price'):
                                bid_size = bid_item.size
                                bid_price = f"{bid_item.price:.2f}"
                            elif isinstance(bid_item, (list, tuple)) and len(bid_item) >= 2:
                                bid_price = f"{bid_item[0]:.2f}"
                                bid_size = bid_item[1]
                            else:
                                bid_size = str(bid_item)
                                bid_price = "--"
                        else:
                            bid_size = ""
                            bid_price = ""
                            
                        # Handle ask side
                        if i < len(asks):
                            ask_item = asks[i]
                            print(f"🔍 DEBUG: Ask {i}: {ask_item} (type: {type(ask_item)})")
                            
                            # Try different ways to access ask data
                            if hasattr(ask_item, 'size') and hasattr(ask_item, 'price'):
                                ask_size = ask_item.size
                                ask_price = f"{ask_item.price:.2f}"
                            elif isinstance(ask_item, (list, tuple)) and len(ask_item) >= 2:
                                ask_price = f"{ask_item[0]:.2f}"
                                ask_size = ask_item[1]
                            else:
                                ask_size = str(ask_item)
                                ask_price = "--"
                        else:
                            ask_size = ""
                            ask_price = ""
                            
                        # Insert the row
                        self.depth_tree.insert("", tk.END, values=(bid_size, bid_price, ask_price, ask_size))
                        
                    except Exception as row_error:
                        print(f"🔍 DEBUG: Error processing row {i}: {row_error}")
                        self.depth_tree.insert("", tk.END, values=("Error", "Error", "Error", "Error"))
            else:
                print(f"🔍 DEBUG: No bid/ask data to display")
                self.depth_tree.insert("", tk.END, values=("--", "No data", "No data", "--"))
                    
        except Exception as e:
            print(f"❌ Error updating market depth: {e}")
            import traceback
            traceback.print_exc()
            
    def switch_to_live_tab(self):
        """Switch to the live data tab"""
        try:
            # Find the live data tab index (it's the second tab, index 1)
            self.notebook.select(1)  # Live data tab
        except Exception as e:
            print(f"Error switching to live tab: {e}")
            
    def clear_live_data(self):
        """Clear live data displays"""
        try:
            # Reset status
            self.live_symbol_label.config(text="No live data streaming")
            self.stream_status_label.config(text="● Disconnected", foreground="red")
            
            # Clear quote data
            self.bid_label.config(text="--")
            self.ask_label.config(text="--")
            self.last_label.config(text="--")
            self.volume_label.config(text="--")
            self.open_label.config(text="--")
            self.high_label.config(text="--")
            self.low_label.config(text="--")
            self.close_label.config(text="--")
            
            # Clear depth data
            for item in self.depth_tree.get_children():
                self.depth_tree.delete(item)
                
        except Exception as e:
            print(f"Error clearing live data: {e}")
    
    def refresh_symbol_list(self):
        """Refresh the symbol list with all loaded data"""
        self.symbols_listbox.delete(0, tk.END)
        
        if hasattr(self.dashboard, 'current_data') and self.dashboard.current_data:
            for symbol in sorted(self.dashboard.current_data.keys()):
                data_info = self.dashboard.current_data[symbol]
                bar_count = len(data_info['data']) if 'data' in data_info else 0
                display_text = f"{symbol} ({bar_count} bars)"
                self.symbols_listbox.insert(tk.END, display_text)
    
    def on_symbol_select(self, event):
        """Handle symbol selection from the list"""
        selection = self.symbols_listbox.curselection()
        if not selection:
            return
            
        # Get selected symbol name (remove the bar count part)
        selected_text = self.symbols_listbox.get(selection[0])
        symbol = selected_text.split(' (')[0]
        
        # Load data for selected symbol
        if hasattr(self.dashboard, 'current_data') and symbol in self.dashboard.current_data:
            data_info = self.dashboard.current_data[symbol]
            self.update_data(symbol, data_info['data'], data_info.get('description', ''))
    
    def refresh_data_list(self):
        """Refresh the data list - called by batch operations"""
        self.refresh_symbol_list()
