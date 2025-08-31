# Setup del progetto

Questo documento fornisce le istruzioni per configurare il progetto su **Linux** e **Windows**.

## **Setup su Linux**
### Prerequisiti

Python 3.11 o precedenti

### 1. **Clonare il repository**

Se non l'hai già fatto, clona il repository sulla Scrivania:

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
### Prerequisiti
Macchina virtuale con una distribuzione di Linux (es. Ubuntu, Debian);
Python 3.11 o precedenti installati sulla macchina viruale

### Installazione
Segui i passaggi per la configurazione su Linux, eseguendoli all'interno della macchina virtuale.
