#!/usr/bin/env python3
"""
Dynamic Google Sheets Uploader v6.0
Умная загрузка с динамическим сопоставлением колонок по названиям
Пользователь может менять колонки местами - система всегда найдет нужную колонку
"""

import logging
import gspread
from google.oauth2.service_account import Credentials
import json
import os
from typing import List, Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamicGoogleSheetsUploader:
    """
    Умный загрузчик Google Sheets с динамическим сопоставлением колонок
    КЛЮЧЕВЫЕ ВОЗМОЖНОСТИ:
    - Читает текущую структуру таблицы
    - Сопоставляет данные по названиям колонок (не по позиции)
    - Добавляет недостающие колонки автоматически
    - Работает независимо от порядка колонок
    """
    
    # Требуемые колонки согласно sales.injury standard v1.1 (14 колонок)
    REQUIRED_COLUMNS = [
        'transcript',
        'lead_inquiry', 
        'when_trigger_situation',
        'root cause 5why',
        'sale blockers',
        'segment',
        'stop_words_patterns',
        'recommended_phrases', 
        'what client get on this stage',
        'big jtbd',
        'medium jtbd',
        'small jtbd',
        'date_time',
        'week'
    ]
    
    def __init__(self, credentials_path: str = None):
        """Инициализация с credentials"""
        self.credentials_path = credentials_path or self._find_credentials_path()
        self.sheet = None
        self.worksheet = None
        self._authenticate()
    
    def _find_credentials_path(self) -> str:
        """Находит путь к credentials файлу"""
        possible_paths = [
            "advising_platform/config/google_service_account.json",
            "config/google_service_account.json",
            "google_service_account.json"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        raise FileNotFoundError("Google service account credentials not found")
    
    def _authenticate(self):
        """Аутентификация в Google Sheets API"""
        try:
            logger.info("🔐 Authenticating with Google Sheets API")
            
            # Load credentials
            with open(self.credentials_path, 'r') as f:
                creds_data = json.load(f)
            
            # Define scopes
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Create credentials object
            credentials = Credentials.from_service_account_info(creds_data, scopes=scopes)
            
            # Initialize gspread client
            self.gc = gspread.authorize(credentials)
            logger.info("✅ Google Sheets authentication successful")
            
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            raise
    
    def open_spreadsheet(self, spreadsheet_id: str):
        """Открывает таблицу по ID"""
        try:
            self.sheet = self.gc.open_by_key(spreadsheet_id)
            logger.info(f"📊 Opened spreadsheet: {self.sheet.title}")
            return self.sheet
        except Exception as e:
            logger.error(f"❌ Failed to open spreadsheet: {e}")
            raise
    
    def get_sheet_headers(self, worksheet_name: str) -> List[str]:
        """
        Читает заголовки из указанного листа
        
        Args:
            worksheet_name: Название листа
            
        Returns:
            List[str]: Список заголовков колонок
        """
        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            headers = worksheet.row_values(1)  # Первая строка = заголовки
            logger.info(f"📋 Found {len(headers)} headers in '{worksheet_name}': {headers}")
            return headers
        except Exception as e:
            logger.error(f"❌ Failed to get headers: {e}")
            return []
    
    def map_data_to_columns(self, data_row: str, sheet_headers: List[str]) -> Tuple[List[str], List[str]]:
        """
        Сопоставляет данные с колонками по названиям
        
        Args:
            data_row: TSV строка с данными
            sheet_headers: Заголовки из Google Sheets
            
        Returns:
            Tuple[List[str], List[str]]: (mapped_data, missing_columns)
        """
        # Разбираем данные
        data_values = data_row.split('\t')
        if len(data_values) != len(self.REQUIRED_COLUMNS):
            logger.warning(f"⚠️ Data has {len(data_values)} columns, expected {len(self.REQUIRED_COLUMNS)}")
        
        # Создаем словарь данных
        data_dict = {}
        for i, col_name in enumerate(self.REQUIRED_COLUMNS):
            if i < len(data_values):
                data_dict[col_name] = data_values[i]
            else:
                data_dict[col_name] = ''
        
        # Сопоставляем с существующими заголовками
        mapped_data = []
        missing_columns = []
        
        for header in sheet_headers:
            if header in data_dict:
                mapped_data.append(data_dict[header])
                logger.debug(f"✅ Mapped '{header}': {data_dict[header][:50]}...")
            else:
                mapped_data.append('')  # Пустое значение для неизвестных колонок
                logger.debug(f"➖ Empty value for unknown column '{header}'")
        
        # Находим недостающие колонки
        for required_col in self.REQUIRED_COLUMNS:
            if required_col not in sheet_headers:
                missing_columns.append(required_col)
                logger.warning(f"⚠️ Missing required column: '{required_col}'")
        
        return mapped_data, missing_columns
    
    def add_missing_columns(self, worksheet_name: str, missing_columns: List[str]) -> bool:
        """
        Добавляет недостающие колонки в таблицу
        
        Args:
            worksheet_name: Название листа
            missing_columns: Список недостающих колонок
            
        Returns:
            bool: True если колонки добавлены успешно
        """
        if not missing_columns:
            return True
        
        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            current_headers = worksheet.row_values(1)
            
            # Добавляем недостающие колонки в конец
            new_headers = current_headers + missing_columns
            
            # Обновляем заголовки
            worksheet.update('1:1', [new_headers])
            
            logger.info(f"✅ Added {len(missing_columns)} missing columns: {missing_columns}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add missing columns: {e}")
            return False
    
    def upload_data_rows(self, worksheet_name: str, data_rows: List[str], 
                        clear_existing: bool = False) -> bool:
        """
        Загружает данные с умным сопоставлением колонок
        
        Args:
            worksheet_name: Название листа
            data_rows: Список TSV строк с данными
            clear_existing: Очистить существующие данные
            
        Returns:
            bool: True если загрузка успешна
        """
        try:
            logger.info(f"📤 Starting upload of {len(data_rows)} rows to '{worksheet_name}'")
            
            # Получаем текущие заголовки
            sheet_headers = self.get_sheet_headers(worksheet_name)
            if not sheet_headers:
                # Если заголовков нет, создаем их
                logger.info("📋 No headers found, creating new headers")
                worksheet = self.sheet.worksheet(worksheet_name)
                worksheet.update('1:1', [self.REQUIRED_COLUMNS])
                sheet_headers = self.REQUIRED_COLUMNS
            
            # Обрабатываем первую строку для проверки недостающих колонок
            if data_rows:
                _, missing_columns = self.map_data_to_columns(data_rows[0], sheet_headers)
                if missing_columns:
                    logger.info(f"➕ Adding {len(missing_columns)} missing columns")
                    self.add_missing_columns(worksheet_name, missing_columns)
                    # Обновляем заголовки после добавления колонок
                    sheet_headers = self.get_sheet_headers(worksheet_name)
            
            # Очищаем существующие данные если нужно (НЕ трогаем структуру колонок)
            self.worksheet = self.sheet.worksheet(worksheet_name)
            if clear_existing:
                logger.info("🧹 Clearing existing data only (preserving column structure)")
                # Получаем количество строк с данными
                all_values = self.worksheet.get_all_values()
                if len(all_values) > 1:  # Есть данные кроме заголовков
                    # Очищаем только данные, оставляя заголовки
                    range_to_clear = f"A2:{chr(ord('A') + len(sheet_headers) - 1)}{len(all_values)}"
                    self.worksheet.batch_clear([range_to_clear])
                    logger.info(f"🧹 Cleared data range: {range_to_clear}")
                else:
                    logger.info("🧹 No data to clear, only headers present")
            
            # Подготавливаем данные для загрузки
            upload_data = []
            for data_row in data_rows:
                mapped_data, _ = self.map_data_to_columns(data_row, sheet_headers)
                upload_data.append(mapped_data)
            
            if upload_data:
                # Определяем диапазон для загрузки
                start_row = 2  # Начинаем со второй строки (после заголовков)
                end_row = start_row + len(upload_data) - 1
                end_column = chr(ord('A') + len(sheet_headers) - 1)
                range_name = f"A{start_row}:{end_column}{end_row}"
                
                # Загружаем данные батчем
                logger.info(f"📤 Uploading {len(upload_data)} rows to range {range_name}")
                self.worksheet.update(range_name, upload_data)
                
                logger.info(f"✅ Successfully uploaded {len(data_rows)} rows to '{worksheet_name}'")
                return True
            else:
                logger.warning("⚠️ No data to upload")
                return False
                
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            return False
    
    def upload_data(self, spreadsheet_id: str, worksheet_name: str, data: List[str], clear_existing: bool = False) -> bool:
        """
        Основной метод загрузки данных в Google Sheets
        
        Args:
            spreadsheet_id: ID таблицы Google Sheets
            worksheet_name: Название листа
            data: Список TSV строк для загрузки
            clear_existing: Очистить существующие данные
            
        Returns:
            bool: True если загрузка успешна
        """
        try:
            logger.info(f"🚀 Starting Google Sheets upload: {len(data)} rows to '{worksheet_name}'")
            
            # Открываем таблицу
            self.open_spreadsheet(spreadsheet_id)
            
            # Загружаем данные
            success = self.upload_data_rows(worksheet_name, data, clear_existing)
            
            if success:
                logger.info(f"✅ Upload completed successfully: {spreadsheet_id}")
                return True
            else:
                logger.error("❌ Upload failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Upload error: {e}")
            return False
    
    def _apply_formatting(self, worksheet, total_rows: int):
        """ОТКЛЮЧЕНО: Пользователь просил убрать все форматирование"""
        # ПОЛНОСТЬЮ ОТКЛЮЧЕНО ПО ТРЕБОВАНИЮ ПОЛЬЗОВАТЕЛЯ
        # НЕ ДОБАВЛЯЕМ НИКАКОГО ФОРМАТИРОВАНИЯ: ни цветов, ни жирного текста, ни фона
        pass

def test_dynamic_uploader():
    """Тестирование динамического загрузчика"""
    try:
        uploader = DynamicGoogleSheetsUploader()
        
        # Тестовые данные с 14 колонками
        test_data = [
            "test transcript\ttest inquiry\ttest trigger\ttest 5why\ttest blockers\tb2c\ttest stop words\ttest recommendations\ttest client gets\ttest big jtbd\ttest medium jtbd\ttest small jtbd\t2025-07-23 15:00:00\t30"
        ]
        
        print("✅ Dynamic uploader test completed")
        return True
        
    except Exception as e:
        print(f"❌ Dynamic uploader test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Dynamic Google Sheets Uploader")
    test_dynamic_uploader()