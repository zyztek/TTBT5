"""
Enhanced Logging and Monitoring System

This module provides comprehensive logging, metrics collection,
alerting, and monitoring capabilities for robust observability.
"""

import asyncio
import functools
import json
import logging
import time
import threading
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union
import uuid
import weakref


class LogLevel(Enum):
    """Enhanced log levels"""
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    SECURITY = 60


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    SET = "set"


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: datetime = field(default_factory=datetime.now)
    level: LogLevel = LogLevel.INFO
    message: str = ""
    logger_name: str = ""
    module: str = ""
    function: str = ""
    line_number: int = 0
    thread_id: str = ""
    correlation_id: str = ""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    extra_data: Dict[str, Any] = field(default_factory=dict)
    exception_info: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.name,
            'message': self.message,
            'logger_name': self.logger_name,
            'module': self.module,
            'function': self.function,
            'line_number': self.line_number,
            'thread_id': self.thread_id,
            'correlation_id': self.correlation_id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'request_id': self.request_id,
            'tags': self.tags,
            'extra_data': self.extra_data,
            'exception_info': self.exception_info
        }


@dataclass
class MetricEntry:
    """Metric entry"""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    unit: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'value': self.value,
            'type': self.metric_type.value,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags,
            'unit': self.unit
        }


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    condition: Callable[[Any], bool]
    severity: AlertSeverity
    message_template: str
    cooldown_minutes: int = 5
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class Alert:
    """Alert instance"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_name: str = ""
    severity: AlertSeverity = AlertSeverity.LOW
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    tags: Dict[str, str] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


class LogHandler(ABC):
    """Abstract log handler"""
    
    @abstractmethod
    async def handle(self, entry: LogEntry) -> None:
        """Handle log entry"""
        pass


class ConsoleLogHandler(LogHandler):
    """Console log handler with formatting"""
    
    def __init__(self, format_json: bool = False, min_level: LogLevel = LogLevel.INFO):
        self.format_json = format_json
        self.min_level = min_level
    
    async def handle(self, entry: LogEntry) -> None:
        """Handle log entry to console"""
        if entry.level.value < self.min_level.value:
            return
        
        if self.format_json:
            print(json.dumps(entry.to_dict(), indent=2))
        else:
            # Formatted output
            timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            level_name = entry.level.name.ljust(8)
            logger_name = entry.logger_name or "root"
            
            message = f"[{timestamp}] {level_name} {logger_name}: {entry.message}"
            
            if entry.tags:
                tags_str = " ".join(f"{k}={v}" for k, v in entry.tags.items())
                message += f" | {tags_str}"
            
            print(message)


class FileLogHandler(LogHandler):
    """File log handler with rotation"""
    
    def __init__(
        self,
        filename: str,
        max_size_mb: int = 10,
        backup_count: int = 5,
        format_json: bool = True
    ):
        self.filename = filename
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.backup_count = backup_count
        self.format_json = format_json
        self.lock = threading.Lock()
    
    async def handle(self, entry: LogEntry) -> None:
        """Handle log entry to file"""
        with self.lock:
            # Check if rotation is needed
            await self._rotate_if_needed()
            
            # Write log entry
            try:
                with open(self.filename, 'a', encoding='utf-8') as f:
                    if self.format_json:
                        f.write(json.dumps(entry.to_dict()) + '\n')
                    else:
                        timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"[{timestamp}] {entry.level.name} {entry.logger_name}: {entry.message}\n")
            except Exception as e:
                print(f"Failed to write log to file: {e}")
    
    async def _rotate_if_needed(self) -> None:
        """Rotate log file if it's too large"""
        import os
        
        try:
            if os.path.exists(self.filename) and os.path.getsize(self.filename) > self.max_size_bytes:
                # Rotate files
                for i in range(self.backup_count - 1, 0, -1):
                    old_file = f"{self.filename}.{i}"
                    new_file = f"{self.filename}.{i + 1}"
                    if os.path.exists(old_file):
                        if os.path.exists(new_file):
                            os.remove(new_file)
                        os.rename(old_file, new_file)
                
                # Move current file to .1
                backup_file = f"{self.filename}.1"
                if os.path.exists(backup_file):
                    os.remove(backup_file)
                os.rename(self.filename, backup_file)
        except Exception as e:
            print(f"Failed to rotate log file: {e}")


class MetricsCollector:
    """Metrics collection and aggregation"""
    
    def __init__(self, max_history_size: int = 10000):
        self.max_history_size = max_history_size
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history_size))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.sets: Dict[str, Set[str]] = defaultdict(set)
        self.lock = threading.RLock()
    
    def record_metric(self, entry: MetricEntry) -> None:
        """Record a metric entry"""
        with self.lock:
            self.metrics[entry.name].append(entry)
            
            # Update aggregated values based on metric type
            if entry.metric_type == MetricType.COUNTER:
                self.counters[entry.name] += entry.value
            elif entry.metric_type == MetricType.GAUGE:
                self.gauges[entry.name] = entry.value
            elif entry.metric_type == MetricType.HISTOGRAM:
                self.histograms[entry.name].append(entry.value)
                # Keep only recent values
                if len(self.histograms[entry.name]) > 1000:
                    self.histograms[entry.name] = self.histograms[entry.name][-1000:]
            elif entry.metric_type == MetricType.TIMER:
                self.timers[entry.name].append(entry.value)
                if len(self.timers[entry.name]) > 1000:
                    self.timers[entry.name] = self.timers[entry.name][-1000:]
            elif entry.metric_type == MetricType.SET:
                self.sets[entry.name].add(str(entry.value))
    
    def get_counter(self, name: str) -> float:
        """Get counter value"""
        with self.lock:
            return self.counters.get(name, 0.0)
    
    def get_gauge(self, name: str) -> float:
        """Get gauge value"""
        with self.lock:
            return self.gauges.get(name, 0.0)
    
    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        """Get histogram statistics"""
        with self.lock:
            values = self.histograms.get(name, [])
            if not values:
                return {}
            
            values_sorted = sorted(values)
            count = len(values)
            
            return {
                'count': count,
                'min': min(values),
                'max': max(values),
                'mean': sum(values) / count,
                'p50': values_sorted[int(count * 0.5)],
                'p90': values_sorted[int(count * 0.9)],
                'p95': values_sorted[int(count * 0.95)],
                'p99': values_sorted[int(count * 0.99)]
            }
    
    def get_timer_stats(self, name: str) -> Dict[str, float]:
        """Get timer statistics"""
        return self.get_histogram_stats(name)  # Same as histogram
    
    def get_set_size(self, name: str) -> int:
        """Get set size"""
        with self.lock:
            return len(self.sets.get(name, set()))
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics summary"""
        with self.lock:
            return {
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'histograms': {name: self.get_histogram_stats(name) for name in self.histograms},
                'timers': {name: self.get_timer_stats(name) for name in self.timers},
                'sets': {name: self.get_set_size(name) for name in self.sets}
            }


class AlertManager:
    """Alert management system"""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.cooldown_tracker: Dict[str, datetime] = {}
        self.handlers: List[Callable[[Alert], None]] = []
        self.lock = threading.RLock()
    
    def add_rule(self, rule: AlertRule) -> None:
        """Add alert rule"""
        with self.lock:
            self.rules[rule.name] = rule
    
    def remove_rule(self, rule_name: str) -> None:
        """Remove alert rule"""
        with self.lock:
            self.rules.pop(rule_name, None)
    
    def add_handler(self, handler: Callable[[Alert], None]) -> None:
        """Add alert handler"""
        self.handlers.append(handler)
    
    async def check_conditions(self, context: Dict[str, Any]) -> List[Alert]:
        """Check all alert conditions"""
        triggered_alerts = []
        
        with self.lock:
            for rule_name, rule in self.rules.items():
                if not rule.enabled:
                    continue
                
                # Check cooldown
                if rule_name in self.cooldown_tracker:
                    cooldown_end = self.cooldown_tracker[rule_name] + timedelta(minutes=rule.cooldown_minutes)
                    if datetime.now() < cooldown_end:
                        continue
                
                # Check condition
                try:
                    if rule.condition(context):
                        alert = Alert(
                            rule_name=rule_name,
                            severity=rule.severity,
                            message=rule.message_template.format(**context),
                            tags=rule.tags.copy(),
                            context=context.copy()
                        )
                        
                        triggered_alerts.append(alert)
                        self.active_alerts[alert.id] = alert
                        self.alert_history.append(alert)
                        self.cooldown_tracker[rule_name] = datetime.now()
                        
                        # Notify handlers
                        for handler in self.handlers:
                            try:
                                handler(alert)
                            except Exception as e:
                                print(f"Alert handler failed: {e}")
                
                except Exception as e:
                    print(f"Alert condition check failed for {rule_name}: {e}")
        
        return triggered_alerts
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert"""
        with self.lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                alert.resolved_at = datetime.now()
                del self.active_alerts[alert_id]
                return True
            return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        with self.lock:
            return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history"""
        with self.lock:
            return self.alert_history[-limit:]


class StructuredLogger:
    """Enhanced structured logger"""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.handlers: List[LogHandler] = []
        self.context: Dict[str, Any] = {}
        self.correlation_id = ""
        self.min_level = LogLevel.INFO
    
    def add_handler(self, handler: LogHandler) -> None:
        """Add log handler"""
        self.handlers.append(handler)
    
    def set_context(self, **context) -> None:
        """Set logging context"""
        self.context.update(context)
    
    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for request tracing"""
        self.correlation_id = correlation_id
    
    def set_min_level(self, level: LogLevel) -> None:
        """Set minimum log level"""
        self.min_level = level
    
    async def log(
        self,
        level: LogLevel,
        message: str,
        **extra
    ) -> None:
        """Log a message"""
        if level.value < self.min_level.value:
            return
        
        # Get caller information
        import inspect
        frame = inspect.currentframe()
        try:
            caller_frame = frame.f_back.f_back if frame and frame.f_back else None
            if caller_frame:
                module = caller_frame.f_globals.get('__name__', '')
                function = caller_frame.f_code.co_name
                line_number = caller_frame.f_lineno
            else:
                module = function = ""
                line_number = 0
        finally:
            del frame
        
        # Create log entry
        entry = LogEntry(
            level=level,
            message=message,
            logger_name=self.name,
            module=module,
            function=function,
            line_number=line_number,
            thread_id=str(threading.get_ident()),
            correlation_id=self.correlation_id,
            tags=self.context.copy(),
            extra_data=extra
        )
        
        # Handle exception info
        if 'exc_info' in extra and extra['exc_info']:
            import traceback
            entry.exception_info = traceback.format_exc()
        
        # Send to handlers
        for handler in self.handlers:
            try:
                await handler.handle(entry)
            except Exception as e:
                print(f"Log handler failed: {e}")
    
    async def trace(self, message: str, **extra) -> None:
        """Log trace message"""
        await self.log(LogLevel.TRACE, message, **extra)
    
    async def debug(self, message: str, **extra) -> None:
        """Log debug message"""
        await self.log(LogLevel.DEBUG, message, **extra)
    
    async def info(self, message: str, **extra) -> None:
        """Log info message"""
        await self.log(LogLevel.INFO, message, **extra)
    
    async def warning(self, message: str, **extra) -> None:
        """Log warning message"""
        await self.log(LogLevel.WARNING, message, **extra)
    
    async def error(self, message: str, **extra) -> None:
        """Log error message"""
        await self.log(LogLevel.ERROR, message, **extra)
    
    async def critical(self, message: str, **extra) -> None:
        """Log critical message"""
        await self.log(LogLevel.CRITICAL, message, **extra)
    
    async def security(self, message: str, **extra) -> None:
        """Log security message"""
        await self.log(LogLevel.SECURITY, message, **extra)


class MonitoringSystem:
    """Comprehensive monitoring system"""
    
    def __init__(self):
        self.logger = StructuredLogger("monitoring")
        self.metrics = MetricsCollector()
        self.alerts = AlertManager()
        self.performance_tracker = PerformanceTracker()
        self.health_checks: Dict[str, Callable[[], bool]] = {}
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
    
    def setup_default_handlers(self) -> None:
        """Setup default logging and alert handlers"""
        # Add console handler
        console_handler = ConsoleLogHandler(format_json=False)
        self.logger.add_handler(console_handler)
        
        # Add file handler
        file_handler = FileLogHandler("logs/application.log")
        self.logger.add_handler(file_handler)
        
        # Add default alert handler
        self.alerts.add_handler(self._default_alert_handler)
    
    def add_health_check(self, name: str, check_func: Callable[[], bool]) -> None:
        """Add health check"""
        self.health_checks[name] = check_func
    
    async def start_monitoring(self, interval_seconds: int = 60) -> None:
        """Start monitoring loop"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop(interval_seconds))
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring loop"""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
    
    async def _monitoring_loop(self, interval_seconds: int) -> None:
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Run health checks
                health_status = await self._run_health_checks()
                
                # Check alert conditions
                context = {
                    'metrics': self.metrics.get_all_metrics(),
                    'health': health_status,
                    'timestamp': datetime.now()
                }
                await self.alerts.check_conditions(context)
                
                await asyncio.sleep(interval_seconds)
            
            except Exception as e:
                await self.logger.error(f"Monitoring loop error: {e}", exc_info=True)
                await asyncio.sleep(interval_seconds)
    
    async def _collect_system_metrics(self) -> None:
        """Collect system metrics"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            self.metrics.record_metric(MetricEntry(
                name="system.cpu.usage_percent",
                value=cpu_percent,
                metric_type=MetricType.GAUGE,
                unit="percent"
            ))
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics.record_metric(MetricEntry(
                name="system.memory.usage_percent",
                value=memory.percent,
                metric_type=MetricType.GAUGE,
                unit="percent"
            ))
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.metrics.record_metric(MetricEntry(
                name="system.disk.usage_percent",
                value=disk_percent,
                metric_type=MetricType.GAUGE,
                unit="percent"
            ))
            
        except ImportError:
            # psutil not available
            pass
        except Exception as e:
            await self.logger.warning(f"Failed to collect system metrics: {e}")
    
    async def _run_health_checks(self) -> Dict[str, bool]:
        """Run all health checks"""
        health_status = {}
        
        for name, check_func in self.health_checks.items():
            try:
                is_healthy = check_func()
                health_status[name] = is_healthy
                
                if not is_healthy:
                    await self.logger.warning(f"Health check failed: {name}")
            
            except Exception as e:
                health_status[name] = False
                await self.logger.error(f"Health check error for {name}: {e}")
        
        return health_status
    
    def _default_alert_handler(self, alert: Alert) -> None:
        """Default alert handler"""
        print(f"🚨 ALERT [{alert.severity.value.upper()}]: {alert.message}")


class PerformanceTracker:
    """Performance tracking and profiling"""
    
    def __init__(self):
        self.function_timings: Dict[str, List[float]] = defaultdict(list)
        self.active_timers: Dict[str, float] = {}
        self.lock = threading.RLock()
    
    def start_timer(self, name: str) -> str:
        """Start a performance timer"""
        timer_id = f"{name}_{uuid.uuid4().hex[:8]}"
        with self.lock:
            self.active_timers[timer_id] = time.time()
        return timer_id
    
    def stop_timer(self, timer_id: str) -> Optional[float]:
        """Stop a performance timer"""
        with self.lock:
            if timer_id in self.active_timers:
                start_time = self.active_timers.pop(timer_id)
                duration = time.time() - start_time
                
                # Extract function name from timer_id
                func_name = timer_id.rsplit('_', 1)[0]
                self.function_timings[func_name].append(duration)
                
                # Keep only recent timings
                if len(self.function_timings[func_name]) > 1000:
                    self.function_timings[func_name] = self.function_timings[func_name][-1000:]
                
                return duration
        return None
    
    def get_stats(self, function_name: str) -> Dict[str, float]:
        """Get performance statistics for a function"""
        with self.lock:
            timings = self.function_timings.get(function_name, [])
            if not timings:
                return {}
            
            timings_sorted = sorted(timings)
            count = len(timings)
            
            return {
                'count': count,
                'min': min(timings),
                'max': max(timings),
                'mean': sum(timings) / count,
                'p50': timings_sorted[int(count * 0.5)],
                'p90': timings_sorted[int(count * 0.9)],
                'p95': timings_sorted[int(count * 0.95)],
                'p99': timings_sorted[int(count * 0.99)]
            }


# Decorators for easy monitoring
def monitor_performance(monitoring_system: Optional[MonitoringSystem] = None):
    """Decorator for performance monitoring"""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            nonlocal monitoring_system
            if monitoring_system is None:
                monitoring_system = get_default_monitoring_system()
            
            func_name = f"{func.__module__}.{func.__name__}"
            timer_id = monitoring_system.performance_tracker.start_timer(func_name)
            
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = monitoring_system.performance_tracker.stop_timer(timer_id)
                if duration is not None:
                    monitoring_system.metrics.record_metric(MetricEntry(
                        name=f"function.{func_name}.duration",
                        value=duration,
                        metric_type=MetricType.TIMER,
                        unit="seconds"
                    ))
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            nonlocal monitoring_system
            if monitoring_system is None:
                monitoring_system = get_default_monitoring_system()
            
            func_name = f"{func.__module__}.{func.__name__}"
            timer_id = monitoring_system.performance_tracker.start_timer(func_name)
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = monitoring_system.performance_tracker.stop_timer(timer_id)
                if duration is not None:
                    monitoring_system.metrics.record_metric(MetricEntry(
                        name=f"function.{func_name}.duration",
                        value=duration,
                        metric_type=MetricType.TIMER,
                        unit="seconds"
                    ))
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def log_calls(logger: Optional[StructuredLogger] = None, level: LogLevel = LogLevel.DEBUG):
    """Decorator for logging function calls"""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_default_logger()
            
            func_name = f"{func.__module__}.{func.__name__}"
            await logger.log(level, f"Calling {func_name}", args=str(args), kwargs=str(kwargs))
            
            try:
                result = await func(*args, **kwargs)
                await logger.log(level, f"Completed {func_name}")
                return result
            except Exception as e:
                await logger.error(f"Failed {func_name}: {e}", exc_info=True)
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_default_logger()
            
            func_name = f"{func.__module__}.{func.__name__}"
            
            # For sync functions, we need to handle async logging
            loop = None
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            loop.run_until_complete(logger.log(level, f"Calling {func_name}", args=str(args), kwargs=str(kwargs)))
            
            try:
                result = func(*args, **kwargs)
                loop.run_until_complete(logger.log(level, f"Completed {func_name}"))
                return result
            except Exception as e:
                loop.run_until_complete(logger.error(f"Failed {func_name}: {e}", exc_info=True))
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


# Global instances
_default_monitoring_system: Optional[MonitoringSystem] = None
_default_logger: Optional[StructuredLogger] = None


def get_default_monitoring_system() -> MonitoringSystem:
    """Get the default monitoring system"""
    global _default_monitoring_system
    if _default_monitoring_system is None:
        _default_monitoring_system = MonitoringSystem()
        _default_monitoring_system.setup_default_handlers()
    return _default_monitoring_system


def get_default_logger() -> StructuredLogger:
    """Get the default logger"""
    global _default_logger
    if _default_logger is None:
        _default_logger = StructuredLogger("default")
        console_handler = ConsoleLogHandler()
        _default_logger.add_handler(console_handler)
    return _default_logger