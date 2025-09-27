"""
Jupyter Notebook Generator for IB Data Manager
Creates analysis notebooks with pre-loaded data and basic analysis templates
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any


class JupyterNotebookGenerator:
    """Simple, proven Jupyter notebook generator for financial data analysis"""
    
    def __init__(self, output_dir: str = "notebooks"):
        """
        Initialize the notebook generator
        
        Args:
            output_dir: Directory to save generated notebooks
        """
        self.output_dir = output_dir
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def create_analysis_notebook(self, csv_path: str, symbol: str, 
                               data_type: str = "historical") -> str:
        """
        Create a Jupyter notebook for data analysis
        
        Args:
            csv_path: Path to the CSV file containing the data
            symbol: Trading symbol (e.g., 'AAPL', 'ES')
            data_type: Type of data ('historical', 'realtime', etc.)
            
        Returns:
            Path to the created notebook
        """
        # Generate notebook filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        notebook_name = f"{symbol}_{data_type}_analysis_{timestamp}.ipynb"
        notebook_path = os.path.join(self.output_dir, notebook_name)
        
        # Create notebook structure
        notebook = self._create_notebook_structure(csv_path, symbol, data_type)
        
        # Save notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2)
        
        return notebook_path
    
    def _create_notebook_structure(self, csv_path: str, symbol: str, 
                                 data_type: str) -> Dict[str, Any]:
        """Create the basic notebook structure with analysis cells"""
        
        # Convert to relative path for portability
        rel_csv_path = os.path.relpath(csv_path, self.output_dir)
        
        cells = [
            self._create_title_cell(symbol, data_type),
            self._create_imports_cell(),
            self._create_data_loading_cell(rel_csv_path, symbol),
            self._create_basic_info_cell(),
            self._create_visualization_cell(),
            self._create_statistics_cell(),
            self._create_analysis_template_cell()
        ]
        
        return {
            "cells": cells,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.8.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
    
    def _create_title_cell(self, symbol: str, data_type: str) -> Dict[str, Any]:
        """Create title markdown cell"""
        title = f"# {symbol} {data_type.title()} Data Analysis"
        subtitle = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                f"{title}\n\n",
                f"{subtitle}\n\n",
                "## Overview\n",
                f"This notebook contains analysis for {symbol} {data_type} data.\n",
                "The data has been automatically loaded and basic analysis templates are provided.\n"
            ]
        }
    
    def _create_imports_cell(self) -> Dict[str, Any]:
        """Create imports cell with common libraries"""
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Standard imports for financial data analysis\n",
                "import pandas as pd\n",
                "import numpy as np\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "from datetime import datetime, timedelta\n",
                "import warnings\n",
                "\n",
                "# Configure plotting\n",
                "plt.style.use('seaborn-v0_8')\n",
                "plt.rcParams['figure.figsize'] = (12, 8)\n",
                "warnings.filterwarnings('ignore')\n",
                "\n",
                "print('Libraries imported successfully!')"
            ]
        }
    
    def _create_data_loading_cell(self, csv_path: str, symbol: str) -> Dict[str, Any]:
        """Create data loading cell"""
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                f"# Load data from CSV\n",
                f"csv_path = '{csv_path}'\n",
                f"symbol = '{symbol}'\n\n",
                "# Read CSV with proper date parsing\n",
                "df = pd.read_csv(csv_path)\n",
                "\n",
                "# Convert date column to datetime\n",
                "if 'date' in df.columns:\n",
                "    df['date'] = pd.to_datetime(df['date'])\n",
                "    df.set_index('date', inplace=True)\n",
                "\n",
                "# Display basic info\n",
                "print(f'Loaded {len(df)} rows of data for {symbol}')\n",
                "print(f'Date range: {df.index.min()} to {df.index.max()}')\n",
                "df.head()"
            ]
        }
    
    def _create_basic_info_cell(self) -> Dict[str, Any]:
        """Create basic data information cell"""
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Basic data information\n",
                "print('=== Data Information ===')\n",
                "print(f'Shape: {df.shape}')\n",
                "print(f'Columns: {list(df.columns)}')\n",
                "print('\\n=== Data Types ===')\n",
                "print(df.dtypes)\n",
                "print('\\n=== Missing Values ===')\n",
                "print(df.isnull().sum())\n",
                "print('\\n=== Basic Statistics ===')\n",
                "df.describe()"
            ]
        }
    
    def _create_visualization_cell(self) -> Dict[str, Any]:
        """Create basic visualization cell"""
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Basic price visualization\n",
                "fig, axes = plt.subplots(2, 2, figsize=(15, 10))\n",
                "fig.suptitle(f'{symbol} Price Analysis', fontsize=16)\n",
                "\n",
                "# Price chart\n",
                "if 'close' in df.columns:\n",
                "    axes[0, 0].plot(df.index, df['close'], label='Close Price')\n",
                "    axes[0, 0].set_title('Close Price Over Time')\n",
                "    axes[0, 0].legend()\n",
                "    axes[0, 0].grid(True)\n",
                "\n",
                "# Volume chart\n",
                "if 'volume' in df.columns:\n",
                "    axes[0, 1].bar(df.index, df['volume'], alpha=0.7)\n",
                "    axes[0, 1].set_title('Volume Over Time')\n",
                "    axes[0, 1].grid(True)\n",
                "\n",
                "# Price distribution\n",
                "if 'close' in df.columns:\n",
                "    axes[1, 0].hist(df['close'], bins=50, alpha=0.7)\n",
                "    axes[1, 0].set_title('Price Distribution')\n",
                "    axes[1, 0].grid(True)\n",
                "\n",
                "# Returns distribution\n",
                "if 'close' in df.columns:\n",
                "    returns = df['close'].pct_change().dropna()\n",
                "    axes[1, 1].hist(returns, bins=50, alpha=0.7)\n",
                "    axes[1, 1].set_title('Returns Distribution')\n",
                "    axes[1, 1].grid(True)\n",
                "\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        }
    
    def _create_statistics_cell(self) -> Dict[str, Any]:
        """Create statistics analysis cell"""
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Calculate key statistics\n",
                "if 'close' in df.columns:\n",
                "    # Price statistics\n",
                "    current_price = df['close'].iloc[-1]\n",
                "    price_change = df['close'].iloc[-1] - df['close'].iloc[0]\n",
                "    price_change_pct = (price_change / df['close'].iloc[0]) * 100\n",
                "    \n",
                "    # Returns analysis\n",
                "    returns = df['close'].pct_change().dropna()\n",
                "    daily_volatility = returns.std()\n",
                "    annualized_volatility = daily_volatility * np.sqrt(252)  # Assuming daily data\n",
                "    \n",
                "    # Display statistics\n",
                "    print('=== Key Statistics ===')\n",
                "    print(f'Current Price: ${current_price:.2f}')\n",
                "    print(f'Price Change: ${price_change:.2f} ({price_change_pct:.2f}%)')\n",
                "    print(f'Daily Volatility: {daily_volatility:.4f} ({daily_volatility*100:.2f}%)')\n",
                "    print(f'Annualized Volatility: {annualized_volatility:.4f} ({annualized_volatility*100:.2f}%)')\n",
                "    print(f'Max Price: ${df[\"close\"].max():.2f}')\n",
                "    print(f'Min Price: ${df[\"close\"].min():.2f}')\n",
                "    \n",
                "    if 'volume' in df.columns:\n",
                "        print(f'Average Volume: {df[\"volume\"].mean():,.0f}')\n",
                "        print(f'Total Volume: {df[\"volume\"].sum():,.0f}')"
            ]
        }
    
    def _create_analysis_template_cell(self) -> Dict[str, Any]:
        """Create template cell for further analysis"""
        return {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Further Analysis Templates\n\n",
                "### Technical Indicators\n",
                "```python\n",
                "# Moving averages\n",
                "df['SMA_20'] = df['close'].rolling(window=20).mean()\n",
                "df['SMA_50'] = df['close'].rolling(window=50).mean()\n",
                "\n",
                "# RSI calculation\n",
                "def calculate_rsi(prices, window=14):\n",
                "    delta = prices.diff()\n",
                "    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()\n",
                "    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()\n",
                "    rs = gain / loss\n",
                "    return 100 - (100 / (1 + rs))\n",
                "\n",
                "df['RSI'] = calculate_rsi(df['close'])\n",
                "```\n\n",
                "### Statistical Analysis\n",
                "```python\n",
                "# Correlation analysis\n",
                "correlation_matrix = df[['open', 'high', 'low', 'close', 'volume']].corr()\n",
                "sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')\n",
                "```\n\n",
                "### Risk Metrics\n",
                "```python\n",
                "# Value at Risk (VaR)\n",
                "returns = df['close'].pct_change().dropna()\n",
                "var_95 = np.percentile(returns, 5)\n",
                "var_99 = np.percentile(returns, 1)\n",
                "print(f'VaR (95%): {var_95:.4f}')\n",
                "print(f'VaR (99%): {var_99:.4f}')\n",
                "```"
            ]
        }


def create_notebook_for_csv(csv_path: str, symbol: str, 
                          output_dir: str = "notebooks") -> str:
    """
    Convenience function to create a notebook for a CSV file
    
    Args:
        csv_path: Path to the CSV file
        symbol: Trading symbol
        output_dir: Directory to save the notebook
        
    Returns:
        Path to the created notebook
    """
    generator = JupyterNotebookGenerator(output_dir)
    return generator.create_analysis_notebook(csv_path, symbol)


if __name__ == "__main__":
    # Example usage
    generator = JupyterNotebookGenerator()
    notebook_path = generator.create_analysis_notebook(
        "sample_data.csv", 
        "AAPL", 
        "historical"
    )
    print(f"Created notebook: {notebook_path}")
