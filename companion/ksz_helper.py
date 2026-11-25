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
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error

VERSION = "2.1.0"
CONFIG_FILE = "ksz_helper.ini"
DEFAULT_API_URL = "http://127.0.0.1:8000/api/v1"


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
        # Гарантируем наличие настройки логов ClearBat
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
        default_exe = settings.get('default_anydesk_exe', '')
        exe_path = find_anydesk_exe(custom_exe or default_exe)

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
        print(f"[*] Начато наблюдение за логом CLEAR_bat ({log_file.name}) для сервера: {server}...")
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
                    print(f"[OK] Успешный ответ лицензирования для {server} зафиксирован в логе!")
                    self._send_license_result_to_server(company_id, task_id, new_text, is_success=True)
                    return

                if has_error:
                    print(f"[!] Ошибка сервера лицензирования для {server}: {error_msg}")
                    self._send_license_result_to_server(company_id, task_id, new_text, is_success=False, error_msg=error_msg)
                    return

            except Exception as e:
                print(f"[!] Ошибка чтения лог-файла: {e}")

        print(f"[!] Мониторинг лога CLEAR_bat для {server} завершен по таймауту (33 сек).")

    def _send_license_result_to_server(self, company_id, task_id: str, log_text: str, is_success: bool, error_msg: str = None):
        if not company_id:
            if task_id:
                res = {"success": is_success, "message": "Лог получен" if is_success else error_msg}
                if error_msg:
                    res["error"] = error_msg
                self.send_task_result(task_id, res)
            return

        url = f"{self.api_url}/companies/{company_id}/license-data/"
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
                print(f"[OK] Данные лицензии заведения #{company_id} успешно доставлены на сервер!")
                return True
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8', errors='ignore')
            print(f"[!] Ошибка отправки на сервер ({e.code}): {err_body}")
        except Exception as e:
            print(f"[!] Ошибка соединения с сервером при отправке лицензии: {e}")
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
                "message": f"База ClearBat не найдена по пути: {db_path}. Настройте путь в {CONFIG_FILE}."
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

    def execute_task(self, task: dict):
        """Диспетчер вызова локальных команд."""
        action = task.get('action')
        payload = task.get('payload', {})
        task_id = task.get('task_id')
        if task_id and 'task_id' not in payload:
            payload['task_id'] = task_id

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
                "Authorization": f"Bearer {self.access_token}",
                "Connection": "close"
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
                    "Authorization": f"Bearer {self.access_token}",
                    "Connection": "close"
                }
            )

            try:
                # Таймаут 35 секунд (на бэкенде опрос длится 25 секунд)
                with urllib.request.urlopen(req, timeout=35) as resp:
                    resp_data = json.loads(resp.read().decode('utf-8'))
                    st = resp_data.get('status')
                    task = resp_data.get('task', {})

                if st == 'command' and task:
                    task_id = task.get('task_id')
                    is_async = task.get('async', False) or task.get('action') in ('launch_license', 'launch_backoffice', 'launch_anydesk')
                    result = self.execute_task(task)
                    if task_id and not is_async:
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
