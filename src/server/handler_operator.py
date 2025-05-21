import json
import os

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

    print(f"{addr}: operatore {code} carrello {cart}")

    # Aggiunta operatore alla lista
    operator = {
        "addr": addr,
        "code": code,
        "cart": cart
    }

    with __globals__.operator_lock:
        __globals__.operators.append(operator)
        print(f"{addr}: operatore aggiunto alla lista")

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

            # Genera log
            with next(get_db()) as session:
                Log_controller.create(session, operator.get("code"), brand, operator.get("cart"))
                print(f"{addr}: log generato")

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
    
def remove_operator(operator):
    with __globals__.operator_lock:
        if (operator in __globals__.operators):
            __globals__.operators.remove(operator)
            print(f"{operator.get('addr')}: operatore rimosso dalla lista")