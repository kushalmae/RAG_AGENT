@echo off
echo 🚀 Starting RAG Q&A Streamlit App
echo ===================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist streamlit_app.py (
    echo ❌ streamlit_app.py not found
    echo Please run this script from the RAG_AGENT directory
    pause
    exit /b 1
)

REM Check if API key is set
if "%OPENAI_API_KEY%"=="" (
    echo ⚠️  Warning: OPENAI_API_KEY environment variable not set
    echo Please set your OpenAI API key:
    echo   set OPENAI_API_KEY=your_api_key_here
    echo Or create a .env file with OPENAI_API_KEY=your_api_key_here
    echo.
    pause
)

echo 🌐 Starting Streamlit app...
echo The app will open in your default web browser
echo Press Ctrl+C to stop the server
echo.

streamlit run streamlit_app.py

pause 