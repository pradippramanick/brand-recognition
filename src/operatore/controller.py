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

    def send(self, msg):
        self.conn.sendall(msg.encode())

    def send_long_msg(self, msg):
        self.conn.sendall(json.dumps(msg).encode() + b"\n\nEND\n\n")

    def rec(self):
        return self.conn.recv(1024).decode()
    
    def rec_long_msg(self):
        buffer = b""
        while True:
            packet = self.conn.recv(1024)
            if not packet:
                break
            buffer += packet
            if b"\n\nEND\n\n" in buffer:
                break
        return json.loads(buffer.replace(b"\n\nEND\n\n", b"").decode())

    def check_data(self, code, cart):
        self.send(json.dumps({"code": f"{code}", "cart": f"{cart}"}))
        return self.rec_long_msg()