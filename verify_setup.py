#!/usr/bin/env python
"""
Verification script to check if all components are installed and configured correctly.
"""

import sys
import importlib
from pathlib import Path
import subprocess

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name.lower()
    
    try:
        importlib.import_module(import_name)
        print(f"✓ {package_name}")
        return True
    except ImportError:
        print(f"✗ {package_name} - NOT INSTALLED")
        return False

def check_file(file_path):
    """Check if a file exists"""
    if Path(file_path).exists():
        print(f"✓ {file_path}")
        return True
    else:
        print(f"✗ {file_path} - MISSING")
        return False

def check_mongodb():
    """Check MongoDB connection"""
    try:
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        print("✓ MongoDB is running and responsive")
        return True
    except Exception as e:
        print(f"✗ MongoDB - {str(e)}")
        return False

def main():
    """Main verification routine"""
    
    print_header("Trade Statistics Platform - Verification")
    
    all_checks = True
    
    # Check Python version
    print("1. Python Environment")
    print("-" * 60)
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 9:
        print(f"✓ Python {python_version.major}.{python_version.minor}")
    else:
        print(f"✗ Python {python_version.major}.{python_version.minor} (requires 3.9+)")
        all_checks = False
    print()
    
    # Check packages
    print("2. Required Packages")
    print("-" * 60)
    
    packages = [
        ("FastAPI", "fastapi"),
        ("Uvicorn", "uvicorn"),
        ("PyMongo", "pymongo"),
        ("Pydantic", "pydantic"),
        ("Streamlit", "streamlit"),
        ("Plotly", "plotly"),
        ("Pandas", "pandas"),
        ("Requests", "requests"),
        ("APScheduler", "apscheduler"),
    ]
    
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_checks = False
    print()
    
    # Check optional packages
    print("3. Optional Packages")
    print("-" * 60)
    
    optional_packages = [
        ("Playwright", "playwright"),
        ("Python Dotenv", "dotenv"),
    ]
    
    for package_name, import_name in optional_packages:
        check_package(package_name, import_name)
    print()
    
    # Check files
    print("4. Project Files")
    print("-" * 60)
    
    files = [
        "api/__init__.py",
        "api/main.py",
        "api/database.py",
        "api/models.py",
        "data_loader/__init__.py",
        "data_loader/loader.py",
        "dashboard/__init__.py",
        "dashboard/app.py",
        "quick_start.py",
        "requirements.txt",
        "SETUP_MONGODB_FASTAPI.md",
        "ARCHITECTURE_MONGODB_FASTAPI.md",
    ]
    
    project_root = Path(__file__).parent
    for file in files:
        if not check_file(project_root / file):
            all_checks = False
    print()
    
    # Check directories
    print("5. Project Directories")
    print("-" * 60)
    
    directories = [
        "api",
        "data_loader",
        "dashboard",
        "data",
        "data/processed",
        "data/raw",
    ]
    
    for dir in directories:
        dir_path = project_root / dir
        if dir_path.exists() and dir_path.is_dir():
            print(f"✓ {dir}/")
        else:
            print(f"✗ {dir}/ - MISSING")
            if "data" not in dir:  # Data dirs are optional if no data yet
                all_checks = False
    print()
    
    # Check MongoDB
    print("6. External Services")
    print("-" * 60)
    
    if not check_mongodb():
        all_checks = False
    print()
    
    # Summary
    print_header("Verification Summary")
    
    if all_checks:
        print("✅ ALL CHECKS PASSED!")
        print("\nYou can now run the platform:")
        print("  python quick_start.py")
        print("\nOr manually start services:")
        print("  Terminal 1: uvicorn api.main:app --reload --port 8000")
        print("  Terminal 2: streamlit run dashboard/app.py")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("\nPlease fix the issues above before continuing.")
        print("\nTo install dependencies:")
        print("  pip install -r requirements.txt")
        print("\nTo start MongoDB:")
        print("  net start MongoDB")
        print("  OR: mongod --dbpath=\"C:\\data\\db\"")
        print("  OR: docker run -d -p 27017:27017 mongo")
        return 1

if __name__ == "__main__":
    sys.exit(main())
