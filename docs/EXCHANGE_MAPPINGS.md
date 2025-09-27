# Exchange Mappings for Interactive Brokers

This document outlines the proper exchange mappings for different instruments in the IB Data Manager.

## 🏛️ **Futures Exchanges**

### CME Group - Equity Index Futures
| Symbol | Name | Exchange |
|--------|------|----------|
| ES | E-mini S&P 500 | CME |
| MES | Micro E-mini S&P 500 | CME |
| NQ | E-mini NASDAQ-100 | CME |
| MNQ | Micro E-mini NASDAQ-100 | CME |
| RTY | E-mini Russell 2000 | CME |
| M2K | Micro E-mini Russell 2000 | CME |
| EMD | E-mini S&P MidCap 400 | CME |

### CBOT - Interest Rate & Agricultural Futures
| Symbol | Name | Exchange |
|--------|------|----------|
| YM | E-mini Dow ($5) | CBOT |
| MYM | Micro E-mini Dow | CBOT |
| ZB | 30-Year Treasury Bond | CBOT |
| ZN | 10-Year Treasury Note | CBOT |
| ZF | 5-Year Treasury Note | CBOT |
| ZT | 2-Year Treasury Note | CBOT |
| UB | Ultra Treasury Bond | CBOT |
| ZC | Corn | CBOT |
| ZS | Soybeans | CBOT |
| ZW | Wheat | CBOT |
| ZM | Soybean Meal | CBOT |
| ZL | Soybean Oil | CBOT |
| ZO | Oats | CBOT |
| ZR | Rough Rice | CBOT |

### NYMEX - Energy Futures
| Symbol | Name | Exchange |
|--------|------|----------|
| CL | Crude Oil WTI | NYMEX |
| MCL | Micro WTI Crude Oil | NYMEX |
| NG | Natural Gas | NYMEX |
| RB | RBOB Gasoline | NYMEX |
| HO | Heating Oil | NYMEX |
| BZ | Brent Crude Oil | NYMEX |

### COMEX - Metals Futures
| Symbol | Name | Exchange |
|--------|------|----------|
| GC | Gold | COMEX |
| MGC | Micro Gold | COMEX |
| SI | Silver | COMEX |
| SIL | Micro Silver | COMEX |
| HG | Copper | COMEX |
| MHG | Micro Copper | COMEX |
| PL | Platinum | COMEX |
| PA | Palladium | COMEX |

### CME - Currency Futures
| Symbol | Name | Exchange |
|--------|------|----------|
| 6E | Euro FX | CME |
| M6E | Micro Euro FX | CME |
| 6B | British Pound | CME |
| M6B | Micro British Pound | CME |
| 6J | Japanese Yen | CME |
| MJY | Micro Japanese Yen | CME |
| 6A | Australian Dollar | CME |
| 6C | Canadian Dollar | CME |
| 6S | Swiss Franc | CME |
| 6N | New Zealand Dollar | CME |

### CME - Livestock Futures
| Symbol | Name | Exchange |
|--------|------|----------|
| LE | Live Cattle | CME |
| GF | Feeder Cattle | CME |
| HE | Lean Hogs | CME |

### ICE/NYBOT - Soft Commodities
| Symbol | Name | Exchange |
|--------|------|----------|
| CC | Cocoa | NYBOT |
| CT | Cotton | NYBOT |
| KC | Coffee | NYBOT |
| SB | Sugar | NYBOT |
| OJ | Orange Juice | NYBOT |

### EUREX - European Futures
| Symbol | Name | Exchange |
|--------|------|----------|
| FESX | Euro Stoxx 50 | EUREX |
| FDAX | DAX | EUREX |
| FGBL | Euro-Bund | EUREX |
| FGBM | Euro-Bobl | EUREX |
| FGBS | Euro-Schatz | EUREX |

## 📈 **Other Instrument Types**

### Stocks (STK)
- **Exchange**: `SMART` (for most US stocks)
- **Description**: SMART routing finds the best execution across multiple exchanges

### Forex (CASH)
- **Exchange**: `IDEALPRO`
- **Description**: IB's institutional forex platform

### Options (OPT)
- **Major Index Options**: `CBOE` (SPX, SPY, QQQ, IWM)
- **Equity Options**: `SMART`

### Indices (IND)
| Symbol | Name | Exchange |
|--------|------|----------|
| SPX | S&P 500 Index | CBOE |
| NDX | NASDAQ-100 Index | NASDAQ |
| RUT | Russell 2000 Index | CBOE |
| VIX | VIX Index | CBOE |
| DJX | Dow Jones Index | CBOE |

### Cryptocurrencies (CRYPTO)
- **Exchange**: `PAXOS`
- **Description**: IB's cryptocurrency exchange

### Other Types
- **CFDs**: `SMART`
- **Bonds**: `SMART`
- **Commodities**: `SMART`
- **Mutual Funds**: `SMART`
- **Warrants**: `SMART`

## 🔧 **How It Works**

The `get_proper_exchange()` method automatically selects the correct exchange based on:

1. **Symbol**: The instrument symbol (e.g., ES, AAPL, GC)
2. **Security Type**: The type of instrument (STK, FUT, OPT, etc.)

### Example Usage:
```python
# Futures - automatically uses CME for ES
contract = connector.create_contract("ES", "FUT")

# Stocks - automatically uses SMART routing
contract = connector.create_contract("AAPL", "STK")

# Gold futures - automatically uses COMEX
contract = connector.create_contract("GC", "FUT")
```

## ⚠️ **Important Notes**

1. **Default Fallbacks**: Unknown futures default to CME, other types default to SMART
2. **Manual Override**: You can still specify an exchange manually if needed
3. **Logging**: The system logs which exchange is selected for each instrument
4. **Real-time Updates**: This mapping can be updated as new instruments are added

## 🚀 **Testing**

To test the exchange mappings:

1. Set contract type to "FUT"
2. Enter a futures symbol (e.g., "ES", "GC", "CL")
3. Click "Live Quotes" or "Level II"
4. Check the console output for exchange selection confirmation

The system will show: `📍 Auto-selected exchange for ES (FUT): CME`
