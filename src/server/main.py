import socket
from concurrent.futures import ThreadPoolExecutor
import threading
import time
from __config__ import HOST, PORT
from database import engine, Base, get_db
from handler_operator import handle_operator
from handler_admin import handle_admin
from controller import Admin_controller, Brand_controller

class Server():
    def __init__(self):

        self.server_socket = None
        self.executor = ThreadPoolExecutor()

        self.client_count = 0
        self.lock = threading.Lock()
        self.shutdown_event = threading.Event()

        self.start()

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen()
        self.server_socket.settimeout(1.0)

        print(f"Server in ascolto su {HOST}:{PORT}")

        running = True
        while running:
            try:
                conn, addr = self.server_socket.accept()
            except socket.timeout:
                if self.shutdown_event.is_set() and self.client_count == 0:
                    running = False
                continue
            except KeyboardInterrupt:
                print("\nInterrotto, avvio della chiusura...")
                self.shutdown_event.set()
                continue  # continua il ciclo per chiudere eventuali connessioni nuove

            if self.shutdown_event.is_set():
                print(f"{addr}: connessione rifiutata, server in chiusura.")
                try:
                    conn.sendall("SERVER_SHUTDOWN".encode())
                except:
                    pass
                conn.close()
                continue
            
            conn.sendall("ACCEPTED".encode())
            with self.lock:
                self.client_count += 1 
            print(f"{addr}: connesso ({self.client_count} client attivi)")

            try:
                mode = conn.recv(1024).decode()
                if mode == "operator":
                    self.executor.submit(self.handle_client, handle_operator, conn, addr)
                elif mode == "admin":
                    self.executor.submit(self.handle_client, handle_admin, conn, addr)
                else:
                    print(f"{addr}: modalità sconosciuta ({mode})")
                    conn.close()
                    with self.lock:
                        self.client_count -= 1
            except Exception as e:
                print(f"{addr}: errore iniziale: {e}")
                conn.close()
                with self.lock:
                    self.client_count -= 1

        self.stop()

    def handle_client(self, handler, conn, addr):
        """Esegue il gestore del client e aggiorna il conteggio quando il client si disconnette."""
        try:
            handler(conn, addr)
        finally:
            with self.lock:
                self.client_count -= 1
                print(f"{addr}: disconnesso ({self.client_count} client attivi)")

    def stop(self):
        """Aspetta che tutti i client si disconnettano prima di spegnere il server."""
        with self.lock:
            if self.client_count > 0:
                print("Il server si spegnerà quando tutti i client saranno spenti.")
        
        while True:
            with self.lock:
                if self.client_count == 0:
                    break
            time.sleep(1)

        self.executor.shutdown(wait=True)

        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
            print("Server socket chiuso")

        print("Server spento correttamente.")


if __name__ == "__main__":
    # Database
    Base.metadata.create_all(bind=engine)
    with next(get_db()) as session:
        if not Admin_controller.get(session, "0000"):
            Admin_controller.create(session, "0000", "admin", "admin")

        if not Brand_controller.get(session, "stop"):
            Brand_controller.create(session, "stop")
            
    # Socket
    server = Server()