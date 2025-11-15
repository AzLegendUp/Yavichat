import socket
import threading
from server_discovery import DiscoveryServer

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5000

clients = {}        # {nombre_usuario: socket}
user_sockets = {}   # {socket: nombre_usuario}

def get_local_ip():
    """Obtiene la IP local real de la interfaz activa (Wi-Fi/Ethernet/hotspot)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def broadcast_user_list():
    """Envía la lista de usuarios conectados a todos."""
    users = ",".join(clients.keys())
    msg = f"USERS|{users}"

    desconectados = []
    for user, sock in list(clients.items()):
        try:
            sock.send(msg.encode("utf-8"))
        except:
            desconectados.append(user)

    for u in desconectados:
        if u in clients:
            del clients[u]
            print(f"🔴 {u} removido (desconectado)")

def handle_client(client_socket):
    username = None
    try:
        username = client_socket.recv(1024).decode("utf-8").strip()
        if not username or username in clients:
            client_socket.send("ERROR|Nombre ya existe".encode("utf-8"))
            client_socket.close()
            return

        clients[username] = client_socket
        user_sockets[client_socket] = username
        print(f"🟢 {username} conectado ({len(clients)} usuarios)")

        broadcast_user_list()

        while True:
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                break

            if data == "GET_USERS":
                client_socket.send(f"USERS|{','.join(clients.keys())}".encode("utf-8"))

            elif data.startswith("MSG|"):
                _, destino, mensaje = data.split("|", 2)
                if destino in clients:
                    try:
                        clients[destino].send(f"MESSAGE|{username}|{mensaje}".encode("utf-8"))
                        clients[destino].send(f"NOTIFICATION|Nuevo mensaje de {username}".encode("utf-8"))
                        print(f"💬 {username} -> {destino}: {mensaje}")
                    except:
                        client_socket.send(f"ERROR|No se pudo enviar a {destino}".encode("utf-8"))
                else:
                    client_socket.send(f"ERROR|Usuario {destino} no encontrado".encode("utf-8"))

    except Exception as e:
        print(f"⚠️ Error con {username}: {e}")

    finally:
        if username and username in clients:
            del clients[username]
            print(f"🔴 {username} desconectado ({len(clients)} usuarios)")
        if client_socket in user_sockets:
            del user_sockets[client_socket]
        broadcast_user_list()
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(10)

    ip_local = get_local_ip()
    print(f"🚀 Servidor YaviChat activo en {ip_local}:{SERVER_PORT}")

    # Lanzar hilo de descubrimiento
    DiscoveryServer(ip_local, SERVER_PORT)

    while True:
        sock, addr = server.accept()
        print(f"🔗 Conexión desde {addr[0]}")
        threading.Thread(target=handle_client, args=(sock,), daemon=True).start()

if __name__ == "__main__":
    start_server()
