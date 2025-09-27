# IB Data Manager - Project Cleanup Plan

## Overview
This document outlines the cleanup strategy to organize the project structure and remove obsolete files.

## Current Issues
- 🗂️ Root directory cluttered with test/debug files
- 🔄 Multiple redundant connection test files
- 📁 Test files scattered across different directories
- 🏗️ Legacy files mixed with production code
- 📜 Excessive batch scripts with overlapping functionality

## Cleanup Strategy

### 1. FILES TO REMOVE (Obsolete/Redundant)
```
Root Directory:
- basic_connect.py (replaced by unified dashboard)
- minimal_connect.py (replaced by unified dashboard)
- fixed_basic_connect.py (redundant)
- fixed_test_connection.py (redundant)
- debug_data_fetch.py (debug file)
- debug_enhanced_da.py (debug file)
- debug_mes_contract.py (debug file)
- test_api_settings.py (move to tests/)
- test_enhanced_gui.py (move to tests/)
- test_market_depth_debug.py (move to tests/)
- test_realtime_streaming.py (move to tests/)
- test_streaming_debug.py (move to tests/)
- connection_diagnostics.py (duplicate functionality)
```

### 2. FILES TO MOVE TO tests/
```
From Root:
- test_api_settings.py
- test_enhanced_gui.py
- test_market_depth_debug.py
- test_realtime_streaming.py
- test_streaming_debug.py

From ib_data_manager/gui/:
- test_async_gui.py

From ib_data_manager/db/:
- test_async_database.py

From ib_data_manager/api/:
- test_*.py files
```

### 3. FILES TO ARCHIVE
```
Move to archive/legacy/:
- configure_analysis_env.py (one-time setup)
- setup_analysis_env.py (one-time setup)
- ib_data_manager/gui/main.py (legacy GUI)
- ib_data_manager/gui/enhanced_data_acquisition.py (legacy GUI)
```

### 4. SCRIPTS CONSOLIDATION
```
Keep Essential Scripts:
- launch_dashboard.bat (main launcher)
- scripts/COMPLETE_SETUP.bat (full setup)
- scripts/create_venv.bat (environment setup)

Archive Redundant Scripts:
- Multiple create_shortcut variants
- Redundant run/install scripts
```

### 5. PRODUCTION STRUCTURE (After Cleanup)
```
ib_data_manager/
├── ib_data_manager/           # Core package
│   ├── api/                   # API connectors
│   ├── config/                # Configuration
│   ├── core/                  # Core functionality
│   ├── db/                    # Database operations
│   ├── gui/                   # GUI components
│   └── utils/                 # Utilities
├── tests/                     # All test files
├── archive/                   # Archived/legacy files
├── data/                      # Data storage
├── docs/                      # Documentation
├── scripts/                   # Essential scripts only
├── launch_unified_dashboard.py # Main entry point
├── requirements.txt           # Dependencies
├── setup.py                   # Package setup
└── README.md                  # Documentation
```

## Benefits After Cleanup
- ✅ Clear separation of production vs test code
- ✅ Reduced root directory clutter (from 30+ files to ~10)
- ✅ Easier navigation and maintenance
- ✅ Better organization for new developers
- ✅ Preserved history in archive for reference

## Execution Order
1. Create organized test directory structure
2. Move test files to appropriate locations
3. Archive legacy/one-time files
4. Remove obsolete files
5. Update imports and documentation
6. Verify functionality after cleanup
