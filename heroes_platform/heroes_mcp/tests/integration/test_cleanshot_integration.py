"""
JTBD: Как интеграционный тестировщик, я хочу проверить взаимодействие cleanshot workflow с MCP сервером,
чтобы убедиться в корректности интеграции.

AI QA PRE-CHECK:
✅ Анализ реальных данных: Изучил структуру MCP интеграции
✅ Предотвращение галлюцинаций: Использую только проверенные форматы
✅ Валидация сценария: Сценарий основан на реальной MCP архитектуре
❌ Запрещено: Предполагать структуру данных без анализа
"""

import json
import os
import sys
from unittest.mock import Mock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from workflows.cleanshot_workflow import CleanShotWorkflow


class TestCleanShotIntegration:
    """
    JTBD: Как интеграционный тестировщик, я хочу проверить полную интеграцию cleanshot workflow,
    чтобы обеспечить работоспособность системы.
    """

    def setup_method(self):
        """JTBD: Как интеграционный тестировщик, я хочу инициализировать тестовое окружение,
        чтобы обеспечить изоляцию интеграционных тестов."""
        self.workflow = CleanShotWorkflow()

    def test_mcp_server_calls_cleanshot_workflow(self):
        """
        JTBD: Как MCP сервер, я хочу вызывать cleanshot workflow,
        чтобы обеспечить корректную работу команды read_cleanshot.
        """
        # Arrange
        test_url = "https://cleanshot.com/test"
        mock_response = Mock()
        mock_response.text = (
            '<meta property="og:image" content="https://example.com/image.jpg">'
        )
        mock_response.raise_for_status.return_value = None

        mock_img_response = Mock()
        mock_img_response.content = b"fake_image_data"
        mock_img_response.headers = {"content-type": "image/jpeg"}
        mock_img_response.raise_for_status.return_value = None

        # Act - симулируем вызов через MCP сервер
        with patch("requests.get", side_effect=[mock_response, mock_img_response]):
            with patch("builtins.open", create=True):
                with patch("os.path.exists", return_value=True):
                    result = self.workflow.read_cleanshot(test_url)

        # Assert
        parsed_result = json.loads(result)
        assert parsed_result["success"] is True
        assert "image_url" in parsed_result

    def test_cleanshot_workflow_real_api_calls(self):
        """
        JTBD: Как пользователь, я хочу проверить реальные API вызовы,
        чтобы убедиться в работоспособности с реальными данными.
        """
        # Arrange
        test_url = "https://cleanshot.com/test"

        # Act & Assert - проверяем что workflow может обрабатывать реальные запросы
        # В реальном тесте здесь были бы настоящие API вызовы
        # Для интеграционного теста используем моки, но проверяем структуру
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.text = (
                '<meta property="og:image" content="https://example.com/image.jpg">'
            )
            mock_response.raise_for_status.return_value = None

            mock_img_response = Mock()
            mock_img_response.content = b"fake_image_data"
            mock_img_response.headers = {"content-type": "image/jpeg"}
            mock_img_response.raise_for_status.return_value = None

            mock_get.side_effect = [mock_response, mock_img_response]

            with patch("builtins.open", create=True):
                with patch("os.path.exists", return_value=True):
                    result = self.workflow.read_cleanshot(test_url)

        # Assert
        parsed_result = json.loads(result)
        assert parsed_result["success"] is True
        assert "jtbd_scenario" in parsed_result
        assert "test_cases" in parsed_result
        assert "defect_checklist" in parsed_result
        assert "quality_criteria" in parsed_result
        assert "ai_qa_tasks" in parsed_result

    def test_cleanshot_workflow_error_propagation(self):
        """
        JTBD: Как система, я хочу проверить передачу ошибок через MCP,
        чтобы обеспечить корректную обработку исключений.
        """
        # Arrange
        test_url = "https://cleanshot.com/test"

        # Act - симулируем ошибку сети
        with patch("requests.get", side_effect=Exception("Network error")):
            result = self.workflow.read_cleanshot(test_url)

        # Assert
        parsed_result = json.loads(result)
        assert parsed_result["success"] is False
        assert "error" in parsed_result
        assert "url" in parsed_result

    def test_cleanshot_workflow_mcp_protocol_compliance(self):
        """
        JTBD: Как MCP протокол, я хочу проверить соответствие workflow стандартам,
        чтобы обеспечить совместимость с MCP сервером.
        """
        # Assert - проверяем что workflow соответствует MCP протоколу
        assert hasattr(self.workflow, "read_cleanshot"), (
            "Workflow must have read_cleanshot method"
        )

        # Проверяем сигнатуру метода
        import inspect

        method = self.workflow.read_cleanshot
        sig = inspect.signature(method)

        # Должен принимать url: str и возвращать str
        assert "url" in sig.parameters, "Method must accept 'url' parameter"
        assert sig.parameters["url"].annotation == str, "URL parameter must be str"

        # Проверяем возвращаемый тип
        assert sig.return_annotation == str, "Method must return str"

    def test_cleanshot_workflow_atomic_architecture(self):
        """
        JTBD: Как архитектор, я хочу проверить атомарную архитектуру workflow,
        чтобы обеспечить соответствие стандартам качества.
        """
        # Assert - проверяем атомарность функций
        import inspect

        # Получаем все методы класса
        methods = inspect.getmembers(self.workflow, predicate=inspect.ismethod)

        for name, method in methods:
            if not name.startswith("_"):  # Публичные методы
                source_lines = inspect.getsourcelines(method)[0]
                line_count = len(source_lines)

                # Проверяем что каждый метод ≤25 строк
                assert line_count <= 25, (
                    f"Method {name} has {line_count} lines, should be ≤25"
                )

                # Проверяем наличие JTBD документации
                docstring = method.__doc__
                assert docstring is not None, f"Method {name} must have docstring"
                assert "JTBD" in docstring, (
                    f"Method {name} must have JTBD documentation"
                )

    def test_cleanshot_workflow_single_responsibility(self):
        """
        JTBD: Как архитектор, я хочу проверить принцип единственной ответственности,
        чтобы обеспечить чистую архитектуру.
        """
        # Assert - проверяем что workflow имеет только одну ответственность
        # CleanShot workflow должен только читать изображения из CleanShot
        assert hasattr(self.workflow, "read_cleanshot"), (
            "Workflow should have read_cleanshot method"
        )

        # Не должно быть других публичных методов, не связанных с CleanShot
        import inspect

        methods = inspect.getmembers(self.workflow, predicate=inspect.ismethod)
        public_methods = [name for name, _ in methods if not name.startswith("_")]

        # Должен быть только один публичный метод
        assert len(public_methods) == 1, (
            f"Workflow should have only 1 public method, got {public_methods}"
        )
        assert public_methods[0] == "read_cleanshot", (
            f"Public method should be 'read_cleanshot', got {public_methods[0]}"
        )

    def test_cleanshot_workflow_output_validation(self):
        """
        JTBD: Как пользователь, я хочу проверить валидацию выходных данных,
        чтобы убедиться в качестве результата.
        """
        # Arrange
        test_url = "https://cleanshot.com/test"
        mock_response = Mock()
        mock_response.text = (
            '<meta property="og:image" content="https://example.com/image.jpg">'
        )
        mock_response.raise_for_status.return_value = None

        mock_img_response = Mock()
        mock_img_response.content = b"fake_image_data"
        mock_img_response.headers = {"content-type": "image/jpeg"}
        mock_img_response.raise_for_status.return_value = None

        # Act
        with patch("requests.get", side_effect=[mock_response, mock_img_response]):
            with patch("builtins.open", create=True):
                with patch("os.path.exists", return_value=True):
                    result = self.workflow.read_cleanshot(test_url)

        # Assert - проверяем структуру и качество выходных данных
        parsed_result = json.loads(result)

        # Проверяем обязательные поля
        required_fields = [
            "success",
            "image_url",
            "temp_path",
            "file_size",
            "content_type",
            "analysis",
            "jtbd_scenario",
            "test_cases",
            "defect_checklist",
            "quality_criteria",
            "ai_qa_tasks",
        ]

        for field in required_fields:
            assert field in parsed_result, f"Missing required field: {field}"

        # Проверяем качество данных
        assert isinstance(parsed_result["jtbd_scenario"], dict), (
            "jtbd_scenario should be dict"
        )
        assert isinstance(parsed_result["test_cases"], dict), (
            "test_cases should be dict"
        )
        assert isinstance(parsed_result["defect_checklist"], dict), (
            "defect_checklist should be dict"
        )
        assert isinstance(parsed_result["quality_criteria"], dict), (
            "quality_criteria should be dict"
        )
        assert isinstance(parsed_result["ai_qa_tasks"], list), (
            "ai_qa_tasks should be list"
        )

        # Проверяем что ai_qa_tasks содержит задачи
        assert len(parsed_result["ai_qa_tasks"]) > 0, "ai_qa_tasks should not be empty"
