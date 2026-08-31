@echo off
title SHNEYDER IA PRO - VERIFICADO
color 0B
cd /d "%~dp0"

where py >nul 2>&1
if %errorlevel%==0 (
    py servidor_movil.py
) else (
    python servidor_movil.py
)
pause
