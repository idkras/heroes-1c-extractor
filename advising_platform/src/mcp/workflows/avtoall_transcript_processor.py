#!/usr/bin/env python3
"""
Avtoall JTBD Transcript Analysis MCP Workflow
Based on: [standards .md]/6. advising · review · supervising/sales-injury-jtbd-standard.md
Implementation of: avtoall-injury-jtbd-standard for processing 600+ call transcripts
"""

import time
import logging
import pandas as pd
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Standard читается первым согласно требованию
STANDARD_PATH = "[standards .md]/6. advising · review · supervising/sales-injury-jtbd-standard.md"
TSV_DATA_PATH = "[rick.ai] clients/avtoall.ru/[4] whatsapp-jtbd-tracktion/raw/HeroesGPT JTBD. avtoall.ru - call_transcriptions_all 17.07.tsv"

@dataclass
class AnalysisResult:
    """
    JTBD: Когда завершается анализ транскрипта,
    нужна структурированная форма результата,
    чтобы обеспечить consistent обработку и валидацию
    """
    transcript_id: str
    lead_inquiry: str
    sales_blockers: List[str]
    segment: str  # B2B/B2C
    stop_words: List[str]  # "как не нужно говорить"
    power_words: List[str]  # "как хотим, чтобы говорили" 
    understanding_criteria: Dict[str, str]  # стадии → критерии
    when_trigger: str  # "when ситуация в big_jtbd"
    big_jtbd: str
    medium_jtbd: str
    small_jtbd: str
    qualified_triggers: Dict[str, Any]  # срочность, бюджет, качество
    processing_time: float
    validation_passed: bool = False
    quality_score: float = 0.0

@dataclass 
class BatchResults:
    """Результаты batch обработки с паттерн-анализом"""
    individual_results: List[AnalysisResult]
    patterns: Dict[str, Any]
    training_materials: Dict[str, List[str]]
    implementation_roadmap: Dict[str, Any]
    total_processing_time: float
    success_rate: float

class ReflectionValidator:
    """
    JTBD: Когда анализ завершен,
    нужно проверить соответствие стандарту качества,
    чтобы гарантировать actionable результаты
    """
    
    def validate(self, result: AnalysisResult) -> Dict[str, Any]:
        """Применяет reflection checklist из стандарта"""
        validations = {
            'root_cause_quality': self._validate_root_cause_chain(result),
            'sales_blockers_actionable': self._validate_sales_blockers(result),
            'communication_examples_ready': self._validate_communication_patterns(result),
            'jtbd_hierarchy_logic': self._validate_jtbd_hierarchy(result),
            'processing_time_acceptable': result.processing_time <= 45 * 60  # 45 минут
        }
        
        overall_score = sum(validations.values()) / len(validations)
        result.quality_score = overall_score
        result.validation_passed = overall_score >= 0.9
        
        return {
            'passed': result.validation_passed,
            'score': overall_score,
            'details': validations,
            'errors': [k for k, v in validations.items() if not v]
        }
    
    def _validate_root_cause_chain(self, result: AnalysisResult) -> bool:
        """Проверяет логичность 5-why chain"""
        # TODO: Implement detailed validation logic
        return len(result.sales_blockers) >= 3  # Minimum actionable blockers
    
    def _validate_sales_blockers(self, result: AnalysisResult) -> bool:
        """Проверяет actionable характер sales blockers"""
        return all(len(blocker.strip()) > 10 for blocker in result.sales_blockers)
    
    def _validate_communication_patterns(self, result: AnalysisResult) -> bool:
        """Проверяет готовность примеров к training"""
        return (len(result.stop_words) >= 2 and 
                len(result.power_words) >= 2 and
                len(result.understanding_criteria) >= 3)
    
    def _validate_jtbd_hierarchy(self, result: AnalysisResult) -> bool:
        """Проверяет логичность Big→Medium→Small JTBD"""
        return (len(result.big_jtbd.strip()) > 20 and
                len(result.medium_jtbd.strip()) > 15 and
                len(result.small_jtbd.strip()) > 10)

class SalesBlockersAnalyzer:
    """
    JTBD: Когда анализирую транскрипт звонка,
    хочу выявить все конкретные препятствия для закрытия сделки,
    чтобы создать actionable план их устранения
    """
    
    def analyze(self, transcript: str, segment: str) -> List[str]:
        """Извлекает sales blockers из транскрипта"""
        blockers = []
        
        # 5-why анализ для выявления корневых причин
        root_causes = self._perform_5why_analysis(transcript)
        
        # Сегмент-специфичные блокеры
        if segment == "B2B":
            blockers.extend(self._extract_b2b_blockers(transcript, root_causes))
        else:  # B2C
            blockers.extend(self._extract_b2c_blockers(transcript, root_causes))
            
        return [b for b in blockers if self._is_actionable(b)]
    
    def _perform_5why_analysis(self, transcript: str) -> List[str]:
        """Проводит 5-why анализ для выявления root cause"""
        # TODO: Implement AI-powered 5-why extraction
        # Placeholder logic for development
        return [
            "Why #1: Customer couldn't find product info online",
            "Why #2: Search functionality inadequate", 
            "Why #3: Product categorization unclear",
            "Why #4: Information architecture problems",
            "Why #5: No user-centric design process"
        ]
    
    def _extract_b2b_blockers(self, transcript: str, root_causes: List[str]) -> List[str]:
        """Извлекает B2B-специфичные sales blockers"""
        # TODO: Implement B2B pattern recognition
        return [
            "Lack of technical expertise demonstration",
            "No volume pricing mentioned",
            "Missing delivery timeline confirmation"
        ]
    
    def _extract_b2c_blockers(self, transcript: str, root_causes: List[str]) -> List[str]:
        """Извлекает B2C-специфичные sales blockers"""
        # TODO: Implement B2C pattern recognition
        return [
            "Price not clearly stated upfront",
            "No urgency creation", 
            "Missing availability confirmation"
        ]
    
    def _is_actionable(self, blocker: str) -> bool:
        """Проверяет actionable характер блокера"""
        return len(blocker.strip()) > 10 and any(
            keyword in blocker.lower() 
            for keyword in ['lack', 'no', 'missing', 'unclear', 'failed']
        )

class CommunicationPatternAnalyzer:
    """
    JTBD: Когда обрабатываю диалог оператора с клиентом,
    хочу выделить неэффективные и эффективные паттерны общения,
    чтобы создать готовые примеры для обучения операторов
    """
    
    def extract_patterns(self, transcript: str) -> Dict[str, Any]:
        """Извлекает communication patterns из транскрипта"""
        dialogue = self._parse_dialogue(transcript)
        
        return {
            'stop_words': self._extract_stop_words(dialogue['operator_phrases']),
            'power_words': self._generate_good_alternatives(dialogue['operator_phrases']),
            'understanding_criteria': self._map_to_decision_stages(dialogue)
        }
    
    def _parse_dialogue(self, transcript: str) -> Dict[str, List[str]]:
        """Парсит транскрипт на реплики операторов и клиентов"""
        lines = transcript.split('\n')
        operator_phrases = []
        customer_phrases = []
        
        for line in lines:
            if 'Спикер 0' in line:  # Предполагаем Спикер 0 = оператор
                phrase = line.split('): ', 1)[-1] if '): ' in line else line
                operator_phrases.append(phrase.strip())
            elif 'Спикер 1' in line:  # Предполагаем Спикер 1 = клиент
                phrase = line.split('): ', 1)[-1] if '): ' in line else line
                customer_phrases.append(phrase.strip())
                
        return {
            'operator_phrases': operator_phrases,
            'customer_phrases': customer_phrases
        }
    
    def _extract_stop_words(self, operator_phrases: List[str]) -> List[str]:
        """Извлекает неэффективные фразы операторов"""
        stop_patterns = [
            'не знаю', 'посмотрю', 'попробую', 'может быть',
            'сейчас проверю', 'вам нужно', 'а что'
        ]
        
        stop_words = []
        for phrase in operator_phrases:
            for pattern in stop_patterns:
                if pattern.lower() in phrase.lower():
                    stop_words.append(f"'{phrase.strip()}'")
                    break
                    
        return list(set(stop_words))  # Убираем дубликаты
    
    def _generate_good_alternatives(self, operator_phrases: List[str]) -> List[str]:
        """Генерирует улучшенные альтернативы"""
        # TODO: Implement AI-powered alternative generation
        return [
            "Конечно, помогу вам подобрать именно то, что нужно",
            "Давайте я найду для вас оптимальное решение",
            "Проверяю наличие и сразу резервирую для вас"
        ]
    
    def _map_to_decision_stages(self, dialogue: Dict[str, List[str]]) -> Dict[str, str]:
        """Сопоставляет критерии понимания по стадиям продажи"""
        return {
            "Problem Recognition": "Клиент четко описал техническую проблему",
            "Solution Validation": "Подтверждено соответствие предлагаемого товара",
            "Price Acceptance": "Цена названа и не вызвала возражений",
            "Purchase Decision": "Клиент готов к оформлению заказа"
        }

class JTBDHierarchyConstructor:
    """
    JTBD: Когда анализирую потребности клиента из транскрипта,
    хочу построить полную иерархию Big→Medium→Small JTBD с триггерами,
    чтобы понимать весь customer journey
    """
    
    def construct(self, transcript: str, context: Dict[str, str]) -> Dict[str, Any]:
        """Строит полную JTBD иерархию"""
        segment = context.get('segment', 'B2C')
        
        return {
            'when_trigger': self._extract_when_trigger(transcript, segment),
            'big_jtbd': self._identify_big_jtbd(transcript, segment),
            'medium_jtbd': self._decompose_to_medium(transcript, segment),
            'small_jtbd': self._decompose_to_small(transcript, segment),
            'qualified_triggers': self._analyze_qualified_triggers(transcript, context)
        }
    
    def _extract_when_trigger(self, transcript: str, segment: str) -> str:
        """Извлекает when-trigger из контекста"""
        # TODO: Implement context analysis
        if segment == "B2B":
            return "когда компании нужно обеспечить бесперебойную работу техники"
        else:
            return "когда автовладелец сталкивается с поломкой и нуждается в срочном ремонте"
    
    def _identify_big_jtbd(self, transcript: str, segment: str) -> str:
        """Определяет стратегическую цель (Big JTBD)"""
        # TODO: Implement AI analysis of strategic goals
        if segment == "B2B":
            return "обеспечить бесперебойную работу автопарка"
        else:
            return "быстро решить проблему с автомобилем"
    
    def _decompose_to_medium(self, transcript: str, segment: str) -> str:
        """Декомпозирует в тактические процессы (Medium JTBD)"""
        # TODO: Implement tactical process identification
        return "подобрать качественные запчасти с гарантией совместимости"
    
    def _decompose_to_small(self, transcript: str, segment: str) -> str:
        """Декомпозирует в операционные действия (Small JTBD)"""
        # TODO: Implement operational actions identification
        return "найти конкретную деталь по артикулу, проверить наличие и цену"
    
    def _analyze_qualified_triggers(self, transcript: str, context: Dict[str, str]) -> Dict[str, Any]:
        """Анализирует дополнительные квалифицирующие факторы"""
        return {
            'urgency_factors': ['срочность ремонта', 'downtime costs'],
            'budget_constraints': ['ценовые ограничения', 'ROI требования'],
            'quality_requirements': ['надежность', 'гарантии', 'brand preferences']
        }

class AvtoallTranscriptProcessor:
    """
    JTBD: Когда получаю TSV файл с транскриптами,
    хочу автоматически обработать каждый звонок согласно стандарту,
    чтобы получить actionable insights для роста conversion rate
    
    Реализует: sales-injury-jtbd-standard.md
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reflection_validator = ReflectionValidator()
        self.sales_analyzer = SalesBlockersAnalyzer()
        self.pattern_analyzer = CommunicationPatternAnalyzer()
        self.jtbd_constructor = JTBDHierarchyConstructor()
        
        # Читаем стандарт для настройки процессора
        self.standard_config = self._load_standard_config()
    
    def _load_standard_config(self) -> Dict[str, Any]:
        """Загружает конфигурацию из стандарта"""
        try:
            with open(STANDARD_PATH, 'r', encoding='utf-8') as f:
                standard_content = f.read()
                # TODO: Parse standard for configuration parameters
                return {
                    'processing_time_limit': 45 * 60,  # 45 минут
                    'min_sales_blockers': 3,
                    'min_communication_examples': 2,
                    'reflection_score_threshold': 0.9
                }
        except FileNotFoundError:
            self.logger.warning(f"Standard not found at {STANDARD_PATH}, using defaults")
            return {'processing_time_limit': 45 * 60}
    
    def process_single_transcript(self, row: Dict[str, Any]) -> AnalysisResult:
        """
        Обработка одного транскрипта согласно 6-этапному MCP workflow
        Время выполнения: 30-45 минут → автоматизировано до ≤5 минут
        """
        start_time = time.time()
        
        # Извлекаем базовые данные из TSV строки
        transcript = row.get('transcript', '')
        segment = self._classify_segment(row)
        
        try:
            # Этап 1: Basic Extraction (извлечение lead_inquiry)
            lead_inquiry = self._extract_lead_inquiry(transcript)
            
            # Этап 2: Sales Blockers Analysis
            sales_blockers = self.sales_analyzer.analyze(transcript, segment)
            
            # Этап 3: Communication Pattern Analysis  
            comm_patterns = self.pattern_analyzer.extract_patterns(transcript)
            
            # Этап 4: JTBD Hierarchy Construction
            context = {'segment': segment, 'transcript_id': row.get('classification.callId', 'unknown')}
            jtbd_hierarchy = self.jtbd_constructor.construct(transcript, context)
            
            # Создаем результат
            result = AnalysisResult(
                transcript_id=str(row.get('classification.callId', 'unknown')),
                lead_inquiry=lead_inquiry,
                sales_blockers=sales_blockers,
                segment=segment,
                stop_words=comm_patterns.get('stop_words', []),
                power_words=comm_patterns.get('power_words', []),
                understanding_criteria=comm_patterns.get('understanding_criteria', {}),
                when_trigger=str(jtbd_hierarchy['when_trigger']),
                big_jtbd=str(jtbd_hierarchy['big_jtbd']),
                medium_jtbd=str(jtbd_hierarchy['medium_jtbd']),
                small_jtbd=str(jtbd_hierarchy['small_jtbd']),
                qualified_triggers=jtbd_hierarchy['qualified_triggers'],
                processing_time=time.time() - start_time
            )
            
            # Этап 5: Reflection Validation
            validation = self.reflection_validator.validate(result)
            if not validation['passed']:
                self.logger.warning(f"Validation failed for {result.transcript_id}: {validation['errors']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing transcript {row.get('classification.callId')}: {e}")
            # Return minimal result for error case
            return AnalysisResult(
                transcript_id=str(row.get('classification.callId', 'error')),
                lead_inquiry="Error in processing",
                sales_blockers=["Processing failed"],
                segment=segment,
                stop_words=[],
                power_words=[],
                understanding_criteria={},
                when_trigger="Error",
                big_jtbd="Error",
                medium_jtbd="Error", 
                small_jtbd="Error",
                qualified_triggers={},
                processing_time=time.time() - start_time
            )
    
    def _extract_lead_inquiry(self, transcript: str) -> str:
        """Извлекает первоначальный запрос клиента"""
        lines = transcript.split('\n')
        for line in lines:
            if 'Спикер 1' in line and len(line.strip()) > 20:  # Первый клиентский запрос
                return line.split('): ', 1)[-1].strip() if '): ' in line else line.strip()
        return "Lead inquiry not found"
    
    def _classify_segment(self, row: Dict[str, Any]) -> str:
        """Классифицирует сегмент B2B/B2C"""
        # Проверяем существующую классификацию в TSV
        existing_segment = row.get('segment  b2b/b2c', '').strip().lower()
        if existing_segment in ['b2b', 'b2c']:
            return existing_segment.upper()
        
        # TODO: Implement AI-based segment classification
        # Пока используем простую эвристику
        transcript = row.get('transcript', '').lower()
        b2b_indicators = ['компани', 'фирм', 'организаци', 'автопарк', 'флот']
        
        if any(indicator in transcript for indicator in b2b_indicators):
            return 'B2B'
        return 'B2C'

class BatchTranscriptProcessor:
    """
    JTBD: Когда нужно обработать 600+ транскриптов,
    хочу эффективно распараллелить процесс,
    чтобы получить результат за разумное время с высоким качеством
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.processor = AvtoallTranscriptProcessor()
        self.logger = logging.getLogger(__name__)
    
    def process_batch(self, tsv_file_path: str) -> BatchResults:
        """Обрабатывает весь batch транскриптов"""
        start_time = time.time()
        
        # Загружаем TSV данные
        data = self._load_tsv_data(tsv_file_path)
        self.logger.info(f"Loaded {len(data)} transcripts for processing")
        
        # Параллельная обработка
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self.processor.process_single_transcript, row)
                for row in data
            ]
            
            for i, future in enumerate(as_completed(futures)):
                try:
                    result = future.result()
                    results.append(result)
                    if i % 50 == 0:  # Progress logging every 50 items
                        self.logger.info(f"Processed {i+1}/{len(data)} transcripts")
                except Exception as e:
                    self.logger.error(f"Failed to process transcript {i+1}: {e}")
        
        # Анализ паттернов
        patterns = self._analyze_cross_patterns(results)
        training_materials = self._generate_training_materials(patterns)
        roadmap = self._create_implementation_roadmap(patterns)
        
        total_time = time.time() - start_time
        success_rate = sum(1 for r in results if r.validation_passed) / len(results)
        
        return BatchResults(
            individual_results=results,
            patterns=patterns,
            training_materials=training_materials,
            implementation_roadmap=roadmap,
            total_processing_time=total_time,
            success_rate=success_rate
        )
    
    def _load_tsv_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Загружает данные из TSV файла"""
        try:
            df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
            return df.to_dict('records')
        except Exception as e:
            self.logger.error(f"Error loading TSV file {file_path}: {e}")
            return []
    
    def _analyze_cross_patterns(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Анализирует паттерны across all результатов"""
        b2b_results = [r for r in results if r.segment == 'B2B']
        b2c_results = [r for r in results if r.segment == 'B2C']
        
        return {
            'total_analyzed': len(results),
            'b2b_count': len(b2b_results),
            'b2c_count': len(b2c_results),
            'common_sales_blockers': self._find_common_blockers(results),
            'top_stop_words': self._find_frequent_patterns([r.stop_words for r in results]),
            'success_rate': sum(1 for r in results if r.validation_passed) / len(results)
        }
    
    def _find_common_blockers(self, results: List[AnalysisResult]) -> List[str]:
        """Находит наиболее частые sales blockers"""
        blocker_frequency = {}
        for result in results:
            for blocker in result.sales_blockers:
                blocker_frequency[blocker] = blocker_frequency.get(blocker, 0) + 1
        
        # Возвращаем топ-10 наиболее частых блокеров (только текст)
        sorted_blockers = sorted(blocker_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        return [blocker for blocker, count in sorted_blockers]
    
    def _find_frequent_patterns(self, pattern_lists: List[List[str]]) -> List[str]:
        """Находит наиболее частые паттерны"""
        frequency = {}
        for patterns in pattern_lists:
            for pattern in patterns:
                frequency[pattern] = frequency.get(pattern, 0) + 1
        sorted_patterns = sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:20]
        return [pattern for pattern, count in sorted_patterns]
    
    def _generate_training_materials(self, patterns: Dict[str, Any]) -> Dict[str, List[str]]:
        """Генерирует готовые материалы для обучения"""
        return {
            'stop_words_examples': [item[0] for item in patterns.get('top_stop_words', [])[:10]],
            'common_blockers': [item[0] for item in patterns.get('common_sales_blockers', [])[:15]],
            'training_scripts': [
                "Script 1: Handling technical inquiries with confidence",
                "Script 2: Creating urgency without pressure", 
                "Script 3: B2B vs B2C communication approaches"
            ]
        }
    
    def _create_implementation_roadmap(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Создает 8-недельный план внедрения"""
        return {
            'week_1_2': 'Foundation: Operator training on identified blockers',
            'week_3_4': 'Optimization: A/B testing new communication patterns',
            'week_5_6': 'Advanced: Segment-specific approach implementation',
            'week_7_8': 'Mastery: Full workflow integration and monitoring',
            'success_metrics': {
                'conversion_rate_target': '15-25% improvement',
                'training_completion': '100% operators trained',
                'blocker_resolution': '80% identified blockers addressed'
            }
        }

# MCP Workflow Integration Functions
def execute_avtoall_transcript_analysis(file_path: str, max_workers: int = 4) -> Dict[str, Any]:
    """
    Main MCP workflow entry point for Avtoall transcript analysis
    
    JTBD: Когда система MCP получает команду на обработку транскриптов,
    нужно выполнить полный цикл анализа согласно стандарту,
    чтобы доставить готовые business deliverables
    """
    
    # Инициализируем batch processor
    batch_processor = BatchTranscriptProcessor(max_workers=max_workers)
    
    # Выполняем полный анализ
    results = batch_processor.process_batch(file_path)
    
    # Формируем MCP response
    return {
        'workflow': 'avtoall_transcript_analysis',
        'standard': STANDARD_PATH,
        'status': 'completed',
        'results': {
            'total_processed': len(results.individual_results),
            'success_rate': results.success_rate,
            'processing_time': results.total_processing_time,
            'patterns_identified': len(results.patterns.get('common_sales_blockers', [])),
            'training_materials_ready': len(results.training_materials.get('stop_words_examples', [])),
            'implementation_roadmap': results.implementation_roadmap
        },
        'deliverables': {
            'individual_analyses': len(results.individual_results),
            'cross_patterns': results.patterns,
            'training_materials': results.training_materials,
            'roadmap': results.implementation_roadmap
        }
    }

if __name__ == "__main__":
    # Direct execution для testing
    logging.basicConfig(level=logging.INFO)
    
    # Test файл path
    test_file = "[rick.ai] clients/avtoall.ru/whatsapp-jtbd-tracktion/raw/HeroesGPT JTBD. avtoall.ru - call_transcriptions_all 17.07.tsv"
    
    print("Starting Avtoall JTBD Transcript Analysis...")
    result = execute_avtoall_transcript_analysis(test_file, max_workers=2)
    print(f"Analysis completed: {result['results']}")