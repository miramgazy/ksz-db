#!/usr/bin/env python3
"""
KSZ Companion Helper GUI v2.0.0 (System Tray & Window Edition)
=============================================================
Графический клиентский агент для Windows / Windows Server 2019 (RDS):
- Работает в фоновом режиме в системном трее (рядом с часами).
- При закрытии или нажатии "Свернуть" уходит в область уведомлений.
- Управляет AnyDesk, iikoBackOffice, ClearBat SQLite базой и буфером обмена.
- Поддерживает автозапуск при входе в сессию Windows.
- Не требует открытых TCP-портов — работает через защищенное исходящее подключение.
"""

import os
import sys
import re
import json
import time
import socket
import base64
import shutil
import sqlite3
import getpass
import threading
import subprocess
import configparser
from pathlib import Path
from datetime import datetime
import urllib.request
import urllib.error

# GUI imports (standard library)
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText

# Optional tray icon imports (graceful fallback if not compiled with pystray)
try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

VERSION = "2.0.0"
CONFIG_FILE = "ksz_helper.ini"
DEFAULT_API_URL = "http://192.168.1.253:17676/api/v1"


def get_default_clearbat_logs_dir():
    """Определяет стандартное расположение папки логов CLEAR_bat."""
    appdata = os.environ.get('APPDATA', '')
    candidates = [
        Path(appdata) / 'CLEAR_bat' / 'Logs' if appdata else None,
        Path(os.environ.get('LOCALAPPDATA', '')) / 'CLEAR_bat' / 'Logs' if os.environ.get('LOCALAPPDATA') else None,
        Path('C:/Users') / os.environ.get('USERNAME', '') / 'AppData' / 'Roaming' / 'CLEAR_bat' / 'Logs',
        Path('C:/CLEAR_bat/Logs'),
    ]
    for c in candidates:
        if c and c.exists():
            return str(c)
    if appdata:
        return str(Path(appdata) / 'CLEAR_bat' / 'Logs')
    return r"C:\Users\miram\AppData\Roaming\CLEAR_bat\Logs"


def get_default_clearbat_db():
    candidates = [
        Path(os.environ.get('APPDATA', '')) / 'ClearBat' / 'ClearBat.db',
        Path(os.environ.get('LOCALAPPDATA', '')) / 'ClearBat' / 'ClearBat.db',
        Path('C:/ClearBat/ClearBat.db'),
        Path('C:/Program Files/ClearBat/ClearBat.db'),
        Path('C:/Program Files (x86)/ClearBat/ClearBat.db'),
        Path.home() / 'ClearBat.db',
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    appdata = os.environ.get('APPDATA', '')
    if appdata:
        return str(Path(appdata) / 'ClearBat' / 'ClearBat.db')
    return "C:/ClearBat/ClearBat.db"


def load_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding='utf-8')
        if 'SETTINGS' in config and 'clearbat_logs_path' not in config['SETTINGS']:
            config['SETTINGS']['clearbat_logs_path'] = get_default_clearbat_logs_dir()
            save_config(config)
    else:
        config['SERVER'] = {
            'api_url': DEFAULT_API_URL,
            'username': '',
            'password': '',
            'token': '',
        }
        config['SETTINGS'] = {
            'clearbat_db_path': get_default_clearbat_db(),
            'clearbat_logs_path': get_default_clearbat_logs_dir(),
            'sandman_path': r'C:\Program Files\Sandboxie-Plus\SandMan.exe',
            'default_anydesk_exe': r'C:\Program Files (x86)\AnyDesk\AnyDesk.exe',
            'autostart': 'False',
            'start_minimized': 'True',
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            config.write(f)
    return config


def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        config.write(f)


def copy_to_clipboard(text: str):
    if not text:
        return
    try:
        if sys.platform.startswith('win'):
            p = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
            p.communicate(input=text.encode('utf-16'))
        elif sys.platform == 'darwin':
            p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            p.communicate(input=text.encode('utf-8'))
        else:
            p = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
            p.communicate(input=text.encode('utf-8'))
    except Exception as e:
        print(f"[!] Ошибка копирования в буфер: {e}")


def launch_protocol_url(url: str):
    """Открывает URL-протокол (например, clearbat:// или anydesk://) в сеансе Windows."""
    try:
        if sys.platform.startswith('win'):
            # os.startfile — нативный, самый надежный способ Win32 ShellExecute в Python:
            # - Не вызывает cmd.exe
            # - Не спотыкается о символы &, %, ?, кавычки, пробелы в паролях
            # - Напрямую передает команду зарегистрированному протоколу Windows
            try:
                os.startfile(url)
            except Exception:
                try:
                    subprocess.Popen(['explorer.exe', url])
                except Exception:
                    subprocess.Popen(['rundll32.exe', 'url.dll,FileProtocolHandler', url])
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', url])
        else:
            subprocess.Popen(['xdg-open', url])
    except Exception as e:
        print(f"[!] Ошибка вызова протокола: {e}")


def find_anydesk_exe(custom_exe: str = '') -> str:
    """Ищет установленный исполняемый файл AnyDesk.exe по стандартным путям Windows."""
    candidates = []
    if custom_exe:
        candidates.append(custom_exe)
    candidates.extend([
        r'C:\Program Files (x86)\AnyDesk\AnyDesk.exe',
        r'C:\Program Files\AnyDesk\AnyDesk.exe',
        os.path.expandvars(r'%LOCALAPPDATA%\Programs\AnyDesk\AnyDesk.exe'),
        os.path.expandvars(r'%LOCALAPPDATA%\AnyDesk\AnyDesk.exe'),
        os.path.expandvars(r'%APPDATA%\AnyDesk\AnyDesk.exe'),
        os.path.expandvars(r'%PROGRAMDATA%\AnyDesk\AnyDesk.exe'),
    ])
    for c in candidates:
        if c and os.path.exists(c):
            return c
    which_anydesk = shutil.which('AnyDesk.exe') or shutil.which('anydesk')
    if which_anydesk:
        return which_anydesk
    return ''


def set_windows_autostart(enable: bool):
    """Настройка автозапуска в реестре Windows текущего пользователя."""
    if not sys.platform.startswith('win'):
        return
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        if enable:
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = f'"{sys.executable}" "{os.path.abspath(__file__)}"'
            winreg.SetValueEx(key, "KSZ-Companion-Agent", 0, winreg.REG_SZ, f'{exe_path} --tray')
        else:
            try:
                winreg.DeleteValue(key, "KSZ-Companion-Agent")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception as e:
        print(f"[!] Ошибка реестра автозапуска: {e}")


def create_tray_image():
    """Создает динамическую иконку для системного трея."""
    if not HAS_TRAY:
        return None
    width = 64
    height = 64
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # Рисуем стильный синий скругленный щит/фон
    draw.rounded_rectangle((4, 4, 60, 60), radius=14, fill=(37, 99, 235))
    # Зеленая точка статуса в углу
    draw.ellipse((42, 42, 58, 58), fill=(16, 185, 129), outline=(255, 255, 255), width=2)
    # Текст KSZ
    draw.text((12, 18), "KSZ", fill=(255, 255, 255))
    return image


def ensure_clearbat_base64_password(pwd: str) -> str:
    """
    Гарантирует, что пароль для таблицы Entities в базе ClearBat закодирован в Base64.
    ClearBat SQLite таблица Entities принимает ТОЛЬКО пароли в Base64 (как в MS Access Form_Company_details).
    """
    if not pwd:
        return ''
    raw = pwd.strip()
    try:
        decoded_bytes = base64.b64decode(raw.encode('ascii'), validate=True)
        if base64.b64encode(decoded_bytes).decode('ascii') == raw:
            decoded_bytes.decode('utf-8')
            return raw
    except Exception:
        pass
    return base64.b64encode(pwd.encode('utf-8')).decode('ascii')


class AgentApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"KSZ-DB Companion Agent v{VERSION}")
        self.root.geometry("640x560")
        self.root.minsize(580, 500)

        # Центрирование окна
        self.center_window(640, 560)

        self.config = load_config()
        self.is_connected = False
        self.worker_thread = None
        self.stop_event = threading.Event()
        self.tray_icon = None

        self.access_token = self.config['SERVER'].get('token', '').strip()
        self.refresh_token = ''
        self.user_info = {}

        self.init_styles()
        self.create_widgets()

        # Перехват кнопки закрытия [X] -> сворачивание в трей
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

        # Инициализация иконки трея
        if HAS_TRAY:
            self.init_tray()

        # Автоподключение, если данные заполнены
        if self.entry_username.get().strip() and self.entry_password.get().strip():
            self.start_agent()

        # Если запущен с параметром --tray или в настройках включен старт в трее
        if '--tray' in sys.argv or self.config['SETTINGS'].getboolean('start_minimized', fallback=False):
            self.root.after(200, self.hide_to_tray)

    def center_window(self, width, height):
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2) - 30
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def init_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', font=('Segoe UI', 9))
        style.configure('Header.TLabel', font=('Segoe UI', 13, 'bold'), foreground='#1e293b')
        style.configure('Status.TLabel', font=('Segoe UI', 10, 'bold'))
        style.configure('Action.TButton', font=('Segoe UI', 9, 'bold'))

    def create_widgets(self):
        # Header banner
        header_frame = tk.Frame(self.root, bg="#2563eb", height=60)
        header_frame.pack(fill="x", side="top")

        lbl_title = tk.Label(
            header_frame,
            text=f"KSZ-DB Companion Agent v{VERSION}",
            font=("Segoe UI", 12, "bold"),
            fg="white",
            bg="#2563eb"
        )
        lbl_title.pack(side="left", padx=16, pady=12)

        self.lbl_tray_hint = tk.Label(
            header_frame,
            text="Сворачивается в трей рядом с часами",
            font=("Segoe UI", 8),
            fg="#bfdbfe",
            bg="#2563eb"
        )
        self.lbl_tray_hint.pack(side="right", padx=16, pady=14)

        # Main container
        main_frame = ttk.Frame(self.root, padding=16)
        main_frame.pack(fill="both", expand=True)

        # Status Bar Card
        status_card = tk.LabelFrame(main_frame, text=" Статус подключения ", font=("Segoe UI", 9, "bold"), padx=12, pady=8)
        status_card.pack(fill="x", pady=(0, 10))

        status_row = ttk.Frame(status_card)
        status_row.pack(fill="x")

        self.status_indicator = tk.Label(status_row, text="●", font=("Segoe UI", 14), fg="#94a3b8")
        self.status_indicator.pack(side="left", padx=(0, 6))

        self.status_text = ttk.Label(status_row, text="Не подключен", style="Status.TLabel", foreground="#64748b")
        self.status_text.pack(side="left")

        self.btn_toggle = ttk.Button(status_row, text="Подключиться", style="Action.TButton", command=self.toggle_connection)
        self.btn_toggle.pack(side="right")

        self.lbl_user_info = ttk.Label(status_card, text="Пользователь: не авторизован", foreground="#475569")
        self.lbl_user_info.pack(fill="x", pady=(4, 0))

        # Settings Card
        settings_card = tk.LabelFrame(main_frame, text=" Настройки подключения к серверу ", font=("Segoe UI", 9, "bold"), padx=12, pady=10)
        settings_card.pack(fill="x", pady=(0, 10))

        # API URL
        row1 = ttk.Frame(settings_card)
        row1.pack(fill="x", pady=2)
        ttk.Label(row1, text="URL сервера:", width=16).pack(side="left")
        self.entry_url = ttk.Entry(row1)
        self.entry_url.insert(0, self.config['SERVER'].get('api_url', DEFAULT_API_URL))
        self.entry_url.pack(side="left", fill="x", expand=True)

        # Username & Password
        row2 = ttk.Frame(settings_card)
        row2.pack(fill="x", pady=4)
        ttk.Label(row2, text="Логин KSZ-DB:", width=16).pack(side="left")
        self.entry_username = ttk.Entry(row2, width=20)
        self.entry_username.insert(0, self.config['SERVER'].get('username', ''))
        self.entry_username.pack(side="left", padx=(0, 12))

        ttk.Label(row2, text="Пароль:").pack(side="left", padx=(0, 6))
        self.entry_password = ttk.Entry(row2, show="•", width=20)
        self.entry_password.insert(0, self.config['SERVER'].get('password', ''))
        self.entry_password.pack(side="left", fill="x", expand=True)

        # ClearBat Path
        row3 = ttk.Frame(settings_card)
        row3.pack(fill="x", pady=4)
        ttk.Label(row3, text="База ClearBat:", width=16).pack(side="left")
        self.entry_clearbat = ttk.Entry(row3)
        self.entry_clearbat.insert(0, self.config['SETTINGS'].get('clearbat_db_path', get_default_clearbat_db()))
        self.entry_clearbat.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(row3, text="Обзор...", width=9, command=self.browse_clearbat).pack(side="right")

        # ClearBat Logs Path
        row3_logs = ttk.Frame(settings_card)
        row3_logs.pack(fill="x", pady=4)
        ttk.Label(row3_logs, text="Логи ClearBat:", width=16).pack(side="left")
        self.entry_clearbat_logs = ttk.Entry(row3_logs)
        self.entry_clearbat_logs.insert(0, self.config['SETTINGS'].get('clearbat_logs_path', get_default_clearbat_logs_dir()))
        self.entry_clearbat_logs.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(row3_logs, text="Обзор...", width=9, command=self.browse_clearbat_logs).pack(side="right")

        # Checkboxes (Autostart & Minimize on launch)
        row4 = ttk.Frame(settings_card)
        row4.pack(fill="x", pady=(6, 0))

        self.var_autostart = tk.BooleanVar(value=self.config['SETTINGS'].getboolean('autostart', fallback=False))
        chk_autostart = ttk.Checkbutton(row4, text="Автозапуск при входе в Windows", variable=self.var_autostart, command=self.on_autostart_change)
        chk_autostart.pack(side="left", padx=(0, 16))

        self.var_minimized = tk.BooleanVar(value=self.config['SETTINGS'].getboolean('start_minimized', fallback=True))
        chk_minimized = ttk.Checkbutton(row4, text="Сворачивать в трей при запуске", variable=self.var_minimized, command=self.save_settings)
        chk_minimized.pack(side="left")

        # Action Log Card
        log_card = tk.LabelFrame(main_frame, text=" Журнал действий агента ", font=("Segoe UI", 9, "bold"), padx=8, pady=8)
        log_card.pack(fill="both", expand=True, pady=(0, 10))

        self.txt_log = ScrolledText(log_card, height=7, font=("Consolas", 8), bg="#f8fafc", fg="#334155")
        self.txt_log.pack(fill="both", expand=True)

        # Footer Buttons
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill="x")

        btn_hide = ttk.Button(footer_frame, text="Свернуть в трей (рядом с часами)", command=self.hide_to_tray)
        btn_hide.pack(side="left")

        btn_clear_log = ttk.Button(footer_frame, text="Очистить лог", command=lambda: self.txt_log.delete('1.0', tk.END))
        btn_clear_log.pack(side="right", padx=(6, 0))

        btn_save = ttk.Button(footer_frame, text="Сохранить настройки", command=self.save_settings)
        btn_save.pack(side="right")

    def log(self, message: str):
        now = datetime.now().strftime("%H:%M:%S")
        self.txt_log.insert(tk.END, f"[{now}] {message}\n")
        self.txt_log.see(tk.END)

    def browse_clearbat(self):
        filename = filedialog.askopenfilename(
            title="Выберите файл ClearBat.db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if filename:
            self.entry_clearbat.delete(0, tk.END)
            self.entry_clearbat.insert(0, filename)
            self.save_settings()

    def browse_clearbat_logs(self):
        folder = filedialog.askdirectory(
            title="Выберите папку логов CLEAR_bat",
            initialdir=self.entry_clearbat_logs.get() or os.environ.get('APPDATA', '')
        )
        if folder:
            self.entry_clearbat_logs.delete(0, tk.END)
            self.entry_clearbat_logs.insert(0, folder)
            self.save_settings()

    def on_autostart_change(self):
        enable = self.var_autostart.get()
        set_windows_autostart(enable)
        self.save_settings()
        self.log(f"Автозапуск в Windows: {'Включен' if enable else 'Отключен'}")

    def save_settings(self):
        self.config['SERVER']['api_url'] = self.entry_url.get().strip().rstrip('/')
        self.config['SERVER']['username'] = self.entry_username.get().strip()
        self.config['SERVER']['password'] = self.entry_password.get().strip()
        self.config['SETTINGS']['clearbat_db_path'] = self.entry_clearbat.get().strip()
        self.config['SETTINGS']['clearbat_logs_path'] = self.entry_clearbat_logs.get().strip()
        self.config['SETTINGS']['autostart'] = str(self.var_autostart.get())
        self.config['SETTINGS']['start_minimized'] = str(self.var_minimized.get())
        save_config(self.config)
        self.log("Настройки сохранены в ksz_helper.ini")

    def hide_to_tray(self):
        """Прячет главное окно в системный трей."""
        if HAS_TRAY and self.tray_icon:
            self.root.withdraw()
            try:
                self.tray_icon.notify(
                    "KSZ-Agent работает в фоне рядом с часами.\nКликните иконку для вызова окна.",
                    "KSZ-DB Companion"
                )
            except Exception:
                pass
        else:
            self.root.iconify()

    def restore_from_tray(self, icon=None, item=None):
        """Восстанавливает окно из трея."""
        self.root.after(0, self._restore_ui)

    def _restore_ui(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def init_tray(self):
        image = create_tray_image()
        menu = pystray.Menu(
            pystray.MenuItem("Открыть окно агента", self.restore_from_tray, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Свернуть в трей", lambda: self.root.after(0, self.hide_to_tray)),
            pystray.MenuItem("Выход", self.exit_app)
        )
        self.tray_icon = pystray.Icon("KSZ-Agent", image, "KSZ-DB Companion Helper", menu)
        tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        tray_thread.start()

    def exit_app(self, icon=None, item=None):
        self.stop_event.set()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self.root.destroy)
        os._exit(0)

    def toggle_connection(self):
        if self.is_connected:
            self.stop_agent()
        else:
            self.start_agent()

    def start_agent(self):
        self.save_settings()
        self.stop_event.clear()
        self.set_status_ui("yellow", "Подключение к серверу...")
        self.btn_toggle.configure(text="Остановить")
        self.worker_thread = threading.Thread(target=self.agent_worker_loop, daemon=True)
        self.worker_thread.start()

    def stop_agent(self):
        self.stop_event.set()
        self.is_connected = False
        self.set_status_ui("gray", "Отключен")
        self.btn_toggle.configure(text="Подключиться")
        self.lbl_user_info.configure(text="Пользователь: отключен")
        self.log("Агент остановлен.")

    def set_status_ui(self, color_key, text):
        colors = {
            "green": "#10b981",
            "red": "#ef4444",
            "yellow": "#f59e0b",
            "gray": "#94a3b8"
        }
        hex_color = colors.get(color_key, "#64748b")
        self.root.after(0, lambda: (
            self.status_indicator.configure(fg=hex_color),
            self.status_text.configure(text=text, foreground=hex_color)
        ))

    # ========================================================
    # РАБОЧИЙ ПОТОК АГЕНТА (СВЯЗЬ С СЕРВЕРОМ)
    # ========================================================

    def agent_worker_loop(self):
        api_url = self.config['SERVER'].get('api_url', DEFAULT_API_URL).rstrip('/')
        username = self.config['SERVER'].get('username', '').strip()
        password = self.config['SERVER'].get('password', '').strip()

        if not username or not password:
            self.set_status_ui("red", "Укажите логин и пароль")
            self.log("[!] Ошибка: логин или пароль не указаны.")
            return

        # 1. Авторизация
        self.log(f"Подключение к {api_url}...")
        login_url = f"{api_url}/auth/login/"
        payload = json.dumps({"username": username, "password": password}).encode('utf-8')
        req = urllib.request.Request(login_url, data=payload, headers={"Content-Type": "application/json; charset=utf-8"})

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                self.access_token = data.get('access')
                self.refresh_token = data.get('refresh')
                self.user_info = data.get('user', {})
                full_name = self.user_info.get('full_name') or username
                role = self.user_info.get('role', 'Пользователь')

                self.root.after(0, lambda: self.lbl_user_info.configure(
                    text=f"Пользователь: {full_name} ({role}) | Сессия: {os.environ.get('USERNAME')}"
                ))
                self.set_status_ui("green", "В сети (Ожидание команд)")
                self.is_connected = True
                self.log(f"Успешный вход: {full_name} ({role}). Ожидание команд...")
        except urllib.error.HTTPError as e:
            err = e.read().decode('utf-8', errors='ignore')
            self.set_status_ui("red", f"Ошибка авторизации ({e.code})")
            self.log(f"[!] Неверный логин или пароль: {err}")
            return
        except Exception as e:
            self.set_status_ui("red", "Нет связи с сервером")
            self.log(f"[!] Ошибка соединения: {e}")
            return

        # 2. Бесконечный опрос команд (Long-Polling)
        poll_url = f"{api_url}/companion/agent/poll/"

        while not self.stop_event.is_set():
            db_path = self.config['SETTINGS'].get('clearbat_db_path', get_default_clearbat_db())
            meta = {
                "version": VERSION,
                "platform": sys.platform,
                "hostname": socket.gethostname(),
                "session_user": os.environ.get('USERNAME') or getpass.getuser(),
                "session_name": os.environ.get('SESSIONNAME', 'Console'),
                "clearbat_db_path": db_path,
                "clearbat_db_exists": os.path.exists(db_path),
            }

            req = urllib.request.Request(
                poll_url,
                data=json.dumps(meta).encode('utf-8'),
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Authorization": f"Bearer {self.access_token}",
                    "Connection": "close"
                }
            )

            try:
                with urllib.request.urlopen(req, timeout=35) as resp:
                    resp_data = json.loads(resp.read().decode('utf-8'))
                    st = resp_data.get('status')
                    task = resp_data.get('task', {})

                # Опрос прошел успешно - гарантированно восстанавливаем статус В сети
                self.set_status_ui("green", "В сети (Ожидание команд)")

                if st == 'command' and task:
                    task_id = task.get('task_id')
                    is_async = task.get('async', False) or task.get('action') in ('launch_license', 'launch_backoffice', 'launch_anydesk')
                    res = self.execute_task(task)
                    # Результат отправляем только для синхронных задач (например, insert_clearbat)
                    if task_id and not is_async:
                        self.send_task_result(api_url, task_id, res)
                elif st == 'idle':
                    continue

            except urllib.error.HTTPError as e:
                if e.code == 401:
                    self.log("[!] Токен истек, автоматическое обновление...")
                    self.refresh_access_token(api_url)
                else:
                    self.log(f"[!] HTTP ошибка {e.code}: {e.reason}, повтор через 3 сек...")
                    time.sleep(3)
            except urllib.error.URLError as e:
                if not self.stop_event.is_set():
                    self.log(f"[!] Связь с сервером прервана ({e.reason}). Восстановление через 3 сек...")
                    self.set_status_ui("yellow", "Восстановление связи...")
                    time.sleep(3)
            except Exception as e:
                if not self.stop_event.is_set():
                    self.log(f"[!] Ошибка связи: {str(e)}. Повтор через 3 сек...")
                    self.set_status_ui("yellow", "Восстановление связи...")
                    time.sleep(3)

    def refresh_access_token(self, api_url):
        refresh_url = f"{api_url}/auth/token/refresh/"
        payload = json.dumps({"refresh": self.refresh_token}).encode('utf-8')
        req = urllib.request.Request(
            refresh_url,
            data=payload,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Connection": "close"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                self.access_token = data.get('access')
                self.set_status_ui("green", "В сети (Ожидание команд)")
        except Exception:
            pass

    def send_task_result(self, api_url: str, task_id: str, result: dict):
        url = f"{api_url}/companion/agent/result/"
        body = json.dumps({"task_id": task_id, "result": result}).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {self.access_token}",
                "Connection": "close"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return True
        except Exception as e:
            self.log(f"[!] Ошибка отправки ответа: {e}")
            return False

    def execute_task(self, task: dict):
        action = task.get('action')
        payload = task.get('payload', {})
        task_id = task.get('task_id')
        if task_id and 'task_id' not in payload:
            payload['task_id'] = task_id
        self.log(f">>> Получена команда: '{action}'")

        if action == 'launch_anydesk':
            res = self.handle_launch_anydesk(payload)
        elif action == 'launch_backoffice':
            res = self.handle_launch_backoffice(payload)
        elif action == 'launch_license':
            res = self.handle_launch_license(payload)
        elif action == 'insert_clearbat':
            res = self.handle_insert_clearbat(payload)
        else:
            res = {"success": False, "message": f"Неизвестное действие: {action}"}

        status_tag = "OK" if res.get('success') else "ОШИБКА"
        self.log(f"[{status_tag}] {res.get('message')}")
        return res

    def handle_launch_anydesk(self, payload: dict):
        anydesk_id = str(payload.get('anydesk_id', '')).strip()
        any_pass = str(payload.get('any_pass', '')).strip()
        version_name = payload.get('version_name', 'Main AnyDesk')
        is_sandbox = bool(payload.get('is_sandbox', False))
        sandbox_params = payload.get('sandbox_params', '').strip()
        custom_exe = payload.get('exe_path', '').strip()

        if not anydesk_id:
            return {"success": False, "message": "AnyDesk ID не указан."}

        settings = self.config['SETTINGS'] if 'SETTINGS' in self.config else {}
        sandman_path = settings.get('sandman_path', r'C:\Program Files\Sandboxie-Plus\SandMan.exe')
        default_exe = settings.get('default_anydesk_exe', '')
        exe_path = find_anydesk_exe(custom_exe or default_exe)

        if any_pass:
            copy_to_clipboard(any_pass)

        launched_mode = "Direct"
        if sys.platform.startswith('win'):
            if is_sandbox:
                if not os.path.exists(sandman_path):
                    for c in [
                        r'C:\Program Files\Sandboxie-Plus\SandMan.exe',
                        r'C:\Program Files\Sandboxie\Start.exe',
                        r'C:\Program Files (x86)\Sandboxie\Start.exe',
                    ]:
                        if os.path.exists(c):
                            sandman_path = c
                            break
                target_exe = exe_path or r'C:\Program Files (x86)\AnyDesk\AnyDesk.exe'
                cmd = f'"{sandman_path}" {sandbox_params} "{target_exe}" {anydesk_id}'
                subprocess.Popen(cmd, shell=True)
                launched_mode = f"Sandboxie ({sandbox_params or 'Песочница'})"
            else:
                if exe_path and os.path.exists(exe_path):
                    args = [exe_path, anydesk_id]
                    if any_pass:
                        args.extend(['--with-password', any_pass])
                    subprocess.Popen(args)
                    launched_mode = "AnyDesk.exe"
                else:
                    launch_protocol_url(f"anydesk:{anydesk_id}")
                    launched_mode = "anydesk:// протокол"
        else:
            launch_protocol_url(f"anydesk:{anydesk_id}")
            launched_mode = "anydesk:// протокол"

        pwd_msg = " Пароль скопирован в буфер обмена." if any_pass else ""
        return {
            "success": True,
            "message": f"AnyDesk {anydesk_id} запущен [{launched_mode}].{pwd_msg}",
            "mode": launched_mode,
            "version_name": version_name
        }

    def handle_launch_backoffice(self, payload: dict):
        server = payload.get('server', '').strip()
        port = str(payload.get('port', '443')).strip()
        login = payload.get('login', 'iikoadm').strip()
        password = payload.get('password', '').strip()

        if not server:
            return {"success": False, "message": "Адрес сервера не указан."}

        raw_params = f"?type=iiko?url={server}:{port}?login={login}?password={password}"
        final_b64 = base64.b64encode(raw_params.encode('utf-8')).decode('ascii')
        full_url = f"clearbat:/{final_b64}?encode=full"

        launch_protocol_url(full_url)
        if password:
            copy_to_clipboard(password)

        return {
            "success": True,
            "message": f"iikoBackOffice ({server}) запущен через ClearBat, пароль скопирован в буфер.",
            "url": full_url
        }

    def handle_launch_license(self, payload: dict):
        server = payload.get('server', '').strip()
        port = str(payload.get('port', '443')).strip()
        login = payload.get('login', 'iikoadm').strip()
        password = payload.get('password', '').strip()
        company_id = payload.get('company_id')
        task_id = payload.get('task_id')

        # 1. Запоминаем текущий размер сегодняшнего лог-файла
        settings = self.config['SETTINGS'] if 'SETTINGS' in self.config else {}
        logs_dir_str = settings.get('clearbat_logs_path') or get_default_clearbat_logs_dir()
        logs_dir = Path(logs_dir_str)
        today_filename = f"full_{datetime.now().strftime('%d%m%y')}.log"
        today_file = logs_dir / today_filename

        initial_pos = today_file.stat().st_size if today_file.exists() else 0

        # 2. Запускаем протокол ClearBat
        full_url = f"clearbat:/type=license?url={server}:{port}?login={login}?password={password}"
        launch_protocol_url(full_url)

        # 3. Запускаем фоновый мониторинг файла лога
        threading.Thread(
            target=self._watch_license_log,
            args=(today_file, initial_pos, company_id, task_id, server),
            daemon=True
        ).start()

        return {
            "success": True,
            "message": f"Обновление лицензии ({server}) запущено через ClearBat. Агент отслеживает лог.",
            "url": full_url
        }

    def _watch_license_log(self, log_file: Path, initial_pos: int, company_id, task_id: str, server: str):
        self.log(f"[*] Начато наблюдение за логом CLEAR_bat ({log_file.name}) для: {server}...")
        max_attempts = 35  # 35 * 1.0 сек = 35 сек
        for attempt in range(max_attempts):
            time.sleep(1.0)

            current_file = log_file
            if not current_file.exists():
                logs_dir = current_file.parent
                if logs_dir.exists():
                    log_files = sorted(logs_dir.glob("full_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
                    if log_files:
                        current_file = log_files[0]

            if not current_file.exists():
                continue

            try:
                curr_size = current_file.stat().st_size
                if curr_size <= initial_pos:
                    continue

                with open(current_file, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(initial_pos)
                    new_text = f.read()

                if not new_text or not new_text.strip():
                    continue

                has_success = "[LicenseArgs] Успешный ответ от сервера лицензирования." in new_text or "Licenses info:" in new_text
                has_error = False
                error_msg = None

                if "ERROR!" in new_text or "[ERROR]" in new_text or "Невозможно разрешить удаленное имя" in new_text or "401" in new_text or "Время ожидания" in new_text:
                    has_error = True
                    for l in new_text.splitlines():
                        if "ERROR!" in l or "Невозможно разрешить удаленное имя" in l or "[ERROR]" in l:
                            clean_l = l.split("в System.")[0].strip()
                            clean_l = re.sub(r"\[.*?\]", "", clean_l).strip()
                            error_msg = clean_l
                            break
                    if not error_msg:
                        error_msg = f"Сервер {server} недоступен или вернул ошибку"

                if has_success and "[LicenseArgs] Успешный ответ от сервера лицензирования." in new_text:
                    self.log(f"[OK] Успешный ответ лицензирования для {server} зафиксирован в логе!")
                    self._send_license_result_to_server(company_id, task_id, new_text, is_success=True)
                    return

                if has_error:
                    self.log(f"[!] Ошибка сервера лицензирования для {server}: {error_msg}")
                    self._send_license_result_to_server(company_id, task_id, new_text, is_success=False, error_msg=error_msg)
                    return

            except Exception as e:
                self.log(f"[!] Ошибка чтения лог-файла: {e}")

        self.log(f"[!] Мониторинг лога CLEAR_bat для {server} завершен по таймауту (33 сек).")

    def _send_license_result_to_server(self, company_id, task_id: str, log_text: str, is_success: bool, error_msg: str = None):
        api_url = self.entry_url.get().strip().rstrip('/')
        if not company_id:
            if task_id:
                res = {"success": is_success, "message": "Лог получен" if is_success else error_msg}
                if error_msg:
                    res["error"] = error_msg
                self.send_task_result(api_url, task_id, res)
            return

        url = f"{api_url}/companies/{company_id}/license-data/"
        payload = {
            "task_id": task_id,
            "log_text": log_text,
            "success": is_success,
        }
        if error_msg:
            payload["error"] = error_msg

        body = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {self.access_token}",
                "Connection": "close"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                self.log(f"[OK] Данные лицензии заведения #{company_id} успешно доставлены на сервер!")
                return True
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8', errors='ignore')
            self.log(f"[!] Ошибка отправки на сервер ({e.code}): {err_body}")
        except Exception as e:
            self.log(f"[!] Ошибка соединения с сервером при отправке лицензии: {e}")
        return False

    def handle_insert_clearbat(self, payload: dict):
        name = payload.get('name', '').strip()
        ip = payload.get('server', payload.get('ip', '')).strip()
        port = str(payload.get('port', '443')).strip()
        login = payload.get('login', 'iikoadm').strip()
        raw_password = payload.get('password', '').strip()

        # База ClearBat принимает только зашифрованный (Base64) пароль (как в Access Form_Company_details)
        password = ensure_clearbat_base64_password(raw_password)

        settings = self.config['SETTINGS'] if 'SETTINGS' in self.config else {}
        db_path = settings.get('clearbat_db_path', get_default_clearbat_db())

        if not os.path.exists(db_path):
            return {
                "success": False,
                "message": f"База ClearBat не найдена по пути: {db_path}."
            }

        try:
            conn = sqlite3.connect(db_path, timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(revision) FROM Entities;")
            row = cursor.fetchone()
            max_rev = row[0] if (row and row[0] is not None) else 0
            new_rev = max_rev + 1

            # Проверяем, существует ли уже такая запись в ClearBat (по имени и не удаленная)
            cursor.execute("SELECT id FROM Entities WHERE name = ? AND (deleted = 'False' OR deleted = 0);", (name,))
            existing = cursor.fetchone()

            if existing:
                cursor.execute("""
                    UPDATE Entities
                    SET type = 'iikoOffice', ip = ?, port = ?, login = ?, password = ?, deleted = 'False', revision = ?
                    WHERE id = ?;
                """, (ip, port, login, password, new_rev, existing[0]))
                action_text = f"Заведение '{name}' успешно обновлено в базе ClearBat (ревизия {new_rev})!"
            else:
                cursor.execute("""
                    INSERT INTO Entities (name, type, folder, ip, port, login, password, deleted, revision)
                    VALUES (?, 'iikoOffice', NULL, ?, ?, ?, ?, 'False', ?);
                """, (name, ip, port, login, password, new_rev))
                action_text = f"Заведение '{name}' успешно добавлено в базу ClearBat (ревизия {new_rev})!"

            conn.commit()
            conn.close()

            return {
                "success": True,
                "revision": new_rev,
                "message": action_text
            }
        except Exception as e:
            return {"success": False, "message": f"Ошибка записи в SQLite базу ClearBat: {str(e)}"}


def main():
    root = tk.Tk()
    app = AgentApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
