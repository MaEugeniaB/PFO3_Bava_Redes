import socket
import threading
import queue
import sqlite3

HOST = "127.0.0.1"
PORT = 5000

task_queue = queue.Queue()

# --- Configurar base de datos SQLite ---
def init_db():
    conn = sqlite3.connect("palabras.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS palabras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            palabra TEXT NOT NULL,
            letras INTEGER NOT NULL,
            worker_id INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def guardar_en_db(palabra, letras, worker_id):
    conn = sqlite3.connect("palabras.db")
    c = conn.cursor()
    c.execute("INSERT INTO palabras (palabra, letras, worker_id) VALUES (?, ?, ?)",
              (palabra, letras, worker_id))
    conn.commit()
    conn.close()

# --- Manejo de clientes y workers ---
def handle_client(conn, addr):
    print(f"[Cliente conectado] {addr}")
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        if data.lower() == "salir":
            print(f"[Cliente desconectado] {addr}")
            break
        print(f"[Tarea recibida] {data}")
        task_queue.put((data, conn))
    conn.close()

def worker(worker_id):
    while True:
        palabra, conn = task_queue.get()
        resultado = len(palabra)
        print(f"[Worker {worker_id}] '{palabra}' → {resultado} letras")

        # Guardar en la base de datos
        guardar_en_db(palabra, resultado, worker_id)

        try:
            conn.sendall(f"La palabra '{palabra}' tiene {resultado} letras.".encode())
        except:
            pass
        task_queue.task_done()

def start_server():
    init_db()  # inicializa la base de datos
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[Servidor] Escuchando en {HOST}:{PORT}")

        # Lanzar 3 workers
        for i in range(1, 4):
            threading.Thread(target=worker, args=(i,), daemon=True).start()
            print(f"[Worker {i}] iniciado")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()

