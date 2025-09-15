# Google Sheets API Setup Instructions

## Проблема
Google Sheets API не включен в проекте 692790870517. Нужна активация API для загрузки данных.

## Решение

### Шаг 1: Активация Google Sheets API
1. Перейдите по ссылке: https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=692790870517
2. Нажмите кнопку "ВКЛЮЧИТЬ" (ENABLE)
3. Подождите несколько минут для активации

### Шаг 2: Проверка доступов Service Account
Убедитесь, что Service Account `replit-ik-service-account@api-project-692790870517.iam.gserviceaccount.com` имеет доступ к таблице:

1. Откройте Google Таблицу: https://docs.google.com/spreadsheets/d/1KQ7eP472By9BBR3yOStE9oJNxxcErNXp73OCbDU6oyc/
2. Нажмите "Настроить доступ" (Share)
3. Добавьте email: `replit-ik-service-account@api-project-692790870517.iam.gserviceaccount.com`
4. Дайте права "Редактор" (Editor)

### Шаг 3: Активация Google Drive API (опционально)
Для полной функциональности также активируйте:
https://console.developers.google.com/apis/api/drive.googleapis.com/overview?project=692790870517

## Альтернативные способы загрузки

### 1. Ручная загрузка TSV
1. Скачайте файл: `[rick.ai] clients/avtoall.ru/[4] whatsapp-jtbd-tracktion/results/avtoall_sales_analyzed.tsv`
2. Откройте Google Таблицу: https://docs.google.com/spreadsheets/d/1KQ7eP472By9BBR3yOStE9oJNxxcErNXp73OCbDU6oyc/
3. Перейдите на вкладку "output IK"
4. Импортируйте TSV: Файл → Импорт → Загрузить → Заменить данные

### 2. CSV экспорт для Google Sheets
```python
# Конвертация TSV в CSV с правильным разделителем
import pandas as pd
df = pd.read_csv('avtoall_sales_analyzed.tsv', sep='\t')
df.to_csv('avtoall_sales_analyzed.csv', index=False)
```

## Проверка после настройки

Запустите тест:
```bash
cd advising_platform
python -c "
import sys
sys.path.append('src')
from integrations.google_sheets.sheets_uploader import upload_avtoall_results
upload_avtoall_results()
"
```

## Текущий статус

- ✅ Service Account создан и настроен
- ✅ JSON ключи сохранены безопасно
- ✅ Код загрузки готов
- ❌ Google Sheets API не активирован
- ❌ Доступ к таблице не предоставлен

## После активации API

Система автоматически загрузит 1,465 записей с результатами анализа в вкладку "output IK".

---
**Дата**: July 22, 2025
**Статус**: Ожидает активации Google Sheets API