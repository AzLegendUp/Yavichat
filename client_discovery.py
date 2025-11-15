import socket
import threading
import time

class DiscoveryClient:
    def __init__(self, broadcast_port=5001):
        self.broadcast_port = broadcast_port
        self.server_ip = None
        self.server_port = None
        self.found = threading.Event()
        threading.Thread(target=self.safe_listen, daemon=True).start()

    def safe_listen(self):
        """Escucha mensajes broadcast del servidor YaviChat, sin cerrar la app en Android."""
        while not self.found.is_set():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(("", self.broadcast_port))
                sock.settimeout(5)

                # No usar print aquí en Android
                for _ in range(5):  # intenta varias veces antes de reiniciar
                    try:
                        data, addr = sock.recvfrom(1024)
                        msg = data.decode("utf-8")
                        if msg.startswith("YAVICHAT:"):
                            _, ip, port = msg.split(":")
                            self.server_ip = ip
                            self.server_port = int(port)
                            self.found.set()
                            break
                    except socket.timeout:
                        pass
                sock.close()
            except Exception:
                time.sleep(3)  # espera y vuelve a intentar
