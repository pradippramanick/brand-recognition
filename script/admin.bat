@echo off
setlocal enabledelayedexpansion

REM === Impostazioni ===
set VENV_DIR=.venv
set PROGRAM=gui.py

REM === Ambiente virtuale ===
cd %USERPROFILE%\Desktop\brand
call %VENV_DIR%\Scripts\activate.bat
cd src\amministratore

REM Esegue il programma Python
..\..\%VENV_DIR%\Scripts\python.exe %PROGRAM%

endlocal
pause