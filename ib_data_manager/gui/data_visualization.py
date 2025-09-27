"""
Advanced data visualization panel for IB Data Manager
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from .modern_theme import ModernTheme

# Configure matplotlib for better appearance
plt.style.use('seaborn-v0_8')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'

class DataVisualizationPanel:
    """Advanced data visualization panel with multiple chart types"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.current_data = None
        self.current_symbol = None
        
        # Create visualization frame
        self.viz_frame = ttk.LabelFrame(parent_frame, text="Data Visualization", padding=10)
        self.viz_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Configure grid weights
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(0, weight=1)
        self.viz_frame.columnconfigure(0, weight=1)
        self.viz_frame.rowconfigure(1, weight=1)
        
        # Chart type selection
        chart_frame = ttk.Frame(self.viz_frame)
        chart_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(chart_frame, text="Chart Type:", style='Heading.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        self.chart_type = ttk.Combobox(chart_frame, values=[
            "Candlestick", "Line Chart", "Volume", "Price & Volume", "Returns Distribution"
        ], state="readonly", width=20)
        self.chart_type.set("Candlestick")
        self.chart_type.pack(side=tk.LEFT, padx=(0, 10))
        self.chart_type.bind("<<ComboboxSelected>>", self.update_chart)
        
        # Refresh button
        ttk.Button(chart_frame, text="Refresh", command=self.update_chart).pack(side=tk.LEFT, padx=5)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(12, 6), dpi=100, facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.figure, self.viz_frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add toolbar
        toolbar_frame = ttk.Frame(self.viz_frame)
        toolbar_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Initial empty chart
        self.show_empty_chart()
        
    def show_empty_chart(self):
        """Show empty chart with instructions"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, 'Fetch historical data to display charts', 
                ha='center', va='center', transform=ax.transAxes,
                fontsize=14, color='gray')
        ax.set_xticks([])
        ax.set_yticks([])
        self.canvas.draw()
        
    def update_data(self, data, symbol):
        """Update chart data"""
        self.current_data = data
        self.current_symbol = symbol
        self.update_chart()
        
    def update_chart(self, event=None):
        """Update chart based on selected type"""
        if not self.current_data:
            self.show_empty_chart()
            return
            
        chart_type = self.chart_type.get()
        self.figure.clear()
        
        try:
            # Convert data to pandas DataFrame
            df = pd.DataFrame([{
                'date': bar.date,
                'open': float(bar.open),
                'high': float(bar.high), 
                'low': float(bar.low),
                'close': float(bar.close),
                'volume': int(bar.volume)
            } for bar in self.current_data])
            
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            if chart_type == "Candlestick":
                self._create_candlestick_chart(df)
            elif chart_type == "Line Chart":
                self._create_line_chart(df)
            elif chart_type == "Volume":
                self._create_volume_chart(df)
            elif chart_type == "Price & Volume":
                self._create_price_volume_chart(df)
            elif chart_type == "Returns Distribution":
                self._create_returns_distribution(df)
                
        except Exception as e:
            # Show error in chart
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, f'Error creating chart:\n{str(e)}', 
                    ha='center', va='center', transform=ax.transAxes,
                    fontsize=12, color='red')
            ax.set_xticks([])
            ax.set_yticks([])
            
        self.canvas.draw()
        
    def _create_candlestick_chart(self, df):
        """Create candlestick chart"""
        ax = self.figure.add_subplot(111)
        
        # Simple candlestick representation using bars
        up = df[df.close >= df.open]
        down = df[df.close < df.open]
        
        # Plot up days
        ax.bar(up.index, up.close - up.open, bottom=up.open, 
               color=ModernTheme.SUCCESS, alpha=0.8, width=0.8)
        ax.bar(up.index, up.high - up.close, bottom=up.close, 
               color=ModernTheme.SUCCESS, alpha=0.4, width=0.1)
        ax.bar(up.index, up.open - up.low, bottom=up.low, 
               color=ModernTheme.SUCCESS, alpha=0.4, width=0.1)
        
        # Plot down days  
        ax.bar(down.index, down.open - down.close, bottom=down.close,
               color=ModernTheme.DANGER, alpha=0.8, width=0.8)
        ax.bar(down.index, down.high - down.open, bottom=down.open,
               color=ModernTheme.DANGER, alpha=0.4, width=0.1)
        ax.bar(down.index, down.close - down.low, bottom=down.low,
               color=ModernTheme.DANGER, alpha=0.4, width=0.1)
        
        ax.set_title(f'{self.current_symbol} - Candlestick Chart', fontsize=14, fontweight='bold')
        ax.set_ylabel('Price', fontsize=12)
        ax.grid(True, alpha=0.3)
        
    def _create_line_chart(self, df):
        """Create line chart"""
        ax = self.figure.add_subplot(111)
        ax.plot(df.index, df.close, color=ModernTheme.PRIMARY, linewidth=2)
        ax.set_title(f'{self.current_symbol} - Price Chart', fontsize=14, fontweight='bold')
        ax.set_ylabel('Price', fontsize=12)
        ax.grid(True, alpha=0.3)
        
    def _create_volume_chart(self, df):
        """Create volume chart"""
        ax = self.figure.add_subplot(111)
        ax.bar(df.index, df.volume, color=ModernTheme.INFO, alpha=0.7)
        ax.set_title(f'{self.current_symbol} - Volume Chart', fontsize=14, fontweight='bold')
        ax.set_ylabel('Volume', fontsize=12)
        ax.grid(True, alpha=0.3)
        
    def _create_price_volume_chart(self, df):
        """Create combined price and volume chart"""
        # Create subplots
        ax1 = self.figure.add_subplot(211)
        ax2 = self.figure.add_subplot(212)
        
        # Price chart
        ax1.plot(df.index, df.close, color=ModernTheme.PRIMARY, linewidth=2)
        ax1.set_title(f'{self.current_symbol} - Price & Volume', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # Volume chart
        ax2.bar(df.index, df.volume, color=ModernTheme.INFO, alpha=0.7)
        ax2.set_ylabel('Volume', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        self.figure.tight_layout()
        
    def _create_returns_distribution(self, df):
        """Create returns distribution histogram"""
        ax = self.figure.add_subplot(111)
        
        # Calculate returns
        returns = df.close.pct_change().dropna()
        
        # Create histogram
        ax.hist(returns, bins=50, color=ModernTheme.SECONDARY, alpha=0.7, edgecolor='black')
        ax.axvline(returns.mean(), color=ModernTheme.DANGER, linestyle='--', 
                  label=f'Mean: {returns.mean():.4f}')
        ax.axvline(returns.median(), color=ModernTheme.SUCCESS, linestyle='--',
                  label=f'Median: {returns.median():.4f}')
        
        ax.set_title(f'{self.current_symbol} - Returns Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('Daily Returns', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
