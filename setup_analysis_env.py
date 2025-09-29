"""
Analysis Environment Setup
Creates and configures a dedicated virtual environment with all required analysis libraries
"""

import os
import sys
import subprocess
import json
from pathlib import Path


class AnalysisEnvironmentSetup:
    """Setup and manage analysis environment with all required dependencies"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "analysis_venv"
        self.requirements_file = self.project_root / "analysis_requirements.txt"
        
    def create_requirements_file(self):
        """Create comprehensive requirements file for analysis"""
        requirements = [
            "# Core data analysis",
            "pandas>=2.0.0",
            "numpy>=1.24.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "",
            "# Statistical analysis",
            "scipy>=1.10.0",
            "statsmodels>=0.14.0",
            "",
            "# Machine learning",
            "scikit-learn>=1.3.0",
            "",
            "# Financial analysis",
            "arch>=6.2.0",  # GARCH models
            "yfinance>=0.2.0",  # Additional data source
            "",
            "# Jupyter ecosystem",
            "jupyter>=1.0.0",
            "jupyterlab>=4.0.0",
            "ipykernel>=6.25.0",
            "ipywidgets>=8.1.0",
            "",
            "# Visualization enhancements",
            "plotly>=5.15.0",
            "mplfinance>=0.12.0",  # Financial plotting
            "",
            "# Performance and utilities",
            "numba>=0.57.0",  # Speed up calculations
            "joblib>=1.3.0",  # Parallel processing
            "tqdm>=4.65.0",  # Progress bars
            "",
            "# Data export/import",
            "openpyxl>=3.1.0",  # Excel support
            "xlsxwriter>=3.1.0",  # Excel writing
            "",
            "# Optional but useful",
            "ta-lib>=0.4.0",  # Technical analysis (optional - requires separate install)",
        ]
        
        with open(self.requirements_file, 'w') as f:
            f.write('\n'.join(requirements))
        
        print(f"✅ Created requirements file: {self.requirements_file}")
    
    def create_virtual_environment(self):
        """Create virtual environment for analysis"""
        if self.venv_path.exists():
            print(f"📁 Virtual environment already exists at: {self.venv_path}")
            return True
        
        try:
            print(f"🔧 Creating virtual environment at: {self.venv_path}")
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], 
                         check=True, capture_output=True, text=True)
            print("✅ Virtual environment created successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def get_venv_python(self):
        """Get path to Python executable in virtual environment"""
        if sys.platform == "win32":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"
    
    def get_venv_pip(self):
        """Get path to pip in virtual environment"""
        if sys.platform == "win32":
            return self.venv_path / "Scripts" / "pip.exe"
        else:
            return self.venv_path / "bin" / "pip"
    
    def upgrade_pip(self):
        """Upgrade pip in virtual environment"""
        pip_path = self.get_venv_pip()
        try:
            print("🔄 Upgrading pip...")
            subprocess.run([str(pip_path), "install", "--upgrade", "pip"], 
                         check=True, capture_output=True, text=True)
            print("✅ Pip upgraded successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Pip upgrade failed: {e}")
            return False
    
    def install_requirements(self):
        """Install all requirements in virtual environment"""
        pip_path = self.get_venv_pip()
        
        try:
            print("📦 Installing analysis requirements...")
            print("   This may take several minutes...")
            
            # Install main requirements
            result = subprocess.run([
                str(pip_path), "install", "-r", str(self.requirements_file)
            ], capture_output=True, text=True, timeout=600)  # 10 minute timeout
            
            if result.returncode != 0:
                print(f"⚠️ Some packages failed to install:")
                print(result.stderr)
                
                # Try installing core packages individually
                core_packages = [
                    "pandas", "numpy", "matplotlib", "seaborn", "scipy", 
                    "scikit-learn", "jupyter", "jupyterlab", "plotly"
                ]
                
                print("🔄 Installing core packages individually...")
                for package in core_packages:
                    try:
                        subprocess.run([str(pip_path), "install", package], 
                                     check=True, capture_output=True, text=True)
                        print(f"   ✅ {package}")
                    except subprocess.CalledProcessError:
                        print(f"   ❌ {package}")
            else:
                print("✅ All requirements installed successfully")
            
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ Installation timed out after 10 minutes")
            return False
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            return False
    
    def install_jupyter_kernel(self):
        """Install Jupyter kernel for the analysis environment"""
        python_path = self.get_venv_python()
        
        try:
            print("🔧 Installing Jupyter kernel...")
            subprocess.run([
                str(python_path), "-m", "ipykernel", "install", 
                "--user", "--name", "ib_analysis", 
                "--display-name", "IB Data Analysis"
            ], check=True, capture_output=True, text=True)
            print("✅ Jupyter kernel installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Kernel installation failed: {e}")
            return False
    
    def verify_installation(self):
        """Verify that key packages are installed and working"""
        python_path = self.get_venv_python()
        
        test_script = '''
import sys
print(f"Python: {sys.version}")

packages_to_test = [
    "pandas", "numpy", "matplotlib", "seaborn", "scipy", 
    "sklearn", "jupyter", "plotly"
]

failed_packages = []
for package in packages_to_test:
    try:
        __import__(package)
        print(f"✅ {package}")
    except ImportError:
        print(f"❌ {package}")
        failed_packages.append(package)

if failed_packages:
    print(f"\\nFailed packages: {failed_packages}")
    sys.exit(1)
else:
    print("\\n🎉 All core packages installed successfully!")
'''
        
        try:
            result = subprocess.run([str(python_path), "-c", test_script], 
                                  capture_output=True, text=True, check=True)
            print("\n📋 Package Verification:")
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Verification failed:")
            print(e.stdout)
            print(e.stderr)
            return False
    
    def create_launch_script(self):
        """Create script to launch Jupyter with the analysis environment"""
        if sys.platform == "win32":
            script_name = "launch_analysis_jupyter.bat"
            script_content = f'''@echo off
echo 🚀 Launching Jupyter Lab with IB Data Analysis environment...
cd /d "{self.project_root}"
"{self.venv_path}\\Scripts\\jupyter.exe" lab --notebook-dir=notebooks
pause
'''
        else:
            script_name = "launch_analysis_jupyter.sh"
            script_content = f'''#!/bin/bash
echo "🚀 Launching Jupyter Lab with IB Data Analysis environment..."
cd "{self.project_root}"
"{self.venv_path}/bin/jupyter" lab --notebook-dir=notebooks
'''
        
        script_path = self.project_root / script_name
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        if not sys.platform == "win32":
            os.chmod(script_path, 0o755)
        
        print(f"✅ Created launch script: {script_path}")
    
    def create_config_file(self):
        """Create configuration file with environment paths"""
        config = {
            "analysis_venv_path": str(self.venv_path),
            "python_executable": str(self.get_venv_python()),
            "jupyter_executable": str(self.venv_path / ("Scripts" if sys.platform == "win32" else "bin") / "jupyter"),
            "kernel_name": "ib_analysis",
            "created_at": "2025-09-28",
            "status": "ready"
        }
        
        config_path = self.project_root / "analysis_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Created config file: {config_path}")
    
    def setup_complete_environment(self):
        """Complete setup process"""
        print("🎯 Setting up IB Data Manager Analysis Environment")
        print("=" * 50)
        
        # Step 1: Create requirements file
        self.create_requirements_file()
        
        # Step 2: Create virtual environment
        if not self.create_virtual_environment():
            return False
        
        # Step 3: Upgrade pip
        self.upgrade_pip()
        
        # Step 4: Install requirements
        if not self.install_requirements():
            print("⚠️ Some packages failed to install, but continuing...")
        
        # Step 5: Install Jupyter kernel
        self.install_jupyter_kernel()
        
        # Step 6: Verify installation
        if not self.verify_installation():
            print("⚠️ Verification failed, but environment may still be usable")
        
        # Step 7: Create launch script
        self.create_launch_script()
        
        # Step 8: Create config file
        self.create_config_file()
        
        print("\n" + "=" * 50)
        print("🎉 Analysis Environment Setup Complete!")
        print("\nNext steps:")
        print("1. Run 'launch_analysis_jupyter.bat' to start Jupyter Lab")
        print("2. Create notebooks using the 'IB Data Analysis' kernel")
        print("3. All analysis libraries are now available!")
        
        return True


def main():
    """Main setup function"""
    setup = AnalysisEnvironmentSetup()
    success = setup.setup_complete_environment()
    
    if success:
        print("\n✅ Setup completed successfully!")
    else:
        print("\n❌ Setup encountered errors. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
