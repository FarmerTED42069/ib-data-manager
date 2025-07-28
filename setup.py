"""
Setup script for IB Data Manager
"""

import subprocess
import sys
import os

def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    dirs = ["logs", "exports"]
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"Created directory: {dir_name}")

def main():
    print("=== IB Data Manager Setup ===")
    print()
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Create directories
    create_directories()
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Make sure IB Gateway is running")
    print("2. Enable API access in IB Gateway settings")
    print("3. Run 'python test_connection.py' to test the connection")
    print("4. Run 'python main.py' to start the application")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()
