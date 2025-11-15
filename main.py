# main.py — UI adaptable (sin Window.size fijo)

import threading
from kivy.config import Config
from kivy.metrics import dp

# Ajustes livianos (no afectan lógica de red)
Config.set('kivy', 'keyboard_mode', 'system')  # usa el teclado nativo del teléfono
Config.set('graphics', 'multisamples', '0')   # deja igual para evitar errores en Android

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout

from client_discovery import DiscoveryClient
from network_client import NetworkClient


# ---------------------------------------------------
# Pantalla: Inicio
# ---------------------------------------------------
class InicioScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = [0.08, 0.09, 0.12, 1]

        # Scroll raíz para evitar cortes en móvil chico
        root_scroll = MDScrollView(size_hint=(1, 1))
        self.add_widget(root_scroll)

        # Centro el contenido vertical/horizontal
        anchor = AnchorLayout(anchor_y="center", anchor_x="center", size_hint=(1, 1))
        root_scroll.add_widget(anchor)

        # Contenido adaptable (NO altura fija)
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            padding=dp(24),
            size_hint=(0.94, None),
            adaptive_height=True,
        )
        anchor.add_widget(content)

        # Título y subtítulo
        content.add_widget(MDLabel(
            text="💬 YaviChat",
            halign="center",
            font_style="H4",
            theme_text_color="Custom",
            text_color=[0.2, 0.7, 1, 1],
            size_hint_y=None,
            height=dp(48),
        ))
        content.add_widget(MDLabel(
            text="Chat en Red Local",
            halign="center",
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=[0.8, 0.8, 1, 0.9],
            size_hint_y=None,
            height=dp(28),
        ))

        # Formulario (alto adaptable)
        form = MDBoxLayout(orientation="vertical", spacing=dp(16), size_hint=(1, None), adaptive_height=True)

        self.nombre_input = MDTextField(
            hint_text="👤 Tu nombre",
            mode="rectangle",
            size_hint=(1, None),
            height=dp(56),
            font_size="18sp",
        )
        form.add_widget(self.nombre_input)

        self.carrera_input = MDTextField(
            hint_text="🎓 Tu carrera",
            mode="rectangle",
            size_hint=(1, None),
            height=dp(56),
            font_size="18sp",
        )
        form.add_widget(self.carrera_input)
        content.add_widget(form)

        # Botón grande y ancho (sin forzar altura de pantalla)
        content.add_widget(MDRaisedButton(
            text="CONTINUAR",
            md_bg_color=[0.2, 0.6, 1, 1],
            size_hint=(1, None),
            height=dp(50),
            font_size="18sp",
            on_release=self.validar_datos,
        ))

    def validar_datos(self, *args):
        nombre = self.nombre_input.text.strip()
        carrera = self.carrera_input.text.strip()
        if not nombre:
            return self._error("Por favor ingresa tu nombre")
        if not carrera:
            return self._error("Por favor ingresa tu carrera")

        app = MDApp.get_running_app()
        app.nombre_usuario = nombre
        app.carrera_usuario = carrera
        self.manager.current = "lista"

    def _error(self, msg):
        dlg = MDDialog(
            title="Error",
            text=msg,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dlg.dismiss())],
            size_hint=(0.86, None),
        )
        dlg.open()


# ---------------------------------------------------
# Pantalla: Lista de usuarios
# ---------------------------------------------------
class ListaUsuariosScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = MDBoxLayout(orientation="vertical", padding=dp(12), spacing=dp(12))
        self.add_widget(root)

        header = MDBoxLayout(size_hint_y=None, height=dp(56), spacing=dp(8))
        self.btn_volver = MDFlatButton(
            text="←",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            size_hint=(None, None),
            size=(dp(44), dp(44)),
            font_size="18sp",
            on_release=self.volver,
        )
        header.add_widget(self.btn_volver)
        header.add_widget(MDLabel(
            text="👥 Usuarios Conectados",
            halign="center",
            font_style="H6",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
        ))
        root.add_widget(header)

        self.estado = MDLabel(
            text="Buscando servidor...",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(28),
            font_size="15sp",
        )
        root.add_widget(self.estado)

        self.scroll = MDScrollView()
        self.contenedor = MDList()
        self.scroll.add_widget(self.contenedor)
        root.add_widget(self.scroll)

        acciones = MDBoxLayout(size_hint_y=None, height=dp(56), spacing=dp(10))
        acciones.add_widget(MDFlatButton(
            text="VOLVER",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            on_release=self.volver,
        ))
        acciones.add_widget(MDRaisedButton(
            text="ACTUALIZAR",
            md_bg_color=[0.2, 0.6, 1, 1],
            on_release=self.actualizar_lista,
        ))
        root.add_widget(acciones)

        self.discovery = None
        self.notification_count = {}

    def on_enter(self):
        self.estado.text = "🔍 Buscando servidor..."
        self.buscar_servidor()

    def buscar_servidor(self):
        self.discovery = DiscoveryClient()
        Clock.schedule_once(lambda dt: threading.Thread(target=self._buscar_thread, daemon=True).start())

    def _buscar_thread(self):
        self.discovery.found.wait(timeout=10)
        if self.discovery.server_ip:
            Clock.schedule_once(lambda dt: self._conectar())
        else:
            Clock.schedule_once(lambda dt: setattr(self.estado, "text", "❌ Servidor no encontrado"))

    def _conectar(self):
        app = MDApp.get_running_app()
        ok = app.network_client.connect(
            self.discovery.server_ip,
            self.discovery.server_port,
            app.nombre_usuario,
            self.on_message_received,
            self.on_users_updated,
            self.on_notification_received,
        )
        if ok:
            self.estado.text = "🟢 Conectado"
            app.network_client.request_users()
        else:
            self.estado.text = "❌ Error de conexión"

    def on_message_received(self, sender, message):
        self.notification_count[sender] = self.notification_count.get(sender, 0) + 1
        old = self.estado.text
        self.estado.text = f"📩 Mensaje de {sender}"
        Clock.schedule_once(lambda dt: setattr(self.estado, "text", old), 2)

    def on_notification_received(self, note):
        self.estado.text = f"🔔 {note}"

    def on_users_updated(self, usuarios):
        Clock.schedule_once(lambda dt: self._pintar(usuarios))

    def _pintar(self, usuarios):
        self.contenedor.clear_widgets()
        app = MDApp.get_running_app()
        for u in usuarios:
            if u and u != app.nombre_usuario:
                n = self.notification_count.get(u, 0)
                txt = f"{u} 📩{n}" if n > 0 else u
                self.contenedor.add_widget(OneLineListItem(
                    text=txt,
                    on_release=lambda x, dest=u: self.ir_chat(dest),
                ))

    def actualizar_lista(self, _):
        self.estado.text = "Actualizando..."
        if getattr(self, "discovery", None):
            self.discovery.found.clear()
        self.buscar_servidor()

    def ir_chat(self, usuario_destino):
        app = MDApp.get_running_app()
        app.usuario_destino = usuario_destino
        if usuario_destino in self.notification_count:
            self.notification_count[usuario_destino] = 0
        self.manager.current = "chat"

    def volver(self, _):
        self.manager.current = "inicio"


# ---------------------------------------------------
# Pantalla: Chat
# ---------------------------------------------------
class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.historial = ""

        root = MDBoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        self.add_widget(root)

        header = MDBoxLayout(size_hint_y=None, height=dp(56), spacing=dp(8))
        header.add_widget(MDFlatButton(
            text="←",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            size_hint=(None, None),
            size=(dp(44), dp(44)),
            font_size="18sp",
            on_release=self.volver,
        ))
        self.header = MDLabel(
            text="Chat",
            font_style="H6",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
        )
        header.add_widget(self.header)
        root.add_widget(header)

        self.scroll = MDScrollView()
        self.chat_log = MDLabel(
            text=self.historial,
            halign="left",
            valign="top",
            size_hint_y=None,
            markup=True,
            theme_text_color="Custom",
            text_color=[0.9, 0.9, 0.9, 1],
            font_size="16sp",
        )
        self.chat_log.bind(texture_size=self._update_height)
        self.scroll.add_widget(self.chat_log)
        root.add_widget(self.scroll)

        box = MDBoxLayout(spacing=dp(8), size_hint_y=None, height=dp(64))
        self.msg_input = MDTextField(
            hint_text="Escribe un mensaje…",
            mode="rectangle",
            size_hint_x=0.72,
            font_size="16sp",
        )
        box.add_widget(self.msg_input)
        box.add_widget(MDRaisedButton(
            text="Enviar",
            md_bg_color=[0.2, 0.6, 1, 1],
            size_hint_x=0.28,
            font_size="16sp",
            on_release=self.enviar,
        ))
        root.add_widget(box)

    def _update_height(self, instance, _value):
        instance.height = instance.texture_size[1]
        instance.text_size = (instance.width, None)
        self.scroll.scroll_y = 0

    def on_enter(self):
        app = MDApp.get_running_app()
        self.header.text = f"Chat con {app.usuario_destino}"
        self.historial = f"Conectado con {app.usuario_destino}\n\n"
        self.chat_log.text = self.historial
        app.network_client.message_callback = self.on_message_received

    def on_message_received(self, sender, message):
        Clock.schedule_once(lambda dt: self._append(sender, message))

    def _append(self, sender, msg):
        app = MDApp.get_running_app()
        if sender == app.usuario_destino:
            self.historial += f"[color=88ff88]{sender}:[/color] {msg}\n"
        else:
            self.historial += f"[color=ff8888]{sender}:[/color] {msg}\n"
        self.chat_log.text = self.historial

    def enviar(self, _):
        app = MDApp.get_running_app()
        txt = self.msg_input.text.strip()
        if txt and app.usuario_destino:
            if app.network_client.send_message(app.usuario_destino, txt):
                self.historial += f"[color=8888ff]Tú:[/color] {txt}\n"
            else:
                self.historial += "[color=ff4444]Error al enviar[/color]\n"
            self.chat_log.text = self.historial
            self.msg_input.text = ""

    def volver(self, _):
        self.manager.current = "lista"


# ---------------------------------------------------
# App
# ---------------------------------------------------
class YaviChatApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.network_client = NetworkClient()

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"

        self.title = "YaviChat LAN"
        self.nombre_usuario = ""
        self.carrera_usuario = ""
        self.usuario_destino = ""

        sm = ScreenManager()
        sm.add_widget(InicioScreen(name="inicio"))
        sm.add_widget(ListaUsuariosScreen(name="lista"))
        sm.add_widget(ChatScreen(name="chat"))
        return sm

    def on_stop(self):
        self.network_client.disconnect()


if __name__ == "__main__":
    YaviChatApp().run()
