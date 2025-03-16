#!/usr/bin/env python
"""
Deployment script for the Fare Calculation Analyzer (FCA) Streamlit app.
This script checks for required dependencies and installs them if needed.
"""

import subprocess
import sys
import os

def check_and_install_dependencies():
    """Check for required dependencies and install them if needed."""
    required_packages = [
        'streamlit',
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'flask',
        'flask-wtf',
        'wtforms',
        'pytest',
        'pytest-cov',
        'tqdm',
        'colorama'
    ]
    
    print("Checking for required dependencies...")
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is not installed. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} has been installed")
    
    print("All required dependencies are installed.")

def check_required_files():
    """Check if all required files exist."""
    required_files = [
        'app.py',
        'enhanced_fca_cleaner.py',
        'fca_cleaner.py',
        'requirements.txt'
    ]
    
    print("Checking for required files...")
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"Warning: The following required files are missing: {', '.join(missing_files)}")
        return False
    else:
        print("All required files are present.")
        return True

def main():
    """Main function to prepare the deployment."""
    print("Preparing deployment for FCA Streamlit app...")
    
    # Check and install dependencies
    check_and_install_dependencies()
    
    # Check required files
    files_exist = check_required_files()
    
    if files_exist:
        print("Deployment preparation complete. You can now run the app with 'streamlit run app.py'")
    else:
        print("Deployment preparation incomplete. Please ensure all required files are present.")

if __name__ == "__main__":
    main() 