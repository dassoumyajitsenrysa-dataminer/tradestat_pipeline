#!/usr/bin/env python
"""
MongoDB Installation Helper for Windows
Automatically installs MongoDB using available package managers
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    try:
        print(f"\n{description}...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def check_command(cmd):
    """Check if a command exists"""
    result = subprocess.run(f"where {cmd}", shell=True, capture_output=True)
    return result.returncode == 0

def install_with_winget():
    """Install MongoDB using Windows Package Manager"""
    if not check_command("winget"):
        return False
    
    print("✓ Windows Package Manager found")
    return run_command(
        "winget install MongoDB.Server -e",
        "Installing MongoDB with winget"
    )

def install_with_chocolatey():
    """Install MongoDB using Chocolatey"""
    if not check_command("choco"):
        return False
    
    print("✓ Chocolatey found")
    return run_command(
        "choco install mongodb-community -y",
        "Installing MongoDB with Chocolatey"
    )

def verify_installation():
    """Verify MongoDB was installed"""
    print("\n" + "=" * 60)
    print("Verifying MongoDB Installation")
    print("=" * 60)
    
    if check_command("mongod"):
        result = subprocess.run("mongod --version", shell=True, capture_output=True, text=True)
        print(f"\n✓ MongoDB installed successfully!")
        print(f"\n{result.stdout}")
        return True
    else:
        print("\n✗ MongoDB not found in PATH")
        return False

def create_data_directory():
    """Create MongoDB data directory"""
    try:
        data_dir = Path("C:/data/db")
        data_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Data directory created: {data_dir}")
        return True
    except Exception as e:
        print(f"⚠ Could not create data directory: {str(e)}")
        return False

def main():
    """Main installation routine"""
    
    print("\n" + "=" * 60)
    print("  MongoDB Installation Helper")
    print("=" * 60)
    print()
    
    # Check if already installed
    if check_command("mongod"):
        print("✓ MongoDB is already installed!")
        verify_installation()
        print("\nYou can now run the platform!")
        return 0
    
    # Try installation methods
    print("Attempting to install MongoDB...\n")
    
    if install_with_winget():
        create_data_directory()
        if verify_installation():
            print("\n" + "=" * 60)
            print("SUCCESS!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Start MongoDB:")
            print("   mongod --dbpath=\"C:\\data\\db\"")
            print("\n2. Or run MongoDB as a service (see MongoDB documentation)")
            print("\n3. In another terminal, run:")
            print("   python verify_setup.py")
            print("   python quick_start.py")
            return 0
    
    if install_with_chocolatey():
        create_data_directory()
        if verify_installation():
            return 0
    
    # If automatic installation failed
    print("\n" + "=" * 60)
    print("Automatic Installation Failed")
    print("=" * 60)
    print("\nPlease install MongoDB manually:")
    print("\n1. Download: https://www.mongodb.com/try/download/community")
    print("2. Select: Windows, .msi installer")
    print("3. Run installer with default settings")
    print("4. Restart terminal and try again")
    print("\nOr use this direct link:")
    print("https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-7.0.6-signed.msi")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
