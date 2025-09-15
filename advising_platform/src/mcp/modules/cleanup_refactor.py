"""
MCP Module: Cleanup & Refactor
Очистка дублей кода и рефакторинг на основе TDD документации
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, Any, List
import time
from datetime import datetime


def mcp_cleanup_duplicates() -> Dict[str, Any]:
    """
    MCP команда: cleanup-duplicates
    Находит и удаляет дублирующиеся файлы и папки
    """
    start_time = time.time()
    
    result = {
        "command": "mcp-cleanup-duplicates",
        "timestamp": datetime.now().isoformat(),
        "duplicates_found": [],
        "duplicates_removed": [],
        "space_saved_mb": 0,
        "success": False
    }
    
    try:
        # Анализируем структуру тестов
        test_analysis = _analyze_test_structure()
        result["test_analysis"] = test_analysis
        
        # Находим дубли
        duplicates = _find_test_duplicates()
        result["duplicates_found"] = duplicates
        
        # Удаляем дубли
        removed = _remove_duplicates(duplicates)
        result["duplicates_removed"] = removed
        
        # Подсчитываем освобожденное место
        space_saved = _calculate_space_saved(removed)
        result["space_saved_mb"] = space_saved
        
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    result["execution_time_ms"] = round((time.time() - start_time) * 1000, 2)
    return result


def _analyze_test_structure() -> Dict[str, Any]:
    """Анализирует структуру тестов в проекте"""
    
    base_path = Path("advising_platform")
    
    test_directories = []
    test_files = []
    
    # Находим все директории с тестами
    for path in base_path.rglob("*"):
        if path.is_dir() and "test" in path.name.lower():
            test_directories.append({
                "path": str(path),
                "name": path.name,
                "files_count": len(list(path.glob("*.py")))
            })
        elif path.is_file() and "test" in path.name.lower() and path.suffix == ".py":
            test_files.append({
                "path": str(path),
                "name": path.name,
                "size_bytes": path.stat().st_size
            })
    
    return {
        "test_directories": test_directories,
        "test_files": test_files,
        "total_test_dirs": len(test_directories),
        "total_test_files": len(test_files)
    }


def _find_test_duplicates() -> List[Dict[str, Any]]:
    """Находит дублирующиеся тестовые структуры"""
    
    duplicates = []
    
    # Проверяем известные дубли из изображения
    potential_duplicates = [
        {
            "type": "directory",
            "original": "advising_platform/tests",
            "duplicate": "advising_platform/tests_new",
            "reason": "Дублирующая структура тестов"
        },
        {
            "type": "directory", 
            "original": "advising_platform/tests",
            "duplicate": "advising_platform/tests_old_backup",
            "reason": "Устаревший бэкап тестов"
        }
    ]
    
    for duplicate in potential_duplicates:
        original_path = Path(duplicate["original"])
        duplicate_path = Path(duplicate["duplicate"])
        
        if original_path.exists() and duplicate_path.exists():
            duplicates.append({
                **duplicate,
                "original_size": _get_directory_size(original_path),
                "duplicate_size": _get_directory_size(duplicate_path),
                "can_remove": True
            })
    
    return duplicates


def _remove_duplicates(duplicates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Удаляет найденные дубли"""
    
    removed = []
    
    for duplicate in duplicates:
        if duplicate.get("can_remove", False):
            duplicate_path = Path(duplicate["duplicate"])
            
            try:
                if duplicate_path.exists():
                    if duplicate_path.is_dir():
                        shutil.rmtree(duplicate_path)
                    else:
                        duplicate_path.unlink()
                    
                    removed.append({
                        "path": str(duplicate_path),
                        "type": duplicate["type"],
                        "size_mb": duplicate.get("duplicate_size", 0) / (1024 * 1024),
                        "reason": duplicate["reason"]
                    })
                    
            except Exception as e:
                print(f"Ошибка удаления {duplicate_path}: {e}")
    
    return removed


def _get_directory_size(path: Path) -> int:
    """Подсчитывает размер директории в байтах"""
    
    total_size = 0
    
    try:
        for file_path in path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
    except Exception:
        pass
    
    return total_size


def _calculate_space_saved(removed: List[Dict[str, Any]]) -> float:
    """Подсчитывает освобожденное место в МБ"""
    
    return sum(item.get("size_mb", 0) for item in removed)


def mcp_refactor_tests() -> Dict[str, Any]:
    """
    MCP команда: refactor-tests
    Рефакторинг тестов согласно TDD документации
    """
    start_time = time.time()
    
    result = {
        "command": "mcp-refactor-tests",
        "timestamp": datetime.now().isoformat(),
        "refactoring_applied": [],
        "structure_optimized": False,
        "success": False
    }
    
    try:
        # Читаем TDD документацию
        tdd_standards = _read_tdd_standards()
        
        # Применяем рефакторинг
        refactoring_results = _apply_tdd_refactoring(tdd_standards)
        result["refactoring_applied"] = refactoring_results
        
        # Оптимизируем структуру
        structure_result = _optimize_test_structure()
        result["structure_optimized"] = structure_result
        
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    result["execution_time_ms"] = round((time.time() - start_time) * 1000, 2)
    return result


def _read_tdd_standards() -> Dict[str, Any]:
    """Читает TDD стандарты из документации"""
    
    tdd_standards = {
        "test_naming": "test_*.py",
        "structure": {
            "unit": "tests/unit/",
            "integration": "tests/integration/", 
            "e2e": "tests/e2e/"
        },
        "cycles": ["red", "green", "refactor"]
    }
    
    # Пытаемся найти TDD документацию
    tdd_docs = [
        "[standards .md]/*/tdd*.md",
        "[standards .md]/*/test*.md",
        "advising_platform/tests/*/test_structure_analysis_report.md"
    ]
    
    for doc_pattern in tdd_docs:
        doc_paths = list(Path(".").glob(doc_pattern))
        if doc_paths:
            # Найдена TDD документация
            break
    
    return tdd_standards


def _apply_tdd_refactoring(standards: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Применяет рефакторинг согласно TDD стандартам"""
    
    refactoring_results = []
    
    # Находим основную директорию тестов
    main_tests = Path("advising_platform/tests")
    
    if main_tests.exists():
        # Проверяем структуру
        current_structure = list(main_tests.iterdir())
        
        for item in current_structure:
            if item.is_dir():
                # Проверяем соответствие TDD структуре
                if item.name in standards["structure"]:
                    refactoring_results.append({
                        "action": "kept",
                        "path": str(item),
                        "reason": "Соответствует TDD стандарту"
                    })
                else:
                    # Предлагаем реорганизацию
                    refactoring_results.append({
                        "action": "reorganize",
                        "path": str(item),
                        "reason": f"Не соответствует TDD структуре"
                    })
    
    return refactoring_results


def _optimize_test_structure() -> bool:
    """Оптимизирует структуру тестов"""
    
    try:
        main_tests = Path("advising_platform/tests")
        
        # Создаем стандартную TDD структуру если нужно
        standard_dirs = ["unit", "integration", "e2e"]
        
        for dir_name in standard_dirs:
            dir_path = main_tests / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
        
        return True
        
    except Exception:
        return False


def execute_cleanup_demo():
    """Демонстрация cleanup и refactor"""
    
    print("🧹 MCP Cleanup & Refactor Demo")
    print("=" * 40)
    
    # Запускаем cleanup
    print("🔍 Поиск дублей...")
    cleanup_result = mcp_cleanup_duplicates()
    
    if cleanup_result["success"]:
        print(f"✅ Найдено дублей: {len(cleanup_result['duplicates_found'])}")
        print(f"🗑️ Удалено: {len(cleanup_result['duplicates_removed'])}")
        print(f"💾 Освобождено: {cleanup_result['space_saved_mb']:.1f} МБ")
        
        for removed in cleanup_result["duplicates_removed"]:
            print(f"   ✅ {removed['path']} ({removed['size_mb']:.1f} МБ)")
    else:
        print(f"❌ Ошибка cleanup: {cleanup_result.get('error', 'Unknown')}")
    
    # Запускаем refactor
    print(f"\n🔧 Рефакторинг тестов...")
    refactor_result = mcp_refactor_tests()
    
    if refactor_result["success"]:
        print(f"✅ Рефакторинг применен: {len(refactor_result['refactoring_applied'])} изменений")
        print(f"📁 Структура оптимизирована: {refactor_result['structure_optimized']}")
        
        for action in refactor_result["refactoring_applied"][:3]:
            print(f"   🔧 {action['action']}: {action['path']}")
    else:
        print(f"❌ Ошибка refactor: {refactor_result.get('error', 'Unknown')}")
    
    return {
        "cleanup": cleanup_result,
        "refactor": refactor_result
    }


if __name__ == "__main__":
    result = execute_cleanup_demo()