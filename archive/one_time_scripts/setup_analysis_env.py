"""
Setup script for creating a dedicated quantitative analysis environment
Creates directory structure, virtual environment, and installs required packages
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def create_analysis_environment(base_path: str = None):
    """
    Create a complete analysis environment for quantitative research
    
    Args:
        base_path: Base directory for the analysis environment
                  If None, will prompt user or use default
    """
    
    if base_path is None:
        # Default to user's home directory
        base_path = os.path.join(os.path.expanduser("~"), "quant_analysis")
    
    print(f"Setting up analysis environment at: {base_path}")
    
    # Create directory structure
    directories = [
        "data/exports",           # Raw CSV exports from IB Data Manager
        "data/processed",         # Cleaned/processed data
        "notebooks/exploratory",  # Data exploration notebooks
        "notebooks/features",     # Feature engineering notebooks
        "notebooks/models",       # ML model development
        "notebooks/backtests",    # Strategy backtesting
        "src/features",          # Feature engineering modules
        "src/models",            # ML model classes
        "src/utils",             # Analysis utilities
        "results/plots",         # Generated plots and charts
        "results/reports",       # Analysis reports
        "results/models",        # Saved model files
        "config"                 # Configuration files
    ]
    
    print("\n1. Creating directory structure...")
    for directory in directories:
        full_path = os.path.join(base_path, directory)
        os.makedirs(full_path, exist_ok=True)
        print(f"   ✓ Created: {directory}")
    
    # Create virtual environment
    print("\n2. Creating virtual environment...")
    venv_path = os.path.join(base_path, "venv")
    
    try:
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
        print(f"   ✓ Virtual environment created at: {venv_path}")
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Failed to create virtual environment: {e}")
        return False
    
    # Determine pip executable path
    if sys.platform.startswith('win'):
        pip_exe = os.path.join(venv_path, "Scripts", "pip.exe")
        python_exe = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        pip_exe = os.path.join(venv_path, "bin", "pip")
        python_exe = os.path.join(venv_path, "bin", "python")
    
    # Install required packages
    print("\n3. Installing analysis packages...")
    packages = [
        "jupyter",
        "jupyterlab",
        "pandas>=2.0",
        "numpy",
        "matplotlib",
        "seaborn",
        "scikit-learn",
        "scipy",
        "plotly",
        "yfinance",  # For additional market data
        "ta-lib",    # Technical analysis library
        "pandas-ta", # Pandas technical analysis
        "quantlib",  # Quantitative finance library
        "zipline-reloaded",  # Backtesting framework
        "pyfolio-reloaded",  # Performance analysis
        "empyrical", # Risk metrics
    ]
    
    for package in packages:
        try:
            print(f"   Installing {package}...")
            subprocess.run([pip_exe, "install", package], 
                         check=True, capture_output=True, text=True)
            print(f"   ✓ Installed: {package}")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠ Warning: Failed to install {package}: {e}")
    
    # Create configuration files
    print("\n4. Creating configuration files...")
    
    # Create Jupyter config
    jupyter_config = {
        "notebook_dir": os.path.join(base_path, "notebooks"),
        "browser": "default",
        "open_browser": True
    }
    
    config_path = os.path.join(base_path, "config", "jupyter_config.json")
    with open(config_path, 'w') as f:
        json.dump(jupyter_config, f, indent=2)
    print(f"   ✓ Created Jupyter config: {config_path}")
    
    # Create analysis environment config for IB Data Manager
    ib_config = {
        "analysis_environment_path": base_path,
        "data_export_path": os.path.join(base_path, "data", "exports"),
        "notebooks_path": os.path.join(base_path, "notebooks"),
        "python_executable": python_exe,
        "venv_path": venv_path
    }
    
    ib_config_path = os.path.join(base_path, "config", "ib_data_manager_config.json")
    with open(ib_config_path, 'w') as f:
        json.dump(ib_config, f, indent=2)
    print(f"   ✓ Created IB Data Manager config: {ib_config_path}")
    
    # Create starter notebooks
    print("\n5. Creating starter notebooks...")
    create_starter_notebooks(base_path)
    
    # Create activation scripts
    print("\n6. Creating activation scripts...")
    create_activation_scripts(base_path, venv_path)
    
    print(f"\n✅ Analysis environment setup complete!")
    print(f"\nEnvironment location: {base_path}")
    print(f"\nNext steps:")
    print(f"1. Activate the environment:")
    if sys.platform.startswith('win'):
        print(f"   {os.path.join(base_path, 'activate_env.bat')}")
    else:
        print(f"   source {os.path.join(base_path, 'activate_env.sh')}")
    print(f"2. Start Jupyter Lab: jupyter lab")
    print(f"3. Configure IB Data Manager to use this environment")
    
    return True


def create_starter_notebooks(base_path: str):
    """Create starter notebooks with templates"""
    
    notebooks = {
        "notebooks/exploratory/data_exploration_template.ipynb": create_exploration_notebook(),
        "notebooks/features/feature_engineering_template.ipynb": create_feature_notebook(),
        "notebooks/models/ml_model_template.ipynb": create_model_notebook(),
        "notebooks/backtests/backtest_template.ipynb": create_backtest_notebook()
    }
    
    for notebook_path, content in notebooks.items():
        full_path = os.path.join(base_path, notebook_path)
        with open(full_path, 'w') as f:
            json.dump(content, f, indent=2)
        print(f"   ✓ Created: {notebook_path}")


def create_exploration_notebook():
    """Create data exploration template notebook"""
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Data Exploration Template\n\n",
                    "This notebook provides a template for exploring financial data exported from IB Data Manager.\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import pandas as pd\n",
                    "import numpy as np\n",
                    "import matplotlib.pyplot as plt\n",
                    "import seaborn as sns\n",
                    "from pathlib import Path\n",
                    "\n",
                    "# Set up plotting\n",
                    "plt.style.use('seaborn-v0_8')\n",
                    "sns.set_palette('husl')\n",
                    "\n",
                    "# Load your data\n",
                    "# data_path = '../data/exports/YOUR_SYMBOL_export_TIMESTAMP/YOUR_SYMBOL_historical_data.csv'\n",
                    "# df = pd.read_csv(data_path, parse_dates=['date'], index_col='date')\n",
                    "\n",
                    "print('Data exploration template ready!')"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }


def create_feature_notebook():
    """Create feature engineering template notebook"""
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Feature Engineering Template\n\n",
                    "Template for creating technical indicators and statistical features.\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import pandas as pd\n",
                    "import numpy as np\n",
                    "import pandas_ta as ta\n",
                    "\n",
                    "def create_technical_features(df):\n",
                    "    \"\"\"Create technical indicator features\"\"\"\n",
                    "    # Moving averages\n",
                    "    df['sma_20'] = df['close'].rolling(20).mean()\n",
                    "    df['sma_50'] = df['close'].rolling(50).mean()\n",
                    "    \n",
                    "    # RSI\n",
                    "    df['rsi'] = ta.rsi(df['close'])\n",
                    "    \n",
                    "    # MACD\n",
                    "    macd = ta.macd(df['close'])\n",
                    "    df = pd.concat([df, macd], axis=1)\n",
                    "    \n",
                    "    return df\n",
                    "\n",
                    "print('Feature engineering template ready!')"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }


def create_model_notebook():
    """Create ML model template notebook"""
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# ML Model Template\n\n",
                    "Template for developing machine learning models for trading strategies.\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from sklearn.ensemble import RandomForestClassifier\n",
                    "from sklearn.model_selection import train_test_split, cross_val_score\n",
                    "from sklearn.metrics import classification_report, confusion_matrix\n",
                    "import pandas as pd\n",
                    "import numpy as np\n",
                    "\n",
                    "def create_target_variable(df, forward_periods=5, threshold=0.01):\n",
                    "    \"\"\"Create binary target for price direction prediction\"\"\"\n",
                    "    future_returns = df['close'].pct_change(forward_periods).shift(-forward_periods)\n",
                    "    return (future_returns > threshold).astype(int)\n",
                    "\n",
                    "print('ML model template ready!')"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }


def create_backtest_notebook():
    """Create backtesting template notebook"""
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Backtesting Template\n\n",
                    "Template for backtesting trading strategies.\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import pandas as pd\n",
                    "import numpy as np\n",
                    "import matplotlib.pyplot as plt\n",
                    "\n",
                    "def simple_backtest(df, signals, initial_capital=10000):\n",
                    "    \"\"\"Simple vectorized backtest\"\"\"\n",
                    "    returns = df['close'].pct_change()\n",
                    "    strategy_returns = signals.shift(1) * returns\n",
                    "    cumulative_returns = (1 + strategy_returns).cumprod()\n",
                    "    \n",
                    "    return {\n",
                    "        'total_return': cumulative_returns.iloc[-1] - 1,\n",
                    "        'sharpe_ratio': strategy_returns.mean() / strategy_returns.std() * np.sqrt(252),\n",
                    "        'max_drawdown': (cumulative_returns / cumulative_returns.cummax() - 1).min()\n",
                    "    }\n",
                    "\n",
                    "print('Backtesting template ready!')"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }


def create_activation_scripts(base_path: str, venv_path: str):
    """Create environment activation scripts"""
    
    if sys.platform.startswith('win'):
        # Windows batch script
        batch_script = f"""@echo off
echo Activating Quant Analysis Environment...
call "{venv_path}\\Scripts\\activate.bat"
echo Environment activated!
echo.
echo Available commands:
echo   jupyter lab          - Start Jupyter Lab
echo   python               - Python interpreter
echo   pip install package  - Install packages
echo.
cd /d "{base_path}"
cmd /k
"""
        script_path = os.path.join(base_path, "activate_env.bat")
        with open(script_path, 'w') as f:
            f.write(batch_script)
        print(f"   ✓ Created activation script: activate_env.bat")
    
    else:
        # Unix shell script
        shell_script = f"""#!/bin/bash
echo "Activating Quant Analysis Environment..."
source "{venv_path}/bin/activate"
echo "Environment activated!"
echo ""
echo "Available commands:"
echo "  jupyter lab          - Start Jupyter Lab"
echo "  python               - Python interpreter"
echo "  pip install package  - Install packages"
echo ""
cd "{base_path}"
exec "$SHELL"
"""
        script_path = os.path.join(base_path, "activate_env.sh")
        with open(script_path, 'w') as f:
            f.write(shell_script)
        os.chmod(script_path, 0o755)
        print(f"   ✓ Created activation script: activate_env.sh")


def main():
    """Main setup function"""
    print("IB Data Manager - Analysis Environment Setup")
    print("=" * 50)
    
    # Get user preference for location
    default_path = os.path.join(os.path.expanduser("~"), "quant_analysis")
    
    print(f"\nDefault location: {default_path}")
    choice = input("Use default location? (y/n): ").lower().strip()
    
    if choice == 'n':
        custom_path = input("Enter custom path: ").strip()
        if custom_path:
            base_path = custom_path
        else:
            base_path = default_path
    else:
        base_path = default_path
    
    # Create the environment
    success = create_analysis_environment(base_path)
    
    if success:
        print(f"\n🎉 Setup completed successfully!")
        print(f"\nYour analysis environment is ready at: {base_path}")
        print(f"\nTo configure IB Data Manager:")
        print(f"1. Copy this path: {base_path}")
        print(f"2. In IB Data Manager GUI, use 'Export CSV' and select this directory")
        print(f"3. The system will remember this as your analysis environment")
    else:
        print(f"\n❌ Setup failed. Please check the error messages above.")


if __name__ == "__main__":
    main()
