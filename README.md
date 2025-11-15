#  YaviChat — Chat sin Internet (LAN Chat con Python + KivyMD)

YaviChat es una aplicación de mensajería instantánea que funciona **sin Internet**, utilizando la red local (LAN) mediante sockets TCP y UDP.  
Todo lo que necesitas para chatear es que los dispositivos estén conectados a la **misma red WiFi o hotspot**.

Incluye:

- App Android desarrollada con **KivyMD**
- Servidor TCP en Python
- Descubrimiento automático del servidor (UDP Broadcast)
- Mensajería en tiempo real
- Interfaz moderna
- Sin necesidad de Internet

---

# Características

- Funciona completamente **sin Internet**
- Conexión automática al servidor con **UDP Discovery**
- Chat entre usuarios en tiempo real
- App Android compilable con Buildozer
- Código en Python fácil de modificar
- Servidor ligero, rápido y estable
- Compatible con PC, laptops y Android

---

# Requisitos del proyecto

## Para ejecutar el servidor (PC/Laptop)
- Python **3.10 o superior**
- Windows, Linux o macOS

Dependencias (se instalan automáticamente en entorno virtual):


---

#  Crear y activar entorno virtual (recomendado)

En Linux o macOS:

```bash
python3 -m venv kivy_venv
source kivy_venv/bin/activate

En Windows:

python -m venv kivy_venv
kivy_venv\Scripts\activate

Instalar dependencias:
pip install kivy kivymd


Ejecutar el servidor
python3 server.py


Deberías ver:
Servidor YaviChat activo en 192.168.1.X:5000
📢 Broadcast enviado...
El servidor debe permanecer encendido para que la app Android funcione.


Instalar la app en Android (APK listo)

No necesitas Linux ni compilar nada.
Descarga el APK aquí:

👉 https://github.com/AzLegendUp/Yavichat/releases

Instálalo en tu teléfono Android.

Asegúrate de que:

El servidor está encendido

El teléfono está conectado a la misma red WiFi o hotspot

Compilar el APK manualmente (solo si tienes Linux)
1️⃣ Instalar dependencias de Buildozer
sudo apt update
sudo apt install python3-pip python3-venv openjdk-17-jdk \
git zip unzip libncurses5 libstdc++6
pip install buildozer
pip install cython==0.29.33

2️⃣ Crear entorno virtual
python3 -m venv kivy_venv
source kivy_venv/bin/activate
pip install kivy kivymd

3️⃣ Compilar
buildozer android debug


El APK se generará en:

./bin/

¿Cómo funciona YaviChat?
1. Descubrimiento del Servidor (UDP)

El servidor manda un broadcast UDP cada 2 segundos:

YAVICHAT:<ip>:<puerto>


La app lo detecta automáticamente y se conecta.

 2. Protocolo de mensajes
USERS|usuario1,usuario2...
MESSAGE|remitente|mensaje
NOTIFICATION|texto
MSG|destino|mensaje


El servidor administra:

lista de usuarios

mensajes privados

mensajes globales

notificaciones

desconexiones

🗂 Estructura del proyecto
Yavichat/
│── main.py               # App principal (UI)
│── network_client.py     # Cliente TCP
│── server.py             # Servidor principal
│── client_discovery.py   # Cliente UDP (busca servidor)
│── server_discovery.py   # Servidor UDP (broadcast)
│── buildozer.spec        # Configuración Buildozer
│── avatar.png
│── logoyavichat.png
│── .gitignore
│── README.md