#!/usr/bin/env python3
"""
Скрипт для извлечения и интерпретации значений полей 1С из JSON/XML данных
Создан согласно AI QA Standard v1.8 и From-The-End Standard v2.9
"""

import json
import xml.etree.ElementTree as ET
from typing import Any


class FieldExtractor:
    """Класс для извлечения и интерпретации полей 1С"""

    def __init__(self) -> None:
        """Инициализация с маппингом полей 1С"""
        self.field_mapping = {
            # Основные поля документа
            "_VERSION": "Версия документа",
            "_MARKED": "Пометка удаления",
            "_NUMBER": "Номер документа",
            "_POSTED": "Проведен",
            "_DATE": "Дата документа",
            # Финансовые поля
            "_FLD4238": "Сумма документа (основная)",
            "_FLD4239": "Сумма документа (итоговая)",
            "_FLD9885": "Сумма НДС",
            "_FLD4240": "Количество позиций",
            # Флаги и статусы
            "_FLD4225": "Флаг проведения",
            "_FLD4226": "Флаг удаления",
            "_FLD4227": "Флаг блокировки",
            "_FLD4236": "Флаг оплаты",
            "_FLD4237": "Флаг отгрузки",
            "_FLD4249": "Флаг возврата",
            "_FLD4252": "Комментарий",
            # Служебные поля
            "_FLD8015": "Код операции",
            "_FLD8070": "Дополнительная информация",
            "_FLD8205": "Флаг архивации",
            "_FLD10651": "Тип документа",
            "_FLD10654": "Флаг корректировки",
            "_FLD13609": "Флаг резерва",
            "_FLD14340": "Флаг блокировки по остаткам",
            "_FLD12955": "Дополнительный код",
            "_FLD12950": "Внутренний код",
        }

    def extract_from_json(self, json_file: str) -> dict[str, Any]:
        """Извлечение данных из JSON файла"""
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            result = {
                "metadata": data.get("metadata", {}),
                "documents": [],
                "extraction_summary": {
                    "total_documents": 0,
                    "successful_extractions": 0,
                    "failed_extractions": 0,
                    "extracted_fields": set(),
                    "missing_fields": set(),
                },
            }

            for doc in data.get("documents", []):
                extracted_doc = self._extract_document_fields(doc)
                result["documents"].append(extracted_doc)
                result["extraction_summary"]["total_documents"] += 1

                if extracted_doc["extraction_status"] == "success":
                    result["extraction_summary"]["successful_extractions"] += 1
                else:
                    result["extraction_summary"]["failed_extractions"] += 1

                # Собираем статистику полей
                for field in extracted_doc.get("extracted_fields", []):
                    result["extraction_summary"]["extracted_fields"].add(
                        field["field_name"],
                    )

                for field in extracted_doc.get("missing_fields", []):
                    result["extraction_summary"]["missing_fields"].add(field)

            return result

        except Exception as e:
            return {"error": f"Ошибка при чтении JSON файла: {e!s}"}

    def extract_from_xml(self, xml_file: str) -> dict[str, Any]:
        """Извлечение данных из XML файла"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            result: dict[str, Any] = {
                "metadata": self._extract_xml_metadata(root),
                "documents": [],
                "extraction_summary": {
                    "total_documents": 0,
                    "successful_extractions": 0,
                    "failed_extractions": 0,
                    "extracted_fields": set(),
                    "missing_fields": set(),
                },
            }

            for doc_elem in root.findall(".//Document"):
                extracted_doc = self._extract_xml_document(doc_elem)
                result["documents"].append(extracted_doc)
                result["extraction_summary"]["total_documents"] += 1

                if extracted_doc["extraction_status"] == "success":
                    result["extraction_summary"]["successful_extractions"] += 1
                else:
                    result["extraction_summary"]["failed_extractions"] += 1

                # Собираем статистику полей
                for field in extracted_doc.get("extracted_fields", []):
                    result["extraction_summary"]["extracted_fields"].add(
                        field["field_name"],
                    )

                for field in extracted_doc.get("missing_fields", []):
                    result["extraction_summary"]["missing_fields"].add(field)

            return result

        except Exception as e:
            return {"error": f"Ошибка при чтении XML файла: {e!s}"}

    def _extract_document_fields(self, doc: dict[str, Any]) -> dict[str, Any]:
        """Извлечение полей из одного документа"""
        result = {
            "document_id": doc.get("document_id", "unknown"),
            "document_type": doc.get("document_type", "unknown"),
            "document_number": doc.get("document_number", "unknown"),
            "extraction_status": "success",
            "extracted_fields": [],
            "missing_fields": [],
            "interpreted_data": {},
            "quality_score": 0,
        }

        # Извлекаем основные поля
        basic_fields = [
            "document_id",
            "document_type",
            "document_number",
            "document_date",
            "is_posted",
            "total_amount",
            "description",
            "counterparty",
        ]

        for field in basic_fields:
            if field in doc and doc[field] is not None:
                result["interpreted_data"][field] = doc[field]
                result["extracted_fields"].append(
                    {
                        "field_name": field,
                        "value": doc[field],
                        "interpretation": self._interpret_field(field, doc[field]),
                    },
                )
            else:
                result["missing_fields"].append(field)

        # Извлекаем поля _FLD*
        all_fields = doc.get("all_fields", {})
        for field_name, value in all_fields.items():
            if field_name.startswith("_FLD"):
                interpretation = self._interpret_field(field_name, value)
                result["extracted_fields"].append(
                    {
                        "field_name": field_name,
                        "value": value,
                        "interpretation": interpretation,
                        "field_description": self.field_mapping.get(
                            field_name,
                            "Неизвестное поле",
                        ),
                    },
                )

        # Извлекаем BLOB данные
        blob_content = doc.get("blob_content", {})
        for field_name, value in blob_content.items():
            if field_name.startswith("_FLD"):
                result["extracted_fields"].append(
                    {
                        "field_name": field_name,
                        "value": value,
                        "interpretation": "BLOB данные",
                        "field_description": "Дополнительное содержимое документа",
                    },
                )

        # Вычисляем качество извлечения
        total_fields = len(basic_fields) + len(all_fields) + len(blob_content)
        extracted_count = len(result["extracted_fields"])
        result["quality_score"] = (
            (extracted_count / total_fields * 100) if total_fields > 0 else 0
        )

        return result

    def _extract_xml_metadata(self, root: ET.Element) -> dict[str, Any]:
        """Извлечение метаданных из XML"""
        metadata = {}
        metadata_elem = root.find("Metadata")
        if metadata_elem is not None:
            for child in metadata_elem:
                metadata[child.tag] = child.text
        return metadata

    def _extract_xml_document(self, doc_elem: ET.Element) -> dict[str, Any]:
        """Извлечение данных из XML документа"""
        id_elem = doc_elem.find("ID")
        type_elem = doc_elem.find("Type")

        result: dict[str, Any] = {
            "document_id": id_elem.text if id_elem is not None else "unknown",
            "document_type": type_elem.text if type_elem is not None else "unknown",
            "extraction_status": "success",
            "extracted_fields": [],
            "missing_fields": [],
            "interpreted_data": {},
            "quality_score": 0,
        }

        # Извлекаем основные поля
        basic_fields = [
            "ID",
            "Type",
            "Number",
            "Date",
            "Posted",
            "TotalAmount",
            "Description",
            "Counterparty",
        ]

        for field in basic_fields:
            elem = doc_elem.find(field)
            if elem is not None and elem.text is not None:
                value = elem.text
                result["interpreted_data"][field.lower()] = value
                result["extracted_fields"].append(
                    {
                        "field_name": field,
                        "value": value,
                        "interpretation": self._interpret_field(field, value),
                    },
                )
            else:
                result["missing_fields"].append(field)

        # Извлекаем поля AllFields
        all_fields_elem = doc_elem.find("AllFields")
        if all_fields_elem is not None:
            for child in all_fields_elem:
                field_name = child.tag
                value = child.text if child.text is not None else ""
                interpretation = self._interpret_field(field_name, value)
                result["extracted_fields"].append(
                    {
                        "field_name": field_name,
                        "value": value,
                        "interpretation": interpretation,
                        "field_description": self.field_mapping.get(
                            field_name,
                            "Неизвестное поле",
                        ),
                    },
                )

        # Извлекаем BLOB данные
        blob_elem = doc_elem.find("BlobContent")
        if blob_elem is not None:
            for child in blob_elem:
                field_name = child.tag
                value = child.text if child.text is not None else ""
                result["extracted_fields"].append(
                    {
                        "field_name": field_name,
                        "value": value,
                        "interpretation": "BLOB данные",
                        "field_description": "Дополнительное содержимое документа",
                    },
                )

        return result

    def _interpret_field(self, field_name: str, value: Any) -> str:
        """Интерпретация значения поля"""
        if field_name in [
            "_POSTED",
            "_MARKED",
            "_FLD4225",
            "_FLD4226",
            "_FLD4227",
            "_FLD4236",
            "_FLD4237",
            "_FLD4249",
            "_FLD8205",
            "_FLD10654",
            "_FLD13609",
            "_FLD14340",
        ]:
            return (
                "Булево значение"
                if isinstance(value, bool)
                else f"Логическое поле: {value}"
            )

        if field_name in ["_FLD4238", "_FLD4239", "_FLD9885"]:
            return (
                f"Финансовая сумма: {value}"
                if isinstance(value, (int, float))
                else f"Финансовое поле: {value}"
            )

        if field_name in ["_FLD4240", "_FLD8015", "_FLD10651"]:
            return (
                f"Числовое значение: {value}"
                if isinstance(value, (int, float))
                else f"Числовое поле: {value}"
            )

        if field_name in ["_FLD4252", "_FLD8070", "_FLD12955", "_FLD12950"]:
            return (
                f"Текстовое поле: {value}"
                if isinstance(value, str)
                else f"Текстовое поле: {value}"
            )

        if field_name in ["_NUMBER", "_VERSION"]:
            return f"Идентификатор: {value}"

        return f"Неизвестное поле: {value}"


def main() -> None:
    """Основная функция для тестирования извлечения полей"""
    extractor = FieldExtractor()

    # Тестируем извлечение из JSON
    print("=== ТЕСТ ИЗВЛЕЧЕНИЯ ИЗ JSON ===")
    json_result = extractor.extract_from_json(
        "[prostocvet-1c]/raw/clean_working_documents.json",
    )

    if "error" in json_result:
        print(f"Ошибка: {json_result['error']}")
    else:
        print(
            f"Извлечено документов: {json_result['extraction_summary']['total_documents']}",
        )
        print(
            f"Успешных извлечений: {json_result['extraction_summary']['successful_extractions']}",
        )
        print(
            f"Неудачных извлечений: {json_result['extraction_summary']['failed_extractions']}",
        )
        print(
            f"Уникальных полей: {len(json_result['extraction_summary']['extracted_fields'])}",
        )
        print(
            f"Отсутствующих полей: {len(json_result['extraction_summary']['missing_fields'])}",
        )

        # Показываем пример извлеченного документа
        if json_result["documents"]:
            first_doc = json_result["documents"][0]
            print(f"\nПример документа: {first_doc['document_id']}")
            print(f"Качество извлечения: {first_doc['quality_score']:.1f}%")
            print(f"Извлечено полей: {len(first_doc['extracted_fields'])}")
            print(f"Отсутствует полей: {len(first_doc['missing_fields'])}")

    # Тестируем извлечение из XML
    print("\n=== ТЕСТ ИЗВЛЕЧЕНИЯ ИЗ XML ===")
    xml_result = extractor.extract_from_xml(
        "[prostocvet-1c]/raw/clean_working_documents.xml",
    )

    if "error" in xml_result:
        print(f"Ошибка: {xml_result['error']}")
    else:
        print(
            f"Извлечено документов: {xml_result['extraction_summary']['total_documents']}",
        )
        print(
            f"Успешных извлечений: {xml_result['extraction_summary']['successful_extractions']}",
        )
        print(
            f"Неудачных извлечений: {xml_result['extraction_summary']['failed_extractions']}",
        )
        print(
            f"Уникальных полей: {len(xml_result['extraction_summary']['extracted_fields'])}",
        )
        print(
            f"Отсутствующих полей: {len(xml_result['extraction_summary']['missing_fields'])}",
        )


if __name__ == "__main__":
    main()
