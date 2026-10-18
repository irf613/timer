@echo off
title Python Timer Pro (GUI)
echo Membuka Python Timer Pro...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Terjadi kesalahan saat menjalankan aplikasi.
    pause
)
