# IB Data Manager

A clean, easy-to-use interface for pulling data from Interactive Brokers Gateway API and storing it in a local database.

## Features

- **Clean GUI Interface**: Simple and intuitive user interface built with Tkinter
- **Multiple Data Types**: 
  - Historical market data (bars)
  - Real-time quotes
  - Account information
- **Local Database Storage**: All data is stored in SQLite database for easy access
- **Data Export**: Export data to CSV files
- **Database Viewer**: Built-in viewer to browse stored data
- **Comprehensive Logging**: All operations are logged for debugging

## Prerequisites

1. **Interactive Brokers Account**: You need an active IB account
2. **IB Gateway or TWS**: Install and configure IB Gateway (recommended) or Trader Workstation
3. **Python 3.8+**: Make sure Python is installed on your system

## Installation

1. Clone or download this repository

2. Install required dependencies:
```bash
cd ib_data_manager
pip install -r requirements.txt
```

## Configuration

1. **Start IB Gateway**:
   - Launch IB Gateway
   - Log in with your credentials
   - Make sure the API is enabled (Configure -> Settings -> API -> Settings)
   - Note the port number (default is 4001 for live, 4002 for paper trading)

2. **Configure API Settings in IB Gateway**:
   - Enable "Enable ActiveX and Socket Clients"
   - Add "127.0.0.1" to trusted IP addresses
   - Uncheck "Read-Only API" if you want to place orders (future feature)

## Usage

1. **Start the application**:
```bash
python main.py
```

2. **Connect to IB Gateway**:
   - Click "Connect" button
   - The status should change to "Connected" in green

3. **Fetch Historical Data**:
   - Enter a symbol (e.g., AAPL, SPY, EUR.USD)
   - Select contract type (STK for stocks, FUT for futures, etc.)
   - Enter exchange (SMART for stocks, GLOBEX for futures)
   - Enter currency (USD, EUR, etc.)
   - Choose "Historical Data" 
   - Set duration (e.g., "1 D" for 1 day, "1 W" for 1 week)
   - Set bar size (1 min, 5 mins, 1 hour, etc.)
   - Click "Fetch Data"

4. **Get Real-time Quotes**:
   - Enter symbol details
   - Choose "Real-time Quotes"
   - Click "Fetch Data"
   - Quotes will update in real-time in the output area

5. **View Account Information**:
   - Choose "Account Info"
   - Click "Fetch Data"
   - Account details will be displayed

6. **View Database**:
   - Click "View Database" to open the database viewer
   - Browse through historical data and real-time quotes
   - Data is displayed in a tabular format

7. **Export Data**:
   - Click "Export CSV"
   - Choose a location and filename
   - Data will be exported to CSV format

## Data Storage

All data is stored in a local SQLite database (`ib_data.db`) with the following tables:

- `historical_data`: Stores historical bar data
- `realtime_quotes`: Stores real-time quote updates
- `account_info`: Stores account information
- `positions`: Stores position data (future feature)
- `orders`: Stores order data (future feature)

## Logging

The application logs all operations to:
- Console output
- `ib_data_manager.log` file

## Example Queries

Here are some example configurations for different instruments:

**Stocks (US)**:
- Symbol: AAPL
- Type: STK
- Exchange: SMART
- Currency: USD

**Forex**:
- Symbol: EUR.USD
- Type: CASH
- Exchange: IDEALPRO
- Currency: USD

**Futures**:
- Symbol: ES
- Type: FUT
- Exchange: GLOBEX
- Currency: USD

**Options**:
- Symbol: AAPL
- Type: OPT
- Exchange: SMART
- Currency: USD

## Duration Examples

- `1 D` - 1 day
- `1 W` - 1 week
- `1 M` - 1 month
- `1 Y` - 1 year
- `10 D` - 10 days

## Bar Size Examples

- `1 secs` - 1 second bars
- `5 secs` - 5 second bars
- `15 secs` - 15 second bars
- `30 secs` - 30 second bars
- `1 min` - 1 minute bars
- `2 mins` - 2 minute bars
- `3 mins` - 3 minute bars
- `5 mins` - 5 minute bars
- `15 mins` - 15 minute bars
- `30 mins` - 30 minute bars
- `1 hour` - 1 hour bars
- `1 day` - Daily bars
- `1 week` - Weekly bars
- `1 month` - Monthly bars

## Troubleshooting

1. **Connection Issues**:
   - Ensure IB Gateway is running
   - Check that the port matches (default 4001)
   - Verify API settings are enabled in IB Gateway
   - Check firewall settings

2. **No Data Received**:
   - Verify the symbol is correct
   - Check that you have market data permissions for the instrument
   - Ensure the exchange is correct for the instrument
   - Try a shorter duration or different bar size

3. **Database Errors**:
   - Check write permissions in the application directory
   - Verify disk space is available
   - Check the log file for detailed error messages

## Future Enhancements

Planned features for future releases:
- Order placement functionality
- Advanced charting capabilities
- Technical indicators
- Portfolio analysis tools
- Automated trading strategies
- Web interface
- Multi-account support

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is provided as-is, without any warranty. Trading financial instruments involves risk. Always test thoroughly with a paper trading account before using with real money.
