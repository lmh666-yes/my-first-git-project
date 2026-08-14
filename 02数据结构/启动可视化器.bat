@echo off
chcp 65001 >nul
cd /d "%~dp0"

set "PYEXE=C:/Users/Administrator/AppData/Local/Python/pythoncore-3.14-64/python.exe"
if not exist "%PYEXE%" set "PYEXE=python"

echo Starting C/C++ Data Structure Visualizer ...
"%PYEXE%" "%~dp0visualizer.py"
if errorlevel 1 (
    echo.
    echo Failed to start. Please make sure Python with tkinter is installed.
    pause
)
