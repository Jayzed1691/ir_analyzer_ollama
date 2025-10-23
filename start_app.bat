@echo off
echo Starting IR Sentiment Analyzer...
echo ================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Check if OPENAI_API_KEY is set
if "%OPENAI_API_KEY%"=="" (
    echo WARNING: OPENAI_API_KEY environment variable is not set
    echo Please set it with: set OPENAI_API_KEY=your-api-key
    echo.
)

REM Create data directory
if not exist "data\uploads\" mkdir data\uploads

REM Start backend
echo Starting backend API on http://localhost:8000...
start /B python backend\main.py

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting frontend UI on http://localhost:8501...
start /B streamlit run frontend\app.py

echo.
echo ================================
echo IR Sentiment Analyzer is running!
echo Frontend: http://localhost:8501
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop all services
echo ================================
echo.

REM Keep window open
pause

