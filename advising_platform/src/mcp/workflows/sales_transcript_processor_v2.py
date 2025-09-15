#!/usr/bin/env python3
"""
Sales Transcript Processor v2.0 - Multiple Rows per Transcript
Исправленная версия с поддержкой множественных JTBD на один транскрипт
"""

import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import re

class SalesTranscriptProcessorV2:
    """Обработчик транскриптов с поддержкой множественных JTBD"""
    
    def __init__(self):
        self.column_mapping = {
            # Оригинальные колонки → Новые английские названия
            'как не нужно говорить, что стоп-слова': 'stop_words_patterns',
            'как хотим, чтобы говорили': 'recommended_phrases', 
            'вопросы на каждой стадии, что нужно понимать клиент': 'client_understanding_criteria'
        }
    
    def load_original_data(self, tsv_path: str) -> pd.DataFrame:
        """Загрузка оригинальных данных"""
        return pd.read_csv(tsv_path, sep='\t')
    
    def extract_multiple_jtbd(self, row: pd.Series) -> List[Dict[str, Any]]:
        """
        Извлечение множественных JTBD из одной строки транскрипта
        
        Согласно sales.injury standard:
        - 1 transcript может содержать несколько Big/Medium/Small JTBD
        - Каждый JTBD = отдельная строка результата
        """
        
        base_data = {
            'transcript': row['transcript'],
            'lead_inquiry': row['lead_inquiry'],
            'root_cause_5why': row['root cause 5why'],
            'sales_blockers': row['sales_blockers'],
            'segment': row['segment'],
            'processing_time_sec': row['processing_time_sec'],
            'quality_score': row['quality_score'],
            'validation_passed': row['validation_passed']
        }
        
        # Извлекаем JTBD компоненты
        big_jtbd = str(row['big_jtbd']) if pd.notna(row['big_jtbd']) else ""
        medium_jtbd = str(row['medium_jtbd']) if pd.notna(row['medium_jtbd']) else ""
        small_jtbd = str(row['small_jtbd']) if pd.notna(row['small_jtbd']) else ""
        when_situation = str(row['when ситуация в big_jtbd']) if pd.notna(row['when ситуация в big_jtbd']) else ""
        qualified_triggers = str(row['qualified_triggers']) if pd.notna(row['qualified_triggers']) else ""
        
        # Коммуникационные паттерны
        stop_words = str(row['как не нужно говорить, что стоп-слова']) if pd.notna(row['как не нужно говорить, что стоп-слова']) else ""
        recommended_phrases = str(row['как хотим, чтобы говорили']) if pd.notna(row['как хотим, чтобы говорили']) else ""
        understanding_criteria = str(row['вопросы на каждой стадии, что нужно понимать клиент']) if pd.notna(row['вопросы на каждой стадии, что нужно понимать клиент']) else ""
        
        # Логика создания множественных строк
        jtbd_entries = []
        
        # Парсим возможные множественные JTBD
        big_jobs = self._split_jtbd_items(big_jtbd)
        medium_jobs = self._split_jtbd_items(medium_jtbd)  
        small_jobs = self._split_jtbd_items(small_jtbd)
        
        # Создаем комбинации (каждый Big может иметь несколько Medium/Small)
        max_items = max(len(big_jobs), len(medium_jobs), len(small_jobs), 1)
        
        for i in range(max_items):
            entry = base_data.copy()
            entry.update({
                'stop_words_patterns': stop_words,
                'recommended_phrases': recommended_phrases,
                'client_understanding_criteria': understanding_criteria,
                'when_situation_big_jtbd': when_situation,
                'big_jtbd': big_jobs[i] if i < len(big_jobs) else big_jobs[-1] if big_jobs else "",
                'medium_jtbd': medium_jobs[i] if i < len(medium_jobs) else medium_jobs[-1] if medium_jobs else "",
                'small_jtbd': small_jobs[i] if i < len(small_jobs) else small_jobs[-1] if small_jobs else "",
                'qualified_triggers': qualified_triggers,
                'jtbd_sequence_number': i + 1,
                'total_jtbd_count': max_items
            })
            jtbd_entries.append(entry)
        
        return jtbd_entries
    
    def _split_jtbd_items(self, jtbd_text: str) -> List[str]:
        """Разделение JTBD на отдельные элементы"""
        if not jtbd_text or jtbd_text == "":
            return []
        
        # Попробуем различные разделители
        separators = [';', '\n', '|', '•', '→']
        items = [jtbd_text]  # По умолчанию один элемент
        
        for sep in separators:
            if sep in jtbd_text:
                items = [item.strip() for item in jtbd_text.split(sep) if item.strip()]
                break
        
        return items if items else [jtbd_text]
    
    def process_tsv_to_multiple_rows(self, input_tsv: str, output_tsv: str) -> Tuple[int, int]:
        """
        Обработка TSV с созданием множественных строк
        
        Returns:
            Tuple[original_rows, processed_rows]
        """
        
        print(f"🔄 Loading data from {input_tsv}")
        df = self.load_original_data(input_tsv)
        original_count = len(df)
        
        print(f"📊 Processing {original_count} transcripts for multiple JTBD extraction")
        
        all_processed_entries = []
        
        for index, row in df.iterrows():
            try:
                # Извлекаем множественные JTBD
                jtbd_entries = self.extract_multiple_jtbd(row)
                all_processed_entries.extend(jtbd_entries)
                
                if (index + 1) % 100 == 0:
                    print(f"✅ Processed {index + 1}/{original_count} transcripts")
                    
            except Exception as e:
                print(f"⚠️ Error processing row {index}: {e}")
                continue
        
        # Создаем новый DataFrame с обновленными колонками
        processed_df = pd.DataFrame(all_processed_entries)
        processed_count = len(processed_df)
        
        # Переупорядочиваем колонки согласно sales.injury standard
        column_order = [
            'transcript',
            'lead_inquiry', 
            'root_cause_5why',
            'sales_blockers',
            'segment',
            'stop_words_patterns',
            'recommended_phrases',
            'client_understanding_criteria',
            'when_situation_big_jtbd',
            'big_jtbd',
            'medium_jtbd',
            'small_jtbd',
            'qualified_triggers',
            'jtbd_sequence_number',
            'total_jtbd_count',
            'processing_time_sec',
            'quality_score',
            'validation_passed'
        ]
        
        # Убедимся что все колонки присутствуют
        for col in column_order:
            if col not in processed_df.columns:
                processed_df[col] = ""
        
        processed_df = processed_df[column_order]
        
        # Сохраняем результат
        processed_df.to_csv(output_tsv, sep='\t', index=False)
        
        print(f"🎯 Processing complete:")
        print(f"   📥 Original transcripts: {original_count}")
        print(f"   📤 Processed rows: {processed_count}")
        print(f"   📈 Expansion factor: {processed_count/original_count:.1f}x")
        print(f"   💾 Saved to: {output_tsv}")
        
        return original_count, processed_count


def main():
    """Основная функция обработки"""
    
    processor = SalesTranscriptProcessorV2()
    
    input_file = "../[rick.ai] clients/avtoall.ru/[4] whatsapp-jtbd-tracktion/results/avtoall_sales_analyzed.tsv"
    output_file = "../[rick.ai] clients/avtoall.ru/[4] whatsapp-jtbd-tracktion/results/avtoall_sales_analyzed_v2.tsv"
    
    try:
        original_count, processed_count = processor.process_tsv_to_multiple_rows(
            input_file, output_file
        )
        
        print(f"\n🎉 SUCCESS! TSV processing completed")
        print(f"📊 Ready for Google Sheets upload: {processed_count} rows")
        
        return True
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main()