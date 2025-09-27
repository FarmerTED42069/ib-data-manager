#!/usr/bin/env python3
"""
Launch script for the Unified IB Data Manager Dashboard
Simple way to start the streamlined interface
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    """Launch the unified dashboard"""
    try:
        from ib_data_manager.gui.unified_dashboard import main as dashboard_main
        print("🚀 Launching IB Data Manager - Unified Dashboard...")
        print("✨ Streamlined interface with no more GUI fragmentation!")
        dashboard_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
