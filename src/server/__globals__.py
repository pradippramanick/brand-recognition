import threading

admin_lock = threading.Lock()       # Per gestire la concorrenza
admin = None                        # Connessione dell'amministratore, serve per controllare che ci sia al più un amministratore connesso

operator_lock = threading.Lock()    # Per gestire la concorrenza
operators = []                      # Lista di operatori attivi; per ogni operatore abbiamo i suoi dati del db e quelli di connessione

chain_lock = threading.Lock()       # Per gestire la concorrenza
chains = {}                         # Lista delle varie filiere attive; per ogni filiera abbiamo la lista della composizione dei 24 cassettoni (ci si accede tramite il numero di filiera)