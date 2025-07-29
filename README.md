# Interactive Brokers Data Manager

A collection of utilities and connection tools for working with Interactive Brokers TWS and IB Gateway via the ib_insync library.

## Overview

This project provides a set of diagnostic and connection tools for Interactive Brokers API integration, designed to help troubleshoot and establish reliable connections for automated trading systems.

## Features

- **Connection Diagnostics**: Comprehensive testing of IB Gateway API connectivity
- **Minimal Connection Tests**: Basic connectivity verification with minimal overhead
- **Enhanced Trading Module**: Advanced futures trading with dynamic contract expiry
- **API Settings Verification**: Specific tests for API configuration and permissions
- **Robust Error Handling**: Detailed logging and connection troubleshooting

## Components

### Core Modules

- **`fixed_ibkr_trader.py`**: Enhanced trading module with dynamic expiry and improved connection handling
- **`connection_diagnostics.py`**: Comprehensive IB Gateway connection diagnostics tool
- **`minimal_connect.py`**: Minimal connection test with no API operations
- **`test_api_settings.py`**: API settings and permissions verification
- **`fixed_basic_connect.py`**: Basic connection test with extended timeout
- **`fixed_test_connection.py`**: Connection test with account information retrieval

## Prerequisites

- Interactive Brokers account with API access enabled
- IB Gateway or TWS running and configured for API connections
- Python 3.7+
- ib_insync library

## Installation

1. Install required dependencies:
   ```bash
   pip install ib_insync
   ```

2. Ensure IB Gateway is running on the correct port:
   - Paper Trading: Port 4002
   - Live Trading: Port 4001

## Usage

### Basic Connection Test
```bash
python minimal_connect.py
```

### Comprehensive Diagnostics
```bash
python connection_diagnostics.py
```

### API Settings Verification
```bash
python test_api_settings.py
```

### Trading Module Usage
```python
from fixed_ibkr_trader import IBKRTrader
trader = IBKRTrader()
# Use trader methods for automated trading
```

## Async GUI & Advanced Features

To launch the async GUI with advanced features:
```bash
python -m ib_data_manager.gui.main_async
```

- Use the Data Type selector for Historical, Real-time, Account, or Market Depth
- Fill in symbol, contract type, expiry (for futures), etc.
- For historical data, set duration and bar size; use chunking for long periods
- For real-time, click 'Fetch Data' to start recording, and 'Stop Realtime' to end
- Use 'Export CSV' and 'View Database' for data management


### Basic Connection Test
```bash
python minimal_connect.py
```

### Comprehensive Diagnostics
```bash
python connection_diagnostics.py
```

### API Settings Verification
```bash
python test_api_settings.py
```

### Trading Module Usage
```python
from fixed_ibkr_trader import IBKRTrader

trader = IBKRTrader()
# Use trader methods for automated trading
```

## Configuration

Default connection settings:
- Host: `127.0.0.1`
- Port: `4002` (IB Gateway Paper Trading)
- Timeout: 20 seconds
- Client IDs: Randomly generated to avoid conflicts

## Troubleshooting

1. **Connection Failed**: Ensure IB Gateway is running and API access is enabled
2. **Permission Denied**: Check API settings in IB Gateway configuration
3. **Timeout Issues**: Increase connection timeout or check network connectivity
4. **Client ID Conflicts**: Scripts use random client IDs to avoid conflicts

## Features

- Dynamic futures contract expiry handling
- Robust connection retry mechanisms
- Comprehensive error logging
- Multiple connection testing approaches
- Paper trading environment support

## Contributing

This is a utility collection designed for IBKR API development and troubleshooting. Feel free to extend or modify for your specific use cases.

## Directory Structure

See PROJECT_STRUCTURE.md for a full breakdown, including async modules, GUI enhancements, and new features (chunking, batch export, real-time recording).

## License

MIT License
