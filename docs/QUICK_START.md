# IB Data Manager - Quick Start Guide

## Project Overview

You now have a complete Interactive Brokers Data Manager application with:

- **Clean GUI Interface** using Tkinter
- **IB Gateway Integration** using ib_insync
- **SQLite Database** for data storage
- **Real-time & Historical Data** capabilities
- **Data Export** functionality
- **Comprehensive Logging**

## Quick Setup

1. **Install Dependencies**:
   ```bash
   cd ib_data_manager
   python setup.py
   ```

2. **Configure IB Gateway**:
   - Start IB Gateway
   - Log in with your credentials
   - Go to Configure → Settings → API → Settings
   - Enable "Enable ActiveX and Socket Clients"
   - Add "127.0.0.1" to trusted IP addresses
   - Note the port (4001 for live, 4002 for paper)

3. **Test Connection**:
   ```bash
   python test_connection.py
   ```

4. **Run Application**:
   ```bash
   python main.py
   ```
   Or double-click `run_app.bat`

## Application Features

### Main Window Components
1. **Connection Status**: Shows IB Gateway connection state
2. **Data Request Panel**: Enter symbol, type, exchange, currency
3. **Data Type Selection**: Historical, Real-time, or Account info
4. **Action Buttons**: Fetch Data, View Database, Export CSV
5. **Output Area**: Displays fetched data and logs

### How to Use

1. **Fetch Historical Data**:
   - Enter symbol (e.g., "AAPL")
   - Select "Historical Data"
   - Set duration (e.g., "1 D", "1 W")
   - Set bar size (e.g., "1 min", "1 hour")
   - Click "Fetch Data"

2. **Get Real-time Quotes**:
   - Enter symbol details
   - Select "Real-time Quotes"
   - Click "Fetch Data"
   - Watch live updates

3. **Export Data**:
   - Click "Export CSV"
   - Choose filename and location
   - Data exports from SQLite database

## File Structure

```
ib_data_manager/
├── main.py                # Main GUI application
├── ib_connector.py        # IB API connection handler
├── database.py            # SQLite database manager
├── config.py              # Configuration management
├── test_connection.py     # Connection test script
├── setup.py               # Installation script
├── requirements.txt       # Python dependencies
├── run_app.bat           # Windows launcher
├── README.md             # Full documentation
└── QUICK_START.md        # This file
```

## Common Symbol Examples

**Stocks**: AAPL, MSFT, TSLA (Exchange: SMART, Currency: USD)
**ETFs**: SPY, QQQ, IWM (Exchange: SMART, Currency: USD)
**Forex**: EUR.USD, GBP.USD (Exchange: IDEALPRO, Currency: USD)
**Futures**: ES, NQ, RTY (Exchange: GLOBEX, Currency: USD)

## Configuration

Edit `config.json` to customize:
- IB Gateway connection settings
- Default values for data requests
- Database settings
- Logging preferences

## Troubleshooting

1. **Connection Failed**:
   - Check IB Gateway is running
   - Verify API is enabled
   - Confirm port matches config
   - Check firewall settings

2. **No Data Received**:
   - Verify symbol is correct
   - Check market data permissions
   - Try different duration/bar size
   - Ensure market is open (for real-time)

3. **Database Errors**:
   - Check write permissions
   - Verify disk space
   - See logs for details

## Next Steps

1. Review the full `README.md` for detailed information
2. Explore the database viewer to see stored data
3. Customize settings in `config.json`
4. Try different symbols and data types
5. Set up automated data collection (future feature)

## Support

- Check `ib_data_manager.log` for detailed logs
- Review IB API documentation for symbol formats
- Test with paper trading account first
- Use small durations initially to verify functionality

Remember to always test with a paper trading account before using live trading!
