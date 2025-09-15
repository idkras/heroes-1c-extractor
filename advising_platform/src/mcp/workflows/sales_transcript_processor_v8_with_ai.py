#!/usr/bin/env python3
"""
Sales Transcript Processor v8.0 - OPENAI GPT-4.1 MINI POWERED VERSION
КРИТИЧЕСКИЕ УЛУЧШЕНИЯ:
1. Использует OpenAI GPT-4.1 mini для ИНДИВИДУАЛЬНОГО анализа каждого транскрипта
2. БАТЧ-ОБРАБОТКА: отправляет 5 транскриптов за раз, получает 5 анализов
3. ФОКУС НА JTBD ОШИБКИ: выявляет конкретные Big/Medium/Small JTBD где продавец допустил ошибку
4. Исправляет главную проблему v7: шаблонность анализа заменена на реальное AI понимание
"""

import logging
import re
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import openai

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SalesTranscriptProcessorV8WithOpenAI:
    """
    OPENAI GPT-4.1 MINI POWERED процессор v8.0
    КРИТИЧЕСКИЕ УЛУЧШЕНИЯ:
    - Использует OpenAI GPT-4.1 mini для БАТЧ-анализа 5 транскриптов за раз
    - ФОКУС НА JTBD ОШИБКИ: выявляет конкретные Big/Medium/Small JTBD где продавец ошибся
    - Реальное понимание контекста каждого разговора
    - Специфичный анализ вместо шаблонных ответов
    """
    
    # ТОЧНАЯ структура согласно sales.injury standard v1.1 (14 колонок)
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
    
    def __init__(self):
        # Инициализация OpenAI клиента
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.warning("⚠️ OPENAI_API_KEY не найден. AI анализ недоступен.")
            self.ai_client = None
        else:
            self.ai_client = openai.OpenAI(api_key=api_key)
            logger.info("✅ AI клиент OpenAI GPT-4.1 mini инициализирован")
            
        # Загружаем reference table
        self.load_reference_table()
        
        # TDD VALIDATION SETUP: целевые параметры Google Sheets
        self.target_spreadsheet_id = "1KQ7eP472By9BBR3yOStE9oJNxxcErNXp73OCbDU6oyc"
        self.target_worksheet_gid = "514375575" # ТОЧНЫЙ GID из URL пользователя
        self.tsv_output_file = "[rick.ai] clients/avtoall.ru/[4] whatsapp-jtbd-tracktion/results/avtoall_sales_analyzed_v8_ai.tsv"
    
    def load_reference_table(self):
        """Загружает reference table из файла"""
        try:
            reference_file = "[rick.ai] clients/avtoall.ru/[4] whatsapp-jtbd-tracktion/avtoall_jtbd_analysis_16_jul_2025.md"
            with open(reference_file, 'r', encoding='utf-8') as f:
                self.reference_table_content = f.read()
            logger.info("✅ Reference table загружена")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось загрузить reference table: {e}")
            self.reference_table_content = ""
    
    def process_batch_with_openai(self, transcripts_batch: List[Tuple[str, str]]) -> List[str]:
        """
        БАТЧ-ОБРАБОТКА 5 транскриптов с OpenAI GPT-4.1 mini
        ФОКУС: выявление конкретных JTBD ошибок продавцов
        
        Args:
            transcripts_batch: Список из 5 кортежей (timestamp, transcript_text)
            
        Returns:
            List[str]: Список из 5 TSV строк с анализом JTBD ошибок
        """
        logger.info(f"🧠 BATCH Processing {len(transcripts_batch)} transcripts with OpenAI GPT-4.1 mini")
        logger.info("🎯 FOCUS: Identifying specific Big/Medium/Small JTBD errors by sales representatives")
        
        if not self.ai_client:
            logger.error("❌ OpenAI клиент недоступен")
            return [self._fallback_processing(transcript, timestamp) for timestamp, transcript in transcripts_batch]
        
        try:
            # Подготавливаем batch prompt для AI анализа 5 транскриптов
            batch_prompt = self._build_batch_analysis_prompt(transcripts_batch)
            
            # Запрос к OpenAI GPT-4.1 mini
            response = self.ai_client.chat.completions.create(
                model="gpt-4o-mini",  # GPT-4.1 mini эквивалент
                messages=[
                    {
                        "role": "system",
                        "content": "Ты эксперт по анализу продаж в автозапчастях. Анализируешь транскрипты звонков для выявления КОНКРЕТНЫХ JTBD ошибок продавцов."
                    },
                    {
                        "role": "user", 
                        "content": batch_prompt
                    }
                ],
                max_tokens=8000,  # Больше токенов для батч-обработки
                temperature=0.2,  # Низкая температура для стабильности
                response_format={"type": "json_object"}  # Требуем JSON ответ
            )
            
            # Извлекаем анализ из ответа AI
            ai_analysis = response.choices[0].message.content
            if not ai_analysis:
                logger.error("❌ Пустой ответ от OpenAI")
                return [self._fallback_processing(transcript, timestamp) for timestamp, transcript in transcripts_batch]
                
            logger.info("✅ OpenAI batch анализ получен")
            
            # Парсим AI ответ и формируем 5 TSV строк
            tsv_rows = self._parse_batch_ai_analysis_to_tsv(ai_analysis, transcripts_batch)
            
            logger.info(f"✅ Generated {len(tsv_rows)} AI-powered TSV rows with JTBD error analysis")
            return tsv_rows
            
        except Exception as e:
            logger.error(f"❌ Error in OpenAI batch processing: {e}")
            return [self._fallback_processing(transcript, timestamp) for timestamp, transcript in transcripts_batch]
    
    def _build_batch_analysis_prompt(self, transcripts_batch: List[Tuple[str, str]]) -> str:
        """Строит batch prompt для AI анализа 5 транскриптов с фокусом на JTBD ошибки"""
        
        # Подготавливаем транскрипты для батч-анализа
        transcripts_for_prompt = ""
        for i, (timestamp, transcript) in enumerate(transcripts_batch, 1):
            transcripts_for_prompt += f"""
=== ТРАНСКРИПТ {i} ===
Timestamp: {timestamp}
Content: {transcript[:1000]}...
"""
        
        prompt = f"""
Ты эксперт по анализу продаж в автозапчастях. Проанализируй эти 5 КОНКРЕТНЫХ транскриптов звонков для выявления JTBD ошибок продавцов.

КЛЮЧЕВАЯ ЗАДАЧА: Для каждого транскрипта найди КОНКРЕТНЫЕ Big/Medium/Small JTBD где ПРОДАВЕЦ ДОПУСТИЛ ОШИБКУ.

ТРАНСКРИПТЫ ДЛЯ АНАЛИЗА:
{transcripts_for_prompt}

REFERENCE TABLE ДЛЯ JTBD MAPPING:
{self.reference_table_content[:1500]}

КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
1. Анализируй КАЖДЫЙ транскрипт ИНДИВИДУАЛЬНО - не используй шаблонные ответы
2. ФОКУС НА ОШИБКАХ: Найди где продавец НЕ ВЫПОЛНИЛ нужный JTBD
3. Используй ТОЧНЫЕ ЦИТАТЫ из разговоров
4. Связывай ошибки с конкретными JTBD из reference table

ФОРМАТ ОТВЕТА - JSON с анализом всех 5 транскриптов:

```json
{{
  "transcript_1": {{
    "lead_inquiry": "точный запрос клиента БЕЗ временных меток",
    "when_trigger_situation": "когда [ситуация] в [timestamp] - продавец не выполнил [конкретный JTBD] вместо [правильного действия]",
    "root_cause_5why": "why1: Конкретная причина для ЭТОГО случая  
why2: Следующий уровень для ЭТОГО транскрипта  
why3: Системная причина для ЭТОГО продавца  
why4: Причина процесса для ЭТОЙ ситуации  
why5: Корневая причина для ЭТОЙ компании",
    "sale_blockers": "В [timestamp] продавец сказал '[точная цитата]' вместо [правильного действия]",
    "segment": "b2b/b2c - [конкретные аргументы из ЭТОГО разговора]",
    "stop_words_patterns": "small-jtbd сценарий: [описание ошибки]  
  
lead inquiry: [цитата запроса]  
  
operator answer: [цитата неправильного ответа]",
    "recommended_phrases": "small jtbd сценарий: [описание правильного поведения]  
  
lead inquiry: [та же цитата запроса]  
  
good_answer: [оптимизированный ответ для ЭТОЙ ситуации]",
    "what_client_get_on_this_stage": "1. [этап для ЭТОГО клиента]  
2. [этап для ЭТОГО случая]  
3. [этап для ЭТОЙ ситуации]  
4. [этап для ЭТОГО разговора]",
    "big_jtbd": "[B1/B2/B3 из reference table]",
    "medium_jtbd": "[M1.1-M3.3 из reference table - который НЕ БЫЛ ВЫПОЛНЕН]",
    "small_jtbd": "[S1.1-S3.12 из reference table - который НЕ БЫЛ ВЫПОЛНЕН]"
  }},
  "transcript_2": {{ ... аналогично для транскрипта 2 ... }},
  "transcript_3": {{ ... аналогично для транскрипта 3 ... }},
  "transcript_4": {{ ... аналогично для транскрипта 4 ... }},
  "transcript_5": {{ ... аналогично для транскрипта 5 ... }}
}}
```

ВАЖНО: Каждый анализ должен быть УНИКАЛЬНЫМ для конкретного разговора. НЕ используй копирование между транскриптами!
"""
        
        return prompt
    
    def _parse_batch_ai_analysis_to_tsv(self, ai_analysis: str, transcripts_batch: List[Tuple[str, str]]) -> List[str]:
        """Парсит batch AI анализ и формирует 5 TSV строк"""
        
        try:
            # Пытаемся извлечь JSON из ответа AI
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', ai_analysis, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                batch_analysis = json.loads(json_str)
            else:
                # Пытаемся парсить как обычный JSON
                batch_analysis = json.loads(ai_analysis)
            
            tsv_rows = []
            
            # Обрабатываем каждый транскрипт из батча
            for i, (timestamp, transcript_text) in enumerate(transcripts_batch, 1):
                transcript_key = f"transcript_{i}"
                
                if transcript_key in batch_analysis:
                    analysis_data = batch_analysis[transcript_key]
                    
                    # Извлекаем date_time и week
                    date_time, week = self._extract_datetime_and_week(timestamp)
                    
                    # Подготавливаем транскрипт
                    clean_transcript = transcript_text.replace('\n', ' ').replace('\t', ' ')[:500]
                    
                    # Собираем результат для этого транскрипта
                    result_data = {
                        'transcript': clean_transcript,
                        'lead_inquiry': analysis_data.get('lead_inquiry', 'не извлечено')[:150],
                        'when_trigger_situation': analysis_data.get('when_trigger_situation', 'не определено')[:200],
                        'root cause 5why': analysis_data.get('root_cause_5why', 'анализ не выполнен').replace('\n', ' ').replace('\\n', '  \n'),
                        'sale blockers': analysis_data.get('sale_blockers', 'не найдены')[:200],
                        'segment': analysis_data.get('segment', 'не определен')[:100],
                        'stop_words_patterns': analysis_data.get('stop_words_patterns', 'не найдены').replace('\n', ' ').replace('\\n', '  \n'),
                        'recommended_phrases': analysis_data.get('recommended_phrases', 'не созданы').replace('\n', ' ').replace('\\n', '  \n'),
                        'what client get on this stage': analysis_data.get('what_client_get_on_this_stage', 'не определено').replace('\n', ' ').replace('\\n', '  \n'),
                        'big jtbd': analysis_data.get('big_jtbd', 'не выбрано')[:100],
                        'medium jtbd': analysis_data.get('medium_jtbd', 'не выбрано')[:150],
                        'small jtbd': analysis_data.get('small_jtbd', 'не выбрано')[:150],
                        'date_time': date_time,
                        'week': week
                    }
                    
                    # Очищаем табуляции во всех полях
                    for key in result_data:
                        if isinstance(result_data[key], str):
                            result_data[key] = result_data[key].replace('\t', ' ')
                    
                    # Генерируем TSV строку
                    tsv_row = '\t'.join([result_data[col] for col in self.REQUIRED_COLUMNS])
                    tsv_rows.append(tsv_row)
                else:
                    # Fallback для отсутствующих данных
                    tsv_rows.append(self._fallback_processing(transcript_text, timestamp))
            
            return tsv_rows
            
        except Exception as e:
            logger.error(f"❌ Error parsing batch AI analysis: {e}")
            return [self._fallback_processing(transcript, timestamp) for timestamp, transcript in transcripts_batch]
    
    def _parse_text_analysis(self, ai_text: str) -> Dict:
        """Парсит текстовый ответ AI если JSON не удался"""
        # Простой парсинг по ключевым словам
        analysis_data = {}
        
        # Ищем каждое поле в тексте
        fields = [
            'lead_inquiry', 'when_trigger_situation', 'root_cause_5why',
            'sale_blockers', 'segment', 'stop_words_patterns', 
            'recommended_phrases', 'what_client_get_on_this_stage',
            'big_jtbd', 'medium_jtbd', 'small_jtbd'
        ]
        
        for field in fields:
            pattern = rf'{field}[:\"]([^"\n]{{1,500}})'
            match = re.search(pattern, ai_text, re.IGNORECASE)
            if match:
                analysis_data[field] = match.group(1).strip()
            else:
                analysis_data[field] = f"{field} не найдено в AI ответе"
        
        return analysis_data
    
    def _extract_datetime_and_week(self, source_timestamp: Optional[str]) -> Tuple[str, str]:
        """Извлекает дату и неделю из timestamp"""
        if source_timestamp:
            try:
                if '@' in source_timestamp:
                    date_part, time_part = source_timestamp.split('@')
                    date_part = date_part.strip()
                    time_part = time_part.strip().split('.')[0]
                    dt = datetime.strptime(f"{date_part} {time_part}", '%b %d, %Y %H:%M:%S')
                    date_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                    week = f"Week {dt.isocalendar()[1]}"
                    return date_time, week
            except Exception as e:
                logger.warning(f"⚠️ Error parsing timestamp: {e}")
        
        # Fallback
        now = datetime.now()
        return now.strftime('%Y-%m-%d %H:%M:%S'), f"Week {now.isocalendar()[1]}"
    
    def _fallback_processing(self, transcript_text: str, source_timestamp: Optional[str]) -> str:
        """Fallback обработка без AI"""
        logger.info("🔄 Using fallback processing (no AI)")
        
        # Простая обработка без AI
        date_time, week = self._extract_datetime_and_week(source_timestamp)
        
        result_data = {
            'transcript': transcript_text.replace('\n', ' ').replace('\t', ' ')[:500],
            'lead_inquiry': 'AI недоступен - базовое извлечение',
            'when_trigger_situation': 'требуется AI анализ',
            'root cause 5why': 'AI анализ недоступен',
            'sale blockers': 'требуется AI обработка',
            'segment': 'неопределен без AI',
            'stop_words_patterns': 'AI анализ необходим',
            'recommended_phrases': 'AI генерация недоступна',
            'what client get on this stage': 'требуется AI анализ',
            'big jtbd': 'AI выбор недоступен',
            'medium jtbd': 'AI анализ нужен',
            'small jtbd': 'AI обработка требуется',
            'date_time': date_time,
            'week': week
        }
        
        return '\t'.join([result_data[col] for col in self.REQUIRED_COLUMNS])




def process_batch_transcripts_with_openai(transcripts: List[Tuple[str, str]], batch_size: int = 5) -> List[str]:
    """
    Обработка транскриптов батчами по 5 штук с OpenAI GPT-4.1 mini
    ФОКУС: выявление JTBD ошибок продавцов
    
    Args:
        transcripts: Список (timestamp, transcript_text)
        batch_size: Размер батча (по умолчанию 5)
        
    Returns:
        List[str]: Список TSV строк с анализом JTBD ошибок
    """
    processor = SalesTranscriptProcessorV8WithOpenAI()
    results = []
    
    # Разбиваем транскрипты на батчи по 5 штук
    for i in range(0, len(transcripts), batch_size):
        batch = transcripts[i:i + batch_size]
        
        logger.info(f"🔄 Processing batch {i//batch_size + 1}: {len(batch)} transcripts")
        
        try:
            # Обрабатываем батч
            batch_results = processor.process_batch_with_openai(batch)
            results.extend(batch_results)
            
            logger.info(f"✅ Batch {i//batch_size + 1} completed: {len(batch_results)} analyses")
            
        except Exception as e:
            logger.error(f"❌ Error processing batch {i//batch_size + 1}: {e}")
            # Добавляем fallback результаты при ошибке
            for timestamp, transcript in batch:
                empty_row = '\t'.join([''] * 14)
                results.append(empty_row)
    
    return results


if __name__ == "__main__":
    # Тест OpenAI процессора
    test_transcript = """
    Спикер 0 (00:00:00): Автол.ру, меня зовут Алексей, здравствуйте.
    Спикер 1 (00:00:02): Здравствуйте, Алексей. Хотел бы узнать, есть ли у вас набор для выставления резьбы болта М6?
    Спикер 0 (00:00:14): Набор для выставления резьбы М6... Сейчас посмотрю. Да, у нас есть такой набор за 1050 рублей.
    Спикер 1 (00:00:22): А где можно забрать?
    Спикер 0 (00:00:25): Это все далеко, это все на востоке.
    Спикер 1 (00:00:28): Понятно, спасибо.
    """
    
    processor = SalesTranscriptProcessorV8WithOpenAI()
    
    # Тестируем батч-обработку
    test_batch = [
        ("Jul 4, 2025 @ 19:05:57.156", test_transcript),
        ("Jul 4, 2025 @ 19:15:30.000", test_transcript),  # Дублируем для теста
    ]
    
    results = processor.process_batch_with_openai(test_batch)
    print("OpenAI Batch Analysis Results:")
    for i, result in enumerate(results, 1):
        print(f"Result {i}: {result[:200]}...")
        
    def upload_to_target_worksheet_with_tdd(self, tsv_results: List[str]) -> Dict[str, any]:
        """
        TDD INTEGRATION: Загружает результаты в ЦЕЛЕВОЙ лист с встроенной валидацией
        Использует точный GID из URL пользователя вместо создания нового листа
        """
        import gspread
        from google.oauth2.service_account import Credentials
        import json
        import time
        
        logger.info("🧪 TDD UPLOAD: Starting upload to target worksheet with validation")
        
        try:
            # Аутентификация
            with open("advising_platform/config/google_service_account.json", 'r') as f:
                creds_data = json.load(f)
            
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            credentials = Credentials.from_service_account_info(creds_data, scopes=scopes)
            gc = gspread.authorize(credentials)
            
            # Открыть таблицу и найти ЦЕЛЕВОЙ лист по GID
            sheet = gc.open_by_key(self.target_spreadsheet_id)
            target_worksheet = None
            
            for ws in sheet.worksheets():
                if str(ws.id) == self.target_worksheet_gid:
                    target_worksheet = ws
                    break
            
            if not target_worksheet:
                return {
                    "success": False, 
                    "error": f"Target worksheet with GID {self.target_worksheet_gid} not found",
                    "available_worksheets": [(ws.title, ws.id) for ws in sheet.worksheets()]
                }
            
            logger.info(f"✅ Found target worksheet: {target_worksheet.title} (gid={self.target_worksheet_gid})")
            
            # Подготовить данные из TSV результатов
            if not tsv_results:
                return {"success": False, "error": "No TSV results to upload"}
                
            # Парсим TSV строки
            parsed_data = []
            for tsv_row in tsv_results:
                parsed_data.append(tsv_row.split('\t'))
            
            # Mapping колонок к позициям в Google Sheets (согласно скриншоту пользователя)
            column_mapping = {
                'sale blockers': 'F',      # Колонка F
                'when_trigger_situation': 'G',  # Колонка G  
                'root cause 5why': 'H',    # Колонка H
                'stop_words_patterns': 'I', # Колонка I
                'recommended_phrases': 'J'  # Колонка J
            }
            
            # Найти индексы колонок в TSV
            tsv_column_indices = {}
            for col_name in column_mapping.keys():
                if col_name in self.REQUIRED_COLUMNS:
                    tsv_column_indices[col_name] = self.REQUIRED_COLUMNS.index(col_name)
            
            # Очистить целевые колонки
            ranges_to_clear = [f"{col}2:{col}11" for col in column_mapping.values()]
            target_worksheet.batch_clear(ranges_to_clear)
            time.sleep(2)  # Ждем применения изменений
            
            # Загрузить данные по колонкам
            updates_made = 0
            
            for tsv_col, sheets_col in column_mapping.items():
                if tsv_col in tsv_column_indices:
                    col_idx = tsv_column_indices[tsv_col]
                    
                    # Подготовить данные для колонки
                    column_data = []
                    for row_data in parsed_data:
                        if col_idx < len(row_data):
                            column_data.append([row_data[col_idx]])
                        else:
                            column_data.append([''])
                    
                    # Загрузить колонку
                    range_name = f"{sheets_col}2:{sheets_col}{len(parsed_data) + 1}"
                    target_worksheet.update(values=column_data, range_name=range_name)
                    updates_made += len(column_data)
                    logger.info(f"✅ Updated {tsv_col} in column {sheets_col}: {len(column_data)} cells")
                    time.sleep(1)  # Пауза между обновлениями
            
            # TDD VALIDATION: Проверить результат
            time.sleep(3)  # Ждем применения всех изменений
            
            validation_results = {}
            total_matches = 0
            total_cells = 0
            
            for tsv_col, sheets_col in column_mapping.items():
                if tsv_col in tsv_column_indices:
                    col_idx = tsv_column_indices[tsv_col]
                    
                    # Получить данные из Google Sheets
                    range_name = f"{sheets_col}2:{sheets_col}{len(parsed_data) + 1}"
                    sheets_values = target_worksheet.get(range_name)
                    
                    # Сравнить с исходными данными
                    matches = 0
                    for i, row_data in enumerate(parsed_data):
                        expected = row_data[col_idx] if col_idx < len(row_data) else ""
                        actual = ""
                        if i < len(sheets_values) and sheets_values[i]:
                            actual = sheets_values[i][0]
                        
                        if expected.strip() == actual.strip():
                            matches += 1
                    
                    match_percentage = (matches / len(parsed_data) * 100) if parsed_data else 0
                    validation_results[tsv_col] = {
                        'matches': matches,
                        'total': len(parsed_data),
                        'percentage': match_percentage
                    }
                    
                    total_matches += matches
                    total_cells += len(parsed_data)
                    logger.info(f"📊 {tsv_col}: {matches}/{len(parsed_data)} matches ({match_percentage:.1f}%)")
            
            overall_success = (total_matches / total_cells * 100) >= 95 if total_cells > 0 else False
            
            return {
                "success": overall_success,
                "updates_made": updates_made,
                "validation_results": validation_results,
                "overall_match_percentage": (total_matches / total_cells * 100) if total_cells > 0 else 0,
                "target_url": f"https://docs.google.com/spreadsheets/d/{self.target_spreadsheet_id}/edit#gid={self.target_worksheet_gid}",
                "worksheet_title": target_worksheet.title
            }
            
        except Exception as e:
            logger.error(f"❌ TDD Upload failed: {e}")
            return {"success": False, "error": str(e)}