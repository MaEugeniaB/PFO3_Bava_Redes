import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 5000

lock = threading.Lock()  # evita que prints se mezclen

def cliente(id_cliente):
    """Cada cliente envía palabras y recibe respuestas."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        with lock:
            print(f"\n[Cliente {id_cliente}] Conectado al servidor.\n")

        while True:
            with lock:
                palabra = input(f"[Cliente {id_cliente}] Ingrese una palabra (o 'salir' para terminar): ")

            s.sendall(palabra.encode())

            if palabra.lower() == "salir":
                with lock:
                    print(f"[Cliente {id_cliente}] Cerrando conexión...\n")
                break

            data = s.recv(1024).decode()
            with lock:
                print(f"[Cliente {id_cliente}] → {data}\n")

def main():
    clientes = []
    for i in range(1, 4):
        t = threading.Thread(target=cliente, args=(i,))
        t.start()
        clientes.append(t)

    for t in clientes:
        t.join()

if __name__ == "__main__":
    main()
    
