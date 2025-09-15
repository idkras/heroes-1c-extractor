#!/usr/bin/env python3
"""
MCP Checksums Updater
Обновляет контрольные суммы после авторизованных изменений MCP файлов
"""

import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src' / 'mcp' / 'modules'))

from documentation_validator import MCPDocumentationValidator


def main():
    """Обновляет контрольные суммы защищенных файлов"""
    validator = MCPDocumentationValidator()
    
    print("🔄 Обновление контрольных сумм MCP файлов...")
    
    checksums_file = validator.project_root / '.mcp_checksums.json'
    checksums = {}
    
    # Вычисляем новые контрольные суммы для всех защищенных файлов
    for file_key, file_path in validator.protected_files.items():
        if file_path.exists():
            new_checksum = validator._calculate_checksum(file_path)
            checksums[file_key] = {
                'checksum': new_checksum,
                'path': str(file_path.relative_to(validator.project_root)),
                'last_updated': validator._get_timestamp(),
                'updated_by': 'mcp_authorized_update'
            }
            print(f"   ✅ {file_key}: {new_checksum[:16]}...")
        else:
            print(f"   ⚠️  {file_key}: файл не найден")
    
    # Сохраняем обновленные контрольные суммы
    validator._save_checksums(checksums_file, checksums)
    
    print(f"✅ Контрольные суммы обновлены: {len(checksums)} файлов")
    print(f"📁 Сохранено в: {checksums_file}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())