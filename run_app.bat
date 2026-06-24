@echo off
title SageAI - AI Assistant
cd /d "%~dp0"

if "%GEMINI_API_KEY%"=="" (
    echo No Gemini API key found for this session.
    echo Get a free one at https://aistudio.google.com/apikey
    echo.
    set /p GEMINI_API_KEY=Paste your Gemini API key here and press Enter (or just press Enter to skip and use offline mode):
)

start "" http://127.0.0.1:5000
python app.py
pause
