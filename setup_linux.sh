#!/bin/bash

# === Impostazioni ===
VENV_DIR=".venv"
ENTRY_SCRIPT_SERVER="server.sh"
ENTRY_SCRIPT_OPERATOR="operator.sh"
ENTRY_SCRIPT_ADMIN="admin.sh"
FONT_SRC_DIR="fonts"
FONT_DEST="$HOME/.local/share/fonts"
DESKTOP_FILE_SERVER="$HOME/Scrivania/server.desktop"
DESKTOP_FILE_OPERATOR="$HOME/Scrivania/operatore.desktop"
DESKTOP_FILE_ADMIN="$HOME/Scrivania/admin.desktop"
ICON_PATH_SERVER="icon/server.png"
ICON_PATH_OPERATOR="icon/operatore.png"
ICON_PATH_ADMIN="icon/amministratore.png"

# === Ambiente virtuale ===
if [ ! -d "$VENV_DIR" ]; then
    echo "Creazione dell'ambiente virtuale..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

# === Installazione font ===
mkdir -p "$FONT_DEST"
cp "$FONT_SRC_DIR"/*.ttf "$FONT_DEST"
fc-cache -f -v
echo "Font installato in $FONT_DEST"

# === Collegamento sul desktop per server ===
echo "[Desktop Entry]
Type=Application
Name=Server
Exec=$(pwd)/script/$ENTRY_SCRIPT_SERVER

Icon=$(pwd)/$ICON_PATH_SERVER
Terminal=true" > "$DESKTOP_FILE_SERVER"

chmod +x "$(pwd)/script/$ENTRY_SCRIPT_SERVER"
chmod +x "$DESKTOP_FILE_SERVER"
echo "Collegamento creato sul desktop: $DESKTOP_FILE_SERVER"

# === Collegamento sul desktop per operatore ===
echo "[Desktop Entry]
Type=Application
Name=Operatore
Exec=$(pwd)/script/$ENTRY_SCRIPT_OPERATOR
Icon=$(pwd)/$ICON_PATH_OPERATOR
Terminal=false" > "$DESKTOP_FILE_OPERATOR"

chmod +x "$(pwd)/script/$ENTRY_SCRIPT_OPERATOR"
chmod +x "$DESKTOP_FILE_OPERATOR"
echo "Collegamento creato sul desktop: $DESKTOP_FILE_OPERATOR"

# === Collegamento sul desktop per amministratore ===
echo "[Desktop Entry]
Type=Application
Name=Admin
Exec=$(pwd)/script/$ENTRY_SCRIPT_ADMIN
Icon=$(pwd)/$ICON_PATH_ADMIN
Terminal=false" > "$DESKTOP_FILE_ADMIN"

chmod +x "$(pwd)/script/$ENTRY_SCRIPT_ADMIN"
chmod +x "$DESKTOP_FILE_ADMIN"
echo "Collegamento creato sul desktop: $DESKTOP_FILE_ADMIN"