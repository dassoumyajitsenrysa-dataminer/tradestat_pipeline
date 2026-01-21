@echo off
REM Quick start script for Trade Statistics Platform
REM Starts MongoDB, FastAPI, and Streamlit in order

echo.
echo ====================================================
echo  Trade Statistics Platform - Quick Start
echo ====================================================
echo.

REM Check if MongoDB is running
echo Checking MongoDB connection...
python -c "from api.database import get_db; db = get_db(); print('✓ MongoDB is healthy' if db.health_check() else '✗ MongoDB connection failed')" 2>nul
if %ERRORLEVEL% neq 0 (
    echo.
    echo ✗ MongoDB is not running!
    echo Please start MongoDB first:
    echo   Option 1: net start MongoDB
    echo   Option 2: mongod --dbpath="C:\data\db"
    echo.
    pause
    exit /b 1
)

echo ✓ MongoDB is running
echo.

REM Load data
echo ====================================================
echo Loading data into MongoDB...
echo ====================================================
echo.
python -m data_loader.loader
echo.

REM Start FastAPI
echo ====================================================
echo Starting FastAPI server on http://localhost:8000
echo ====================================================
echo.
echo Starting in a new window...
start cmd /k "uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait for FastAPI to start
timeout /t 3 /nobreak

REM Check FastAPI health
echo Checking FastAPI health...
python -c "
import requests
import time
for i in range(10):
    try:
        r = requests.get('http://localhost:8000/health', timeout=2)
        if r.status_code == 200:
            print('✓ FastAPI is healthy')
            exit(0)
    except:
        pass
    time.sleep(1)
print('✗ FastAPI health check failed')
exit(1)
" 2>nul

if %ERRORLEVEL% neq 0 (
    echo.
    echo ✗ FastAPI failed to start
    pause
    exit /b 1
)

echo.

REM Start Streamlit
echo ====================================================
echo Starting Streamlit dashboard on http://localhost:8501
echo ====================================================
echo.
streamlit run dashboard/app.py

pause
