#!/usr/bin/env python3

"""
Скрипт для исправления оставшихся ошибок линтера
JTBD: Как система исправления ошибок линтера, я хочу исправить оставшиеся
ошибки которые не могут быть исправлены автоматически.
"""

import os
import re
import subprocess
import sys
from pathlib import Path


def fix_print_statements(file_path: str) -> bool:
    """Заменить print statements на logging"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Проверяем есть ли уже logging
        has_logging = "import logging" in content or "from logging" in content

        if not has_logging:
            # Добавляем import logging в начало файла
            lines = content.split("\n")
            import_line = -1
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    import_line = i

            if import_line >= 0:
                lines.insert(import_line + 1, "import logging")
                lines.insert(import_line + 2, "")
                lines.insert(import_line + 3, "logger = logging.getLogger(__name__)")
                content = "\n".join(lines)

        # Заменяем print statements
        content = re.sub(r"print\(", "logger.info(", content)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"❌ Ошибка при исправлении print statements в {file_path}: {e}")
        return False


def fix_shebang_in_py_files(file_path: str) -> bool:
    """Удалить shebang из .py файлов которые не должны быть исполняемыми"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Удаляем shebang если файл не должен быть исполняемым
        if content.startswith("#!/usr/bin/env python3\n"):
            content = content.replace("#!/usr/bin/env python3\n", "")
            # Убираем лишние пустые строки в начале
            content = content.lstrip("\n")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"❌ Ошибка при удалении shebang из {file_path}: {e}")
        return False


def fix_long_lines(file_path: str) -> bool:
    """Разбить длинные строки"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            if len(line) > 88 and not line.strip().startswith("#"):
                # Разбиваем длинные строки
                if 'f"' in line and "{" in line:
                    # F-strings - разбиваем по логическим местам
                    if 'f"' in line:
                        # Простое разбиение f-strings
                        if len(line) > 88:
                            # Находим место для разбиения
                            parts = line.split('f"')
                            if len(parts) > 1:
                                # Разбиваем f-string
                                before_f = parts[0] + 'f"'
                                f_content = parts[1]
                                if len(before_f) + len(f_content) > 88:
                                    # Разбиваем на несколько строк
                                    indent = len(line) - len(line.lstrip())
                                    spaces = " " * (indent + 4)
                                    fixed_line = (
                                        before_f
                                        + f_content[:50]
                                        + '"\n'
                                        + spaces
                                        + f_content[50:]
                                    )
                                    fixed_lines.append(fixed_line)
                                else:
                                    fixed_lines.append(line)
                            else:
                                fixed_lines.append(line)
                        else:
                            fixed_lines.append(line)
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(fixed_lines))

        return True
    except Exception as e:
        print(f"❌ Ошибка при разбиении длинных строк в {file_path}: {e}")
        return False


def fix_exception_handling(file_path: str) -> bool:
    """Исправить обработку исключений"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Заменяем except Exception: на except Exception as e:
        content = re.sub(r"except Exception:", "except Exception as e:", content)

        # Заменяем {e} на {e} в f-strings
        content = re.sub(r"\{e\}", "{e}", content)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"❌ Ошибка при исправлении обработки исключений в {file_path}: {e}")
        return False


def fix_dict_keys_usage(file_path: str) -> bool:
    """Исправить использование .keys()"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Заменяем .keys() на прямую итерацию
        content = re.sub(r"for (\w+) in (\w+)\.keys\(\):", r"for \1 in \2:", content)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"❌ Ошибка при исправлении .keys() в {file_path}: {e}")
        return False


def fix_open_usage(file_path: str) -> bool:
    """Заменить open() на Path.open()"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Добавляем import Path если его нет
        if "from pathlib import Path" not in content and "open(" in content:
            lines = content.split("\n")
            import_line = -1
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    import_line = i

            if import_line >= 0:
                lines.insert(import_line + 1, "from pathlib import Path")
                content = "\n".join(lines)

        # Заменяем open() на Path().open()
        content = re.sub(r"open\(([^)]+)\)", r"Path(\1).open()", content)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"❌ Ошибка при замене open() в {file_path}: {e}")
        return False


def fix_datetime_usage(file_path: str) -> bool:
    """Исправить использование datetime.now()"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Заменяем datetime.now() на datetime.now(timezone.utc)
        if "datetime.now()" in content:
            # Добавляем import timezone если его нет
            if "from datetime import timezone" not in content:
                lines = content.split("\n")
                import_line = -1
                for i, line in enumerate(lines):
                    if "from datetime import" in line:
                        import_line = i
                        break

                if import_line >= 0:
                    lines[import_line] = lines[import_line].replace(
                        "from datetime import datetime",
                        "from datetime import datetime, timezone",
                    )
                    content = "\n".join(lines)

            # Заменяем datetime.now() на datetime.now(timezone.utc)
            content = content.replace("datetime.now()", "datetime.now(timezone.utc)")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"❌ Ошибка при исправлении datetime в {file_path}: {e}")
        return False


def main():
    """Основная функция"""
    print("🔧 Исправление оставшихся ошибок линтера...")

    # Получаем список файлов с ошибками
    result = subprocess.run(
        ["bash", "-c", "source .venv/bin/activate && ruff check --no-fix"],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    if result.returncode != 0:
        print("❌ Ошибка при получении списка файлов с ошибками")
        return False

    # Парсим вывод и получаем файлы
    files_with_errors = set()
    for line in result.stdout.split("\n"):
        if "-->" in line:
            file_path = line.split("-->")[1].split(":")[0].strip()
            files_with_errors.add(file_path)

    print(f"📊 Найдено файлов с ошибками: {len(files_with_errors)}")

    fixed_count = 0
    error_count = 0

    for file_path in files_with_errors:
        if not os.path.exists(file_path):
            continue

        print(f"🔧 Исправление {file_path}...")

        try:
            # Применяем все исправления
            fixes = [
                fix_print_statements,
                fix_shebang_in_py_files,
                fix_long_lines,
                fix_exception_handling,
                fix_dict_keys_usage,
                fix_open_usage,
                fix_datetime_usage,
            ]

            success = True
            for fix_func in fixes:
                if not fix_func(file_path):
                    success = False
                    break

            if success:
                fixed_count += 1
                print(f"✅ {file_path}: Исправлено")
            else:
                error_count += 1
                print(f"❌ {file_path}: Ошибки при исправлении")

        except Exception as e:
            error_count += 1
            print(f"❌ {file_path}: Исключение: {e}")

    print("\n📊 Результат исправления:")
    print(f"   ✅ Исправлено: {fixed_count}")
    print(f"   ❌ Ошибки: {error_count}")

    return error_count == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
