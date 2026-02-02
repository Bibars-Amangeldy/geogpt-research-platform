@echo off
echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║   🌍 Starting GeoGPT Research Platform                        ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

:: Start backend in new window
start "GeoGPT Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat 2>nul || echo No venv, using system Python && python main.py"

:: Wait a moment for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend in new window
start "GeoGPT Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo 🚀 Servers starting...
echo.
echo    Backend:  http://localhost:8000
echo    Frontend: http://localhost:3000
echo    API Docs: http://localhost:8000/docs
echo.
echo Press any key to open the application in your browser...
pause >nul

:: Open in default browser
start http://localhost:3000
