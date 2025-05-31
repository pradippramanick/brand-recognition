import json
import os
import time

import __globals__
from database import get_db
from controller import Operator_controller, Brand_controller, Log_controller

CART_FILE = "num_cart.json"

num_cart = None

def handle_operator(conn, addr):
    print(f"{addr}: smistato al gestore operatori")

    operator = login(conn, addr)
    send_hotwords(conn, addr)
    work(conn, addr, operator)

def login(conn, addr):
    global num_cart
    num_cart = get_num_cart()
    send_num_cart(conn, addr, num_cart)

    # Controllo codice e carrello
    code_valid = ""
    cart_valid = ""
    while code_valid != "ok" or cart_valid != "ok":
        try:
            data = conn.recv(1024).decode()
        except ConnectionResetError:
            conn.close()
            print(f"{addr}: connessione chiusa")
            return

        json_data = json.loads(data)
        code = json_data.get("code")
        cart = json_data.get("cart")

        code_valid = check_code(code)
        cart_valid = check_cart(cart)

        res = { "code": f"{code_valid}", "cart": f"{cart_valid}" }
        conn.sendall(json.dumps(res).encode() + b"\n\nEND\n\n")

        chain = (int(cart) + 1) // 2 # calcolo la filiera in base al carrello (carrelli 1 e 2 = filiera 1, carrelli 3 e 4 = filiera 2, ecc)

    print(f"{addr}: operatore {code} carrello {cart}, filiera {chain}")

    # Aggiunta operatore alla lista
    operator = {
        "addr": addr,
        "code": code,
        "cart": cart,
        "chain": chain
    }

    with __globals__.operator_lock:
        __globals__.operators.append(operator)
        print(f"{addr}: operatore aggiunto alla lista")

    if not is_chain_initialized(conn, operator):
        init_chain(conn, operator)

    return operator

def get_num_cart():
    if os.path.exists(CART_FILE):
        with open(CART_FILE, "r") as f:
            return int((json.load(f)).get("num_cart"))
    else:
        default_config = {"num_cart": "2"}
        with open(CART_FILE, "w") as f:
            json.dump(default_config, f)
        return 2
    
def send_num_cart(conn, addr, num_cart):
    conn.sendall(f"{num_cart}".encode())
    print(f"{addr}: numero carrelli inviato")

def send_hotwords(conn, addr):
    # Manda la lista di hotwords
    with next(get_db()) as session:
        hotwords = Brand_controller.get_list(session)
        conn.sendall(json.dumps(hotwords).encode() + b"\n\nEND\n\n")
        print(f"{addr}: lista brand inviata")

def work(conn, addr, operator):
    # Attesa di messaggi dall'operatore
    while True:
        try:
            msg = conn.recv(1024).decode()
        except ConnectionResetError:
            remove_operator(operator)
            conn.close()
            print(f"{addr}: connessione chiusa")

        if not msg:
            remove_operator(operator)
            conn.close()
            print(f"{addr}: connessione chiusa (vuoto)")
            break 

        if msg == "logout":
            remove_operator(operator)
            new_op = login(conn, addr)
            work(conn, addr, new_op)
        elif msg == "exit":
            remove_operator(operator)
            conn.close()
            print(f"{addr}: connessione chiusa")
            break
        else:
            with next(get_db()) as session:
                # se il brand che è arrivato era normalizzato, ottengo il nome com'è scritto nel db, altrimenti None
                brand = Brand_controller.get_name_by_normalized_name(session, msg)
                if brand == None:
                    # se sono qui vuol dire che avevo un nome già corretto (a meno di maiuscole, per questo recupero il nome corrispondente dal db)
                    brand = Brand_controller.get_name(session, msg)

            # ottengo il numero del cassettone
            bin = get_bin(brand, operator.get('chain'))
            
            if bin is not None:
                # Genera log
                with next(get_db()) as session:
                    Log_controller.create(session, operator.get('code'), brand, operator.get('cart'), operator.get('chain'), bin)
                    print(f"{addr}: log generato")
            else:
                print(f"{addr}: brand non registrato perchè non presente in questa filiera")

def check_code(code):
    if code == "\n\nNONE\n\n":
        return "none"
    
    # Controlla che non è già connesso
    with __globals__.operator_lock:
        for operator in __globals__.operators:
            if operator["code"] == code:
                return "already logged" 
    # Controlla se esiste
    with next(get_db()) as session:
        find = Operator_controller.get(session, code)
    if find == None:
        return "not exists"
    return "ok"

def check_cart(cart):
    if cart == "\n\nNONE\n\n":
        return "none"
    
    global num_cart
    new = get_num_cart()
    if num_cart != new:
        num_cart = new
        return new
    
    try:
        cart = int(cart)
    except ValueError:
        return "not int"
    if cart < 1 or cart > num_cart:
        return "out of range"
    find = False
    with __globals__.operator_lock:
        for operator in __globals__.operators:
            if (int(operator.get("cart")) == cart):
                find = True
        if find:
            return "already logged"
        else:
            return "ok"
        
def is_chain_initialized(conn, current_operator):
    chain = current_operator.get('chain')

    find = False
    with __globals__.operator_lock:
        for operator in __globals__.operators:
            if operator != current_operator:
                if (int(operator.get('chain')) == chain):
                    find = True
                if find:
                    print(f"{operator.get('addr')}: filiera già inizializzata")
                    conn.sendall("already_init".encode())
                    return True
                
    print(f"{operator.get('addr')}: filiera da inizializzare")
    conn.sendall("not_init".encode())
    return False

def init_chain(conn, current_operator):
    chain = current_operator.get('chain')                           # recupero il numero di filiera

    with next(get_db()) as session:
        brands = Brand_controller.get_name_list(session)            # recupero la lista dei nomi di brand
    conn.sendall(json.dumps(brands).encode() + b"\n\nEND\n\n")      # la mando

    bins_list = rec_long_msg(conn)                                  # ricevo una lisa di 24 elementi, in cui ogni elemento contiene 0, 1 o più brand
    print(f"filiera {chain}: {bins_list}")

    with __globals__.chain_lock:                                    # acquisisco il lock della variabile globale che conserva la composizione della filiere
        __globals__.chains[chain] = bins_list                       # inserisco nella lista di filiere (in corrispondenza del numero di filiera), la lista dei cassettoni

def rec_long_msg(conn):
    buffer = b""
    while True:
        packet = conn.recv(1024)
        if not packet:
            break
        buffer += packet
        if b"\n\nEND\n\n" in buffer:
            break
    return json.loads(buffer.replace(b"\n\nEND\n\n", b"").decode())

def get_bin(brand, n_chain):
    with __globals__.chain_lock:
        chain_list = __globals__.chains[n_chain]
        position = 0
        for list in chain_list:
            position+=1
            for b in list:
                if b == brand:
                    return position
    return None
    
def remove_operator(operator):
    with __globals__.operator_lock:
        if (operator in __globals__.operators):
            __globals__.operators.remove(operator)
            print(f"{operator.get('addr')}: operatore rimosso dalla lista")