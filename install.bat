@echo off
REM Soups, Snacks & More - Windows Installation Script
REM Prerequisites: Python 3.10+, Node.js 18+

echo.
echo ======================================
echo   Soups, Snacks ^& More - Installer
echo ======================================
echo.

REM Check Python
echo Checking prerequisites...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is required but not installed.
    echo   Install from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo √ Python found

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo X Node.js is required but not installed.
    echo   Install from: https://nodejs.org/
    pause
    exit /b 1
)
echo √ Node.js found

REM Check npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo X npm is required but not installed.
    pause
    exit /b 1
)
echo √ npm found

echo.
echo Creating Python virtual environment...
python -m venv SSCo

echo Activating virtual environment...
call SSCo\Scripts\activate.bat

echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Installing frontend dependencies...
cd frontend
call npm install
cd ..

echo.
echo Setting up database...
python manage.py migrate

echo.
echo ======================================
echo   Installation Complete!
echo ======================================
echo.
echo Next steps:
echo.
echo 1. Seed demo data (optional):
echo    python seed_demo_data.py
echo.
echo 2. Or create your own admin user:
echo    python manage.py createsuperuser
echo.
echo 3. Start the application:
echo    setup.bat
echo.
echo 4. Open in browser:
echo    http://localhost:3000
echo.
echo Demo credentials (if seeded):
echo    admin / admin123
echo    operator / operator123
echo    cook / cook123
echo.
pause
