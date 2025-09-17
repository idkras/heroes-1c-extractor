#!/usr/bin/env python3
"""
AIGuidanceWorkflow - Единый workflow для всех guidance команд
Объединяет 11 дублирующих команд в один параметризованный API

TDD подход с устранением дублирования JTBD сценариев
"""

import logging
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class GuidanceType(str, Enum):
    """Типы guidance для единого workflow"""

    # AI Guidance команды (4 команды)
    AI_GUIDANCE_CHECKLIST = "ai_guidance_checklist"
    COMMON_MISTAKES_PREVENTION = "common_mistakes_prevention"
    QUALITY_VALIDATION = "quality_validation"
    APPROACH_RECOMMENDATION = "approach_recommendation"

    # Registry команды (5 команд)
    REGISTRY_COMPLIANCE_CHECK = "registry_compliance_check"
    REGISTRY_OUTPUT_VALIDATE = "registry_output_validate"
    REGISTRY_DOCS_AUDIT = "registry_docs_audit"
    REGISTRY_GAP_REPORT = "registry_gap_report"
    REGISTRY_RELEASE_BLOCK = "registry_release_block"

    # Validation команды (2 команды)
    VALIDATE_OUTPUT_ARTEFACT = "validate_output_artefact"
    VALIDATE_ACTUAL_OUTCOME = "validate_actual_outcome"


class GuidanceRequest(BaseModel):
    """Модель запроса для AIGuidanceWorkflow"""

    guidance_type: GuidanceType = Field(..., description="Тип guidance")
    task_type: Optional[str] = Field(None, description="Тип задачи")
    domain: Optional[str] = Field(None, description="Домен")
    problem: Optional[str] = Field(None, description="Проблема")
    context: Optional[str] = Field(None, description="Контекст")
    result: Optional[str] = Field(None, description="Результат")
    criteria: Optional[str] = Field(None, description="Критерии")
    jtbd: Optional[str] = Field(None, description="JTBD")
    artifact: Optional[str] = Field(None, description="Артефакт")
    paths: Optional[str] = Field(None, description="Пути")
    expected: Optional[str] = Field(None, description="Ожидаемое")
    actual: Optional[str] = Field(None, description="Фактическое")
    decision: Optional[str] = Field(None, description="Решение")
    until: Optional[str] = Field(None, description="До")
    artefact_path: Optional[str] = Field(None, description="Путь к артефакту")
    artefact_type: Optional[str] = Field(None, description="Тип артефакта")
    quality_criteria: Optional[str] = Field(None, description="Критерии качества")
    url: Optional[str] = Field(None, description="URL")
    expected_features: Optional[str] = Field(None, description="Ожидаемые функции")
    test_cases: Optional[str] = Field(None, description="Тест-кейсы")
    take_screenshot: Optional[bool] = Field(True, description="Делать скриншот")


class GuidanceResponse(BaseModel):
    """Модель ответа для AIGuidanceWorkflow"""

    success: bool = Field(..., description="Успешность выполнения")
    guidance_type: GuidanceType = Field(..., description="Тип guidance")
    result: str = Field(..., description="Результат")
    reflection_checkpoint: Optional[str] = Field(
        None, description="Reflection checkpoint"
    )
    error: Optional[str] = Field(None, description="Ошибка")


class AIGuidanceWorkflow:
    """
    Единый AIGuidanceWorkflow для всех guidance команд

    JTBD: Как архитектор, я хочу создать единый AIGuidanceWorkflow,
    объединяющий все guidance команды с одинаковыми JTBD сценариями,
    чтобы устранить дублирование кода, упростить поддержку и обеспечить
    соответствие стандартам.
    """

    def __init__(self):
        self.guidance_templates = self._initialize_guidance_templates()
        logger.info("AIGuidanceWorkflow initialized with 11 guidance types")

    def _initialize_guidance_templates(self) -> dict[GuidanceType, dict[str, Any]]:
        """Инициализация шаблонов для всех типов guidance"""
        return {
            # AI Guidance команды
            GuidanceType.AI_GUIDANCE_CHECKLIST: {
                "template": "AI Guidance Checklist для {task_type}",
                "description": "Чеклист для проверки AI работы",
                "jtbd": "Как guidance system, я хочу дать AI чеклист для проверки",
            },
            GuidanceType.COMMON_MISTAKES_PREVENTION: {
                "template": "Предотвращение типичных ошибок в {domain}",
                "description": "Предупреждение о типичных ошибках",
                "jtbd": "Как prevention system, я хочу предупредить о типичных ошибках",
            },
            GuidanceType.QUALITY_VALIDATION: {
                "template": "Валидация качества результата: {result}",
                "description": "Проверка качества результата AI",
                "jtbd": "Как validator, я хочу проверить качество результата AI",
            },
            GuidanceType.APPROACH_RECOMMENDATION: {
                "template": "Рекомендация подхода для проблемы: {problem}",
                "description": "Рекомендация подхода к решению проблемы",
                "jtbd": "Как advisor, я хочу рекомендовать подход к решению проблемы",
            },
            # Registry команды
            GuidanceType.REGISTRY_COMPLIANCE_CHECK: {
                "template": "Проверка соответствия Registry Standard",
                "description": "Проверка соответствия Registry Standard",
                "jtbd": "Проверка соответствия Registry Standard",
            },
            GuidanceType.REGISTRY_OUTPUT_VALIDATE: {
                "template": "Валидация output артефакта: {artifact}",
                "description": "Проверка артефакта",
                "jtbd": "Как guidance system, я хочу дать AI Agent чеклист для проверки артефакта",
            },
            GuidanceType.REGISTRY_DOCS_AUDIT: {
                "template": "Аудит документации по путям: {paths}",
                "description": "Аудит документации",
                "jtbd": "Как guidance system, я хочу дать AI Agent чеклист для аудита документации",
            },
            GuidanceType.REGISTRY_GAP_REPORT: {
                "template": "Gap анализ: ожидаемое={expected}, фактическое={actual}",
                "description": "Анализ gap",
                "jtbd": "Как guidance system, я хочу дать AI Agent чеклист для анализа gap",
            },
            GuidanceType.REGISTRY_RELEASE_BLOCK: {
                "template": "Блокировка релиза до: {until}",
                "description": "Блокировка релиза",
                "jtbd": "Как guidance system, я хочу дать AI Agent чеклист для блокировки релиза",
            },
            # Validation команды
            GuidanceType.VALIDATE_OUTPUT_ARTEFACT: {
                "template": "Валидация output артефакта: {artefact_path}",
                "description": "Проверка output артефакта",
                "jtbd": "Как валидатор output, я хочу проверить output artefact",
            },
            GuidanceType.VALIDATE_ACTUAL_OUTCOME: {
                "template": "Валидация фактического результата: {url}",
                "description": "Проверка фактического результата",
                "jtbd": "Как валидатор outcome, я хочу проверить фактический результат",
            },
        }

    def execute_guidance(self, request: GuidanceRequest) -> GuidanceResponse:
        """
        Выполнение guidance workflow

        Args:
            request: Запрос с параметрами guidance

        Returns:
            GuidanceResponse: Результат выполнения
        """
        try:
            logger.info(f"Executing guidance: {request.guidance_type}")

            # Получение шаблона для типа guidance
            template_info = self.guidance_templates.get(request.guidance_type)
            if not template_info:
                return GuidanceResponse(
                    success=False,
                    guidance_type=request.guidance_type,
                    result="",
                    error=f"Unknown guidance type: {request.guidance_type}",
                    reflection_checkpoint=None,
                )

            # Выполнение конкретного типа guidance
            result = self._execute_specific_guidance(request, template_info)

            # Reflection checkpoint
            reflection_checkpoint = self._create_reflection_checkpoint(request, result)

            return GuidanceResponse(
                success=True,
                guidance_type=request.guidance_type,
                result=result,
                reflection_checkpoint=reflection_checkpoint,
                error=None,
            )

        except Exception as e:
            logger.error(f"Error in execute_guidance: {e}")
            return GuidanceResponse(
                success=False,
                guidance_type=request.guidance_type,
                result="",
                error=str(e),
                reflection_checkpoint=None,
            )

    def _execute_specific_guidance(
        self, request: GuidanceRequest, template_info: dict[str, Any]
    ) -> str:
        """Выполнение конкретного типа guidance"""
        guidance_type = request.guidance_type

        if guidance_type == GuidanceType.AI_GUIDANCE_CHECKLIST:
            return self._ai_guidance_checklist(request)
        elif guidance_type == GuidanceType.COMMON_MISTAKES_PREVENTION:
            return self._common_mistakes_prevention(request)
        elif guidance_type == GuidanceType.QUALITY_VALIDATION:
            return self._quality_validation(request)
        elif guidance_type == GuidanceType.APPROACH_RECOMMENDATION:
            return self._approach_recommendation(request)
        elif guidance_type == GuidanceType.REGISTRY_COMPLIANCE_CHECK:
            return self._registry_compliance_check(request)
        elif guidance_type == GuidanceType.REGISTRY_OUTPUT_VALIDATE:
            return self._registry_output_validate(request)
        elif guidance_type == GuidanceType.REGISTRY_DOCS_AUDIT:
            return self._registry_docs_audit(request)
        elif guidance_type == GuidanceType.REGISTRY_GAP_REPORT:
            return self._registry_gap_report(request)
        elif guidance_type == GuidanceType.REGISTRY_RELEASE_BLOCK:
            return self._registry_release_block(request)
        elif guidance_type == GuidanceType.VALIDATE_OUTPUT_ARTEFACT:
            return self._validate_output_artefact(request)
        elif guidance_type == GuidanceType.VALIDATE_ACTUAL_OUTCOME:
            return self._validate_actual_outcome(request)
        else:
            return f"Unknown guidance type: {guidance_type}"

    def _ai_guidance_checklist(self, request: GuidanceRequest) -> str:
        """AI Guidance Checklist"""
        task_type = request.task_type or "general"
        template_info = self.guidance_templates[GuidanceType.AI_GUIDANCE_CHECKLIST]
        return f"""
# AI Guidance Checklist для {task_type}

## ✅ Чеклист проверки AI работы:

1. **Релевантность ответа**
   - Ответ соответствует запросу пользователя
   - Учтены все аспекты задачи

2. **Точность информации**
   - Факты проверены и корректны
   - Нет противоречий в данных

3. **Полнота решения**
   - Рассмотрены все варианты
   - Учтены edge cases

4. **Практическая применимость**
   - Решение можно реализовать
   - Учтены ограничения системы

5. **Соответствие стандартам**
   - Соблюдены coding standards
   - Применены best practices

## 🎯 JTBD: {template_info["jtbd"]}
"""

    def _common_mistakes_prevention(self, request: GuidanceRequest) -> str:
        """Common Mistakes Prevention"""
        domain = request.domain or "general"
        template_info = self.guidance_templates[GuidanceType.COMMON_MISTAKES_PREVENTION]
        return f"""
# Предотвращение типичных ошибок в {domain}

## ⚠️ Типичные ошибки и их предотвращение:

1. **Архитектурные ошибки**
   - Неправильное разделение ответственности
   - Нарушение принципов SOLID

2. **Ошибки безопасности**
   - Недостаточная валидация входных данных
   - Отсутствие аутентификации

3. **Ошибки производительности**
   - N+1 запросы к базе данных
   - Отсутствие кэширования

4. **Ошибки тестирования**
   - Недостаточное покрытие тестами
   - Отсутствие integration тестов

5. **Ошибки документации**
   - Устаревшая документация
   - Отсутствие примеров использования

## 🎯 JTBD: {template_info["jtbd"]}
"""

    def _quality_validation(self, request: GuidanceRequest) -> str:
        """Quality Validation"""
        result = request.result or "результат"
        criteria = request.criteria or "general"
        template_info = self.guidance_templates[GuidanceType.QUALITY_VALIDATION]
        return f"""
# Валидация качества результата

## 📊 Анализ качества: {result}

### Критерии оценки ({criteria}):
1. **Функциональность** - работает ли как задумано
2. **Надежность** - стабильность работы
3. **Производительность** - скорость выполнения
4. **Безопасность** - защищенность данных
5. **Удобство использования** - простота интерфейса

### Результат валидации:
- ✅ Соответствует требованиям
- ⚠️ Требует доработки
- ❌ Не соответствует критериям

## 🎯 JTBD: {template_info["jtbd"]}
"""

    def _approach_recommendation(self, request: GuidanceRequest) -> str:
        """Approach Recommendation"""
        problem = request.problem or "проблема"
        context = request.context or ""
        template_info = self.guidance_templates[GuidanceType.APPROACH_RECOMMENDATION]
        return f"""
# Рекомендация подхода к решению

## 🎯 Проблема: {problem}

### Контекст: {context}

## 💡 Рекомендуемый подход:

1. **Анализ проблемы**
   - Определение корневых причин
   - Анализ зависимостей

2. **Выбор решения**
   - Оценка вариантов
   - Выбор оптимального подхода

3. **Планирование реализации**
   - Разбивка на этапы
   - Оценка ресурсов

4. **Контроль качества**
   - Тестирование
   - Валидация результата

## 🎯 JTBD: {template_info["jtbd"]}
"""

    def _registry_compliance_check(self, request: GuidanceRequest) -> str:
        """Registry Compliance Check"""
        template_info = self.guidance_templates[GuidanceType.REGISTRY_COMPLIANCE_CHECK]
        return f"""
# Проверка соответствия Registry Standard

## ✅ Registry Compliance Check

### Проверяемые аспекты:
1. **Структура проекта**
   - Соответствие стандартам именования
   - Правильная организация файлов

2. **Документация**
   - Наличие README.md
   - Актуальность документации

3. **Тестирование**
   - Покрытие тестами
   - Качество тестов

4. **CI/CD**
   - Настройка pipeline
   - Автоматизация процессов

5. **Безопасность**
   - Проверка зависимостей
   - Анализ уязвимостей

## 🎯 JTBD: {template_info["jtbd"]}
"""

    def _registry_output_validate(self, request: GuidanceRequest) -> str:
        """Registry Output Validate - проверка соответствия релизов стандарту 1.4 from-the-end.process"""
        artifact = request.artifact or "артефакт"
        template_info = self.guidance_templates[GuidanceType.REGISTRY_OUTPUT_VALIDATE]
        return f"""
# Валидация Registry Output согласно стандарту 1.4 from-the-end.process

## 📋 Валидация артефакта: {artifact}

### 🚨 ОБЯЗАТЕЛЬНЫЕ ЭЛЕМЕНТЫ РЕЛИЗА (стандарт 1.4):

#### 1. 🤖 AI Agent Output (ОБЯЗАТЕЛЬНО)
- [ ] Есть шаблон ✅📝🔗
- [ ] Указано название релиза
- [ ] Описаны конкретные данные/метрики
- [ ] Есть ссылка на артефакт
- [ ] Приведена статистика

#### 2. 👁️ "Что увидит пользователь" (ОБЯЗАТЕЛЬНО)
- [ ] Описаны конкретные изменения в интерфейсе/процессе
- [ ] Перечислены новые возможности/функции
- [ ] Указаны улучшения в работе/производительности

#### 3. ✅ Критерии проверки (ОБЯЗАТЕЛЬНО)
- [ ] Ссылка работает и доступна
- [ ] Результат соответствует ожиданиям заказчика
- [ ] Можно доверять результату (валидирован)
- [ ] Есть специфичные для релиза критерии

#### 4. 🎯 Outcome и Artifact (ОБЯЗАТЕЛЬНО)
- [ ] Outcome: что изменится в бизнесе (измеримо в деньгах/часах/метриках)
- [ ] Artifact: конкретный файл/ссылка для проверки пользователем

#### 5. 📋 Чеклист соответствия стандарту (ОБЯЗАТЕЛЬНО)
- [ ] Есть AI Agent Output с шаблоном ✅📝🔗
- [ ] Описано "Что увидит пользователь"
- [ ] Указаны критерии проверки
- [ ] Определен Outcome и Artifact
- [ ] Результат измерим и проверяем
- [ ] **ОБЯЗАТЕЛЬНО: Определен эталон для сравнения (Reference of Truth)**
- [ ] **ОБЯЗАТЕЛЬНО: Выполнен Artefact Comparison Challenge**
- [ ] **ОБЯЗАТЕЛЬНО: Проведен end-to-end тест с опровержением успеха**
- [ ] **ОБЯЗАТЕЛЬНО: При критических проблемах включен RSA анализ**

#### 6. 🔗 Dependency Management Status (ОБЯЗАТЕЛЬНО)
- [ ] Обновлены зависимости согласно Enhanced Dependency Management Protocol
- [ ] Пройдены все automated tests
- [ ] Валидирован пользовательский опыт

### 🔒 Validation Gate (ОБЯЗАТЕЛЬНО)
- [ ] Приложены evidence (telegram.audit / docs.audit / скриншоты)
- [ ] **Релиз запущен и проверен на реальных данных**
- [ ] **Сравнение фактического и ожидаемого output выполнено**
- [ ] **Gap Analysis проведен и задокументирован**

### 📊 Общие критерии валидации:
1. **Соответствие стандартам**
   - Формат данных
   - Структура

2. **Полнота данных**
   - Все обязательные поля
   - Корректность значений

3. **Качество контента**
   - Читаемость
   - Полезность

4. **Соответствие JTBD**
   - Решает ли задачу
   - Удовлетворяет ли потребности

## 🎯 JTBD: {template_info["jtbd"]}

## ⚠️ ВНИМАНИЕ: Если любой из 6 обязательных элементов отсутствует, релиз НЕ СООТВЕТСТВУЕТ стандарту 1.4 from-the-end.process!
"""

    def _registry_docs_audit(self, request: GuidanceRequest) -> str:
        """Registry Docs Audit"""
        paths = request.paths or "пути"
        template_info = self.guidance_templates[GuidanceType.REGISTRY_DOCS_AUDIT]
        return f"""
# Аудит документации Registry

## 📚 Аудит документации по путям: {paths}

### Проверяемые аспекты:
1. **Структура документации**
   - Логическая организация
   - Навигация

2. **Качество контента**
   - Актуальность
   - Полнота

3. **Форматирование**
   - Единообразие
   - Читаемость

4. **Примеры и инструкции**
   - Практичность
   - Понятность

## 🎯 JTBD: {template_info["jtbd"]}
"""

    def _registry_gap_report(self, request: GuidanceRequest) -> str:
        """Registry Gap Report"""
        expected = request.expected or "ожидаемое"
        actual = request.actual or "фактическое"
        decision = request.decision or "решение"
        template_info = self.guidance_templates[GuidanceType.REGISTRY_GAP_REPORT]
        return f"""
# Gap Analysis Report

## 📊 Анализ разрыва между ожидаемым и фактическим

### Ожидаемое: {expected}
### Фактическое: {actual}
### Решение: {decision}

### Выявленные gaps:
1. **Функциональные gaps**
   - Отсутствующие функции
   - Неполная реализация

2. **Качественные gaps**
   - Несоответствие стандартам
   - Проблемы производительности

3. **Процессные gaps**
   - Неэффективные процессы
   - Отсутствие автоматизации

### Рекомендации по устранению:
- Приоритизация gaps
- Планирование исправлений
- Контроль выполнения

## 🎯 JTBD: {template_info["jtbd"]}
"""

    def _registry_release_block(self, request: GuidanceRequest) -> str:
        """Registry Release Block"""
        until = request.until or "до исправления"
        template_info = self.guidance_templates[GuidanceType.REGISTRY_RELEASE_BLOCK]
        return f"""
# Блокировка релиза Registry

## 🚫 Блокировка релиза до: {until}

### Причины блокировки:
1. **Критические баги**
   - Блокирующие ошибки
   - Проблемы безопасности

2. **Несоответствие стандартам**
   - Нарушение coding standards
   - Отсутствие тестов

3. **Неполная функциональность**
   - Незавершенные features
   - Отсутствующая документация

### Требования для разблокировки:
- Исправление всех критических проблем
- Прохождение всех тестов
- Соответствие стандартам качества

## 🎯 JTBD: {template_info["jtbd"]}
"""

    def _validate_output_artefact(self, request: GuidanceRequest) -> str:
        """Validate Output Artefact"""
        artefact_path = request.artefact_path or "путь к артефакту"
        artefact_type = request.artefact_type or "analysis"
        quality_criteria = request.quality_criteria or "general"
        template_info = self.guidance_templates[GuidanceType.VALIDATE_OUTPUT_ARTEFACT]
        return f"""
# Валидация Output Артефакта

## 📋 Валидация артефакта: {artefact_path}

### Тип артефакта: {artefact_type}
### Критерии качества: {quality_criteria}

### Проверяемые аспекты:
1. **Структура данных**
   - Корректность формата
   - Полнота информации

2. **Качество контента**
   - Логичность изложения
   - Практическая ценность

3. **Соответствие требованиям**
   - Выполнение JTBD
   - Удовлетворение потребностей

4. **Техническое качество**
   - Отсутствие ошибок
   - Производительность

## 🎯 JTBD: {template_info["jtbd"]}
"""

    def _validate_actual_outcome(self, request: GuidanceRequest) -> str:
        """Validate Actual Outcome"""
        url = request.url or "URL"
        expected_features = request.expected_features or "ожидаемые функции"
        test_cases = request.test_cases or "тест-кейсы"
        take_screenshot = request.take_screenshot or True
        template_info = self.guidance_templates[GuidanceType.VALIDATE_ACTUAL_OUTCOME]
        return f"""
# Валидация фактического результата

## 🌐 Валидация URL: {url}

### Ожидаемые функции: {expected_features}
### Тест-кейсы: {test_cases}
### Скриншот: {"Да" if take_screenshot else "Нет"}

### Результаты валидации:
1. **Функциональное тестирование**
   - Проверка основных функций
   - Тестирование edge cases

2. **UI/UX тестирование**
   - Удобство использования
   - Визуальное соответствие

3. **Производительность**
   - Скорость загрузки
   - Отзывчивость интерфейса

4. **Совместимость**
   - Работа в разных браузерах
   - Адаптивность

## 🎯 JTBD: {template_info["jtbd"]}
"""

    def _create_reflection_checkpoint(
        self, request: GuidanceRequest, result: str
    ) -> str:
        """Создание reflection checkpoint"""
        from datetime import datetime

        return f"""
## 🔄 Reflection Checkpoint

### Выполненный guidance: {request.guidance_type}
### Время выполнения: {datetime.now().isoformat()}
### Статус: {"✅ Успешно" if result else "❌ Ошибка"}

### Анализ результата:
- Соответствует ли результат ожиданиям?
- Есть ли области для улучшения?
- Нужны ли дополнительные действия?

### Следующие шаги:
- Валидация результата
- Применение рекомендаций
- Мониторинг эффективности
"""


# Глобальный экземпляр workflow
ai_guidance_workflow = AIGuidanceWorkflow()
