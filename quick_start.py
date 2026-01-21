#!/usr/bin/env python
"""
Quick start script for Trade Statistics Platform
Starts MongoDB (check), FastAPI, and Streamlit in sequence
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def check_mongodb():
    """Check if MongoDB is running and healthy"""
    print("Checking MongoDB connection...")
    try:
        from api.database import get_db
        db = get_db()
        if db.health_check():
            print("✓ MongoDB is healthy and running\n")
            return True
        else:
            print("✗ MongoDB connection failed\n")
            return False
    except Exception as e:
        print(f"✗ MongoDB check failed: {str(e)}\n")
        return False


def load_data():
    """Load data into MongoDB"""
    print_header("Loading Data into MongoDB")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "data_loader.loader"],
            cwd=Path(__file__).parent,
            capture_output=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"✗ Data loading failed: {str(e)}\n")
        return False


def start_fastapi():
    """Start FastAPI server"""
    print_header("Starting FastAPI Backend (Port 8000)")
    print("Starting FastAPI in background...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", 
             "api.main:app", 
             "--host", "0.0.0.0", 
             "--port", "8000",
             "--reload"],
            cwd=Path(__file__).parent
        )
        
        # Wait for FastAPI to start
        print("Waiting for FastAPI to initialize...")
        for i in range(15):
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    print("✓ FastAPI is healthy and running\n")
                    return process
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(1)
        
        print("✗ FastAPI health check failed\n")
        process.terminate()
        return None
    
    except Exception as e:
        print(f"✗ Failed to start FastAPI: {str(e)}\n")
        return None


def start_streamlit():
    """Start Streamlit dashboard"""
    print_header("Starting Streamlit Dashboard (Port 8501)")
    print("Opening dashboard in browser...")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", 
             "dashboard/app.py"],
            cwd=Path(__file__).parent
        )
    except Exception as e:
        print(f"✗ Failed to start Streamlit: {str(e)}\n")


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("  Trade Statistics Platform - Quick Start")
    print("=" * 60)
    
    # Step 1: Check MongoDB
    print_header("Step 1: Verifying MongoDB")
    if not check_mongodb():
        print("Please ensure MongoDB is running:")
        print("  Option 1: Start the MongoDB service")
        print("  Option 2: Run: mongod --dbpath=\"C:\\data\\db\"")
        print("  Option 3: Use Docker: docker run -d -p 27017:27017 mongo")
        print("\nAborting startup.\n")
        sys.exit(1)
    
    # Step 2: Load data
    print_header("Step 2: Loading Data")
    if not load_data():
        print("Data loading encountered errors, but continuing...\n")
    
    # Step 3: Start FastAPI
    print_header("Step 3: Starting FastAPI")
    fastapi_process = start_fastapi()
    if not fastapi_process:
        print("Failed to start FastAPI. Please check the error above.")
        sys.exit(1)
    
    # Step 4: Start Streamlit
    print_header("Step 4: Starting Streamlit Dashboard")
    try:
        start_streamlit()
    except KeyboardInterrupt:
        print("\n\nShutting down services...")
        fastapi_process.terminate()
        fastapi_process.wait(timeout=5)
    except Exception as e:
        print(f"\n\nError: {str(e)}")
        fastapi_process.terminate()
        fastapi_process.wait(timeout=5)


if __name__ == "__main__":
    main()
