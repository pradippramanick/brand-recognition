@echo off
SETLOCAL ENABLEEXTENSIONS
cd /d %~dp0

:: === Impostazioni ===
set VENV_DIR=.venv
set FONTFILE=fonts\InterVariable.ttf
set FONTNAME=InterVariable.ttf
set FONTDEST=%WINDIR%\Fonts
set DESKTOP=%USERPROFILE%\Desktop

:: === Script e icone ===
set ENTRY_SCRIPT_SERVER=script\server.bat
set ENTRY_SCRIPT_OPERATOR=script\operator.bat
set ENTRY_SCRIPT_ADMIN=script\admin.bat
set ICON_SERVER=icon\server.ico
set ICON_OPERATOR=icon\operatore.ico
set ICON_ADMIN=icon\amministratore.ico

:: === Controllo file
if not exist requirements.txt (
    echo ERRORE: requirements.txt non trovato!
    pause
    exit /b
)

if not exist fonts\*.ttf (
    echo ERRORE: Nessun file TTF trovato nella cartella fonts\
    pause
    exit /b
)

:: === Creazione ambiente virtuale ===
if not exist %VENV_DIR% (
    echo Creazione ambiente virtuale...
    python -m venv %VENV_DIR%
)

:: Aggiorna pip
%VENV_DIR%\Scripts\python.exe -m pip install --upgrade pip

:: Installa requirements
if exist requirements.txt (
    echo Installazione pacchetti...
    for /f "delims=" %%i in (requirements.txt) do (
        echo Installando %%i...
        %VENV_DIR%\Scripts\python.exe -m pip install %%i
        if errorlevel 1 (
            echo ERRORE durante l'installazione di %%i
            pause
            exit /b
        )
    )
) else (
    echo ERRORE: requirements.txt non trovato
    pause
    exit /b
)

:: Copia il font nella cartella Fonts di sistema
copy %FONTFILE% %FONTDEST% >nul

:: Registra il font nel registro di sistema
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "Inter Variable (TrueType)" /t REG_SZ /d "%FONTNAME%" /f

echo Font installato correttamente.

:: Collegamenti
echo Creazione scorciatoie sul Desktop...

powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%DESKTOP%\Server.lnk');$s.TargetPath='%CD%\%ENTRY_SCRIPT_SERVER%';$s.IconLocation='%CD%\%ICON_SERVER%';$s.Save()"
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%DESKTOP%\Operatore.lnk');$s.TargetPath='%CD%\%ENTRY_SCRIPT_OPERATOR%';$s.IconLocation='%CD%\%ICON_OPERATOR%';$s.Save()"
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%DESKTOP%\Admin.lnk');$s.TargetPath='%CD%\%ENTRY_SCRIPT_ADMIN%';$s.IconLocation='%CD%\%ICON_ADMIN%';$s.Save()"

echo Setup completato con successo.
pause
ENDLOCAL
