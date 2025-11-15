import socket
import threading
from kivy.clock import Clock

class NetworkClient:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.message_callback = None
        self.users_callback = None
        self.notification_callback = None
        
    def connect(self, ip, port, username, on_message, on_users_update, on_notification):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)  
            self.socket.connect((ip, port))
            self.socket.settimeout(None)  
            
            # Enviar nombre de usuario
            self.socket.send(username.encode("utf-8"))
            
            # Configurar callbacks
            self.message_callback = on_message
            self.users_callback = on_users_update
            self.notification_callback = on_notification
            
            self.connected = True
            
            # Iniciar hilo de recepción
            threading.Thread(target=self._receive_loop, daemon=True).start()
            return True
            
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False
    
    def _receive_loop(self):
        while self.connected and self.socket:
            try:
                data = self.socket.recv(1024).decode("utf-8")
                if not data:
                    break
                    
                if data.startswith("USERS|"):
                    users = data.split("|", 1)[1].split(",")
                    if self.users_callback:
                        Clock.schedule_once(lambda dt: self.users_callback(users))
                    
                elif data.startswith("MESSAGE|"):
                    parts = data.split("|", 2)
                    if len(parts) == 3 and self.message_callback:
                        _, sender, message = parts
                        Clock.schedule_once(lambda dt: self.message_callback(sender, message))
                        
                elif data.startswith("NOTIFICATION|") and self.notification_callback:
                    notification = data.split("|", 1)[1]
                    Clock.schedule_once(lambda dt: self.notification_callback(notification))
                    
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error en receive_loop: {e}")
                break
                
        self.connected = False
    
    def send_message(self, target_user, message):
        if self.connected and self.socket:
            try:
                self.socket.send(f"MSG|{target_user}|{message}".encode("utf-8"))
                return True
            except Exception as e:
                print(f"Error enviando mensaje: {e}")
                return False
        return False
    
    def request_users(self):
        if self.connected and self.socket:
            try:
                self.socket.send(b"GET_USERS")
                return True
            except Exception as e:
                print(f"Error solicitando usuarios: {e}")
                return False
        return False
    
    def disconnect(self):
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None