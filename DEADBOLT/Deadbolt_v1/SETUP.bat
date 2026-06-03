@echo off
title Deadbolt Endpoint Shield Setup
echo ====================================================
echo    Deadbolt Endpoint Shield v1.0 - Setup
echo ====================================================
echo.
echo Starting with animated pixel lock intro...
echo.

cd /d "%~dp0"
python LAUNCHER.py

if errorlevel 1 (
    echo.
    echo Launching wizard directly...
    python PROFESSIONAL_WIZARD.py
    pause
)
