#!/usr/bin/env python3
"""
Node.js PDF генератор через md-to-pdf
Использует npm пакет md-to-pdf для качественной конвертации Markdown в PDF
"""

import subprocess
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class NodeJSPDFGenerator:
    """PDF генератор через md-to-pdf npm пакет"""
    
    def __init__(self):
        self.check_dependencies()
        
    def check_dependencies(self) -> bool:
        """Проверяет наличие Node.js и md-to-pdf"""
        try:
            # Проверяем Node.js
            result = subprocess.run(
                ["node", "--version"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            logger.info(f"Node.js версия: {result.stdout.strip()}")
            
            # Проверяем npm
            result = subprocess.run(
                ["npm", "--version"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            logger.info(f"npm версия: {result.stdout.strip()}")
            
            # Проверяем md-to-pdf
            result = subprocess.run(
                ["npx", "md-to-pdf", "--version"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if result.returncode != 0:
                logger.warning("md-to-pdf не установлен, устанавливаем...")
                self.install_md_to_pdf()
            else:
                logger.info(f"md-to-pdf версия: {result.stdout.strip()}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка проверки зависимостей: {e}")
            return False
        except FileNotFoundError:
            logger.error("Node.js или npm не установлены")
            return False
    
    def install_md_to_pdf(self) -> bool:
        """Устанавливает md-to-pdf глобально"""
        try:
            logger.info("Устанавливаю md-to-pdf...")
            result = subprocess.run(
                ["npm", "install", "-g", "md-to-pdf"],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("md-to-pdf успешно установлен")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка установки md-to-pdf: {e}")
            return False
    
    def create_custom_css(self) -> str:
        """Создает кастомные CSS стили для md-to-pdf"""
        
        css_content = """
        /* Кастомные стили для md-to-pdf */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        :root {
            --primary-color: #2563eb;
            --text-primary: #1f2937;
            --text-secondary: #6b7280;
            --border-color: #e5e7eb;
            --background-light: #f9fafb;
            --code-background: #f3f4f6;
            
            --font-size-base: 16px;
            --line-height-base: 1.6;
            --spacing-unit: 8px;
        }
        
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: var(--font-size-base);
            line-height: var(--line-height-base);
            color: var(--text-primary);
            margin: 0;
            padding: 40px 20px;
            background: white;
            max-width: 800px;
            margin: 0 auto;
        }
        
        /* Заголовки */
        h1, h2, h3, h4, h5, h6 {
            font-weight: 600;
            line-height: 1.3;
            margin-top: 32px;
            margin-bottom: 16px;
            color: var(--text-primary);
        }
        
        h1 {
            font-size: 2.5rem;
            margin-top: 0;
            text-align: center;
            border-bottom: 3px solid var(--primary-color);
            padding-bottom: 16px;
        }
        
        h2 {
            font-size: 2rem;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 8px;
        }
        
        h3 {
            font-size: 1.5rem;
        }
        
        h4 {
            font-size: 1.25rem;
        }
        
        /* Параграфы и списки */
        p {
            margin: 0 0 16px 0;
            text-align: justify;
            hyphens: auto;
        }
        
        ul, ol {
            margin: 16px 0;
            padding-left: 24px;
        }
        
        li {
            margin-bottom: 8px;
        }
        
        /* Таблицы */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 24px 0;
            font-size: 14px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        
        th {
            background-color: var(--primary-color);
            color: white;
            font-weight: 600;
            padding: 16px 12px;
            text-align: left;
            border: none;
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid var(--border-color);
            vertical-align: top;
            word-wrap: break-word;
            max-width: 200px;
        }
        
        tr:nth-child(even) {
            background-color: var(--background-light);
        }
        
        tr:hover {
            background-color: #f0f9ff;
        }
        
        /* Details блоки */
        details {
            margin: 24px 0;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
        }
        
        summary {
            background-color: var(--background-light);
            padding: 16px;
            font-weight: 600;
            cursor: pointer;
            border-bottom: 1px solid var(--border-color);
            color: var(--primary-color);
        }
        
        details > div:not(summary) {
            padding: 16px;
        }
        
        /* Код блоки */
        pre {
            background-color: var(--code-background);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 16px;
            margin: 16px 0;
            overflow-x: auto;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.4;
        }
        
        code {
            background-color: var(--code-background);
            padding: 4px 6px;
            border-radius: 4px;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Courier New', monospace;
            font-size: 0.9em;
            color: #dc2626;
        }
        
        /* Блоки цитат */
        blockquote {
            margin: 24px 0;
            padding: 16px 24px;
            border-left: 4px solid var(--primary-color);
            background-color: var(--background-light);
            font-style: italic;
            color: var(--text-secondary);
        }
        
        /* Ссылки */
        a {
            color: var(--primary-color);
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-bottom-color 0.2s;
        }
        
        a:hover {
            border-bottom-color: var(--primary-color);
        }
        
        /* Горизонтальные линии */
        hr {
            border: none;
            border-top: 2px solid var(--border-color);
            margin: 32px 0;
        }
        
        /* Адаптивность для печати */
        @media print {
            body {
                max-width: none;
                padding: 20px;
            }
            
            table {
                box-shadow: none;
                border: 1px solid #000;
            }
            
            details {
                border: 1px solid #000;
            }
        }
        """
        
        return css_content
    
    def convert_md_to_pdf(self, md_file_path: str, output_pdf_path: str, 
                          custom_css: Optional[str] = None) -> Dict[str, Any]:
        """Конвертирует markdown в PDF через md-to-pdf"""
        
        try:
            # Создаем временный CSS файл
            css_content = custom_css or self.create_custom_css()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False, encoding='utf-8') as css_file:
                css_file.write(css_content)
                css_path = css_file.name
            
            try:
                # Команда md-to-pdf с кастомными стилями
                # md-to-pdf автоматически создает PDF с тем же именем
                cmd = [
                    "npx", "md-to-pdf",
                    md_file_path,
                    "--stylesheet", css_path,
                    "--pdf-options", '{"format": "A4", "margin": {"top": "20mm", "right": "20mm", "bottom": "20mm", "left": "20mm"}}'
                ]
                
                logger.info(f"Выполняю команду: {' '.join(cmd)}")
                
                # Запускаем md-to-pdf
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=120  # 2 минуты таймаут
                )
                
                logger.info("md-to-pdf выполнен успешно")
                logger.debug(f"stdout: {result.stdout}")
                
                # md-to-pdf создает PDF в той же папке что и markdown файл
                md_file = Path(md_file_path)
                generated_pdf = md_file.with_suffix('.pdf')
                
                # Перемещаем PDF в нужную папку
                if generated_pdf.exists():
                    import shutil
                    shutil.move(str(generated_pdf), output_pdf_path)
                    
                    file_size = Path(output_pdf_path).stat().st_size
                    
                    return {
                        "success": True,
                        "output_path": output_pdf_path,
                        "file_size": file_size,
                        "file_size_kb": file_size / 1024,
                        "message": "PDF успешно создан через md-to-pdf",
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
                else:
                    return {
                        "success": False,
                        "error": "PDF файл не был создан",
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
                    
            finally:
                # Удаляем временный CSS файл
                if os.path.exists(css_path):
                    os.unlink(css_path)
                    
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Превышен таймаут выполнения md-to-pdf (2 минуты)"
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Ошибка выполнения md-to-pdf: {e}",
                "stdout": e.stdout,
                "stderr": e.stderr,
                "returncode": e.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Неожиданная ошибка: {str(e)}"
            }
    
    def convert_with_advanced_options(self, md_file_path: str, output_pdf_path: str,
                                    options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Конвертация с расширенными опциями"""
        
        default_options = {
            "format": "A4",
            "margin": "20mm",
            "css": None,
            "highlight": True,
            "toc": False,
            "numbered": False
        }
        
        if options:
            default_options.update(options)
        
        # Создаем команду с опциями
        cmd = ["npx", "md-to-pdf", md_file_path]
        
        # Добавляем опции
        if default_options["format"] or default_options["margin"]:
            pdf_options = {}
            if default_options["format"]:
                pdf_options["format"] = default_options["format"]
            if default_options["margin"]:
                pdf_options["margin"] = default_options["margin"]
            
            cmd.extend(["--pdf-options", json.dumps(pdf_options)])
        
        if default_options["css"]:
            cmd.extend(["--stylesheet", default_options["css"]])
        
        if default_options["highlight"]:
            cmd.append("--highlight-style")
            cmd.append("github")
        
        # md-to-pdf не поддерживает --toc и --numbered напрямую
        # Эти опции можно реализовать через CSS или post-processing
        
        try:
            logger.info(f"Выполняю команду с опциями: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=120
            )
            
            # md-to-pdf создает PDF в той же папке что и markdown файл
            md_file = Path(md_file_path)
            generated_pdf = md_file.with_suffix('.pdf')
            
            # Перемещаем PDF в нужную папку
            if generated_pdf.exists():
                import shutil
                shutil.move(str(generated_pdf), output_pdf_path)
                
                file_size = Path(output_pdf_path).stat().st_size
                
                return {
                    "success": True,
                    "output_path": output_pdf_path,
                    "file_size": file_size,
                    "file_size_kb": file_size / 1024,
                    "message": "PDF создан с расширенными опциями",
                    "options_used": default_options,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                return {
                    "success": False,
                    "error": "PDF файл не был создан",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка с расширенными опциями: {str(e)}"
            }

# Функции для удобного использования
def convert_md_to_pdf_nodejs(md_file_path: str, output_pdf_path: str, 
                            custom_css: Optional[str] = None) -> Dict[str, Any]:
    """Удобная функция для конвертации через md-to-pdf"""
    generator = NodeJSPDFGenerator()
    return generator.convert_md_to_pdf(md_file_path, output_pdf_path, custom_css)

def convert_md_to_pdf_nodejs_advanced(md_file_path: str, output_pdf_path: str,
                                     options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Удобная функция для конвертации с расширенными опциями"""
    generator = NodeJSPDFGenerator()
    return generator.convert_with_advanced_options(md_file_path, output_pdf_path, options)
