@echo off
REM Soups, Snacks & More - Windows Startup Script
REM Starts both Django backend and React frontend

echo.
echo ======================================
echo   Soups, Snacks ^& More
echo ======================================
echo.
echo Starting servers...
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press Ctrl+C in each window to stop.
echo.

REM Activate virtual environment and start Django in a new window
start "Django Backend" cmd /k "call SSCo\Scripts\activate.bat && python manage.py runserver"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start React frontend in a new window
start "React Frontend" cmd /k "cd frontend && npm start"

echo.
echo Servers starting in separate windows...
echo.
echo Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul

start http://localhost:3000
