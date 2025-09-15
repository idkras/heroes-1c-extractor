#!/usr/bin/env python3
"""
Бережная загрузка в Google Sheets с поиском колонок по названиям
Согласно Registry Standard v4.7 и требованиям пользователя
"""

import gspread
from google.oauth2.service_account import Credentials
import json
import logging
import argparse
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_column_by_name(worksheet, column_name, max_search_range=20):
    """
    Находит колонку по названию (бережный поиск)
    
    Args:
        worksheet: gspread worksheet объект
        column_name: название колонки для поиска
        max_search_range: максимальный диапазон поиска
    
    Returns:
        int: номер колонки (1-based) или None если не найдена
    """
    try:
        # Получаем первую строку (заголовки)
        header_row = worksheet.row_values(1)
        
        # Ищем точное совпадение
        for i, header in enumerate(header_row[:max_search_range], 1):
            if header.strip().lower() == column_name.strip().lower():
                logger.info(f"📍 Found {column_name} at column {i}")
                return i
        
        # Если точного совпадения нет, ищем частичное
        for i, header in enumerate(header_row[:max_search_range], 1):
            if column_name.strip().lower() in header.strip().lower():
                logger.info(f"📍 Found partial match for {column_name} at column {i}: '{header}'")
                return i
        
        logger.warning(f"❌ Column '{column_name}' not found in header row")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error finding column {column_name}: {e}")
        return None

def upload_with_user_settings(spreadsheet_id, worksheet_name, tsv_file, target_columns=None):
    """
    Бережная загрузка данных в Google Sheets
    
    Args:
        spreadsheet_id: ID Google Sheets документа
        worksheet_name: название листа (НЕ gid)
        tsv_file: путь к TSV файлу
        target_columns: список названий колонок для обновления
    """
    
    # DEFAULT TARGET COLUMNS (пользователь может изменить)
    if target_columns is None:
        target_columns = [
            "sale blockers",
            "when_trigger_situation", 
            "root cause 5why",
            "stop_words_patterns",
            "recommended_phrases"
        ]
    
    try:
        logger.info("🚀 Starting user-friendly Google Sheets upload")
        logger.info("🔐 Authenticating with Google Sheets API")
        
        # Load credentials (Registry Standard: atomic operation)
        try:
            with open("advising_platform/config/google_service_account.json", 'r') as f:
                creds_data = json.load(f)
        except FileNotFoundError:
            logger.error("❌ Service account credentials not found")
            return False
        
        # Create credentials (Registry Standard: reflection checkpoint)
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_info(creds_data, scopes=scopes)
        gc = gspread.authorize(credentials)
        
        logger.info("✅ Authentication successful")
        
        # Open spreadsheet (Registry Standard: atomic operation)
        sheet = gc.open_by_key(spreadsheet_id)
        logger.info(f"📊 Opened spreadsheet: {sheet.title}")
        
        # Find worksheet BY NAME (НЕ по gid!)
        target_worksheet = None
        for ws in sheet.worksheets():
            if ws.title.strip() == worksheet_name.strip():
                target_worksheet = ws
                break
        
        if not target_worksheet:
            logger.error(f"❌ Target worksheet '{worksheet_name}' not found")
            available = [ws.title for ws in sheet.worksheets()]
            logger.info(f"Available worksheets: {available}")
            return False
        
        logger.info(f"✅ Found target worksheet: {target_worksheet.title}")
        
        # Read TSV file (Registry Standard: reflection checkpoint)
        logger.info(f"📂 Reading data from: {tsv_file}")
        with open(tsv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Parse TSV data
        data_rows = []
        for line in lines:
            if line.strip():
                row_data = line.strip().split('\t')
                data_rows.append(row_data)
        
        logger.info(f"📊 Parsed {len(data_rows)} rows (including header)")
        
        if len(data_rows) < 2:
            logger.error("❌ No data rows found in TSV file")
            return False
        
        # Extract TSV structure
        tsv_header = data_rows[0]
        tsv_data = data_rows[1:]
        
        logger.info(f"📊 TSV header: {tsv_header}")
        logger.info(f"📊 Data rows: {len(tsv_data)}")
        
        # БЕРЕЖНОЕ ОБНОВЛЕНИЕ: находим колонки по названиям
        column_mappings = {}
        
        for target_col in target_columns:
            # Находим в TSV
            tsv_index = None
            for i, header in enumerate(tsv_header):
                if header.strip().lower() == target_col.strip().lower():
                    tsv_index = i
                    break
            
            # Находим в Google Sheets
            sheets_column = find_column_by_name(target_worksheet, target_col)
            
            if tsv_index is not None and sheets_column is not None:
                column_mappings[target_col] = {
                    'tsv_index': tsv_index,
                    'sheets_column': sheets_column
                }
                logger.info(f"📍 Found {target_col} at index {tsv_index}")
            else:
                logger.warning(f"⚠️ Could not map column: {target_col}")
        
        if not column_mappings:
            logger.error("❌ No columns could be mapped")
            return False
        
        # ОБНОВЛЕНИЕ БЕЗ ФОРМАТИРОВАНИЯ (Registry Standard: atomic operations)
        updates_count = 0
        
        for target_col, mapping in column_mappings.items():
            tsv_index = mapping['tsv_index']
            sheets_column = mapping['sheets_column']
            
            # Подготавливаем данные для колонки
            column_data = []
            for row in tsv_data:
                if tsv_index < len(row):
                    cell_value = row[tsv_index]
                    column_data.append([cell_value])  # gspread требует 2D array
                else:
                    column_data.append([""])  # пустая ячейка если данных нет
            
            # Обновляем колонку (НАЧИНАЯ СО СТРОКИ 2, чтобы не затронуть заголовки)
            if column_data:
                range_name = f"{chr(64 + sheets_column)}2:{chr(64 + sheets_column)}{len(column_data) + 1}"
                
                # КРИТИЧНО: НЕ ПРИМЕНЯЕМ НИКАКОГО ФОРМАТИРОВАНИЯ
                target_worksheet.update(range_name, column_data)
                
                logger.info(f"✅ Updated {target_col} in column {chr(64 + sheets_column)}: {len(column_data)} cells")
                updates_count += len(column_data)
        
        logger.info(f"✅ Successfully updated {updates_count} cells in target worksheet")
        logger.info(f"🔗 Direct link: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={target_worksheet.id}")
        logger.info("✅ Upload completed successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        return False

def main():
    """Main function with user-friendly arguments"""
    parser = argparse.ArgumentParser(description="Бережная загрузка в Google Sheets")
    parser.add_argument("--spreadsheet-id", required=True, help="ID Google Sheets документа")
    parser.add_argument("--worksheet-name", required=True, help="Название листа (НЕ gid)")
    parser.add_argument("--tsv-file", required=True, help="Путь к TSV файлу")
    parser.add_argument("--columns", nargs='+', help="Список колонок для обновления")
    parser.add_argument("--test-run", action='store_true', help="Тестовый запуск (только проверка)")
    
    args = parser.parse_args()
    
    if args.test_run:
        logger.info("🧪 TEST RUN MODE - никаких изменений не будет")
        # TODO: добавить проверку доступности файлов и листов
        return
    
    success = upload_with_user_settings(
        spreadsheet_id=args.spreadsheet_id,
        worksheet_name=args.worksheet_name,
        tsv_file=args.tsv_file,
        target_columns=args.columns
    )
    
    if success:
        logger.info("🎉 UPLOAD SUCCESSFUL")
        sys.exit(0)
    else:
        logger.error("💥 UPLOAD FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()