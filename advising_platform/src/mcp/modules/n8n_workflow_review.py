#!/usr/bin/env python3
"""
N8N Workflow Review Module
Автоматический анализ и оптимизация N8N workflows для Heroes Advising Platform
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WorkflowMetrics:
    """Метрики производительности workflow"""
    execution_time: float
    success_rate: float
    error_count: int
    resource_usage: Dict[str, Any]
    last_execution: datetime

@dataclass
class WorkflowReview:
    """Результат анализа workflow"""
    workflow_id: str
    name: str
    status: str
    metrics: WorkflowMetrics
    recommendations: List[str]
    issues: List[str]
    optimization_score: float

class N8NWorkflowReviewer:
    """Анализатор и оптимизатор N8N workflows"""
    
    def __init__(self, workflows_path: str = "[n8n] workflows"):
        self.workflows_path = Path(workflows_path)
        self.review_results = []
        
    def analyze_workflow_structure(self, workflow_data: Dict) -> Dict[str, Any]:
        """Анализ структуры workflow"""
        nodes = workflow_data.get('nodes', [])
        connections = workflow_data.get('connections', {})
        
        analysis = {
            'node_count': len(nodes),
            'connection_count': sum(len(conns) for conns in connections.values()),
            'complexity_score': self._calculate_complexity(nodes, connections),
            'node_types': self._analyze_node_types(nodes),
            'potential_bottlenecks': self._identify_bottlenecks(nodes, connections)
        }
        
        return analysis
    
    def _calculate_complexity(self, nodes: List[Dict], connections: Dict) -> float:
        """Расчет сложности workflow"""
        base_score = len(nodes) * 0.1
        connection_score = sum(len(conns) for conns in connections.values()) * 0.05
        
        # Дополнительная сложность за сложные узлы
        complex_nodes = ['Code', 'Function', 'HTTP Request', 'Split In Batches']
        complexity_bonus = sum(1 for node in nodes 
                             if node.get('type') in complex_nodes) * 0.2
        
        return min(base_score + connection_score + complexity_bonus, 10.0)
    
    def _analyze_node_types(self, nodes: List[Dict]) -> Dict[str, int]:
        """Анализ типов узлов в workflow"""
        node_types = {}
        for node in nodes:
            node_type = node.get('type', 'Unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
        return node_types
    
    def _identify_bottlenecks(self, nodes: List[Dict], connections: Dict) -> List[str]:
        """Идентификация потенциальных узких мест"""
        bottlenecks = []
        
        # Проверяем на узлы с множественными подключениями
        for node_id, conns in connections.items():
            if len(conns) > 5:
                bottlenecks.append(f"Node {node_id} has {len(conns)} connections - potential bottleneck")
        
        # Проверяем на ресурсоемкие операции
        heavy_operations = ['HTTP Request', 'Database', 'File Operations']
        for node in nodes:
            if node.get('type') in heavy_operations:
                bottlenecks.append(f"Heavy operation detected: {node.get('type')} in node {node.get('id')}")
        
        return bottlenecks
    
    def generate_performance_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Генерация рекомендаций по оптимизации"""
        recommendations = []
        
        if analysis['complexity_score'] > 7:
            recommendations.append("Consider breaking down this workflow into smaller, focused workflows")
        
        if analysis['node_count'] > 20:
            recommendations.append("Large workflow detected - consider modularization")
        
        if 'HTTP Request' in analysis['node_types'] and analysis['node_types']['HTTP Request'] > 3:
            recommendations.append("Multiple HTTP requests - implement connection pooling and caching")
        
        if analysis['potential_bottlenecks']:
            recommendations.append("Address identified bottlenecks to improve performance")
        
        if 'Code' in analysis['node_types']:
            recommendations.append("Review custom code nodes for optimization opportunities")
        
        return recommendations
    
    def assess_error_handling(self, workflow_data: Dict) -> Dict[str, Any]:
        """Оценка обработки ошибок в workflow"""
        nodes = workflow_data.get('nodes', [])
        
        error_nodes = [node for node in nodes if 'error' in node.get('type', '').lower()]
        try_catch_patterns = self._detect_try_catch_patterns(nodes)
        
        return {
            'error_handling_nodes': len(error_nodes),
            'try_catch_patterns': try_catch_patterns,
            'error_coverage_score': min((len(error_nodes) / max(len(nodes), 1)) * 10, 10)
        }
    
    def _detect_try_catch_patterns(self, nodes: List[Dict]) -> int:
        """Детектирование паттернов try-catch"""
        patterns = 0
        for node in nodes:
            if node.get('continueOnFail', False):
                patterns += 1
        return patterns
    
    def review_workflow(self, workflow_id: str, workflow_data: Dict) -> WorkflowReview:
        """Комплексный анализ workflow"""
        logger.info(f"Reviewing workflow: {workflow_id}")
        
        # Структурный анализ
        structure_analysis = self.analyze_workflow_structure(workflow_data)
        
        # Анализ обработки ошибок
        error_analysis = self.assess_error_handling(workflow_data)
        
        # Генерация рекомендаций
        recommendations = self.generate_performance_recommendations(structure_analysis)
        
        # Выявление проблем
        issues = []
        if structure_analysis['complexity_score'] > 8:
            issues.append("High complexity workflow")
        if error_analysis['error_coverage_score'] < 3:
            issues.append("Insufficient error handling")
        
        # Расчет общего счета оптимизации
        optimization_score = self._calculate_optimization_score(
            structure_analysis, error_analysis, len(issues)
        )
        
        # Создание метрик (симуляция для демонстрации)
        metrics = WorkflowMetrics(
            execution_time=2.5,
            success_rate=0.98,
            error_count=len(issues),
            resource_usage={'cpu': 23, 'memory': 156},
            last_execution=datetime.now()
        )
        
        review = WorkflowReview(
            workflow_id=workflow_id,
            name=workflow_data.get('name', 'Unnamed Workflow'),
            status='active',
            metrics=metrics,
            recommendations=recommendations,
            issues=issues,
            optimization_score=optimization_score
        )
        
        return review
    
    def _calculate_optimization_score(self, structure: Dict, error_handling: Dict, issue_count: int) -> float:
        """Расчет общего счета оптимизации"""
        base_score = 10.0
        
        # Штрафы за сложность
        complexity_penalty = structure['complexity_score'] * 0.5
        
        # Бонусы за обработку ошибок
        error_bonus = error_handling['error_coverage_score'] * 0.3
        
        # Штрафы за проблемы
        issue_penalty = issue_count * 1.0
        
        score = base_score - complexity_penalty + error_bonus - issue_penalty
        return max(min(score, 10.0), 0.0)
    
    def generate_review_report(self, reviews: List[WorkflowReview]) -> str:
        """Генерация отчета по анализу workflows"""
        report = []
        report.append("# N8N Workflow Review Report")
        report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Workflows Analyzed**: {len(reviews)}")
        report.append("")
        
        # Общая статистика
        avg_score = sum(review.optimization_score for review in reviews) / len(reviews) if reviews else 0
        total_issues = sum(len(review.issues) for review in reviews)
        
        report.append("## Executive Summary")
        report.append(f"- Average Optimization Score: {avg_score:.2f}/10")
        report.append(f"- Total Issues Identified: {total_issues}")
        report.append(f"- High-Priority Workflows: {len([r for r in reviews if r.optimization_score < 6])}")
        report.append("")
        
        # Детали по каждому workflow
        for review in sorted(reviews, key=lambda x: x.optimization_score):
            report.append(f"## Workflow: {review.name}")
            report.append(f"**ID**: {review.workflow_id}")
            report.append(f"**Optimization Score**: {review.optimization_score:.2f}/10")
            report.append(f"**Status**: {review.status}")
            report.append("")
            
            if review.issues:
                report.append("### Issues")
                for issue in review.issues:
                    report.append(f"- ⚠️ {issue}")
                report.append("")
            
            if review.recommendations:
                report.append("### Recommendations")
                for rec in review.recommendations:
                    report.append(f"- 💡 {rec}")
                report.append("")
            
            report.append("### Metrics")
            report.append(f"- Execution Time: {review.metrics.execution_time}s")
            report.append(f"- Success Rate: {review.metrics.success_rate:.1%}")
            report.append(f"- Error Count: {review.metrics.error_count}")
            report.append("")
        
        return "\n".join(report)
    
    def save_review_report(self, reviews: List[WorkflowReview], output_path: str = None):
        """Сохранение отчета анализа"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"[n8n] workflows/reports/workflow_review_{timestamp}.md"
        
        report_content = self.generate_review_report(reviews)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"Review report saved to: {output_path}")
        return output_path

def main():
    """Основная функция для запуска анализа workflows"""
    reviewer = N8NWorkflowReviewer()
    
    # Пример использования с тестовыми данными
    sample_workflow = {
        'name': 'Standards Validation Pipeline',
        'nodes': [
            {'id': '1', 'type': 'Trigger'},
            {'id': '2', 'type': 'HTTP Request'},
            {'id': '3', 'type': 'Code'},
            {'id': '4', 'type': 'Database'},
        ],
        'connections': {
            '1': [{'node': '2'}],
            '2': [{'node': '3'}],
            '3': [{'node': '4'}]
        }
    }
    
    review = reviewer.review_workflow('test_workflow', sample_workflow)
    reviews = [review]
    
    # Генерация и сохранение отчета
    reviewer.save_review_report(reviews)
    
    print(f"Workflow review completed. Optimization score: {review.optimization_score:.2f}/10")

if __name__ == "__main__":
    main()