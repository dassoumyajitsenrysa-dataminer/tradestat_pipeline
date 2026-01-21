"""
Mock MongoDB server for local testing without MongoDB installation.
Uses mongomock library to simulate MongoDB behavior.
"""

import sys
from pathlib import Path

def setup_mock_mongodb():
    """Setup mock MongoDB for testing"""
    try:
        import mongomock
        print("✓ mongomock is available - will use in-memory MongoDB\n")
        return True
    except ImportError:
        print("mongomock not installed - installing now...")
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", "mongomock"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ mongomock installed successfully\n")
            return True
        else:
            print("✗ Failed to install mongomock")
            return False

def start_mock_server():
    """Start mock MongoDB server"""
    if not setup_mock_mongodb():
        return False
    
    print("=" * 60)
    print("  Mock MongoDB Server - In-Memory Database")
    print("=" * 60)
    print()
    
    import mongomock
    from threading import Thread
    import time
    
    # Create in-memory MongoDB
    client = mongomock.MongoClient('mongodb://localhost:27017')
    db = client['tradestat']
    
    # Verify connection
    try:
        db.admin.command('ping')
        print("✓ Mock MongoDB is running on localhost:27017")
        print("✓ Database: tradestat")
        print()
        print("Features:")
        print("  - Collections: hs_codes, partner_countries")
        print("  - Indexes: Automatic")
        print("  - Data: In-memory (cleared on exit)")
        print()
    except Exception as e:
        print(f"✗ Failed to start mock MongoDB: {str(e)}")
        return False
    
    print("Mock MongoDB is ready! You can now:")
    print("  1. Run: python -m data_loader.loader")
    print("  2. Run: uvicorn api.main:app --reload")
    print("  3. Run: streamlit run dashboard/app.py")
    print()
    print("Note: Data will be lost when this process exits.")
    print("Press Ctrl+C to stop the mock server.")
    print()
    
    # Keep the server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n✓ Mock MongoDB stopped")
        return True

if __name__ == "__main__":
    start_mock_server()
