"""
Jupyter Notebook Generator for IB Data Manager
Creates analysis notebooks with pre-loaded data and customizable analysis features
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from ib_data_manager.analysis import FEATURE_LIBRARY


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
                               data_type: str = "historical", 
                               selected_features: Optional[List[str]] = None) -> str:
        """
        Create a Jupyter notebook for data analysis
        
        Args:
            csv_path: Path to the CSV file containing the data
            symbol: Trading symbol (e.g., 'AAPL', 'ES')
            data_type: Type of data ('historical', 'realtime', etc.)
            selected_features: List of selected analysis features
            
        Returns:
            Path to the created notebook
        """
        # Generate notebook filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        notebook_name = f"{symbol}_{data_type}_analysis_{timestamp}.ipynb"
        notebook_path = os.path.join(self.output_dir, notebook_name)
        
        # Create notebook structure
        notebook = self._create_notebook_structure(csv_path, symbol, data_type, selected_features)
        
        # Save notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2)
        
        return notebook_path
    
    def _create_notebook_structure(self, csv_path: str, symbol: str, 
                                 data_type: str, selected_features: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create the notebook structure with selected analysis features"""
        
        # Convert to relative path for portability
        rel_csv_path = os.path.relpath(csv_path, self.output_dir)
        
        cells = [
            self._create_title_cell(symbol, data_type, selected_features),
            self._create_imports_cell(selected_features),
            self._create_data_loading_cell(rel_csv_path, symbol),
            self._create_basic_info_cell(),
            self._create_visualization_cell()
        ]
        
        # Add selected feature analysis cells
        if selected_features:
            cells.extend(self._create_feature_cells(selected_features))
        else:
            # Add default basic analysis
            cells.extend([
                self._create_statistics_cell(),
                self._create_analysis_template_cell()
            ])
        
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
    
    def _create_title_cell(self, symbol: str, data_type: str, selected_features: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create title markdown cell"""
        title = f"# {symbol} {data_type.title()} Data Analysis"
        subtitle = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Add feature summary
        feature_summary = ""
        if selected_features:
            feature_summary = f"\n\n## Selected Analysis Features\n"
            for i, feature_name in enumerate(selected_features, 1):
                feature = FEATURE_LIBRARY.get_feature(feature_name)
                if feature:
                    feature_summary += f"{i}. **{feature.name}** - {feature.description}\n"
        
        return {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                f"{title}\n\n",
                f"{subtitle}\n\n",
                "## Overview\n",
                f"This notebook contains customized analysis for {symbol} {data_type} data.\n",
                "The data has been automatically loaded and selected analysis features are ready to run.\n",
                feature_summary
            ]
        }
    
    def _create_imports_cell(self, selected_features: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create imports cell with smart dependency handling"""
        
        # Base imports that should be available in most environments
        imports = [
            "# Financial time series analysis imports",
            "import pandas as pd",
            "import numpy as np",
            "import matplotlib.pyplot as plt",
            "import matplotlib.dates as mdates",
            "from datetime import datetime, timedelta",
            "import warnings",
            "",
            "# Optional imports with fallbacks",
            "try:",
            "    import seaborn as sns",
            "    sns.set_style('whitegrid')",
            "except ImportError:",
            "    print('📝 Seaborn not available - using matplotlib styling')",
            "",
            "try:",
            "    from scipy import stats",
            "except ImportError:",
            "    print('📝 Scipy not available - some statistical features limited')",
            "",
            "try:",
            "    from sklearn.ensemble import RandomForestRegressor",
            "    from sklearn.model_selection import train_test_split",
            "    from sklearn.metrics import mean_squared_error, r2_score",
            "    from sklearn.preprocessing import StandardScaler",
            "except ImportError:",
            "    print('📝 Scikit-learn not available - ML features will be skipped')"
        ]
        
        # Add feature-specific imports with error handling
        if selected_features:
            additional_imports = []
            for feature_name in selected_features:
                feature = FEATURE_LIBRARY.get_feature(feature_name)
                if feature:
                    for dep in feature.dependencies:
                        if dep == "arch":
                            additional_imports.extend([
                                "try:",
                                "    from arch import arch_model",
                                "except ImportError:",
                                "    print('📝 ARCH not available - install with: pip install arch')"
                            ])
                        elif dep == "plotly":
                            additional_imports.extend([
                                "try:",
                                "    import plotly.graph_objects as go",
                                "    import plotly.express as px",
                                "except ImportError:",
                                "    print('📝 Plotly not available - install with: pip install plotly')"
                            ])
                        elif dep == "statsmodels":
                            additional_imports.extend([
                                "try:",
                                "    import statsmodels.api as sm",
                                "    from statsmodels.tsa.arima.model import ARIMA",
                                "except ImportError:",
                                "    print('📝 Statsmodels not available - install with: pip install statsmodels')"
                            ])
            
            if additional_imports:
                imports.append("")
                imports.append("# Feature-specific imports")
                imports.extend(additional_imports)
        
        imports.extend([
            "",
            "# Configure plotting for financial analysis",
            "plt.rcParams['figure.figsize'] = (15, 10)",
            "plt.rcParams['font.size'] = 10",
            "plt.rcParams['axes.grid'] = True",
            "plt.rcParams['grid.alpha'] = 0.3",
            "plt.rcParams['lines.linewidth'] = 1.5",
            "warnings.filterwarnings('ignore')",
            "",
            "print('✅ Core libraries loaded successfully!')",
            "print('📊 Ready for financial analysis')"
        ])
        
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": "\n".join(imports)
        }
    
    def _create_data_loading_cell(self, csv_path: str, symbol: str) -> Dict[str, Any]:
        """Create proper time series data loading and cleaning cell"""
        
        code_lines = [
            f"# Load and clean financial time series data",
            f"csv_path = '{csv_path}'",
            f"symbol = '{symbol}'",
            "",
            "print(f'📊 Loading data for {symbol}...')",
            "",
            "# Read CSV with proper parsing",
            "try:",
            "    df_raw = pd.read_csv(csv_path)",
            "    print(f'✅ Raw data loaded: {len(df_raw)} rows')",
            "except Exception as e:",
            "    print(f'❌ Error loading CSV: {e}')",
            "    raise",
            "",
            "# Clean and prepare time series data",
            "def clean_financial_data(df):",
            '    """Clean and prepare financial time series data"""',
            "    df_clean = df.copy()",
            "    ",
            "    # Handle date column (multiple possible formats)",
            "    date_columns = ['date', 'Date', 'datetime', 'timestamp', 'time']",
            "    date_col = None",
            "    ",
            "    for col in date_columns:",
            "        if col in df_clean.columns:",
            "            date_col = col",
            "            break",
            "    ",
            "    if date_col:",
            "        # Convert to datetime with multiple format handling",
            "        try:",
            "            df_clean[date_col] = pd.to_datetime(df_clean[date_col], utc=True)",
            "            # Convert to local timezone if needed",
            "            df_clean[date_col] = df_clean[date_col].dt.tz_convert(None)",
            "        except:",
            "            # Fallback to infer_datetime_format",
            "            df_clean[date_col] = pd.to_datetime(df_clean[date_col], infer_datetime_format=True)",
            "        ",
            "        # Set as index",
            "        df_clean.set_index(date_col, inplace=True)",
            "        df_clean.index.name = 'date'",
            "    else:",
            "        print('⚠️  No date column found - using row index')",
            "    ",
            "    # Standardize column names (lowercase)",
            "    df_clean.columns = df_clean.columns.str.lower()",
            "    ",
            "    # Ensure numeric columns are properly typed",
            "    numeric_cols = ['open', 'high', 'low', 'close', 'volume']",
            "    for col in numeric_cols:",
            "        if col in df_clean.columns:",
            "            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')",
            "    ",
            "    # Remove any rows with all NaN values",
            "    df_clean.dropna(how='all', inplace=True)",
            "    ",
            "    # Sort by date index",
            "    if isinstance(df_clean.index, pd.DatetimeIndex):",
            "        df_clean.sort_index(inplace=True)",
            "    ",
            "    # Remove duplicate timestamps",
            "    df_clean = df_clean[~df_clean.index.duplicated(keep='first')]",
            "    ",
            "    return df_clean",
            "",
            "# Clean the data",
            "df = clean_financial_data(df_raw)",
            "",
            "# Data quality checks",
            "print('\\n📋 Data Quality Report:')",
            "print(f'   Rows after cleaning: {len(df)}')",
            "print(f'   Columns: {list(df.columns)}')",
            "",
            "if isinstance(df.index, pd.DatetimeIndex):",
            '    print(f\'   Date range: {df.index.min().strftime("%Y-%m-%d")} to {df.index.max().strftime("%Y-%m-%d")}\')',
            '    print(f\'   Frequency: {pd.infer_freq(df.index) or "Irregular"}\')',
            "",
            "# Check for missing values",
            "missing_data = df.isnull().sum()",
            "if missing_data.sum() > 0:",
            "    print('\\n⚠️  Missing values detected:')",
            "    for col, count in missing_data[missing_data > 0].items():",
            "        print(f'   {col}: {count} missing ({count/len(df)*100:.1f}%)')",
            "else:",
            "    print('   ✅ No missing values')",
            "",
            "# Display sample data",
            "print('\\n📊 Sample Data:')",
            "display(df.head())",
            "",
            "print('\\n📈 Data Statistics:')",
            "display(df.describe())"
        ]
        
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": "\n".join(code_lines)
        }
    
    def _create_basic_info_cell(self) -> Dict[str, Any]:
        """Create basic data information cell"""
        code_lines = [
            "# Basic data information",
            "print('=== Data Information ===')",
            "print(f'Shape: {df.shape}')",
            "print(f'Columns: {list(df.columns)}')",
            "print('\\n=== Data Types ===')",
            "print(df.dtypes)",
            "print('\\n=== Missing Values ===')",
            "print(df.isnull().sum())",
            "print('\\n=== Basic Statistics ===')",
            "df.describe()"
        ]
        
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": "\n".join(code_lines)
        }
    
    def _create_visualization_cell(self) -> Dict[str, Any]:
        """Create professional financial time series visualization"""
        code_lines = [
            "# Professional financial time series visualization",
            "def create_financial_charts(df, symbol):",
            '    """Create comprehensive financial charts"""',
            "    ",
            "    has_close = 'close' in df.columns",
            "    has_volume = 'volume' in df.columns",
            "    ",
            "    if not has_close:",
            "        print('❌ No close price data available')",
            "        return",
            "    ",
            "    # Create figure with subplots",
            "    fig = plt.figure(figsize=(16, 12))",
            "    ",
            "    # Price chart",
            "    ax1 = plt.subplot(3, 2, (1, 2))  # Top row, full width",
            "    ax1.plot(df.index, df['close'], linewidth=1.5, color='#1f77b4', label='Close Price')",
            "    ax1.set_title(f'{symbol} Price Chart', fontweight='bold', fontsize=14)",
            "    ax1.set_ylabel('Price ($)')",
            "    ax1.legend()",
            "    ax1.grid(True, alpha=0.3)",
            "    ",
            "    # Format dates on x-axis",
            "    if isinstance(df.index, pd.DatetimeIndex):",
            "        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))",
            "        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)",
            "    ",
            "    # Volume chart (if available)",
            "    if has_volume:",
            "        ax2 = plt.subplot(3, 2, (3, 4))  # Second row, full width",
            "        ax2.bar(df.index, df['volume'], alpha=0.7, color='orange', width=1)",
            "        ax2.set_title('Volume', fontweight='bold')",
            "        ax2.set_ylabel('Volume')",
            "        ax2.grid(True, alpha=0.3)",
            "        ",
            "        # Format volume numbers",
            "        max_vol = df['volume'].max()",
            "        if max_vol > 1e6:",
            "            ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))",
            "        elif max_vol > 1e3:",
            "            ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e3:.0f}K'))",
            "    ",
            "    # Returns analysis",
            "    returns = df['close'].pct_change().dropna()",
            "    ",
            "    # Returns over time",
            "    ax3 = plt.subplot(3, 2, 5)",
            "    ax3.plot(returns.index, returns * 100, linewidth=1, alpha=0.7, color='green')",
            "    ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)",
            "    ax3.set_title('Daily Returns (%)', fontweight='bold')",
            "    ax3.set_ylabel('Return (%)')",
            "    ax3.grid(True, alpha=0.3)",
            "    ",
            "    # Returns distribution",
            "    ax4 = plt.subplot(3, 2, 6)",
            "    ax4.hist(returns * 100, bins=50, alpha=0.7, color='green', edgecolor='black')",
            "    ax4.axvline(x=0, color='red', linestyle='--', alpha=0.7)",
            "    ax4.set_title('Returns Distribution', fontweight='bold')",
            "    ax4.set_xlabel('Return (%)')",
            "    ax4.set_ylabel('Frequency')",
            "    ax4.grid(True, alpha=0.3)",
            "    ",
            "    plt.tight_layout()",
            "    return fig",
            "",
            "# Create the charts",
            "fig = create_financial_charts(df, symbol)",
            "plt.show()",
            "",
            "# Print summary statistics",
            "if 'close' in df.columns:",
            "    returns = df['close'].pct_change().dropna()",
            "    ",
            "    print('\\n📊 Quick Statistics:')",
            '    print(f\'   Current Price: ${df["close"].iloc[-1]:.2f}\')',
            '    print(f\'   Price Range: ${df["close"].min():.2f} - ${df["close"].max():.2f}\')',
            '    print(f\'   Total Return: {((df["close"].iloc[-1] / df["close"].iloc[0]) - 1) * 100:.2f}%\')',
            "    print(f'   Daily Volatility: {returns.std() * 100:.2f}%')",
            "    print(f'   Annualized Volatility: {returns.std() * np.sqrt(252) * 100:.2f}%')",
            "    ",
            "    if 'volume' in df.columns:",
            '        print(f\'   Average Volume: {df["volume"].mean():,.0f}\')'
        ]
        
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": "\n".join(code_lines)
        }
    
    def _create_statistics_cell(self) -> Dict[str, Any]:
        """Create statistics analysis cell"""
        code_lines = [
            "# Calculate key statistics",
            "if 'close' in df.columns:",
            "    # Price statistics",
            "    current_price = df['close'].iloc[-1]",
            "    price_change = df['close'].iloc[-1] - df['close'].iloc[0]",
            "    price_change_pct = (price_change / df['close'].iloc[0]) * 100",
            "    ",
            "    # Returns analysis",
            "    returns = df['close'].pct_change().dropna()",
            "    daily_volatility = returns.std()",
            "    annualized_volatility = daily_volatility * np.sqrt(252)  # Assuming daily data",
            "    ",
            "    # Display statistics",
            "    print('=== Key Statistics ===')",
            "    print(f'Current Price: ${current_price:.2f}')",
            "    print(f'Price Change: ${price_change:.2f} ({price_change_pct:.2f}%)')",
            "    print(f'Daily Volatility: {daily_volatility:.4f} ({daily_volatility*100:.2f}%)')",
            "    print(f'Annualized Volatility: {annualized_volatility:.4f} ({annualized_volatility*100:.2f}%)')",
            '    print(f\'Max Price: ${df["close"].max():.2f}\')',
            '    print(f\'Min Price: ${df["close"].min():.2f}\')',
            "    ",
            "    if 'volume' in df.columns:",
            '        print(f\'Average Volume: {df["volume"].mean():,.0f}\')',
            '        print(f\'Total Volume: {df["volume"].sum():,.0f}\')'
        ]
        
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": "\n".join(code_lines)
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
    
    def _create_feature_cells(self, selected_features: List[str]) -> List[Dict[str, Any]]:
        """Create cells for selected analysis features"""
        cells = []
        
        for feature_name in selected_features:
            feature = FEATURE_LIBRARY.get_feature(feature_name)
            if feature:
                # Add feature header cell
                header_cell = {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        f"## {feature.name}\n\n",
                        f"**Category:** {feature.category.value}\n\n",
                        f"**Description:** {feature.description}\n\n",
                        f"**Complexity:** {feature.complexity}\n\n"
                    ]
                }
                cells.append(header_cell)
                
                # Add feature code cell
                code_cell = {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": feature.code_template.split('\n')
                }
                cells.append(code_cell)
        
        return cells


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
