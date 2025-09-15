# Mac Keychain Integration для Google Service Account

## Обзор
Храните Google Service Account ключи безопасно в Mac Keychain вместо файлов на диске.

## Настройка Mac Keychain

### Шаг 1: Сохранение ключей в Keychain
```bash
# Сохранить JSON credentials в Mac Keychain
security add-generic-password \
  -s "google-service-account" \
  -a "replit-ik-service-account" \
  -w '{"type":"service_account","project_id":"api-project-692790870517",...}' \
  -T /System/Applications/Python.app/Contents/MacOS/Python
```

### Шаг 2: Проверка сохранения
```bash
# Проверить, что ключи сохранились
security find-generic-password \
  -s "google-service-account" \
  -a "replit-ik-service-account" \
  -w
```

## Автоматическое использование

Код автоматически проверяет:
1. **Файл**: `advising_platform/config/google_service_account.json`
2. **Mac Keychain**: если файла нет
3. **Fallback**: сообщение об ошибке

## Преимущества Mac Keychain

### Безопасность
- ✅ Ключи зашифрованы в системном keychain
- ✅ Требует аутентификацию пользователя
- ✅ Не сохраняются в файлах на диске
- ✅ Автоматическое управление доступом

### Удобство
- ✅ Центральное место для всех секретов
- ✅ Интеграция с macOS Security Framework
- ✅ Автоматическая синхронизация с iCloud Keychain (опционально)

## Альтернативные методы хранения

### 1. Environment Variables
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service_account.json"
```

### 2. Replit Secrets (для продакшена)
```python
import os
import json
credentials_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT')
credentials = json.loads(credentials_json)
```

### 3. External Secret Managers
- AWS Secrets Manager
- HashiCorp Vault  
- Azure Key Vault

## Использование

Код автоматически определяет доступный метод:

```python
from integrations.google_sheets.sheets_uploader import GoogleSheetsUploader

# Автоматически попробует:
# 1. Файл в config/
# 2. Mac Keychain
uploader = GoogleSheetsUploader()
success, url = uploader.upload_tsv_to_sheets("data.tsv")
```

## Troubleshooting

### Ошибка доступа к Keychain
```
⚠️ Keychain access failed: Command '[security, find-generic-password, ...]' returned non-zero exit status 44
```

**Решение**: Убедитесь, что:
1. Ключи сохранены в Keychain
2. Python приложение имеет доступ к Keychain
3. Используется правильное имя сервиса и аккаунта

### Права доступа
Добавьте Python в список доверенных приложений:
```bash
security add-generic-password \
  -s "google-service-account" \
  -a "replit-ik-service-account" \
  -w 'JSON_DATA_HERE' \
  -T /usr/bin/python3 \
  -T /usr/local/bin/python3
```

## Статус реализации

- ✅ Поддержка Mac Keychain в коде
- ✅ Fallback на файловое хранение
- ✅ Автоматическое определение метода
- ✅ Error handling для всех сценариев
- 📋 Документация и инструкции

---

**Создано**: July 22, 2025  
**Совместимость**: macOS 10.12+, Python 3.7+