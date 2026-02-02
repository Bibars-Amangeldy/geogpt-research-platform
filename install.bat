@echo off
echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║   🌍 GeoGPT Research Platform                                 ║
echo ║   State-of-the-Art Geospatial AI                              ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.10+
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18+
    pause
    exit /b 1
)

echo ✅ Python and Node.js detected
echo.

:: Create Python virtual environment if it doesn't exist
if not exist "backend\venv" (
    echo 📦 Creating Python virtual environment...
    cd backend
    python -m venv venv
    cd ..
)

:: Activate virtual environment and install dependencies
echo 📦 Installing Python dependencies...
cd backend
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
cd ..

:: Install Node.js dependencies
echo 📦 Installing Node.js dependencies...
cd frontend
call npm install --silent
cd ..

echo.
echo ✅ Installation complete!
echo.
echo To start the application:
echo   1. Start backend:  cd backend ^& venv\Scripts\activate ^& python main.py
echo   2. Start frontend: cd frontend ^& npm run dev
echo.
echo Or use: start-servers.bat
echo.
pause
