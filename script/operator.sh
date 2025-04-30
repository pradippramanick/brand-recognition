#!/bin/bash

# === Impostazioni ===
VENV_DIR=".venv"
PROGRAM="gui.py"

# === Ambiente virtuale ===
cd
cd Scrivania
source brand/$VENV_DIR/bin/activate

# === Working directory ===
cd brand/src/operatore

# Esegue il programma Python
python3 $PROGRAM