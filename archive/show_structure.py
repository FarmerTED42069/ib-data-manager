"""
Display the project structure
"""

import os

def print_tree(directory, prefix="", is_last=True):
    """Print directory tree structure"""
    if prefix == "":
        print(os.path.basename(directory) + "/")
    
    items = sorted(os.listdir(directory))
    dirs = [item for item in items if os.path.isdir(os.path.join(directory, item))]
    files = [item for item in items if os.path.isfile(os.path.join(directory, item))]
    
    # Print directories first
    for i, dir_name in enumerate(dirs):
        is_last_dir = (i == len(dirs) - 1) and (len(files) == 0)
        print(prefix + ("└── " if is_last_dir else "├── ") + dir_name + "/")
        extension = "    " if is_last_dir else "│   "
        print_tree(os.path.join(directory, dir_name), prefix + extension, is_last_dir)
    
    # Then print files
    for i, file_name in enumerate(files):
        is_last_file = (i == len(files) - 1)
        print(prefix + ("└── " if is_last_file else "├── ") + file_name)

def main():
    print("IB Data Manager Project Structure:")
    print("=" * 40)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print_tree(current_dir)
    
    print("\n" + "=" * 40)
    print("File Descriptions:")
    print("=" * 40)
    
    descriptions = {
        "main.py": "Main application entry point with GUI",
        "ib_connector.py": "Interactive Brokers API connection handler",
        "database.py": "SQLite database management and operations",
        "config.py": "Configuration management system",
        "requirements.txt": "Python package dependencies",
        "setup.py": "Installation and setup script",
        "test_connection.py": "IB Gateway connection test script",
        "architecture_diagram.py": "Creates visual architecture diagrams",
        "show_structure.py": "Displays project structure (this file)",
        "run_app.bat": "Windows batch file to run the application",
        "README.md": "Project documentation and instructions",
    }
    
    for file, desc in descriptions.items():
        print(f"{file:<25} - {desc}")
    
    print("\n" + "=" * 40)
    print("Next Steps:")
    print("=" * 40)
    print("1. Run 'python setup.py' to install dependencies")
    print("2. Start IB Gateway and enable API access")
    print("3. Run 'python test_connection.py' to test connection")
    print("4. Run 'python main.py' or double-click 'run_app.bat'")
    print("5. Check README.md for detailed instructions")

if __name__ == "__main__":
    main()
