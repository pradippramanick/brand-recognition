Setup del progetto

Questo documento fornisce le istruzioni per configurare il progetto su Linux e Windows.
Setup su Linux
1. Clonare il repository

Se non l'hai già fatto, clona il repository nella cartella desiderata:

git clone https://github.com/tuo-utente/tuo-repository.git
cd tuo-repository

2. Eseguire lo script di setup

Assicurati che il tuo sistema abbia i permessi di esecuzione per lo script di setup (setup_linux.sh). Se non li ha, aggiungili con il comando:

chmod +x setup_linux.sh

Poi esegui lo script di setup:

./setup_linux.sh

Lo script eseguirà le seguenti operazioni:

    Crea un ambiente virtuale Python se non esiste.

    Installa tutti i pacchetti necessari da requirements.txt.

    Installa i font presenti nella cartella fonts.

    Crea collegamenti sul desktop per Server, Operatore, e Amministratore.

3. Aggiungere i permessi ai file .desktop

Dopo aver eseguito lo script, i collegamenti .desktop creati sul desktop potrebbero necessitare di permessi di esecuzione. Aggiungi i permessi con i seguenti comandi:

chmod +x ~/Scrivania/server.desktop
chmod +x ~/Scrivania/operatore.desktop
chmod +x ~/Scrivania/admin.desktop

4. Eseguire il programma

Ora puoi avviare il programma facendo doppio clic sull'icona corrispondente sul desktop (Server, Operatore o Amministratore).

Se hai problemi con le icone, assicurati che siano correttamente impostate e che i file .desktop siano eseguibili.
Setup su Windows
1. Clonare il repository

Se non l'hai già fatto, clona il repository in una cartella sul tuo sistema:

git clone https://github.com/tuo-utente/tuo-repository.git
cd tuo-repository

2. Eseguire lo script di setup

Prima di eseguire lo script, assicurati di avere Python e Git installati.

Crea il file setup_windows.bat nella stessa cartella del progetto e inserisci il codice fornito precedentemente.

Poi esegui lo script di setup come amministratore. Segui questi passaggi:

    Fai clic destro sul file setup_windows.bat e seleziona "Esegui come amministratore".

    Lo script eseguirà le seguenti operazioni:

        Crea un ambiente virtuale Python se non esiste.

        Installa tutti i pacchetti necessari da requirements.txt.

        Copia i font nella cartella Fonts di Windows.

        Crea collegamenti sul desktop per Server, Operatore, e Amministratore.

3. Aggiungere i permessi di amministratore (se necessario)

    Alcune operazioni, come l'installazione dei font, potrebbero richiedere permessi di amministratore. Quando esegui il file setup_windows.bat come amministratore, questi permessi sono già inclusi.

    Se ricevi errori riguardanti i permessi, assicurati di avere i diritti di amministratore sul sistema o prova ad eseguire nuovamente lo script come amministratore.

4. Eseguire il programma

Dopo aver eseguito lo script, puoi avviare il programma semplicemente facendo doppio clic sull'icona corrispondente sul desktop (Server, Operatore o Amministratore).

Se hai problemi con le icone, assicurati che siano di tipo .ico e siano correttamente configurate nei collegamenti.
Considerazioni Aggiuntive

    Linux: Se lo script di setup non funziona correttamente, verifica che il sistema abbia i pacchetti necessari come python3, pip, e fc-cache per la gestione dei font.

    Windows: Alcune versioni di Windows potrebbero bloccare i file .lnk se non li riconoscono come provenienti da una fonte sicura. In tal caso, dovrai fare clic con il tasto destro e selezionare "Proprietà" per sbloccare il file.