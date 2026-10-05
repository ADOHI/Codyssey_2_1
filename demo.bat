@echo off
rem Windows 더블클릭용. 실제 내용은 demo.py (Mac/Linux: python3 demo.py)
chcp 65001 >nul
cd /d "%~dp0"
python demo.py %*
pause
