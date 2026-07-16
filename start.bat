@echo off
title OrchestratorUI
echo ===================================================
echo               Starting OrchestratorUI
echo ===================================================
echo.

echo [1/2] Checking and installing Python dependencies...
pip install -q fastapi uvicorn websockets psutil pynvml

echo.
echo [2/2] Launching the FastAPI Server...
echo.
echo Dashboard will be available at: http://localhost:8000/static/index.html
echo.

uvicorn main:app --host 0.0.0.0 --port 8000

pause
