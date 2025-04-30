import json
import __globals__
from database import get_db
from controller import Admin_controller, Brand_controller, Log_controller, Operator_controller
import os

CART_FILE = "num_cart.json"

code = None

def handle_admin(conn, addr):
    print(f"{addr}: smistato al gestore admin")

    # Controllo che non ci siano altri admin connessi
    with __globals__.admin_lock:
        if __globals__.admin:
            conn.sendall("ERROR".encode())
            conn.close()
            print(f"{addr}: connessione chiusa: c'è già un amministratore connesso")
            return
        else:
            conn.sendall("SUCCESS".encode())

    with __globals__.admin_lock:
        __globals__.admin = conn

    work(conn, addr)

def work(conn, addr):
    # Controllo che il codice sia valido
    global code
    while True:
        try:
            code = conn.recv(1024).decode()
        except ConnectionResetError:
            remove_admin(addr)
            conn.close()
            print(f"{addr}: connessione chiusa")
            return
        if check_admin_code(code):
            break
        else:
            conn.sendall("ERROR".encode())
    conn.sendall("SUCCESS".encode())
    print(f"{addr}: codice admin {code}")

    # Attesa e gestione messaggi
    while True:
        try:
            data = conn.recv(1024).decode()
        except ConnectionResetError:
            remove_admin(addr)
            conn.close()
            print(f"{addr}: connessione chiusa")
            return
        if not data:
            break
        json_data = json.loads(data)
        handle_request(conn, addr, json_data)

def check_admin_code(code):
    with next(get_db()) as session:
        find = Admin_controller.get(session, code)
    if find == None:
        return False
    return True

def remove_admin(addr):
    with __globals__.admin_lock:
        __globals__.admin = None
    print(f"{addr}: admin rimosso")

def handle_request(conn, addr, json_data):
    action = json_data.get("action")
        
    if action == "logout":
        print(f"{addr}: logout")
        work(conn, addr)
    
    if action == "exit":
        remove_admin(addr)
        conn.close()
        print(f"{addr}: connessione chiusa")
        return
    
    if action == "get_num_cart":
        num_cart = get_num_cart()
        conn.sendall(f"{num_cart}".encode())

    if action == "set_num_cart":
        response = set_num_cart(json_data.get("number"))
        conn.sendall(response.encode())
    
    if action in ["create", "update", "delete", "get"]:
        table = json_data.get("table")
        response = process_db_action(action, table, json_data)
        conn.sendall(response)

def process_db_action(action, table, json_data):
    controller_map = {
        "operator": Operator_controller,
        "admin": Admin_controller,
        "brand": Brand_controller,
        "log": Log_controller
    }
    controller = controller_map.get(table)
    if not controller:
        return "ERROR".encode()
    
    with next(get_db()) as session:
        if action == "create":
            data = create_entry(session, controller, json_data)
            return data.encode()
        elif action == "update":
            data = update_entry(session, controller, json_data)
            return data.encode()
        elif action == "delete":
            data = delete_entry(session, controller, json_data)
            return data.encode()
        elif action == "get":
            data = get_entries(session, controller, json_data)
            return json.dumps(data).encode() + b"\n\nEND\n\n"
    
    return "ERROR".encode()

def create_entry(session, controller, json_data):
    id = json_data.get("code") or json_data.get("name")
    if controller.get(session, id) is None:
        if controller == Brand_controller:
            controller.create(session, id, json_data.get("normalized_name"), json_data.get("language"))
        else:
            controller.create(session, id, json_data.get("first_name"), json_data.get("last_name"))
        return "SUCCESS"
    return "ERROR"

def update_entry(session, controller, json_data):
    id = json_data.get("code") or json_data.get("name")
    if controller == Brand_controller:
        if controller.update(session, id, json_data.get("normalized_name"), json_data.get("language")):
            return "SUCCESS"
    else:
        if controller.update(session, id, json_data.get("first_name"), json_data.get("last_name")):
            return "SUCCESS"
    return "ERROR"

def delete_entry(session, controller, json_data):
    id = json_data.get("code") or json_data.get("name")

    # Impedisco all'admin di eliminarsi da solo
    global code
    if (controller == Admin_controller) and (code == id):
        return "ERROR"
    
    # Impedisco che si possano eliminare operatori attualmente connessi
    if controller == Operator_controller:
        with __globals__.operator_lock:
            if any(op["code"] == id for op in __globals__.operators):
                return "ERROR"
    
    if controller.delete(session, id):
        return "SUCCESS"
    return "ERROR"

def get_entries(session, controller, json_data):
    if controller == Log_controller:
        return controller.get_logs(session, json_data.get("code"), json_data.get("day"))
    return controller.get_all(session)

def get_num_cart():
    if os.path.exists(CART_FILE):
        with open(CART_FILE, "r") as f:
            return int((json.load(f)).get("num_cart"))
    else:
        default_config = {"num_cart": "2"}
        with open(CART_FILE, "w") as f:
            json.dump(default_config, f)
        return 2

def set_num_cart(num_cart):
    with __globals__.operator_lock:
        if  len(__globals__.operators) != 0:
            return "OP CONN"
    
    config = {"num_cart": f"{num_cart}"}
    try:
        with open(CART_FILE, "w") as f:
            json.dump(config, f)
            return "SUCCESS"
    except Exception as e:
        return "ERROR"