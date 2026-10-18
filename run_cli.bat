@echo off
title Python Timer Pro (CLI Terminal)
python cli_timer.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    pause
)
