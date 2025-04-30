# Setup del progetto

Questo documento fornisce le istruzioni per configurare il progetto su **Linux** e **Windows**.

## **Setup su Linux**

### 1. **Clonare il repository**

Se non l'hai già fatto, clona il repository nella cartella desiderata:

```bash
git clone https://github.com/Francescasba/brand.git
cd brand
```

### 2. **Eseguire lo script di setup**

Aggiungi i permessi di esecuzione per lo script di setup (setup_linux.sh) e successivamente eseguilo:

```bash
chmod +x setup_linux.sh
./setup_linux.sh
```

Verranno creati i collegamenti sul desktop per Server, Operatore, e Amministratore. L'operazione potrebbe richiedere un po' di tempo.

### 3. **Eseguire il programma**

Ora puoi avviare il programma facendo doppio clic sull'icona corrispondente sul desktop (Server, Operatore o Amministratore).

### **Considerazioni aggiuntive**

Se lo script di setup non funziona correttamente, verifica che il sistema abbia i pacchetti necessari come python3, pip, e fc-cache per la gestione dei font.

## **Setup su Windows**
### 1. **Clonare il repository**

Se non l'hai già fatto, clona il repository nella cartella desiderata:

```bash
git clone https://github.com/Francescasba/brand.git
cd brand
```

### 2. **Eseguire lo script di setup**

Prima di eseguire lo script, assicurati di avere Python e Git installati.

Apri la cartella brand e fai clic destro sul file setup_windows.bat e seleziona "Esegui come amministratore".

Verranno creati i collegamenti sul desktop per Server, Operatore, e Amministratore. L'operazione potrebbe richiedere un po' di tempo.

### 3. **Aggiungere i permessi di amministratore (se necessario)**

Alcune operazioni, come l'installazione dei font, potrebbero richiedere permessi di amministratore. Quando esegui il file setup_windows.bat come amministratore, questi permessi sono già inclusi.

Se ricevi errori riguardanti i permessi, assicurati di avere i diritti di amministratore sul sistema o prova ad eseguire nuovamente lo script come amministratore.

### 4. **Eseguire il programma**

Dopo aver eseguito lo script, puoi avviare il programma semplicemente facendo doppio clic sull'icona corrispondente sul desktop (Server, Operatore o Amministratore).

### **Considerazioni aggiuntive**

Alcune versioni di Windows potrebbero bloccare i file .lnk se non li riconoscono come provenienti da una fonte sicura. In tal caso, dovrai fare clic con il tasto destro e selezionare "Proprietà" per sbloccare il file.