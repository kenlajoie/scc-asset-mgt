@echo off
REM Navigate to project directory
cd /d C:\users\ken\PyCharmProjects\FastApi

REM Activate virtual environment
call .venv\Scripts\activate

REM Start the Uvicorn server
uvicorn AssetMgtApp.main:app --host 0.0.0.0 --port 8004 --reload

REM Pause the terminal so it doesn’t close immediately on error
pause
