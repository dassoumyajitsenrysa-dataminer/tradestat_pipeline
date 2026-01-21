@echo off
REM MongoDB Installation Script for Windows
REM Requires Admin Rights

echo.
echo ====================================================
echo  MongoDB Installation for Trade Statistics
echo ====================================================
echo.

REM Check if running as Admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script requires Administrator privileges!
    echo.
    echo Please right-click this script and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Installing MongoDB Community Server...
echo.

REM Try winget first (most modern)
where winget >nul 2>&1
if %errorLevel% equ 0 (
    echo Using Windows Package Manager (winget)...
    winget install MongoDB.Server -e
    echo.
    echo Waiting for installation to complete...
    timeout /t 15 /nobreak
    goto :verify
)

REM Try Chocolatey
where choco >nul 2>&1
if %errorLevel% equ 0 (
    echo Using Chocolatey...
    choco install mongodb-community -y
    goto :verify
)

REM If neither package manager available, guide user to manual installation
echo.
echo Package managers not found. Please install MongoDB manually:
echo.
echo 1. Visit: https://www.mongodb.com/try/download/community
echo 2. Select Windows and download the .msi installer
echo 3. Run the installer with default settings
echo 4. Come back and run this script again
echo.
pause
exit /b 1

:verify
echo.
echo ====================================================
echo Verifying MongoDB Installation
echo ====================================================
echo.

mongod --version
if %errorLevel% equ 0 (
    echo.
    echo SUCCESS! MongoDB is installed.
    echo.
    echo Next steps:
    echo 1. Create data directory: mkdir C:\data\db
    echo 2. Start MongoDB: mongod --dbpath="C:\data\db"
    echo 3. Or install as service: https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/
    echo.
) else (
    echo.
    echo ERROR: MongoDB installation could not be verified.
    echo Please check the installation manually.
    echo.
)

pause
