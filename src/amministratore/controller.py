import socket
import json
from __config__ import HOST, PORT

class Controller:
    def __init__(self):
        self.conn = None

    def connect(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.conn.connect((HOST, PORT))
        except Exception:
            return False
        print("Connesso al server")
        return True

    def check_code(self, code):
        self.conn.sendall(code.encode())
        return self._rec_msg()
    
    def get_users(self, type):
        self._send_user_req("get", type)
        return self._receive_long_messages()
    
    def delete_user(self, type, code):
        self._send_user_req("delete", type, code)
        return self._rec_msg()
    
    def update_or_create_user(self, action, type, code, first_name, last_name):
        self._send_user_req(action, type, code, first_name, last_name)
        return self._rec_msg()
    
    def get_brands(self):
        self._send_brand_req("get")
        return self._receive_long_messages()
    
    def delete_brand(self, name):
        self._send_brand_req("delete", name)
        return self._rec_msg()
    
    def update_or_create_brand(self, action, name, normalized_name, language):
        self._send_brand_req(action, name, normalized_name, language)
        return self._rec_msg()
    
    def get_logs(self, code: str = "", day: str = ""):
        self._send_log_req(code=code, day=day)
        return self._receive_long_messages()
    
    def get_num_carts(self):
        self._send_cart_req("get_num_cart")
        return self.conn.recv(1024).decode()
    
    def set_num_carts(self, number):
        self._send_cart_req("set_num_cart", number)
        return self.conn.recv(1024).decode()
    

    # Funzioni per mandare messaggi
    def send(self, msg):
        self.conn.sendall(f"{msg}".encode())

    def send_msg(self, msg):
        msg = {"action": f"{msg}"}
        self.conn.sendall(json.dumps(msg).encode())
    
    def _send_user_req(self, action, table, code=None, first_name=None, last_name=None):
        msg = {"action": f"{action}", "table": f"{table}", "code": f"{code}", "first_name": f"{first_name}", "last_name": f"{last_name}"}
        self.conn.sendall(json.dumps(msg).encode())

    def _send_brand_req(self, action, name=None, normalized_name=None, language=None):
        msg = {"action": f"{action}", "table": "brand", "name": f"{name}", "normalized_name": f"{normalized_name}", "language": f"{language}"}
        self.conn.sendall(json.dumps(msg).encode())

    def _send_log_req(self, code: str = "", day: str = ""):
        msg = {"action": "get", "table": "log", "code": f"{code}", "day": f"{day}"}
        self.conn.sendall(json.dumps(msg).encode())
        
    def _send_cart_req(self, action, number=None):
        msg = {"action": f"{action}", "number": f"{number}"}
        self.conn.sendall(json.dumps(msg).encode())


    # Funzioni per ricevere messaggi
    def rec(self):
        return self.conn.recv(1024).decode()
    
    def _receive_long_messages(self):
        buffer = b""
        while True:
            packet = self.conn.recv(1024)
            if not packet:
                break
            buffer += packet
            if b"\n\nEND\n\n" in buffer:  # Controlla se ha ricevuto tutto
                break
        return json.loads(buffer.replace(b"\n\nEND\n\n", b"").decode())

    def _rec_msg(self):
        res = self.conn.recv(1024).decode()
        return False if res == "ERROR" else True if res == "SUCCESS" else None