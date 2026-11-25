@echo off
REM AI Virtual Gym Trainer - Local Run Script (Windows)
REM Usage: run_local.bat [enhanced^|original^|dev]

set APP_MODE=%~1
if "%APP_MODE%"=="" set APP_MODE=enhanced

echo 🏋️ AI Virtual Gym Trainer - Local Runner
echo =========================================
echo Mode: %APP_MODE%
echo.

REM Check Python version
python --version

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip > nul 2>&1

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Run the appropriate app
if "%APP_MODE%"=="enhanced" (
    echo Starting ENHANCED app on http://localhost:8501
    streamlit run streamlit_app_enhanced.py --server.port=8501
) else if "%APP_MODE%"=="original" (
    echo Starting ORIGINAL app on http://localhost:8501
    streamlit run streamlit_app.py --server.port=8501
) else if "%APP_MODE%"=="dev" (
    echo Starting DEVELOPMENT mode with hot reload on http://localhost:8502
    set STREAMLIT_SERVER_RUN_ON_SAVE=true
    streamlit run streamlit_app_enhanced.py --server.port=8502
) else (
    echo Unknown mode: %APP_MODE%
    echo Usage: run_local.bat [enhanced^|original^|dev]
    exit /b 1
)