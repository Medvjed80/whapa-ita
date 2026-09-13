@echo off
cd /d "%~dp0"
python whapa-gui.py
if errorlevel 1 pause
