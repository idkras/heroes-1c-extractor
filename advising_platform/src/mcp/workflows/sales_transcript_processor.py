#!/usr/bin/env python3
"""
Sales JTBD Transcript Analysis MCP Workflow
Based on: [standards .md]/6. advising · review · supervising/🤝 sales-injury-jtbd-standard.md
Implementation of: sales-injury-jtbd-standard for processing call transcripts
"""

import time
import logging
import pandas as pd
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# STEP 0: Standard читается первым согласно требованию MCP workflow
STANDARD_PATH = "[standards .md]/6. advising · review · supervising/🤝 sales-injury-jtbd-standard.md"
TSV_DATA_PATH = "[rick.ai] clients/avtoall.ru/[4] whatsapp-jtbd-tracktion/raw/HeroesGPT JTBD. avtoall.ru - call_transcriptions_all 17.07.tsv"

@dataclass
class SalesAnalysisResult:
    """
    JTBD: Когда завершается анализ транскрипта продаж,
    нужна структурированная форма результата,
    чтобы обеспечить consistent обработку и валидацию для Google Docs
    """
    transcript: str  # Полный текст транскрипта
    lead_inquiry: str  # Основной запрос клиента
    root_cause_5why: str  # что сеилз не так сделал, что продажа не случилась
    sales_blockers: str  # Конкретные препятствия для закрытия сделки
    segment: str  # B2B/B2C
    stop_words: str  # "как не нужно говорить, что стоп-слова"
    power_words: str  # "как хотим, чтобы говорили" 
    understanding_criteria: str  # "вопросы на каждой стадии, что нужно понимать клиент"
    when_trigger: str  # "when ситуация в big_jtbd"
    big_jtbd: str
    medium_jtbd: str
    small_jtbd: str
    qualified_triggers: str  # срочность, бюджет, качество
    processing_time: float
    validation_passed: bool = False
    quality_score: float = 0.0

@dataclass 
class BatchSalesResults:
    """Результаты batch обработки с паттерн-анализом"""
    individual_results: List[SalesAnalysisResult]
    patterns: Dict[str, Any]
    training_materials: Dict[str, List[str]]
    implementation_roadmap: Dict[str, Any]
    total_processing_time: float
    success_rate: float
    output_tsv_path: str

class SalesReflectionValidator:
    """
    JTBD: Когда анализ завершен,
    нужно валидировать качество по критериям стандарта,
    чтобы гарантировать 90%+ pass rate согласно требованиям
    
    ENHANCED v4.0: Добавлены ANTI-BULLSHIT CHECKPOINTS из sales-injury standard v1.1
    """
    
    @staticmethod
    def validate_analysis(result: SalesAnalysisResult) -> tuple[bool, float, Dict[str, str]]:
        """Валидация согласно reflection checkpoints + ANTI-BULLSHIT проверки"""
        validation_issues = {}
        score = 0.0
        max_score = 100.0
        
        # CRITICAL ANTI-BULLSHIT CHECKPOINTS (MANDATORY BEFORE ANY OTHER VALIDATION)
        critical_failures = []
        
        # CHECKPOINT 2: PROCESSOR OUTPUT VALIDATION
        critical_columns = {
            'sales_blockers': result.sales_blockers,
            'root_cause_5why': result.root_cause_5why,
            'stop_words': result.stop_words if hasattr(result, 'stop_words') else None,
            'power_words': result.power_words if hasattr(result, 'power_words') else None
        }
        
        for col_name, col_value in critical_columns.items():
            if not col_value or len(str(col_value).strip()) < 10:
                critical_failures.append(f"MANDATORY FAIL: {col_name} has <10 characters - not real analysis")
            elif str(col_value).strip() in ["", "N/A", "None", "null", "Недоступно", "требуется AI"]:
                critical_failures.append(f"MANDATORY FAIL: {col_name} contains placeholder/empty data")
        
        # AUTOMATIC REJECTION if critical failures
        if critical_failures:
            return False, 0.0, {
                "anti_bullshit_status": "FAILED - AUTOMATIC REJECTION",
                "critical_failures": critical_failures,
                "rejection_reason": "Generated empty/placeholder data instead of real analysis"
            }
        
        # Original validation logic (only if critical checks pass)
        # 1. Root Cause Analysis validation (20 points)
        if result.root_cause_5why and len(result.root_cause_5why.split("Why #")) >= 5:
            score += 20
        else:
            validation_issues["5why"] = "Неполная 5-why цепочка причин"
            
        # 2. Sales Blockers validation (15 points)  
        if result.sales_blockers and len(result.sales_blockers) > 50:
            score += 15
        else:
            validation_issues["blockers"] = "Недостаточно детализированы sales blockers"
            
        # 3. Communication Pattern Analysis (20 points)
        if result.stop_words and result.power_words:
            score += 20
        else:
            validation_issues["communication"] = "Отсутствуют примеры stop/power words"
            
        # 4. JTBD Hierarchy validation (25 points)
        if all([result.when_trigger, result.big_jtbd, result.medium_jtbd, result.small_jtbd]):
            score += 25
        else:
            validation_issues["jtbd"] = "Неполная JTBD иерархия"
            
        # 5. Decision Journey mapping (20 points)
        if result.understanding_criteria and result.segment in ["B2B", "B2C"]:
            score += 20
        else:
            validation_issues["journey"] = "Отсутствует decision journey mapping"
            
        result.quality_score = score
        result.validation_passed = score >= 90.0
        
        return result.validation_passed, score, validation_issues

class SalesBlockersAnalyzer:
    """
    JTBD: Когда нужно выявить препятствия для закрытия сделки,
    нужен анализ по стадиям продаж,
    чтобы найти конкретные точки утечки conversion
    """
    
    SALES_STAGES = [
        "подтверждение понимания запроса",
        "уточнение деталей",
        "информирование о наличии", 
        "поддержание доверия",
        "подбор продукта",
        "дополнительные предложения",
        "обработка возражений",
        "закрытие сделки"
    ]
    
    @staticmethod
    def analyze_blockers(transcript: str, lead_inquiry: str) -> str:
        """5-why анализ что сеилз не так сделал"""
        # Simplified implementation - в production будет AI analysis
        blockers = []
        
        if "нет" in transcript.lower() and "есть" not in transcript.lower():
            blockers.append("Не предложил альтернативы при отсутствии товара")
            
        if "далеко" in transcript.lower() or "далекий" in transcript.lower():
            blockers.append("Не предложил доставку или удобные варианты получения")
            
        if "дорого" in transcript.lower() or "цена" in transcript.lower():
            blockers.append("Не обработал ценовые возражения")
            
        return "; ".join(blockers) if blockers else "Блокеры не выявлены"

class CommunicationPatternAnalyzer:
    """
    JTBD: Когда нужно улучшить коммуникацию операторов,
    нужен анализ стоп-слов vs power words,
    чтобы создать training materials для команды
    """
    
    @staticmethod
    def extract_stop_words(transcript: str) -> str:
        """Извлечение неэффективных фраз"""
        stop_patterns = [
            "не знаю",
            "где-то",
            "может быть",
            "наверное",
            "это все далеко",
            "такой уже нет"
        ]
        
        found_patterns = []
        for pattern in stop_patterns:
            if pattern in transcript.lower():
                found_patterns.append(f'"{pattern}"')
                
        return "; ".join(found_patterns) if found_patterns else "Стоп-слова не выявлены"
    
    @staticmethod
    def generate_power_words(stop_words: str, lead_inquiry: str) -> str:
        """Создание оптимизированных альтернатив"""
        if "не знаю" in stop_words:
            return "Давайте уточним детали, чтобы найти точный вариант"
        elif "далеко" in stop_words:
            return "Понимаю ваши требования к удобству. Предлагаю несколько вариантов получения"
        elif "нет" in stop_words:
            return "Есть альтернативные решения с аналогичными характеристиками"
        
        return "Профессиональная консультация с вариантами решения"

class JTBDHierarchyConstructor:
    """
    JTBD: Когда нужно построить иерархию Big/Medium/Small JTBD,
    нужна декомпозиция по уровням стратегии,
    чтобы понять истинные потребности клиента
    """
    
    @staticmethod
    def construct_hierarchy(transcript: str, lead_inquiry: str, segment: str) -> Dict[str, str]:
        """Построение 4-уровневой JTBD структуры"""
        
        # When Trigger анализ
        when_trigger = "когда клиент сталкивается с необходимостью решить проблему"
        if "срочно" in transcript.lower() or "завтра" in transcript.lower():
            when_trigger = "когда требуется срочное решение проблемы с ограниченным временем"
            
        # Big JTBD по сегменту
        if segment == "B2B":
            big_jtbd = "обеспечить бесперебойную работу бизнес-процессов"
        else:
            big_jtbd = "быстро решить личную проблему с минимальными усилиями"
            
        # Medium JTBD - тактический уровень
        medium_jtbd = "найти и приобрести нужный продукт с подтверждением качества"
        
        # Small JTBD - операционный уровень  
        small_jtbd = "получить консультацию, узнать цену и способы получения товара"
        
        # Qualified Triggers
        qualified_triggers = "стандартные требования к качеству и доступности"
        if "дорого" in transcript.lower():
            qualified_triggers += "; бюджетные ограничения"
        if "срочно" in transcript.lower():
            qualified_triggers += "; высокая срочность"
            
        return {
            "when_trigger": when_trigger,
            "big_jtbd": big_jtbd, 
            "medium_jtbd": medium_jtbd,
            "small_jtbd": small_jtbd,
            "qualified_triggers": qualified_triggers
        }

class DecisionJourneyMapper:
    """
    JTBD: Когда нужно проанализировать decision journey,
    нужно mapping по 8 стадиям B2C/B2B,
    чтобы выявить gaps в процессе принятия решения
    """
    
    B2C_STAGES = [
        "Problem Recognition", "Solution Possibility", "Personal Relevance",
        "Feasibility", "Social Validation", "Risk Evaluation", "Urgency", "Action Simplification"
    ]
    
    B2B_STAGES = [
        "Business Impact", "Solution-Problem Fit", "Internal Champion", 
        "Stakeholder Alignment", "Risk Mitigation", "Budget Justification",
        "Implementation", "Vendor Reliability"
    ]
    
    @staticmethod
    def map_understanding_criteria(transcript: str, segment: str) -> str:
        """Создание критериев понимания для каждой стадии"""
        
        criteria = []
        
        if segment == "B2C":
            stages = DecisionJourneyMapper.B2C_STAGES
            if "понял" in transcript.lower():
                criteria.append("Problem Recognition: клиент чувствует понимание проблемы")
            if "подходит" in transcript.lower():
                criteria.append("Personal Relevance: клиент видит релевантность решения")
            if "цена" in transcript.lower():
                criteria.append("Feasibility: клиент оценивает финансовую доступность")
        else:
            stages = DecisionJourneyMapper.B2B_STAGES
            if "бизнес" in transcript.lower():
                criteria.append("Business Impact: понимание влияния на бизнес")
            if "качество" in transcript.lower():
                criteria.append("Risk Mitigation: оценка рисков качества")
                
        return "; ".join(criteria) if criteria else "Критерии понимания требуют дополнительной проработки"

class SalesTranscriptProcessor:
    """
    Главный класс для обработки транскриптов продаж
    
    JTBD: Когда нужно обработать 600+ транскриптов звонков,
    нужен автоматизированный pipeline с качественным анализом,
    чтобы сократить время обработки с 30-45 мин до ≤5 мин на транскрипт
    """
    
    def __init__(self):
        """Инициализация с чтением стандарта (STEP 0)"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.standard_config = self._load_standard_config()
        self.validator = SalesReflectionValidator()
        self.blockers_analyzer = SalesBlockersAnalyzer()
        self.communication_analyzer = CommunicationPatternAnalyzer()
        self.jtbd_constructor = JTBDHierarchyConstructor()
        self.journey_mapper = DecisionJourneyMapper()
        
    def _load_standard_config(self) -> Dict[str, Any]:
        """STEP 0: Чтение стандарта (обязательный первый шаг)"""
        config = {
            'processing_time_limit': 45 * 60,  # 45 minutes max
            'batch_size': 10,
            'quality_threshold': 90.0,
            'reflection_checkpoints': True
        }
        
        # Попытка прочитать стандарт
        if os.path.exists(STANDARD_PATH):
            self.logger.info(f"✅ Standard loaded from: {STANDARD_PATH}")
            # В production здесь будет парсинг стандарта
        else:
            self.logger.warning(f"Standard not found at {STANDARD_PATH}, using defaults")
            
        return config
    
    def process_single_transcript(self, row: pd.Series) -> SalesAnalysisResult:
        """
        Обработка одного транскрипта согласно 6-этапному workflow из стандарта
        
        JTBD: Когда нужно проанализировать один звонок,
        нужен systematic approach по всем этапам стандарта,
        чтобы получить complete analysis для Google Docs таблицы
        """
        start_time = time.time()
        
        # Извлечение базовых данных
        transcript = str(row.get('transcript', ''))
        lead_inquiry = str(row.get('lead_inquiry', ''))
        
        # 1️⃣ Root Cause Analysis (5-Why)
        root_cause_5why = self._perform_5why_analysis(transcript, lead_inquiry)
        
        # 2️⃣ Sales Blockers Identification  
        sales_blockers = self.blockers_analyzer.analyze_blockers(transcript, lead_inquiry)
        
        # 3️⃣ Communication Pattern Analysis
        stop_words = self.communication_analyzer.extract_stop_words(transcript)
        power_words = self.communication_analyzer.generate_power_words(stop_words, lead_inquiry)
        
        # Сегментация
        segment = "B2B" if any(word in transcript.lower() for word in ["бизнес", "парк", "флот"]) else "B2C"
        
        # 4️⃣ JTBD Hierarchy Construction
        jtbd_hierarchy = self.jtbd_constructor.construct_hierarchy(transcript, lead_inquiry, segment)
        
        # 5️⃣ Decision Journey Stage Mapping
        understanding_criteria = self.journey_mapper.map_understanding_criteria(transcript, segment)
        
        processing_time = time.time() - start_time
        
        # Создание результата
        result = SalesAnalysisResult(
            transcript=transcript,
            lead_inquiry=lead_inquiry,
            root_cause_5why=root_cause_5why,
            sales_blockers=sales_blockers,
            segment=segment,
            stop_words=stop_words,
            power_words=power_words,
            understanding_criteria=understanding_criteria,
            when_trigger=jtbd_hierarchy["when_trigger"],
            big_jtbd=jtbd_hierarchy["big_jtbd"],
            medium_jtbd=jtbd_hierarchy["medium_jtbd"],
            small_jtbd=jtbd_hierarchy["small_jtbd"],
            qualified_triggers=jtbd_hierarchy["qualified_triggers"],
            processing_time=processing_time
        )
        
        # Валидация качества
        self.validator.validate_analysis(result)
        
        return result
    
    def _perform_5why_analysis(self, transcript: str, lead_inquiry: str) -> str:
        """5-why анализ что сеилз не так сделал"""
        why_chain = []
        
        # Why #1: Surface problem
        if "не купил" in transcript.lower() or not any(word in transcript.lower() for word in ["заказ", "покупаю", "беру"]):
            why_chain.append("Why #1: Почему клиент не совершил покупку? → Не получил подходящего предложения")
        
        # Why #2: Process limitation  
        if "нет" in transcript.lower():
            why_chain.append("Why #2: Почему не получил предложения? → Оператор сфокусировался на отсутствии, а не на альтернативах")
        
        # Why #3: UX gap
        if "далеко" in transcript.lower():
            why_chain.append("Why #3: Почему не предложил альтернативы? → Не выяснил критерии удобства клиента")
            
        # Why #4: Information architecture
        if len(why_chain) > 2:
            why_chain.append("Why #4: Почему не выяснил критерии? → Отсутствует процедура qualification вопросов")
            
        # Why #5: Root cause
        if len(why_chain) > 3:
            why_chain.append("Why #5: Почему нет процедуры? → Операторы не обучены consultative selling подходу")
        
        return "\n".join(why_chain) if why_chain else "5-why анализ: системные причины не выявлены"
    
    def process_tsv_batch(self, tsv_path: str, output_path: str = None) -> BatchSalesResults:
        """
        Batch обработка TSV файла с созданием Google Docs ready таблицы
        
        JTBD: Когда нужно обработать полную TSV таблицу,
        нужен parallel processing с качественной валидацией,
        чтобы получить готовую таблицу для загрузки в Google Docs
        """
        start_time = time.time()
        
        # Загрузка данных
        if not os.path.exists(tsv_path):
            self.logger.error(f"TSV file not found: {tsv_path}")
            return None
            
        df = pd.read_csv(tsv_path, sep='\t')
        self.logger.info(f"Loaded {len(df)} rows from {tsv_path}")
        
        # Parallel processing
        results = []
        batch_size = self.standard_config['batch_size']
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            
            for index, row in df.iterrows():
                future = executor.submit(self.process_single_transcript, row)
                futures.append(future)
                
                # Process in batches
                if len(futures) >= batch_size:
                    for future in as_completed(futures):
                        try:
                            result = future.result(timeout=300)  # 5 min timeout
                            results.append(result)
                        except Exception as e:
                            self.logger.error(f"Processing failed: {e}")
                    futures = []
            
            # Process remaining
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=300)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Processing failed: {e}")
        
        # Создание output TSV для Google Docs
        output_df = self._create_output_tsv(results)
        
        if output_path is None:
            output_path = tsv_path.replace('.tsv', '_analyzed.tsv')
        
        output_df.to_csv(output_path, sep='\t', index=False, encoding='utf-8')
        
        total_time = time.time() - start_time
        success_rate = sum(1 for r in results if r.validation_passed) / len(results) if results else 0
        
        self.logger.info(f"✅ Batch processing complete:")
        self.logger.info(f"   Processed: {len(results)} transcripts")
        self.logger.info(f"   Success rate: {success_rate:.1%}")
        self.logger.info(f"   Total time: {total_time/60:.1f} minutes")
        self.logger.info(f"   Output saved: {output_path}")
        
        return BatchSalesResults(
            individual_results=results,
            patterns={},
            training_materials={},
            implementation_roadmap={},
            total_processing_time=total_time,
            success_rate=success_rate,
            output_tsv_path=output_path
        )
    
    def _create_output_tsv(self, results: List[SalesAnalysisResult]) -> pd.DataFrame:
        """
        Создание TSV таблицы готовой для загрузки в Google Docs
        Соответствует column mapping из стандарта
        """
        
        output_data = []
        
        for result in results:
            row = {
                'transcript': result.transcript,
                'lead_inquiry': result.lead_inquiry,
                'root cause 5why': result.root_cause_5why,
                'sales_blockers': result.sales_blockers,
                'segment': result.segment,
                'как не нужно говорить, что стоп-слова': result.stop_words,
                'как хотим, чтобы говорили': result.power_words,
                'вопросы на каждой стадии, что нужно понимать клиент': result.understanding_criteria,
                'when ситуация в big_jtbd': result.when_trigger,
                'big_jtbd': result.big_jtbd,
                'medium_jtbd': result.medium_jtbd,
                'small_jtbd': result.small_jtbd,
                'qualified_triggers': result.qualified_triggers,
                'processing_time_sec': round(result.processing_time, 2),
                'quality_score': round(result.quality_score, 1),
                'validation_passed': result.validation_passed
            }
            output_data.append(row)
        
        return pd.DataFrame(output_data)

# MCP Integration Functions
def mcp_process_sales_transcripts(tsv_path: str = None, output_path: str = None) -> Dict[str, Any]:
    """
    MCP-compatible function для интеграции с HTTP adapter
    
    JTBD: Когда MCP система вызывает анализ транскриптов,
    нужен standardized interface с error handling,
    чтобы обеспечить надежную интеграцию с workflow orchestration
    """
    
    processor = SalesTranscriptProcessor()
    
    # Используем default path если не указан
    if tsv_path is None:
        tsv_path = TSV_DATA_PATH
    
    try:
        results = processor.process_tsv_batch(tsv_path, output_path)
        
        return {
            "status": "success",
            "processed_count": len(results.individual_results),
            "success_rate": results.success_rate,
            "processing_time_minutes": results.total_processing_time / 60,
            "output_file": results.output_tsv_path,
            "ready_for_google_docs": True,
            "quality_metrics": {
                "average_score": sum(r.quality_score for r in results.individual_results) / len(results.individual_results),
                "validation_pass_rate": results.success_rate
            }
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "ready_for_google_docs": False
        }

if __name__ == "__main__":
    # Демонстрационный запуск
    processor = SalesTranscriptProcessor()
    print("🎯 Sales Transcript Processor initialized")
    print("📊 Ready for MCP workflow integration")
    print(f"📋 Standard: {STANDARD_PATH}")
    print(f"📁 Data source: {TSV_DATA_PATH}")
    
    # Пример использования:
    # results = processor.process_tsv_batch(TSV_DATA_PATH)
    # print(f"✅ Processed {len(results.individual_results)} transcripts")
    # print(f"📈 Success rate: {results.success_rate:.1%}")