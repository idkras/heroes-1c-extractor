#!/usr/bin/env python3
"""
Google Sheets Integration for MCP Workflow Results
Загружает обработанные TSV данные в Google Sheets как новую вкладку
"""

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import sys
import os
import json
from datetime import datetime
from pathlib import Path
import subprocess

# Настройки Google Sheets API
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Конфигурация по умолчанию
DEFAULT_SPREADSHEET_ID = '1KQ7eP472By9BBR3yOStE9oJNxxcErNXp73OCbDU6oyc'
SERVICE_ACCOUNT_FILE = 'config/google_service_account.json'

class GoogleSheetsUploader:
    """Класс для загрузки данных в Google Sheets"""
    
    def __init__(self, service_account_path=None, spreadsheet_id=None):
        # ИСПРАВЛЕНИЕ пути для корректной работы
        if service_account_path is None:
            service_account_path = 'advising_platform/config/google_service_account.json'
        self.service_account_path = service_account_path
        self.spreadsheet_id = spreadsheet_id or DEFAULT_SPREADSHEET_ID
        self.gc = None
    
    def authenticate(self):
        """Аутентификация в Google Sheets API с поддержкой Mac Keychain"""
        try:
            credentials = None
            
            # Попробуем загрузить из файла
            if os.path.exists(self.service_account_path):
                credentials = Credentials.from_service_account_file(
                    self.service_account_path, scopes=SCOPES
                )
                print(f"✅ Loaded credentials from file: {self.service_account_path}")
            else:
                # Попробуем загрузить из Mac Keychain (если доступен)
                try:
                    keychain_data = self._load_from_keychain()
                    if keychain_data:
                        credentials = Credentials.from_service_account_info(
                            keychain_data, scopes=SCOPES
                        )
                        print(f"✅ Loaded credentials from Mac Keychain")
                    else:
                        print(f"❌ Service account file not found: {self.service_account_path}")
                        print("📋 Please ensure google_service_account.json is in advising_platform/config/ or Mac Keychain")
                        return False
                except Exception as keychain_error:
                    print(f"⚠️ Keychain access failed: {keychain_error}")
                    print(f"❌ Service account file not found: {self.service_account_path}")
                    return False
            
            if credentials:
                self.gc = gspread.authorize(credentials)
                print(f"✅ Google Sheets authentication successful")
                return True
            else:
                print(f"❌ No valid credentials found")
                return False
            
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    def _load_from_keychain(self):
        """Загрузка credentials из Mac Keychain"""
        try:
            # Попробуем получить данные из Mac Keychain
            keychain_service = "GCP-service-account-api-project-692790870517"
            keychain_account = "replit-ik-service-account@api-project-692790870517.iam.gserviceaccount.com"
            
            cmd = [
                'security', 'find-generic-password',
                '-s', keychain_service,
                '-a', keychain_account,
                '-w'  # Только пароль
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if result.stdout.strip():
                # Декодируем JSON из keychain
                return json.loads(result.stdout.strip())
            return None
            
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            # Mac Keychain недоступен или данные не найдены
            return None
    
    def upload_tsv_to_sheets(self, tsv_file_path, sheet_name=None, target_sheet_name="output IK"):
        """
        Загружает TSV файл в Google Sheets как новую вкладку или в существующую
        
        Args:
            tsv_file_path (str): Путь к TSV файлу
            sheet_name (str): Имя новой вкладки (опционально)  
            target_sheet_name (str): Имя существующей вкладки для записи
        """
        
        if not self.authenticate():
            return False, None
        
        try:
            # Открываем таблицу
            spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            print(f"✅ Connected to Google Sheets: {spreadsheet.title}")
            
            # Читаем TSV файл
            if not os.path.exists(tsv_file_path):
                print(f"❌ File not found: {tsv_file_path}")
                return False, None
                
            df = pd.read_csv(tsv_file_path, sep='\t')
            print(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns from TSV")
            
            # Пытаемся найти существующую вкладку
            worksheet = None
            try:
                worksheet = spreadsheet.worksheet(target_sheet_name)
                print(f"✅ Found existing worksheet: {target_sheet_name}")
                # Очищаем содержимое
                worksheet.clear()
            except gspread.WorksheetNotFound:
                # Создаем новую вкладку
                if sheet_name is None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                    sheet_name = f"Sales_Analysis_{timestamp}"
                
                try:
                    worksheet = spreadsheet.add_worksheet(
                        title=sheet_name,
                        rows=len(df) + 10,
                        cols=len(df.columns) + 2
                    )
                    print(f"✅ Created new worksheet: {sheet_name}")
                except Exception as e:
                    print(f"⚠️ Worksheet creation issue: {e}")
                    return False, None
            
            # Подготавливаем данные для загрузки
            headers = df.columns.tolist()
            
            # Данные (конвертируем все в строки, СОХРАНЯЯ существующие переносы строк)
            data_rows = []
            for _, row in df.iterrows():
                data_row = []
                for val in row.values:
                    if pd.notna(val):
                        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: НЕ изменяем переносы строк - они уже правильные в TSV
                        str_val = str(val)
                        # УБИРАЕМ неправильную замену: str_val = str_val.replace('\\n', '\n')
                        # В TSV уже есть НАСТОЯЩИЕ переносы \n, не экранированные \\n
                        data_row.append(str_val)
                    else:
                        data_row.append('')
                data_rows.append(data_row)
            
            # Загружаем заголовки
            worksheet.update('A1', [headers])
            print(f"✅ Headers uploaded ({len(headers)} columns)")
            
            # Проверяем и расширяем таблицу при необходимости
            try:
                current_rows = worksheet.row_count
                needed_rows = len(data_rows) + 10  # +10 для заголовков и буфера
                
                if needed_rows > current_rows:
                    worksheet.add_rows(needed_rows - current_rows)
                    print(f"✅ Expanded worksheet to {needed_rows} rows")
            except Exception as e:
                print(f"⚠️ Worksheet expansion warning: {e}")
            
            # Загружаем данные батчами
            batch_size = 100
            total_batches = (len(data_rows) + batch_size - 1) // batch_size
            
            for i in range(0, len(data_rows), batch_size):
                batch = data_rows[i:i + batch_size]
                start_row = i + 2  # +2 потому что заголовки в строке 1
                end_row = start_row + len(batch) - 1
                
                # Определяем нужный диапазон колонок
                end_col_letter = chr(ord('A') + len(headers) - 1) if len(headers) <= 26 else 'Z'
                range_name = f'A{start_row}:{end_col_letter}{end_row}'
                
                try:
                    worksheet.update(range_name, batch)
                    batch_num = i // batch_size + 1
                    print(f"✅ Batch {batch_num}/{total_batches} uploaded: rows {start_row}-{end_row}")
                except Exception as e:
                    print(f"⚠️ Batch upload error: {e}")
                    # Попробуем загрузить оставшиеся данные меньшими батчами
                    if "exceeds grid limits" in str(e):
                        print("🔧 Trying smaller batch size...")
                        for j in range(i, len(data_rows), 50):  # Уменьшаем batch до 50
                            small_batch = data_rows[j:j + 50]
                            if not small_batch:
                                break
                            try:
                                small_start = j + 2
                                small_end = small_start + len(small_batch) - 1
                                small_range = f'A{small_start}:{end_col_letter}{small_end}'
                                worksheet.update(small_range, small_batch)
                                print(f"✅ Small batch uploaded: rows {small_start}-{small_end}")
                            except Exception as small_e:
                                print(f"⚠️ Small batch failed: {small_e}")
                                break
                        break
            
            # УБРАНО ВСЕ ФОРМАТИРОВАНИЕ согласно требованию пользователя
            # Используется только существующее форматирование шаблона Google Sheets
            print(f"✅ Data uploaded using existing template formatting")
            
            # Получаем ссылку
            sheet_url = f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/edit#gid={worksheet.id}"
            
            print(f"🎯 Upload complete!")
            print(f"📊 Uploaded {len(data_rows)} rows to '{worksheet.title}'")
            print(f"🔗 Direct link: {sheet_url}")
            
            return True, sheet_url
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            import traceback
            traceback.print_exc()
            return False, None


def upload_avtoall_results():
    """Быстрая загрузка результатов Avtoall v4 в Google Sheets"""
    
    uploader = GoogleSheetsUploader()
    
    # Путь к результатам v4 (относительно корня проекта)
    results_file = "../[rick.ai] clients/avtoall.ru/[4] whatsapp-jtbd-tracktion/results/avtoall_sales_analyzed_v4.tsv"
    
    # Альтернативный путь от корня
    if not os.path.exists(results_file):
        results_file = "[rick.ai] clients/avtoall.ru/[4] whatsapp-jtbd-tracktion/results/avtoall_sales_analyzed_v4.tsv"
    
    if not os.path.exists(results_file):
        print(f"⚠️ Results file v4 not found in expected locations")
        print("Checking current directory for v4 TSV files...")
        # Поиск TSV файлов v4 сначала, затем других
        import glob
        tsv_files = glob.glob("**/*analyzed_v4*.tsv", recursive=True)
        if not tsv_files:
            tsv_files = glob.glob("**/*analyzed*.tsv", recursive=True)
        if tsv_files:
            results_file = tsv_files[0]
            print(f"📁 Found TSV file: {results_file}")
        else:
            print("❌ No TSV files found")
            return False
    
    print(f"🚀 Uploading Avtoall sales analysis v4 results from: {results_file}")
    success, url = uploader.upload_tsv_to_sheets(results_file, target_sheet_name="output IK")
    
    if success:
        print(f"✅ SUCCESS! Results uploaded to Google Sheets")
        print(f"🔗 URL: {url}")
    else:
        print(f"❌ Upload failed")
    
    return success


def upload_tsv_with_line_breaks_fix(tsv_file_path, worksheet_name="calls jtbd IK"):
    """
    Загрузка TSV файла в Google Sheets с исправлением line breaks и text wrapping
    КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ для правильного отображения переносов строк
    """
    uploader = GoogleSheetsUploader()
    
    if not uploader.authenticate():
        return False
    
    try:
        # Открываем spreadsheet
        spreadsheet = uploader.gc.open_by_key(uploader.spreadsheet_id)
        print(f"✅ Opened spreadsheet: {spreadsheet.title}")
        
        # Читаем TSV файл с сохранением line breaks
        df = pd.read_csv(tsv_file_path, sep='\t', encoding='utf-8', keep_default_na=False)
        print(f"✅ Read TSV file: {len(df)} rows, {len(df.columns)} columns")
        
        # Проверяем/создаем вкладку
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            print(f"✅ Found existing worksheet: {worksheet_name}")
            worksheet.clear()  # Очищаем существующие данные
        except gspread.WorksheetNotFound:
            # Создаем новую вкладку
            worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=len(df)+100, cols=len(df.columns)+5)
            print(f"✅ Created new worksheet: {worksheet_name}")
        
        # Подготавливаем данные для загрузки с сохранением переносов строк
        headers = df.columns.tolist()
        
        # Обрабатываем данные для сохранения line breaks
        data = []
        for _, row in df.iterrows():
            processed_row = []
            for value in row:
                if pd.isna(value):
                    processed_row.append("")
                else:
                    # Сохраняем переносы строк как есть
                    processed_row.append(str(value))
            data.append(processed_row)
        
        # Добавляем заголовки в начало
        all_data = [headers] + data
        
        # Загружаем данные
        worksheet.update(range_name='A1', values=all_data)
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: применяем text wrapping для корректного отображения переносов строк
        print("🔧 Applying text wrapping and formatting...")
        
        # Определяем диапазон данных
        end_col_letter = chr(ord('A') + len(headers) - 1)  # A, B, C, etc.
        
        # Применяем форматирование с text wrapping
        format_request = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": worksheet.id,
                            "startRowIndex": 0,
                            "endRowIndex": len(all_data),
                            "startColumnIndex": 0,
                            "endColumnIndex": len(headers)
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "wrapStrategy": "WRAP",
                                "verticalAlignment": "TOP"
                            }
                        },
                        "fields": "userEnteredFormat.wrapStrategy,userEnteredFormat.verticalAlignment"
                    }
                }
            ]
        }
        
        # Выполняем форматирование
        spreadsheet.batch_update(format_request)
        print("✅ Text wrapping applied successfully")
        
        print(f"✅ Successfully uploaded {len(df)} rows to worksheet '{worksheet_name}'")
        print(f"🔗 Access at: https://docs.google.com/spreadsheets/d/{uploader.spreadsheet_id}/edit#gid={worksheet.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False


if __name__ == "__main__":
    upload_avtoall_results()