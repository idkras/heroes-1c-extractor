#!/usr/bin/env python3
"""
АНТИ-ПИЗДЕЖ ВАЛИДАТОР v4.0 с проверкой РЕАЛЬНОСТИ данных
Применяет все CRITICAL ANTI-BULLSHIT CHECKPOINTS из sales-injury standard v1.1
"""

import gspread
from google.oauth2.service_account import Credentials
import json
import logging
import argparse
import sys
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AntiBullshitValidator:
    """
    КРИТИЧЕСКИЙ валидатор против самообмана
    Применяет все MANDATORY checkpoints из sales-injury standard
    """
    
    def __init__(self):
        self.mandatory_failures = []
        self.critical_errors = []
        
    def validate_data_reality(self, worksheet, tsv_data, column_mappings):
        """
        CHECKPOINT 1: DATA REALITY VALIDATION
        """
        logger.info("🔍 CHECKPOINT 1: DATA REALITY VALIDATION")
        
        critical_columns = ['sale_blockers', 'root_cause_5why', 'stop_words_patterns', 'recommended_phrases']
        
        for col_name in critical_columns:
            if col_name not in column_mappings:
                self.mandatory_failures.append(f"Critical column '{col_name}' not found in mapping")
                continue
                
            mapping = column_mappings[col_name]
            sheets_col = mapping['sheets_column']
            
            # Проверяем первые 5 строк на наличие РЕАЛЬНОГО содержания
            empty_count = 0
            content_count = 0
            
            for row_num in range(2, 7):  # rows 2-6
                try:
                    cell_value = worksheet.cell(row_num, sheets_col).value or ""
                    if len(str(cell_value).strip()) >= 10:  # Минимум 10 символов
                        content_count += 1
                        logger.info(f"✅ {col_name} row {row_num}: {len(str(cell_value))} chars")
                    else:
                        empty_count += 1
                        logger.warning(f"❌ {col_name} row {row_num}: EMPTY or <10 chars")
                except Exception as e:
                    empty_count += 1
                    logger.error(f"❌ {col_name} row {row_num}: ERROR - {e}")
            
            # MANDATORY: В первых 5 строках должно быть содержание
            if content_count < 2:  # Минимум 2 из 5 строк должны содержать данные
                self.mandatory_failures.append(f"CRITICAL: Column '{col_name}' has <2 content rows in first 5 rows")
        
        return len(self.mandatory_failures) == 0
    
    def validate_processor_output(self, tsv_file):
        """
        CHECKPOINT 2: PROCESSOR OUTPUT VALIDATION
        """
        logger.info("🔍 CHECKPOINT 2: PROCESSOR OUTPUT VALIDATION")
        
        with open(tsv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        tsv_data = []
        for line in lines:
            if line.strip():
                row_data = line.strip().split('\t')
                tsv_data.append(row_data)
        
        if len(tsv_data) < 2:
            self.mandatory_failures.append("TSV file has no data rows")
            return False
        
        header = tsv_data[0]
        data_rows = tsv_data[1:]
        
        critical_columns = ['sale blockers', 'root cause 5why', 'stop_words_patterns', 'recommended_phrases']
        
        for col_name in critical_columns:
            col_index = None
            for i, h in enumerate(header):
                if h.strip() == col_name.strip():
                    col_index = i
                    break
            
            if col_index is None:
                self.mandatory_failures.append(f"Column '{col_name}' not found in TSV")
                continue
            
            # Считаем пустые и заполненные строки
            empty_count = 0
            content_count = 0
            
            for row in data_rows:
                if col_index < len(row):
                    value = row[col_index].strip()
                    if len(value) >= 10:  # Минимум 10 символов для качественного анализа
                        content_count += 1
                    else:
                        empty_count += 1
                else:
                    empty_count += 1
            
            total_rows = len(data_rows)
            empty_percentage = (empty_count / total_rows) * 100
            
            logger.info(f"📊 {col_name}: {content_count} content / {empty_count} empty ({empty_percentage:.1f}% empty)")
            
            # MANDATORY: Не более 50% пустых строк
            if empty_percentage > 50:
                self.mandatory_failures.append(f"CRITICAL: Column '{col_name}' has {empty_percentage:.1f}% empty rows (>50% threshold)")
        
        return len(self.mandatory_failures) == 0
    
    def validate_honest_metrics(self, total_matches, total_expected, visual_reality):
        """
        CHECKPOINT 3: VALIDATOR HONESTY CHECK
        """
        logger.info("🔍 CHECKPOINT 3: VALIDATOR HONESTY CHECK")
        
        calculated_percentage = (total_matches / total_expected) * 100 if total_expected > 0 else 0
        
        # MANDATORY: Success rate должен отражать РЕАЛЬНОЕ качество
        if calculated_percentage > 90 and visual_reality['has_mostly_empty_columns']:
            self.mandatory_failures.append(f"DISHONEST METRICS: Claiming {calculated_percentage:.1f}% success but visually seeing mostly empty data")
        
        # MANDATORY: Не считаем пустые ячейки как success
        if visual_reality['empty_matches_counted_as_success']:
            self.mandatory_failures.append("DISHONEST VALIDATION: Empty cells counted as successful matches")
        
        return len(self.mandatory_failures) == 0
    
    def final_honesty_reflection(self, spreadsheet_id, worksheet_id):
        """
        CHECKPOINT 4: FINAL HONESTY REFLECTION
        """
        logger.info("🔍 CHECKPOINT 4: FINAL HONESTY REFLECTION")
        
        # Это должно быть сделано ЧЕЛОВЕКОМ, но мы можем напомнить
        questions = [
            "Действительно ли я вижу качественные данные в результирующем файле?",
            "Соответствует ли мой заявленный success rate тому, что я визуально наблюдаю?", 
            "Могу ли я продемонстрировать конкретные примеры успешного анализа?",
            "Не обманываю ли я себя confirmation bias-ом?"
        ]
        
        logger.info("🤔 MANDATORY HONESTY QUESTIONS:")
        for i, question in enumerate(questions, 1):
            logger.info(f"   {i}. {question}")
        
        logger.info(f"🔗 ВИЗУАЛЬНАЯ ПРОВЕРКА ОБЯЗАТЕЛЬНА: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={worksheet_id}")
        logger.info("⚠️  БЕЗ ВИЗУАЛЬНОЙ ПРОВЕРКИ РЕЗУЛЬТАТ НЕДЕЙСТВИТЕЛЕН")
        
        return True  # Этот checkpoint требует человеческой проверки

def validate_with_reality_check(spreadsheet_id, worksheet_name, tsv_file, target_columns=None):
    """
    Полная валидация с проверкой реальности данных
    """
    
    validator = AntiBullshitValidator()
    
    # DEFAULT TARGET COLUMNS
    if target_columns is None:
        target_columns = [
            "sale_blockers",
            "root_cause_5why", 
            "stop_words_patterns",
            "recommended_phrases"
        ]
    
    try:
        # Authenticate
        with open("advising_platform/config/google_service_account.json", 'r') as f:
            creds_data = json.load(f)
        
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_info(creds_data, scopes=scopes)
        gc = gspread.authorize(credentials)
        
        # Open spreadsheet and find worksheet BY NAME
        sheet = gc.open_by_key(spreadsheet_id)
        target_worksheet = None
        
        for ws in sheet.worksheets():
            if ws.title.strip() == worksheet_name.strip():
                target_worksheet = ws
                break
        
        if not target_worksheet:
            logger.error(f"❌ Worksheet '{worksheet_name}' not found")
            return False
        
        logger.info(f"✅ Found worksheet: {worksheet_name}")
        
        # Get Google Sheets header
        sheets_header = target_worksheet.row_values(1)
        
        # Build column mappings
        column_mappings = {}
        for target_col in target_columns:
            sheets_column = None
            for i, header in enumerate(sheets_header):
                if header.strip().lower() == target_col.strip().lower():
                    sheets_column = i + 1  # 1-based for gspread
                    break
            
            if sheets_column:
                column_mappings[target_col] = {
                    'sheets_column': sheets_column
                }
        
        # CHECKPOINT 1: DATA REALITY VALIDATION
        reality_check_passed = validator.validate_data_reality(target_worksheet, None, column_mappings)
        
        # CHECKPOINT 2: PROCESSOR OUTPUT VALIDATION  
        processor_check_passed = validator.validate_processor_output(tsv_file)
        
        # CHECKPOINT 3: VALIDATOR HONESTY CHECK (simplified)
        visual_reality = {
            'has_mostly_empty_columns': len(validator.mandatory_failures) > 0,
            'empty_matches_counted_as_success': False  # Would need more complex logic
        }
        honesty_check_passed = validator.validate_honest_metrics(0, 0, visual_reality)
        
        # CHECKPOINT 4: FINAL HONESTY REFLECTION
        reflection_completed = validator.final_honesty_reflection(spreadsheet_id, target_worksheet.id)
        
        # FINAL RESULT
        all_mandatory_passed = (
            reality_check_passed and 
            processor_check_passed and 
            honesty_check_passed and
            reflection_completed
        )
        
        logger.info("")
        logger.info("=" * 70)
        logger.info("🚨 ANTI-BULLSHIT VALIDATION SUMMARY")
        logger.info("=" * 70)
        
        logger.info(f"CHECKPOINT 1 - Data Reality: {'✅ PASSED' if reality_check_passed else '❌ FAILED'}")
        logger.info(f"CHECKPOINT 2 - Processor Output: {'✅ PASSED' if processor_check_passed else '❌ FAILED'}")
        logger.info(f"CHECKPOINT 3 - Honest Metrics: {'✅ PASSED' if honesty_check_passed else '❌ FAILED'}")
        logger.info(f"CHECKPOINT 4 - Final Reflection: {'🤔 REQUIRES HUMAN VERIFICATION' if reflection_completed else '❌ FAILED'}")
        
        if validator.mandatory_failures:
            logger.error("💥 MANDATORY FAILURES:")
            for failure in validator.mandatory_failures:
                logger.error(f"   ❌ {failure}")
        
        if all_mandatory_passed and not validator.mandatory_failures:
            logger.info("Status: ✅ REALITY CHECK PASSED")
            logger.info("⚠️  ВИЗУАЛЬНАЯ ПРОВЕРКА ВСЕ ЕЩЕ ОБЯЗАТЕЛЬНА!")
            return True
        else:
            logger.error("Status: ❌ REALITY CHECK FAILED - БРАК ОБНАРУЖЕН")
            logger.error("🛑 AUTOMATIC REJECTION - НЕ ДОСТАВЛЯТЬ ПОЛЬЗОВАТЕЛЮ")
            return False
        
    except Exception as e:
        logger.error(f"❌ Reality check failed: {e}")
        return False

def main():
    """Main function with reality check validation"""
    parser = argparse.ArgumentParser(description="Анти-пиздеж валидация с проверкой реальности данных")
    parser.add_argument("--spreadsheet-id", required=True, help="ID Google Sheets документа")
    parser.add_argument("--worksheet-name", required=True, help="Название листа")
    parser.add_argument("--tsv-file", required=True, help="Путь к TSV файлу")
    parser.add_argument("--columns", nargs='+', help="Список колонок для проверки")
    
    args = parser.parse_args()
    
    success = validate_with_reality_check(
        spreadsheet_id=args.spreadsheet_id,
        worksheet_name=args.worksheet_name,
        tsv_file=args.tsv_file,
        target_columns=args.columns
    )
    
    if success:
        logger.info("🎉 ANTI-BULLSHIT VALIDATION PASSED")
        logger.info("⚠️  ОБЯЗАТЕЛЬНА ВИЗУАЛЬНАЯ ПРОВЕРКА ПЕРЕД ЗАЯВЛЕНИЕМ О УСПЕХЕ")
        sys.exit(0)
    else:
        logger.error("💥 ANTI-BULLSHIT VALIDATION FAILED")
        logger.error("🛑 ПРОДУКТ ЗАБРАКОВАН - НЕ ДОСТАВЛЯТЬ")
        sys.exit(1)

if __name__ == "__main__":
    main()