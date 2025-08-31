#!/bin/bash

# --- Create Conda Environment ---
echo "Creating Conda environment from environment.yml..."
conda env create -f environment.yml

# --- Install system dependency ---
echo "Installing pavucontrol..."
sudo apt update && sudo apt install -y pavucontrol

# --- Script Directories and Files ---
DESKTOP_DIR="$(xdg-user-dir DESKTOP)" || DESKTOP_DIR="$HOME/Desktop"
ENTRY_SCRIPT_SERVER="server.sh"
ENTRY_SCRIPT_OPERATOR="operator.sh"
ENTRY_SCRIPT_ADMIN="admin.sh"
ICON_PATH_SERVER="icon/server.png"
ICON_PATH_OPERATOR="icon/operatore.png"
ICON_PATH_ADMIN="icon/amministratore.png"

# --- Desktop Shortcuts ---
echo "Creating desktop shortcuts..."
mkdir -p "${DESKTOP_DIR}"

create_shortcut() {
    local name="$1"
    local exec_script="$2"
    local icon_path="$3"
    local dest_file="${DESKTOP_DIR}/${name}.desktop"
    local script_dir="script" # Assuming a 'script' subdirectory

    if [ -f "${script_dir}/${exec_script}" ]; then
        chmod +x "${script_dir}/${exec_script}"
    fi

    echo "[Desktop Entry]
Type=Application
Name=${name}
Exec=gnome-terminal -- ${PWD}/${script_dir}/${exec_script}
Icon=${PWD}/${icon_path}
Terminal=true
Categories=Utility;" > "${dest_file}"

    chmod +x "${dest_file}"
    echo "Shortcut created: ${dest_file}"
}

create_shortcut "Server" "${ENTRY_SCRIPT_SERVER}" "${ICON_PATH_SERVER}"
create_shortcut "Operatore" "${ENTRY_SCRIPT_OPERATOR}" "${ICON_PATH_OPERATOR}"
create_shortcut "Admin" "${ENTRY_SCRIPT_ADMIN}" "${ICON_PATH_ADMIN}"

echo "Script completed successfully."

