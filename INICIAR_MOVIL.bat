@echo off
title SERVIDOR MOVIL - IA LOTERIAS
color 0B
cd /d "%~dp0"
set "PY_EXE=%LOCALAPPDATA%\Programs\Python\pythoncore-3.14-64\python.exe"
if exist "%PY_EXE%" (
    "%PY_EXE%" servidor_movil.py
) else (
    py servidor_movil.py
)
pause