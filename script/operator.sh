#!/bin/bash

# Percorso del progetto
PROJECT_DIR="$HOME/brand-recognition-fixed"

# Carica Conda
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate totaro

# Vai nella cartella dell'operatore
cd "$PROJECT_DIR/src/operatore"

# Esegui il file Python
python gui.py

# Mantieni il terminale aperto
echo
read -p "Premi invio per chiudere..."

