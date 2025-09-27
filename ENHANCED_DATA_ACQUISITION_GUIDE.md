# Enhanced Historical Data Acquisition Guide

## 🚀 Overview

The Enhanced Data Acquisition interface provides comprehensive multi-asset data collection capabilities with advanced timeframe selection, batch processing, and automated export features.

## 🎯 Key Features

### Multi-Asset Selection
- **Quick Select Presets**: Pre-configured asset groups for common use cases
  - Major Stocks (AAPL, MSFT, GOOGL, AMZN, TSLA, etc.)
  - Tech Stocks (focused technology companies)
  - Major ETFs (SPY, QQQ, IWM, VTI, etc.)
  - ES Futures (ES, NQ, YM, RTY, CL, GC)
  - Major Forex (EUR/USD, GBP/USD, JPY/USD, etc.)
  - Crypto ETFs (BITO, ETHE, GBTC)

- **Manual Entry**: Add individual assets with custom specifications
- **Bulk Entry**: Comma-separated list for quick asset addition
- **Asset Management**: Remove, clear, and modify selected assets

### Advanced Timeframe Selection
- **Preset Categories**:
  - **Intraday**: 1 min to 1 hour bars for short-term analysis
  - **Daily**: Daily bars from 1 month to 2 years
  - **Weekly/Monthly**: Long-term data up to 10 years

- **Custom Timeframes**: Manual duration and bar size specification
- **IBKR Compliance**: Automatic validation of duration/bar size combinations

### Batch Processing
- **Sequential Processing**: Controlled request timing to avoid rate limits
- **Progress Tracking**: Real-time progress bar and status updates
- **Error Handling**: Individual asset failures don't stop the batch
- **Configurable Delays**: Adjustable delays between requests (1-10 seconds)

### Export Capabilities
- **Bulk CSV Export**: Export all acquired data to organized CSV files
- **Automatic Jupyter Integration**: Seamless export to analysis environment
- **Timestamped Files**: Organized file naming with timestamps
- **Results Summary**: Detailed acquisition results with bar counts and status

## 📋 Usage Instructions

### 1. Launch Enhanced Interface
```bash
cd C:\Users\tnova\Dev\ib_data_manager
python test_enhanced_gui.py
```

### 2. Connect to IB Gateway
- Ensure IB Gateway/TWS is running
- Click "Connect" in the Connection Status section
- Wait for "Connected" status (green indicator)

### 3. Select Assets
- Click "Select Assets" button
- Choose from preset categories or add manually
- Use bulk entry for multiple symbols (comma-separated)
- Review selected assets in the list

### 4. Configure Timeframe
- **Option A - Presets**: Select category and preset combination
- **Option B - Custom**: Enter duration (e.g., "1 Y") and bar size

### 5. Set Options
- **Regular Trading Hours**: Check for RTH-only data
- **Delay**: Set delay between requests (recommended: 1-2 seconds)

### 6. Start Acquisition
- Click "Start Acquisition"
- Monitor progress bar and status messages
- View results in the summary table
- Stop anytime using "Stop" button

### 7. Export Results
- Click "Export All" to save all data as CSV files
- Choose export directory
- Files are automatically organized with timestamps

## 🎛️ Advanced Features

### Timeframe Presets Examples
- **"1 Min - Last Hour"**: Perfect for scalping analysis
- **"Daily - Last Year"**: Standard daily analysis
- **"Weekly - Last Year"**: Swing trading analysis
- **"Monthly - Last 5 Years"**: Long-term trend analysis

### Asset Preset Examples
- **Major Stocks**: Top 10 market cap stocks for broad market analysis
- **Tech Stocks**: Technology sector focus for sector analysis
- **ES Futures**: Complete futures suite for derivatives analysis
- **Major Forex**: Primary currency pairs for FX analysis

### Batch Processing Benefits
- **Efficiency**: Process 10-100+ assets in one operation
- **Rate Limiting**: Automatic delays prevent API throttling
- **Error Recovery**: Individual failures don't stop the batch
- **Progress Tracking**: Real-time status for each asset

## 🔧 Integration with Analysis Environment

The enhanced data acquisition seamlessly integrates with your quantitative analysis environment:

1. **Automatic Export**: Data exports to `C:\Users\tnova\quant_analysis\data\exports`
2. **Jupyter Integration**: Automatic notebook generation for analysis
3. **Organized Structure**: Timestamped folders and standardized CSV format
4. **Database Storage**: All data automatically saved to SQLite database

## 📊 Data Quality Features

- **IBKR Validation**: Automatic validation of duration/bar size combinations
- **Error Reporting**: Detailed error messages for failed requests
- **Data Verification**: Bar count verification and status reporting
- **Retry Logic**: Built-in retry for transient failures

## 🚀 Next Steps

After acquiring your data:

1. **Analysis**: Use the exported CSV files in your analysis environment
2. **Jupyter Notebooks**: Leverage auto-generated notebooks for quick analysis
3. **Database Queries**: Access historical data via the database viewer
4. **Scheduling**: Set up automated data collection using the scheduler

## 💡 Tips for Optimal Usage

1. **Start Small**: Begin with 5-10 assets to test your setup
2. **Use Presets**: Leverage preset timeframes for common analysis periods
3. **Monitor Progress**: Watch for any connection or data issues
4. **Regular Updates**: Run daily/weekly to maintain current datasets
5. **Backup Data**: Export important datasets for long-term storage

## 🔍 Troubleshooting

- **Connection Issues**: Ensure IB Gateway is running and configured
- **Rate Limiting**: Increase delay between requests if getting errors
- **Memory Issues**: Process smaller batches for large datasets
- **Export Errors**: Check file permissions and disk space

## 📈 Future Enhancements

Coming soon:
- **Options Data**: Options chains and Greeks data acquisition
- **Order Flow Data**: Level 2 market depth and tape data
- **Real-time Streaming**: Live data feeds with database storage
- **Advanced Scheduling**: Automated data collection schedules
