#!/usr/bin/env python3
"""
🏥 Health Checker для мониторинга состояния системы

JTBD: Как health checker, я хочу проверять состояние всех критических компонентов,
чтобы обеспечить system availability и proactive monitoring.

Основано на: dependency_mapping.md анализе
Стандарт: TDD-doc + RADAR принципы
Автор: AI Assistant
Дата: 25 May 2025
"""

import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Статусы health check компонентов"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Результат health check компонента"""
    component: str
    status: HealthStatus
    message: str
    timestamp: datetime
    metrics: Dict[str, Any]
    response_time_ms: float


class SystemHealthChecker:
    """
    JTBD: Как system health checker, я хочу проверять все критические компоненты системы,
    чтобы обеспечить comprehensive monitoring.
    """
    
    def __init__(self):
        self.last_check_time = None
        self.check_history: List[Dict[str, HealthCheckResult]] = []
        self.max_history_size = 100
    
    def check_all_components(self) -> Dict[str, HealthCheckResult]:
        """Проверяет все компоненты системы"""
        start_time = time.time()
        results = {}
        
        results['workflows'] = self._check_workflows()
        results['cache_system'] = self._check_cache_system()
        results['file_system'] = self._check_file_system()
        results['event_system'] = self._check_event_system()
        
        total_time = (time.time() - start_time) * 1000
        self._save_to_history(results, total_time)
        self.last_check_time = datetime.now()
        
        return results
    
    def _check_workflows(self) -> HealthCheckResult:
        """Проверяет состояние workflows"""
        start_time = time.time()
        
        try:
            # Простая проверка доступности портов
            web_port_check = self._check_port(5000)
            api_port_check = self._check_port(5003)
            
            response_time = (time.time() - start_time) * 1000
            
            if web_port_check and api_port_check:
                status = HealthStatus.HEALTHY
                message = "All workflows responding"
            elif web_port_check or api_port_check:
                status = HealthStatus.WARNING
                message = f"Partial availability: Web={web_port_check}, API={api_port_check}"
            else:
                status = HealthStatus.CRITICAL
                message = "No workflows available"
            
            return HealthCheckResult(
                component="workflows",
                status=status,
                message=message,
                timestamp=datetime.now(),
                metrics={
                    'web_server_available': web_port_check,
                    'api_server_available': api_port_check
                },
                response_time_ms=response_time
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="workflows",
                status=HealthStatus.UNKNOWN,
                message=f"Check failed: {str(e)}",
                timestamp=datetime.now(),
                metrics={},
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    def _check_cache_system(self) -> HealthCheckResult:
        """Проверяет состояние кеш-системы"""
        start_time = time.time()
        
        try:
            cache_files = [
                ".cache_state.json",
                ".cache_detailed_state.json", 
                ".critical_instructions_cache.json"
            ]
            
            cache_files_status = {}
            readable_count = 0
            
            for cache_file in cache_files:
                if os.path.exists(cache_file):
                    try:
                        with open(cache_file, 'r') as f:
                            f.read()
                        cache_files_status[cache_file] = "readable"
                        readable_count += 1
                    except:
                        cache_files_status[cache_file] = "corrupted"
                else:
                    cache_files_status[cache_file] = "missing"
            
            response_time = (time.time() - start_time) * 1000
            
            if readable_count == len(cache_files):
                status = HealthStatus.HEALTHY
                message = "Cache system operational"
            elif readable_count > 0:
                status = HealthStatus.WARNING
                message = f"Some cache files missing ({readable_count}/{len(cache_files)})"
            else:
                status = HealthStatus.CRITICAL
                message = "Cache system unavailable"
            
            return HealthCheckResult(
                component="cache_system",
                status=status,
                message=message,
                timestamp=datetime.now(),
                metrics={
                    'cache_files_status': cache_files_status,
                    'readable_files_count': readable_count
                },
                response_time_ms=response_time
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="cache_system",
                status=HealthStatus.CRITICAL,
                message=f"Cache check failed: {str(e)}",
                timestamp=datetime.now(),
                metrics={},
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    def _check_file_system(self) -> HealthCheckResult:
        """Проверяет доступность критических файлов"""
        start_time = time.time()
        
        try:
            critical_files = [
                "[todo · incidents]/todo.md",
                "[todo · incidents]/ai.incidents.md",
                "advising_platform/dependency_mapping.md"
            ]
            
            files_status = {}
            accessible_count = 0
            
            for file_path in critical_files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            f.read()
                        files_status[file_path] = "readable"
                        accessible_count += 1
                    except:
                        files_status[file_path] = "permission_error"
                else:
                    files_status[file_path] = "missing"
            
            response_time = (time.time() - start_time) * 1000
            
            if accessible_count == len(critical_files):
                status = HealthStatus.HEALTHY
                message = "All critical files accessible"
            elif accessible_count > 0:
                status = HealthStatus.WARNING
                message = f"Some files inaccessible ({accessible_count}/{len(critical_files)})"
            else:
                status = HealthStatus.CRITICAL
                message = "Critical files unavailable"
            
            return HealthCheckResult(
                component="file_system",
                status=status,
                message=message,
                timestamp=datetime.now(),
                metrics={
                    'files_status': files_status,
                    'accessible_files': accessible_count
                },
                response_time_ms=response_time
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="file_system",
                status=HealthStatus.CRITICAL,
                message=f"File system check failed: {str(e)}",
                timestamp=datetime.now(),
                metrics={},
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    def _check_event_system(self) -> HealthCheckResult:
        """Проверяет событийную систему"""
        start_time = time.time()
        
        try:
            event_files = [
                "advising_platform/src/events/event_system.py",
                "advising_platform/src/events/event_bus.py"
            ]
            
            files_exist = sum(1 for f in event_files if os.path.exists(f))
            response_time = (time.time() - start_time) * 1000
            
            if files_exist == len(event_files):
                status = HealthStatus.HEALTHY
                message = "Event system components available"
            elif files_exist > 0:
                status = HealthStatus.WARNING
                message = f"Some event components missing ({files_exist}/{len(event_files)})"
            else:
                status = HealthStatus.CRITICAL
                message = "Event system unavailable"
            
            return HealthCheckResult(
                component="event_system",
                status=status,
                message=message,
                timestamp=datetime.now(),
                metrics={
                    'components_available': files_exist,
                    'total_components': len(event_files)
                },
                response_time_ms=response_time
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="event_system",
                status=HealthStatus.UNKNOWN,
                message=f"Event system check failed: {str(e)}",
                timestamp=datetime.now(),
                metrics={},
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    def _check_port(self, port: int) -> bool:
        """Проверяет доступность порта"""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except:
            return False
    
    def _save_to_history(self, results: Dict[str, HealthCheckResult], total_time: float):
        """Сохраняет результаты в историю"""
        history_entry = {
            'timestamp': datetime.now(),
            'total_time_ms': total_time,
            'results': results,
            'overall_status': self._calculate_overall_status(results)
        }
        
        self.check_history.append(history_entry)
        
        if len(self.check_history) > self.max_history_size:
            self.check_history.pop(0)
    
    def _calculate_overall_status(self, results: Dict[str, HealthCheckResult]) -> HealthStatus:
        """Вычисляет общий статус системы"""
        statuses = [result.status for result in results.values()]
        
        if any(s == HealthStatus.CRITICAL for s in statuses):
            return HealthStatus.CRITICAL
        elif any(s == HealthStatus.WARNING for s in statuses):
            return HealthStatus.WARNING
        elif any(s == HealthStatus.UNKNOWN for s in statuses):
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Возвращает краткую сводку состояния системы"""
        if not self.check_history:
            return {
                'status': 'never_checked',
                'message': 'Health check not performed yet'
            }
        
        latest = self.check_history[-1]
        
        return {
            'overall_status': latest['overall_status'].value,
            'last_check': latest['timestamp'].isoformat(),
            'total_time_ms': latest['total_time_ms'],
            'components_count': len(latest['results']),
            'healthy_components': len([r for r in latest['results'].values() if r.status == HealthStatus.HEALTHY]),
            'warning_components': len([r for r in latest['results'].values() if r.status == HealthStatus.WARNING]),
            'critical_components': len([r for r in latest['results'].values() if r.status == HealthStatus.CRITICAL])
        }


# Глобальный экземпляр
_global_health_checker: Optional[SystemHealthChecker] = None

def get_health_checker() -> SystemHealthChecker:
    """Возвращает глобальный экземпляр health checker"""
    global _global_health_checker
    if _global_health_checker is None:
        _global_health_checker = SystemHealthChecker()
    return _global_health_checker


if __name__ == '__main__':
    print("🏥 Health Check Demo...")
    
    checker = get_health_checker()
    results = checker.check_all_components()
    
    print("\n📊 Health Check Results:")
    for component, result in results.items():
        print(f"  {component}: {result.status.value} - {result.message} ({result.response_time_ms:.2f}ms)")
    
    summary = checker.get_health_summary()
    print(f"\n✅ Overall Status: {summary['overall_status']}")
    print(f"📈 Healthy/Warning/Critical: {summary['healthy_components']}/{summary['warning_components']}/{summary['critical_components']}")