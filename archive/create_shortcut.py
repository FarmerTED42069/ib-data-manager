"""
Create a desktop shortcut for IB Data Manager
"""

import os
import winshell
from win32com.client import Dispatch
import sys

def create_desktop_shortcut():
    """Create a shortcut on the desktop for IB Data Manager"""
    try:
        # Get the desktop path
        desktop = winshell.desktop()
        
        # Path to the main application
        app_dir = os.path.dirname(os.path.abspath(__file__))
        target = os.path.join(app_dir, "main.py")
        
        # Path to Python executable
        python_exe = sys.executable
        
        # Create shortcut
        path = os.path.join(desktop, "IB Data Manager.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        
        # Set the target to python.exe with main.py as argument
        shortcut.Targetpath = python_exe
        shortcut.Arguments = f'"{target}"'
        shortcut.WorkingDirectory = app_dir
        shortcut.IconLocation = python_exe
        shortcut.Description = "Interactive Brokers Data Manager"
        
        shortcut.save()
        
        print(f"✓ Desktop shortcut created successfully!")
        print(f"Location: {path}")
        
        # Also create a batch file shortcut
        batch_target = os.path.join(app_dir, "run_app.bat")
        batch_path = os.path.join(desktop, "IB Data Manager (Batch).lnk")
        
        batch_shortcut = shell.CreateShortCut(batch_path)
        batch_shortcut.Targetpath = batch_target
        batch_shortcut.WorkingDirectory = app_dir
        batch_shortcut.IconLocation = "%SystemRoot%\\System32\\cmd.exe"
        batch_shortcut.Description = "Interactive Brokers Data Manager (Batch)"
        
        batch_shortcut.save()
        
        print(f"✓ Batch shortcut created successfully!")
        print(f"Location: {batch_path}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating shortcut: {str(e)}")
        return False

def create_start_menu_shortcut():
    """Create a shortcut in the Start Menu"""
    try:
        # Get the Start Menu Programs path
        programs = winshell.programs()
        
        # Create IB Data Manager folder in Start Menu
        ib_folder = os.path.join(programs, "IB Data Manager")
        os.makedirs(ib_folder, exist_ok=True)
        
        # Path to the main application
        app_dir = os.path.dirname(os.path.abspath(__file__))
        target = os.path.join(app_dir, "main.py")
        
        # Path to Python executable
        python_exe = sys.executable
        
        # Create shortcut
        path = os.path.join(ib_folder, "IB Data Manager.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        
        shortcut.Targetpath = python_exe
        shortcut.Arguments = f'"{target}"'
        shortcut.WorkingDirectory = app_dir
        shortcut.IconLocation = python_exe
        shortcut.Description = "Interactive Brokers Data Manager"
        
        shortcut.save()
        
        print(f"✓ Start Menu shortcut created successfully!")
        print(f"Location: {path}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating Start Menu shortcut: {str(e)}")
        return False

if __name__ == "__main__":
    print("Creating shortcuts for IB Data Manager...")
    print("-" * 50)
    
    # Create desktop shortcut
    desktop_success = create_desktop_shortcut()
    
    # Create Start Menu shortcut
    start_menu_success = create_start_menu_shortcut()
    
    print("-" * 50)
    
    if desktop_success and start_menu_success:
        print("✓ All shortcuts created successfully!")
    else:
        print("⚠ Some shortcuts could not be created. Check the error messages above.")
    
    print("\nYou can now:")
    print("1. Double-click 'IB Data Manager' on your desktop")
    print("2. Find 'IB Data Manager' in your Start Menu")
    print("3. Or run 'python main.py' from the command line")
    
    input("\nPress Enter to exit...")
