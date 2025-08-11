"""
Application Context Pattern

This module implements an Application Context pattern for centralized
state management, dependency coordination, and lifecycle management.
"""

import asyncio
import threading
import weakref
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Callable
from enum import Enum

from .dependency_injection import DIContainer
from .observer import EventBus, Event


class ApplicationPhase(Enum):
    """Application lifecycle phases"""
    INITIALIZING = "initializing"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ApplicationMetrics:
    """Application-wide metrics"""
    start_time: datetime = field(default_factory=datetime.now)
    requests_processed: int = 0
    errors_encountered: int = 0
    active_connections: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    uptime_seconds: float = 0.0


class LifecycleHook(ABC):
    """Abstract base class for lifecycle hooks"""
    
    @abstractmethod
    async def on_startup(self, context: 'ApplicationContext') -> None:
        """Called during application startup"""
        pass
    
    @abstractmethod
    async def on_shutdown(self, context: 'ApplicationContext') -> None:
        """Called during application shutdown"""
        pass
    
    async def on_error(self, context: 'ApplicationContext', error: Exception) -> None:
        """Called when an error occurs"""
        pass


class ResourceManager:
    """Manages application resources with automatic cleanup"""
    
    def __init__(self):
        self._resources: Dict[str, Any] = {}
        self._cleanup_handlers: Dict[str, Callable] = {}
        self._lock = threading.RLock()
    
    def register_resource(self, name: str, resource: Any, cleanup_handler: Optional[Callable] = None):
        """Register a resource with optional cleanup handler"""
        with self._lock:
            self._resources[name] = resource
            if cleanup_handler:
                self._cleanup_handlers[name] = cleanup_handler
    
    def get_resource(self, name: str) -> Optional[Any]:
        """Get a registered resource"""
        with self._lock:
            return self._resources.get(name)
    
    def remove_resource(self, name: str) -> bool:
        """Remove and cleanup a resource"""
        with self._lock:
            if name in self._resources:
                # Call cleanup handler if exists
                if name in self._cleanup_handlers:
                    try:
                        self._cleanup_handlers[name](self._resources[name])
                    except Exception as e:
                        print(f"Error cleaning up resource {name}: {e}")
                
                del self._resources[name]
                self._cleanup_handlers.pop(name, None)
                return True
            return False
    
    async def cleanup_all(self):
        """Cleanup all registered resources"""
        with self._lock:
            for name in list(self._resources.keys()):
                self.remove_resource(name)


T = TypeVar('T')


class ApplicationContext:
    """
    Central application context for managing state, dependencies, and lifecycle
    
    Features:
    - Centralized dependency injection container
    - Event bus for application-wide communication
    - Resource management with automatic cleanup
    - Lifecycle management with hooks
    - Application metrics tracking
    - Thread-safe operations
    """
    
    _instance: Optional['ApplicationContext'] = None
    _lock = threading.RLock()
    
    def __new__(cls) -> 'ApplicationContext':
        """Singleton pattern implementation"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.container = DIContainer()
        self.event_bus = EventBus()
        self.resource_manager = ResourceManager()
        self.metrics = ApplicationMetrics()
        
        self._phase = ApplicationPhase.INITIALIZING
        self._lifecycle_hooks: List[LifecycleHook] = []
        self._shutdown_event = asyncio.Event()
        self._error_handlers: List[Callable[[Exception], None]] = []
        
        # Register core services
        self.container.register('context', self, singleton=True)
        self.container.register('event_bus', self.event_bus, singleton=True)
        self.container.register('resource_manager', self.resource_manager, singleton=True)
        
        # Setup event handlers
        self.event_bus.subscribe('application.error', self._handle_application_error)
        self.event_bus.subscribe('application.metrics_updated', self._handle_metrics_update)
    
    @property
    def phase(self) -> ApplicationPhase:
        """Get current application phase"""
        return self._phase
    
    @property
    def is_running(self) -> bool:
        """Check if application is running"""
        return self._phase == ApplicationPhase.RUNNING
    
    def register_service(self, name: str, service_type: Type[T], **kwargs) -> None:
        """Register a service in the DI container"""
        self.container.register(name, service_type, **kwargs)
    
    def get_service(self, name: str) -> Any:
        """Get a service from the DI container"""
        return self.container.resolve(name)
    
    def register_lifecycle_hook(self, hook: LifecycleHook) -> None:
        """Register a lifecycle hook"""
        self._lifecycle_hooks.append(hook)
    
    def register_error_handler(self, handler: Callable[[Exception], None]) -> None:
        """Register an error handler"""
        self._error_handlers.append(handler)
    
    async def startup(self) -> None:
        """Start the application"""
        try:
            self._phase = ApplicationPhase.STARTING
            self.event_bus.publish(Event('application.starting', {'phase': self._phase}))
            
            # Execute startup hooks
            for hook in self._lifecycle_hooks:
                await hook.on_startup(self)
            
            self._phase = ApplicationPhase.RUNNING
            self.event_bus.publish(Event('application.started', {'phase': self._phase}))
            
        except Exception as e:
            self._phase = ApplicationPhase.ERROR
            await self._handle_error(e)
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the application"""
        try:
            self._phase = ApplicationPhase.STOPPING
            self.event_bus.publish(Event('application.stopping', {'phase': self._phase}))
            
            # Execute shutdown hooks
            for hook in reversed(self._lifecycle_hooks):  # Reverse order
                try:
                    await hook.on_shutdown(self)
                except Exception as e:
                    print(f"Error in shutdown hook: {e}")
            
            # Cleanup resources
            await self.resource_manager.cleanup_all()
            
            self._phase = ApplicationPhase.STOPPED
            self.event_bus.publish(Event('application.stopped', {'phase': self._phase}))
            self._shutdown_event.set()
            
        except Exception as e:
            self._phase = ApplicationPhase.ERROR
            await self._handle_error(e)
            raise
    
    async def wait_for_shutdown(self) -> None:
        """Wait for application shutdown"""
        await self._shutdown_event.wait()
    
    def update_metrics(self, **kwargs) -> None:
        """Update application metrics"""
        for key, value in kwargs.items():
            if hasattr(self.metrics, key):
                setattr(self.metrics, key, value)
        
        # Calculate uptime
        self.metrics.uptime_seconds = (datetime.now() - self.metrics.start_time).total_seconds()
        
        # Publish metrics update event
        self.event_bus.publish(Event('application.metrics_updated', {
            'metrics': self.metrics,
            'timestamp': datetime.now()
        }))
    
    async def _handle_error(self, error: Exception) -> None:
        """Handle application errors"""
        # Execute error handlers
        for handler in self._error_handlers:
            try:
                handler(error)
            except Exception as e:
                print(f"Error in error handler: {e}")
        
        # Execute lifecycle hook error handlers
        for hook in self._lifecycle_hooks:
            try:
                await hook.on_error(self, error)
            except Exception as e:
                print(f"Error in lifecycle hook error handler: {e}")
        
        # Publish error event
        self.event_bus.publish(Event('application.error', {
            'error': str(error),
            'error_type': type(error).__name__,
            'phase': self._phase
        }))
    
    def _handle_application_error(self, event: Event) -> None:
        """Handle application error events"""
        self.metrics.errors_encountered += 1
    
    def _handle_metrics_update(self, event: Event) -> None:
        """Handle metrics update events"""
        # Could trigger alerts, logging, etc.
        pass
    
    @contextmanager
    def resource_scope(self, name: str, resource: Any, cleanup_handler: Optional[Callable] = None):
        """Context manager for automatic resource cleanup"""
        self.resource_manager.register_resource(name, resource, cleanup_handler)
        try:
            yield resource
        finally:
            self.resource_manager.remove_resource(name)
    
    @asynccontextmanager
    async def async_resource_scope(self, name: str, resource: Any, cleanup_handler: Optional[Callable] = None):
        """Async context manager for automatic resource cleanup"""
        self.resource_manager.register_resource(name, resource, cleanup_handler)
        try:
            yield resource
        finally:
            self.resource_manager.remove_resource(name)


class ConfigurationLifecycleHook(LifecycleHook):
    """Lifecycle hook for configuration management"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
    
    async def on_startup(self, context: ApplicationContext) -> None:
        """Initialize configuration on startup"""
        await self.config_manager.load_configuration()
        context.register_service('config', self.config_manager, singleton=True)
    
    async def on_shutdown(self, context: ApplicationContext) -> None:
        """Save configuration on shutdown"""
        await self.config_manager.save_configuration()


class LoggingLifecycleHook(LifecycleHook):
    """Lifecycle hook for logging setup"""
    
    def __init__(self, logger_factory):
        self.logger_factory = logger_factory
    
    async def on_startup(self, context: ApplicationContext) -> None:
        """Setup logging on startup"""
        logger = self.logger_factory.create_logger()
        context.register_service('logger', logger, singleton=True)
        logger.info("Application starting up")
    
    async def on_shutdown(self, context: ApplicationContext) -> None:
        """Cleanup logging on shutdown"""
        logger = context.get_service('logger')
        if logger:
            logger.info("Application shutting down")


class PerformanceMonitoringHook(LifecycleHook):
    """Lifecycle hook for performance monitoring"""
    
    def __init__(self, monitor):
        self.monitor = monitor
    
    async def on_startup(self, context: ApplicationContext) -> None:
        """Start performance monitoring"""
        self.monitor.start()
        context.register_service('performance_monitor', self.monitor, singleton=True)
        
        # Start metrics collection task
        asyncio.create_task(self._collect_metrics(context))
    
    async def on_shutdown(self, context: ApplicationContext) -> None:
        """Stop performance monitoring"""
        self.monitor.stop()
    
    async def _collect_metrics(self, context: ApplicationContext) -> None:
        """Collect system metrics periodically"""
        import psutil
        
        while context.is_running:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent()
                memory_info = psutil.virtual_memory()
                memory_mb = memory_info.used / (1024 * 1024)
                
                # Update context metrics
                context.update_metrics(
                    cpu_usage_percent=cpu_percent,
                    memory_usage_mb=memory_mb
                )
                
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                print(f"Error collecting metrics: {e}")
                await asyncio.sleep(60)  # Wait longer on error


# Convenience functions
def get_application_context() -> ApplicationContext:
    """Get the global application context"""
    return ApplicationContext()


def register_service(name: str, service_type: Type[T], **kwargs) -> None:
    """Register a service in the global context"""
    context = get_application_context()
    context.register_service(name, service_type, **kwargs)


def get_service(name: str) -> Any:
    """Get a service from the global context"""
    context = get_application_context()
    return context.get_service(name)


def publish_event(event_name: str, data: Any = None) -> None:
    """Publish an event through the global context"""
    context = get_application_context()
    context.event_bus.publish(Event(event_name, data))


# Decorators for easy integration
def with_context(func):
    """Decorator to inject application context"""
    def wrapper(*args, **kwargs):
        context = get_application_context()
        return func(context, *args, **kwargs)
    return wrapper


def async_with_context(func):
    """Async decorator to inject application context"""
    async def wrapper(*args, **kwargs):
        context = get_application_context()
        return await func(context, *args, **kwargs)
    return wrapper