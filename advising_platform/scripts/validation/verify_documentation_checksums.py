#!/usr/bin/env python3
"""
Documentation Checksums Verifier
Проверяет контрольные суммы защищенных файлов MCP
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src' / 'mcp' / 'modules'))

from documentation_validator import MCPDocumentationValidator


def main():
    """Основная функция проверки контрольных сумм"""
    validator = MCPDocumentationValidator()
    
    print("🔐 Проверка контрольных сумм защищенных файлов...")
    
    # Запускаем проверку контрольных сумм
    checksums_result = validator._validate_checksums()
    
    if checksums_result['status'] == 'passed':
        if 'action' in checksums_result and checksums_result['action'] == 'created_checksums':
            print("✅ Контрольные суммы созданы для защищенных файлов")
        else:
            print("✅ Все контрольные суммы совпадают")
            
        # Показываем проверенные файлы
        if 'checksums' in checksums_result:
            for file_key, checksum_info in checksums_result['checksums'].items():
                status = "✅" if checksum_info['match'] else "❌"
                print(f"   {status} {file_key}")
        
        return 0
        
    else:
        print("❌ Обнаружены несоответствия контрольных сумм:")
        
        if 'checksums' in checksums_result:
            for file_key, checksum_info in checksums_result['checksums'].items():
                if not checksum_info['match']:
                    print(f"   ❌ {file_key}: файл был изменен")
                    print(f"      Текущий:   {checksum_info['current'][:16]}...")
                    print(f"      Сохранен:  {checksum_info['stored'][:16]}...")
        
        print("\n⚠️  Внимание: Все изменения защищенных файлов должны")
        print("   проходить через MCP workflow с авторизацией [MCP-AUTHORIZED]")
        
        return 1


if __name__ == '__main__':
    sys.exit(main())