#!/bin/bash

# === Impostazioni ===
ENTRY_SCRIPT_TEST="test.sh"
DESKTOP_FILE_TEST="$HOME/Scrivania/test.desktop"
ICON_PATH_TEST="icon/test.png"

# === Collegamento sul desktop ===
echo "[Desktop Entry]
Type=Application
Name=Test
Exec=$(pwd)/script/$ENTRY_SCRIPT_TEST

Icon=$(pwd)/$ICON_PATH_TEST
Terminal=true" > "$DESKTOP_FILE_TEST"

chmod +x "$(pwd)/script/$ENTRY_SCRIPT_TEST"
chmod +x "$DESKTOP_FILE_TEST"
echo "Collegamento creato sul desktop: $DESKTOP_FILE_TEST"