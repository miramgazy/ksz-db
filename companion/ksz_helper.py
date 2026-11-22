#!/usr/bin/env python3
"""
KSZ Companion Helper v2.0.0 (Client Agent for Windows Server / RDS)
===================================================================
Локальный клиентский агент для взаимодействия веб-интерфейса KSZ-DB с рабочим местом инженера:
1. Запуск iikoBackOffice через ClearBat без предупреждений браузера.
2. Прямая запись заведения в локальную SQLite базу ClearBat (таблица Entities).
3. Запуск обновления лицензий ClearBat.
4. Быстрый запуск AnyDesk (напрямую или через Sandboxie).
5. Автокопирование паролей в буфер обмена инженера.

Архитектура v2.0:
- Агент подключается как клиент к серверу KSZ-DB (исходящее соединение Long-Polling).
- НЕ слушает локальные порты: полностью исключены конфликты портов между RDP-сессиями на Windows Server 2019!
- Полная изоляция: каждый инженер в своей сессии RDP управляет своими окнами и своим буфером обмена.
- Использует исключительно стандартную библиотеку Python (не требует сторонних pip-библиотек).
"""

import os
import sys
import json
import time
import socket
import base64
import sqlite3
import getpass
import subprocess
import configparser
from pathlib import Path
import urllib.request
import urllib.error

VERSION = "2.0.0"
CONFIG_FILE = "ksz_helper.ini"
DEFAULT_API_URL = "http://127.0.0.1:8000/api/v1"


def get_default_clearbat_db():
    """Определяет стандартное расположение SQLite базы ClearBat."""
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
    """Загружает конфигурационный файл ksz_helper.ini."""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding='utf-8')
    else:
        config['SERVER'] = {
            'api_url': DEFAULT_API_URL,
            'username': '',
            'password': '',
            'token': '',
        }
        config['SETTINGS'] = {
            'clearbat_db_path': get_default_clearbat_db(),
            'sandman_path': r'C:\Program Files\Sandboxie-Plus\SandMan.exe',
            'default_anydesk_exe': r'C:\Program Files (x86)\AnyDesk\AnyDesk.exe',
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            config.write(f)
    return config


def save_config(config):
    """Сохраняет конфигурацию в файл."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        config.write(f)


def copy_to_clipboard(text: str):
    """Копирует текст в системный буфер обмена текущей пользовательской сессии."""
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
        print(f"[!] Предупреждение: не удалось скопировать в буфер: {e}")


def launch_protocol_url(url: str):
    """Открывает URL-протокол (например, clearbat:// или anydesk://) в сеансе Windows."""
    try:
        if sys.platform.startswith('win'):
            cmd = f'rundll32.exe url.dll,FileProtocolHandler "{url}"'
            subprocess.Popen(cmd, shell=True)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', url])
        else:
            subprocess.Popen(['xdg-open', url])
    except Exception as e:
        print(f"[!] Ошибка вызова протокола: {e}")


class KSZClientAgent:
    def __init__(self):
        self.config = load_config()
        self.api_url = self.config['SERVER'].get('api_url', DEFAULT_API_URL).rstrip('/')
        self.access_token = self.config['SERVER'].get('token', '').strip()
        self.refresh_token = ''
        self.username = self.config['SERVER'].get('username', '').strip()
        self.password = self.config['SERVER'].get('password', '').strip()
        self.user_info = {}

    def ensure_auth(self):
        """Проверяет или запрашивает учетные данные пользователя."""
        if not self.access_token and not (self.username and self.password):
            print("\n" + "=" * 65)
            print("  ПЕРВЫЙ ЗАПУСК: АВТОРИЗАЦИЯ АГЕНТА В KSZ-DB")
            print("=" * 65)
            print(f"Адрес сервера по умолчанию: {self.api_url}")
            custom_url = input(f"Введите адрес API [{self.api_url}]: ").strip()
            if custom_url:
                self.api_url = custom_url.rstrip('/')
                self.config['SERVER']['api_url'] = self.api_url

            while not self.username:
                self.username = input("Логин в KSZ-DB: ").strip()

            while not self.password:
                try:
                    self.password = getpass.getpass("Пароль: ").strip()
                except Exception:
                    self.password = input("Пароль: ").strip()

            self.config['SERVER']['username'] = self.username
            self.config['SERVER']['password'] = self.password
            save_config(self.config)

        if not self.access_token or not self.test_token():
            self.login()

    def login(self):
        """Выполняет вход на сервер по логину и паролю и получает JWT-токены."""
        login_url = f"{self.api_url}/auth/login/"
        payload = json.dumps({
            "username": self.username,
            "password": self.password
        }).encode('utf-8')

        req = urllib.request.Request(
            login_url,
            data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                self.access_token = data.get('access', '')
                self.refresh_token = data.get('refresh', '')
                self.user_info = data.get('user', {})
                print(f"[OK] Вход выполнен: {self.user_info.get('full_name') or self.username} ({self.user_info.get('role', 'Пользователь')})")
                return True
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8', errors='ignore')
            print(f"[ОШИБКА] Неверный логин или пароль ({e.code}): {err_body}")
            # Сброс пароля в конфиге для повторного ввода при следующем старте
            self.config['SERVER']['password'] = ''
            save_config(self.config)
            sys.exit(1)
        except Exception as e:
            print(f"[ОШИБКА] Не удалось подключиться к серверу {self.api_url}: {e}")
            raise e

    def test_token(self):
        """Проверяет валидность текущего access_token."""
        if not self.access_token:
            return False
        req = urllib.request.Request(
            f"{self.api_url}/companion/status/",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                self.user_info = data.get('user', {})
                return True
        except Exception:
            return False

    def refresh_access_token(self):
        """Обновляет JWT токен или перелогинивается."""
        if self.refresh_token:
            refresh_url = f"{self.api_url}/auth/token/refresh/"
            payload = json.dumps({"refresh": self.refresh_token}).encode('utf-8')
            req = urllib.request.Request(
                refresh_url,
                data=payload,
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    self.access_token = data.get('access')
                    return True
            except Exception:
                pass
        # Если refresh не помог — повторный login
        return self.login()

    def get_metadata(self):
        """Собирает системные метаданные сессии инженера для сервера."""
        settings = self.config['SETTINGS'] if 'SETTINGS' in self.config else {}
        db_path = settings.get('clearbat_db_path', get_default_clearbat_db())
        hostname = socket.gethostname()
        win_user = os.environ.get('USERNAME') or getpass.getuser()
        session_name = os.environ.get('SESSIONNAME', 'Console')

        return {
            "version": VERSION,
            "platform": sys.platform,
            "hostname": hostname,
            "session_user": win_user,
            "session_name": session_name,
            "clearbat_db_path": db_path,
            "clearbat_db_exists": os.path.exists(db_path),
        }

    # ==========================================
    # ОБРАБОТЧИКИ КОМАНД
    # ==========================================

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
        default_exe = settings.get('default_anydesk_exe', r'C:\Program Files (x86)\AnyDesk\AnyDesk.exe')
        exe_path = custom_exe if custom_exe else default_exe

        # Копируем пароль в буфер обмена
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

                cmd = f'"{sandman_path}" {sandbox_params} "{exe_path}" {anydesk_id}'
                subprocess.Popen(cmd, shell=True)
                launched_mode = f"Sandboxie ({sandbox_params or 'Песочница'})"
            else:
                if os.path.exists(exe_path):
                    if any_pass:
                        cmd = f'"{exe_path}" {anydesk_id} --with-password {any_pass}'
                    else:
                        cmd = f'"{exe_path}" {anydesk_id}'
                    subprocess.Popen(cmd, shell=True)
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

        full_url = f"clearbat:/type=license?url={server}:{port}?login={login}?password={password}"
        launch_protocol_url(full_url)

        return {
            "success": True,
            "message": f"Обновление лицензии ({server}) запущено через ClearBat.",
            "url": full_url
        }

    def handle_insert_clearbat(self, payload: dict):
        name = payload.get('name', '').strip()
        ip = payload.get('server', payload.get('ip', '')).strip()
        port = str(payload.get('port', '443')).strip()
        login = payload.get('login', 'iikoadm').strip()
        password = payload.get('password', '').strip()

        settings = self.config['SETTINGS'] if 'SETTINGS' in self.config else {}
        db_path = settings.get('clearbat_db_path', get_default_clearbat_db())

        if not os.path.exists(db_path):
            return {
                "success": False,
                "message": f"База ClearBat не найдена по пути: {db_path}. Настройте путь в {CONFIG_FILE}."
            }

        try:
            conn = sqlite3.connect(db_path, timeout=10)
            cursor = conn.cursor()

            cursor.execute("SELECT MAX(revision) FROM Entities;")
            row = cursor.fetchone()
            max_rev = row[0] if (row and row[0] is not None) else 0
            new_rev = max_rev + 1

            cursor.execute("""
                INSERT INTO Entities (name, type, folder, ip, port, login, password, deleted, revision)
                VALUES (?, 'iikoOffice', NULL, ?, ?, ?, ?, 'False', ?);
            """, (name, ip, port, login, password, new_rev))

            conn.commit()
            conn.close()

            return {
                "success": True,
                "revision": new_rev,
                "message": f"Заведение '{name}' успешно добавлено в базу ClearBat!"
            }
        except Exception as e:
            return {"success": False, "message": f"Ошибка записи в SQLite базу: {str(e)}"}

    def execute_task(self, task: dict):
        """Диспетчер вызова локальных команд."""
        action = task.get('action')
        payload = task.get('payload', {})

        print(f"\n[>>> КОМАНДА] Получено действие: '{action}'")

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

        status_tag = "[OK]" if res.get('success') else "[ОШИБКА]"
        print(f"{status_tag} Результат: {res.get('message')}")
        return res

    def send_task_result(self, task_id: str, result: dict):
        """Отправляет результат выполнения задачи обратно на сервер."""
        url = f"{self.api_url}/companion/agent/result/"
        body = json.dumps({"task_id": task_id, "result": result}).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {self.access_token}"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return True
        except Exception as e:
            print(f"[!] Ошибка отправки результата на сервер: {e}")
            return False

    def poll_loop(self):
        """Основной бесконечный цикл ожидания команд от сервера."""
        print("\n" + "=" * 65)
        print(f"  KSZ-DB Companion Helper v{VERSION} активен!")
        print(f"  Пользователь : {self.user_info.get('full_name') or self.username}")
        print(f"  Хост / Сессия: {socket.gethostname()} ({os.environ.get('USERNAME')})")
        print(f"  База ClearBat: {self.config['SETTINGS'].get('clearbat_db_path', '')}")
        print("=" * 65)
        print("[*] Подключение к серверу установлено. Ожидание команд от веб-интерфейса...")
        print("[*] Для остановки нажмите Ctrl + C\n")

        poll_url = f"{self.api_url}/companion/agent/poll/"

        while True:
            metadata = self.get_metadata()
            payload = json.dumps(metadata).encode('utf-8')

            req = urllib.request.Request(
                poll_url,
                data=payload,
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Authorization": f"Bearer {self.access_token}"
                }
            )

            try:
                # Таймаут 35 секунд (на бэкенде опрос длится 25 секунд)
                with urllib.request.urlopen(req, timeout=35) as resp:
                    resp_data = json.loads(resp.read().decode('utf-8'))
                    st = resp_data.get('status')

                    if st == 'command':
                        task = resp_data.get('task', {})
                        task_id = task.get('task_id')
                        result = self.execute_task(task)
                        if task_id:
                            self.send_task_result(task_id, result)
                    elif st == 'idle':
                        # Сервер вернул idle по истечению таймаута — сразу начинаем следующий цикл
                        continue

            except urllib.error.HTTPError as e:
                if e.code == 401:
                    print("[!] Токен доступа истек. Выполняется автоматическое обновление...")
                    try:
                        self.refresh_access_token()
                    except Exception:
                        print("[!] Не удалось обновить токен, повторная попытка через 5 сек...")
                        time.sleep(5)
                else:
                    print(f"[!] HTTP ошибка {e.code}: {e.reason}. Повтор через 3 сек...")
                    time.sleep(3)

            except (urllib.error.URLError, TimeoutError) as e:
                print(f"[!] Связь с сервером прервана ({e}). Переподключение через 3 сек...")
                time.sleep(3)

            except Exception as e:
                print(f"[!] Непредвиденная ошибка: {e}. Переподключение через 3 сек...")
                time.sleep(3)


def main():
    print("=" * 65)
    print(f"  KSZ Companion Helper v{VERSION} (Client-Server RDS Edition)")
    print("=================================================================")
    agent = KSZClientAgent()
    try:
        agent.ensure_auth()
        agent.poll_loop()
    except KeyboardInterrupt:
        print("\n[!] Остановка агента по сигналу пользователя. До свидания!")
        sys.exit(0)


if __name__ == '__main__':
    main()
