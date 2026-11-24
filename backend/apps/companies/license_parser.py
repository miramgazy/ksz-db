"""
Модуль парсинга логов CLEAR_bat для извлечения информации о лицензиях заведений iiko.
Поддерживает:
1. Парсинг успешного ответа: реквизиты (CRMID, UID, CompanyName, expiration, generated, version, edition)
   и таблицу активных модулей с количеством подключений и сроками (From - To).
2. Распознавание и извлечение ошибок сервера (сервер выключен, DNS-ошибка, таймаут, 401).
"""

import re
from datetime import datetime
from typing import Dict, Any, List, Optional


def clean_str(val: Optional[str]) -> str:
    return val.strip() if val else ""


def parse_clearbat_license_log(text: str) -> Dict[str, Any]:
    """
    Парсит фрагмент или полный лог CLEAR_bat.
    Возвращает dict с флагом 'success': True/False и разобранными полями.
    """
    if not text or not text.strip():
        return {
            "success": False,
            "error": "Пустой лог ответа от CLEAR_bat",
            "raw_error": "Empty log",
        }

    lines = [line.strip() for line in text.splitlines()]

    # 1. Проверяем наличие ошибки в логе (ERROR, Невозможно разрешить удаленное имя и т.д.)
    error_match = None
    for line in lines:
        if "ERROR!" in line:
            m = re.search(r"ERROR!\s*(.*)", line)
            if m:
                error_match = m.group(1).strip()
                break
        elif "[ERROR]" in line:
            m = re.search(r"\[ERROR\](?:\[[^\]]+\])?\s*(.*)", line)
            if m:
                # Отрезаем возможный стек-трейс C#
                err_text = m.group(1).split("в System.")[0].strip()
                if err_text:
                    error_match = err_text
                    break

    # Дополнительные типовые ошибки сети и сервера
    if not error_match:
        for line in lines:
            if "Невозможно разрешить удаленное имя" in line:
                error_match = line.split("в System.")[0].strip()
                break
            elif "Не удалось подключиться к удаленному серверу" in line:
                error_match = "Не удалось подключиться к удаленному серверу (соединение разорвано)"
                break
            elif "Время ожидания операции истекло" in line:
                error_match = "Время ожидания ответа от сервера истекло (Connection Timeout)"
                break
            elif "(401) Несанкционированный" in line or "401 Unauthorized" in line:
                error_match = "Ошибка авторизации (401 Unauthorized): неверный логин или пароль"
                break

    # 2. Ищем секцию Licenses info:
    # Ищем с конца, чтобы взять последнюю запись в логе
    lic_info_idx = -1
    for i in range(len(lines) - 1, -1, -1):
        if "Licenses info:" in lines[i]:
            lic_info_idx = i
            break

    if lic_info_idx == -1:
        # Если блок лицензий не найден, но была ошибка — возвращаем ошибку
        if error_match:
            clean_err = error_match
            if "Невозможно разрешить удаленное имя" in clean_err:
                clean_err += " (Сервер выключен, имя домена недоступно или не существует)"
            return {
                "success": False,
                "error": clean_err,
                "raw_error": error_match,
            }
        return {
            "success": False,
            "error": "В логе не найден блок информации о лицензиях (Licenses info:)",
            "raw_error": "No licenses info found",
        }

    # 3. Извлекаем версию iiko и Edition перед блоком Licenses info
    version = ""
    edition = ""
    # Просматриваем до 20 строк перед lic_info_idx
    search_start = max(0, lic_info_idx - 25)
    for j in range(lic_info_idx - 1, search_start - 1, -1):
        line = lines[j]
        v_match = re.search(r"Version\s*-\s*([0-9.]+)\s+Edition\s*-\s*([A-Za-z0-9_]+)", line)
        if v_match:
            version = v_match.group(1).strip()
            edition = v_match.group(2).strip()
            break
        elif "Version -" in line:
            v_match2 = re.search(r"Version\s*-\s*([0-9.]+)", line)
            if v_match2:
                version = v_match2.group(1).strip()
            e_match2 = re.search(r"Edition\s*-\s*([A-Za-z0-9_]+)", line)
            if e_match2:
                edition = e_match2.group(1).strip()
            if version:
                break

    # 4. Извлекаем метаданные лицензии из строк после Licenses info:
    company_name = ""
    uid = ""
    crm_id = ""
    generated = ""
    expiration = ""

    table_header_idx = -1
    for idx in range(lic_info_idx + 1, min(len(lines), lic_info_idx + 20)):
        line = lines[idx]
        if line.startswith("CompanyName -"):
            company_name = clean_str(line.replace("CompanyName -", ""))
        elif line.startswith("UID -"):
            uid = clean_str(line.replace("UID -", ""))
        elif line.startswith("CRMID -"):
            crm_id = clean_str(line.replace("CRMID -", ""))
        elif line.startswith("generated -"):
            generated = clean_str(line.replace("generated -", ""))
        elif line.startswith("expiration -"):
            expiration = clean_str(line.replace("expiration -", ""))
        elif "Name | ID | ConnectionsCount" in line or (line.startswith("Name") and "|" in line):
            table_header_idx = idx
            break

    # 5. Парсим таблицу модулей
    modules: List[Dict[str, Any]] = []
    if table_header_idx != -1:
        for idx in range(table_header_idx + 1, len(lines)):
            line = lines[idx]
            # Маркер окончания таблицы
            if not line or "[LicenseArgs]" in line or "[INFO]" in line or "[DEPLOY]" in line:
                break
            if "|" not in line:
                continue

            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                mod_name = parts[0]
                mod_id = parts[1]
                try:
                    count = int(parts[2])
                except (ValueError, TypeError):
                    count = 1

                date_from = parts[3] if len(parts) > 3 and parts[3] else None
                date_to = parts[4] if len(parts) > 4 and parts[4] else None

                modules.append({
                    "name": mod_name,
                    "id": mod_id,
                    "count": count,
                    "from": date_from,
                    "to": date_to,
                })

    return {
        "success": True,
        "company_name": company_name,
        "uid": uid,
        "crm_id": crm_id,
        "generated": generated,
        "expiration": expiration,
        "iiko_version": version,
        "edition": edition,
        "modules_count": len(modules),
        "modules": modules,
        "parsed_at": datetime.now().isoformat(),
    }
