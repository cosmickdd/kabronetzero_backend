@echo off
REM Quick Start Script - Kabro NetZero Auth API (Windows)
REM Run this to get started locally

setlocal enabledelayedexpansion

echo ======================================
echo Kabro NetZero - Auth API Quick Start
echo ======================================
echo.

REM Step 1: Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    exit /b 1
)
python --version
echo.

REM Step 2: Create virtual environment
echo [2/5] Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

REM Activate venv
call venv\Scripts\activate.bat

REM Step 3: Install dependencies
echo [3/5] Installing dependencies...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Step 4: Setup environment
echo [4/5] Setting up environment...
if not exist ".env" (
    (
        echo DEBUG=True
        echo SECRET_KEY=dev-secret-key-change-in-production
        echo MONGODB_URI=mongodb://localhost:27017/kabro_netzero_db
        echo ALLOWED_HOSTS=localhost,127.0.0.1
    ) > .env
    echo [OK] .env file created
    echo     Edit .env to configure MongoDB connection
) else (
    echo [OK] .env file already exists
)
echo.

REM Step 5: Summary
echo [5/5] Setup complete!
echo.
echo ==================================================
echo API Server: http://localhost:8000
echo API Docs:   http://localhost:8000/v1/
echo Health:     http://localhost:8000/health/
echo ==================================================
echo.
echo To start the server, run:
echo   python manage.py runserver
echo.
echo To test the API:
echo   curl http://localhost:8000/health/
echo.
echo For more info, see:
echo   - AUTH_ENDPOINTS_SUMMARY.md (quick reference)
echo   - AUTH_API_DOCUMENTATION.md (full reference)
echo   - DEPLOYMENT_GUIDE.md (setup and deployment)
echo.

REM Optional: Run migrations
set /p runmig="Run migrations now? (y/n): "
if /i "%runmig%"=="y" (
    echo Running migrations...
    python manage.py migrate --noinput
    echo [OK] Migrations complete
    
    set /p seedroles="Seed roles and permissions? (y/n): "
    if /i "%seedroles%"=="y" (
        python manage.py seed_roles_permissions
        echo [OK] Roles and permissions seeded
    )
)

echo.
echo Ready to go! 🚀
echo.
pause
