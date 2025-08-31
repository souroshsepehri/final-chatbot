@echo off
echo Starting Semantic Search Demo...
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Checking dependencies...
pip show numpy >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Checking environment configuration...
if not exist ".env" (
    echo WARNING: .env file not found
    echo Please copy config.env.example to .env and add your OpenAI API key
    echo.
    echo Example .env content:
    echo OPENAI_API_KEY=your_actual_api_key_here
    echo EMBEDDING_MODEL=text-embedding-3-small
    echo SEMANTIC_TOP_K=3
    echo SEMANTIC_THRESHOLD=0.82
    echo.
    pause
)

echo.
echo Starting semantic search demo...
python demo_semantic.py

echo.
echo Demo completed. Press any key to exit...
pause >nul







