"""
Simple configuration script to connect IB Data Manager with the analysis environment
"""

import os
import json

def configure_ib_data_manager():
    """Configure IB Data Manager to use the analysis environment"""
    
    # Analysis environment path
    analysis_path = os.path.join(os.path.expanduser("~"), "quant_analysis")
    
    # Check if analysis environment exists
    if not os.path.exists(analysis_path):
        print("❌ Analysis environment not found!")
        print(f"Expected location: {analysis_path}")
        print("\nPlease run setup_analysis_env.py first.")
        return False
    
    # Create settings for IB Data Manager
    settings = {
        "analysis_env_path": analysis_path,
        "export_dir": os.path.join(analysis_path, "data", "exports"),
        "notebooks_dir": os.path.join(analysis_path, "notebooks"),
        "auto_create_notebooks": True,
        "default_export_to_analysis": True
    }
    
    # Save settings file
    settings_file = "settings.json"
    
    try:
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        print("✅ IB Data Manager configured successfully!")
        print(f"\nConfiguration saved to: {settings_file}")
        print(f"Analysis environment: {analysis_path}")
        print(f"Export directory: {settings['export_dir']}")
        print("\nNow when you use 'Export CSV' in the GUI:")
        print("1. It will default to your analysis environment")
        print("2. Automatically create Jupyter notebooks")
        print("3. Organize everything in timestamped folders")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")
        return False

def test_configuration():
    """Test if the configuration is working"""
    
    print("\n" + "="*50)
    print("Testing Configuration...")
    print("="*50)
    
    # Check settings file
    if os.path.exists("settings.json"):
        try:
            with open("settings.json", 'r') as f:
                settings = json.load(f)
            
            print("✅ Settings file found")
            print(f"   Analysis path: {settings.get('analysis_env_path', 'Not set')}")
            print(f"   Export dir: {settings.get('export_dir', 'Not set')}")
            
            # Check if paths exist
            analysis_path = settings.get('analysis_env_path')
            if analysis_path and os.path.exists(analysis_path):
                print("✅ Analysis environment exists")
                
                # Check key directories
                key_dirs = ["data/exports", "notebooks", "venv"]
                for dir_name in key_dirs:
                    dir_path = os.path.join(analysis_path, dir_name)
                    if os.path.exists(dir_path):
                        print(f"   ✅ {dir_name}")
                    else:
                        print(f"   ❌ {dir_name} missing")
            else:
                print("❌ Analysis environment path not found")
                
        except Exception as e:
            print(f"❌ Error reading settings: {e}")
    else:
        print("❌ Settings file not found")
    
    print("\n" + "="*50)

def main():
    """Main configuration function"""
    print("IB Data Manager - Analysis Environment Configuration")
    print("="*55)
    
    # Configure
    success = configure_ib_data_manager()
    
    if success:
        # Test configuration
        test_configuration()
        
        print("\n🎉 Configuration complete!")
        print("\nNext steps:")
        print("1. Run the async GUI: python -m ib_data_manager.gui.main_async")
        print("2. Fetch some historical data")
        print("3. Click 'Export CSV' - it will use your analysis environment")
        print("4. Open the generated Jupyter notebook to start analysis")
        
        print(f"\nYour analysis environment is at:")
        print(f"📁 {os.path.join(os.path.expanduser('~'), 'quant_analysis')}")
        
    else:
        print("\n❌ Configuration failed!")

if __name__ == "__main__":
    main()
