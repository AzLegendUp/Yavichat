import socket
import threading
import time

BROADCAST_PORT = 5001
BROADCAST_INTERVAL = 2  # segundos

class DiscoveryServer:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.running = True
        threading.Thread(target=self.broadcast_loop, daemon=True).start()

    def broadcast_loop(self):
        """Envía broadcasts periódicos anunciando el servidor."""
        while self.running:
            try:
                # Se crea un socket nuevo en cada envío para evitar bloqueos
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

                message = f"YAVICHAT:{self.server_ip}:{self.server_port}"
                # Usa el broadcast universal — Android y Linux lo traducen automáticamente
                sock.sendto(message.encode("utf-8"), ("<broadcast>", BROADCAST_PORT))

                sock.close()
                print(f"📢 Broadcast enviado desde {self.server_ip}:{self.server_port}")
            except Exception as e:
                print(f"[Advertencia] No se pudo enviar broadcast: {e}")
            time.sleep(BROADCAST_INTERVAL)
