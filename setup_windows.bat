@echo off
setlocal enabledelayedexpansion

REM === Impostazioni ===
set VENV_DIR=.venv
set ENTRY_SCRIPT_SERVER=script\server.bat
set ENTRY_SCRIPT_OPERATOR=script\operator.bat
set ENTRY_SCRIPT_ADMIN=script\admin.bat
set FONT_SRC_DIR=fonts
set FONT_NAME=*.ttf
set FONT_DEST=%WINDIR%\Fonts

set ICON_PATH_SERVER=icon\server.ico
set ICON_PATH_OPERATOR=icon\operatore.ico
set ICON_PATH_ADMIN=icon\amministratore.ico

set SHORTCUT_SERVER=%USERPROFILE%\Desktop\server.lnk
set SHORTCUT_OPERATOR=%USERPROFILE%\Desktop\operatore.lnk
set SHORTCUT_ADMIN=%USERPROFILE%\Desktop\admin.lnk

REM === Ambiente virtuale ===
IF NOT EXIST %VENV_DIR% (
    echo Creazione dell'ambiente virtuale...
    python -m venv %VENV_DIR%
)

call %VENV_DIR%\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

REM === Installazione font ===
echo Installazione del font...
for %%f in (%FONT_SRC_DIR%\%FONT_NAME%) do (
    copy "%%f" "%FONT_DEST%" >nul
    reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "%%~nxf (TrueType)" /t REG_SZ /d "%%~nxf" /f >nul 2>&1
)

if %errorlevel% neq 0 (
    echo [!] Font copiato, ma non registrato (forse servono permessi amministrativi).
) else (
    echo Font installato in %FONT_DEST%.
)

REM === Collegamenti sul desktop ===
set PYTHON_PATH=%CD%\%VENV_DIR%\Scripts\python.exe

REM Collegamento Server
powershell -Command "$s = (New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT_SERVER%'); $s.TargetPath = '%PYTHON_PATH%'; $s.Arguments = '%CD%\%ENTRY_SCRIPT_SERVER%'; $s.IconLocation = '%CD%\%ICON_PATH_SERVER%'; $s.WindowStyle = 1; $s.Save()"

REM Collegamento Operatore
powershell -Command "$s = (New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT_OPERATOR%'); $s.TargetPath = '%PYTHON_PATH%'; $s.Arguments = '%CD%\%ENTRY_SCRIPT_OPERATOR%'; $s.IconLocation = '%CD%\%ICON_PATH_OPERATOR%'; $s.WindowStyle = 1; $s.Save()"

REM Collegamento Admin
powershell -Command "$s = (New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT_ADMIN%'); $s.TargetPath = '%PYTHON_PATH%'; $s.Arguments = '%CD%\%ENTRY_SCRIPT_ADMIN%'; $s.IconLocation = '%CD%\%ICON_PATH_ADMIN%'; $s.WindowStyle = 1; $s.Save()"

echo Collegamenti creati sul desktop.

endlocal
