"""
Enhanced Integration Demo

This example demonstrates the integration of all advanced patterns:
- Application Context
- Enhanced Error Handling & Validation
- Advanced Caching System
- Enhanced Logging & Monitoring
- Integration with existing patterns (DI, Observer, Circuit Breaker, etc.)
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Import all our advanced patterns
from src.patterns.application_context import (
    ApplicationContext, ApplicationPhase, LifecycleHook,
    get_application_context, application_lifecycle
)
from src.patterns.error_handling import (
    ErrorManager, ApplicationError, ValidationError, SecurityError,
    ErrorSeverity, ErrorCategory, Validator, handle_errors, validate_parameters
)
from src.patterns.caching import (
    CacheManager, MemoryCacheBackend, DiskCacheBackend, HierarchicalCache,
    CacheLevel, cached, cache_invalidate, get_default_cache_manager
)
from src.patterns.logging_monitoring import (
    MonitoringSystem, StructuredLogger, AlertRule, AlertSeverity,
    MetricEntry, MetricType, monitor_performance, log_calls,
    get_default_monitoring_system, get_default_logger
)

# Import existing patterns
from src.patterns.dependency_injection import DIContainer, inject
from src.patterns.observer import EventBus, event_handler
from src.patterns.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from src.resilience.retry import Retry, RetryConfig


class EnhancedVoiceChatService:
    """Enhanced Voice Chat Service with all patterns integrated"""
    
    def __init__(self):
        self.conversation_history = []
        self.user_preferences = {}
        self.active_sessions = {}
    
    @inject('cache_manager', 'logger', 'error_manager')
    @cached(ttl=300, tags={'voice_chat', 'ai_response'})
    @monitor_performance()
    @log_calls()
    @handle_errors()
    async def generate_ai_response(
        self,
        user_input: str,
        user_id: str,
        cache_manager: CacheManager,
        logger: StructuredLogger,
        error_manager: ErrorManager
    ) -> str:
        """Generate AI response with full pattern integration"""
        
        # Validate input
        Validator.validate_type(user_input, str, "user_input")
        Validator.validate_length(user_input, min_length=1, max_length=1000, field_name="user_input")
        
        if not user_id:
            raise ValidationError("user_id", user_id, "User ID cannot be empty")
        
        await logger.info(f"Generating AI response for user {user_id}", user_id=user_id)
        
        # Simulate AI processing with potential failures
        if "error" in user_input.lower():
            raise ApplicationError(
                "Simulated AI processing error",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.EXTERNAL_SERVICE,
                recovery_suggestions=["Try rephrasing your question", "Check your internet connection"]
            )
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        response = f"AI Response to: {user_input} (processed at {datetime.now()})"
        
        # Record metrics
        monitoring = get_default_monitoring_system()
        monitoring.metrics.record_metric(MetricEntry(
            name="ai.response.generated",
            value=1,
            metric_type=MetricType.COUNTER,
            tags={"user_id": user_id}
        ))
        
        return response
    
    @inject('event_bus')
    @monitor_performance()
    @log_calls()
    async def start_conversation(
        self,
        user_id: str,
        event_bus: EventBus
    ) -> Dict[str, Any]:
        """Start a new conversation"""
        
        session_id = f"session_{user_id}_{int(time.time())}"
        
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'started_at': datetime.now(),
            'message_count': 0
        }
        
        self.active_sessions[session_id] = session_data
        
        # Emit event
        await event_bus.emit('conversation_started', {
            'session_id': session_id,
            'user_id': user_id,
            'timestamp': datetime.now()
        })
        
        return session_data
    
    @cache_invalidate(tags={'voice_chat', 'user_preferences'})
    @monitor_performance()
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> None:
        """Update user preferences and invalidate related cache"""
        self.user_preferences[user_id] = preferences
        
        # Emit event for preference update
        context = get_application_context()
        event_bus = context.get_dependency('event_bus')
        await event_bus.emit('user_preferences_updated', {
            'user_id': user_id,
            'preferences': preferences
        })


class ConversationAnalytics:
    """Analytics service for conversation data"""
    
    @inject('logger', 'cache_manager')
    @event_handler('conversation_started')
    @monitor_performance()
    async def on_conversation_started(
        self,
        event_data: Dict[str, Any],
        logger: StructuredLogger,
        cache_manager: CacheManager
    ) -> None:
        """Handle conversation started event"""
        
        await logger.info(
            "Conversation analytics: New conversation started",
            session_id=event_data['session_id'],
            user_id=event_data['user_id']
        )
        
        # Update analytics cache
        analytics_key = f"analytics:daily:{datetime.now().strftime('%Y-%m-%d')}"
        daily_stats = await cache_manager.get(analytics_key) or {'conversations': 0, 'users': set()}
        
        daily_stats['conversations'] += 1
        daily_stats['users'].add(event_data['user_id'])
        
        await cache_manager.set(analytics_key, daily_stats, ttl=86400)  # 24 hours
    
    @event_handler('user_preferences_updated')
    async def on_preferences_updated(self, event_data: Dict[str, Any]) -> None:
        """Handle user preferences update"""
        logger = get_default_logger()
        await logger.info(
            "User preferences updated",
            user_id=event_data['user_id'],
            preferences_count=len(event_data['preferences'])
        )


class SecurityAuditHook(LifecycleHook):
    """Security audit lifecycle hook"""
    
    async def on_startup(self, context: ApplicationContext) -> None:
        """Perform security audit on startup"""
        logger = context.get_dependency('logger')
        await logger.security("Security audit: Application starting up")
        
        # Simulate security checks
        security_checks = [
            "API key validation",
            "SSL certificate verification",
            "Database connection security",
            "File permission checks"
        ]
        
        for check in security_checks:
            await logger.info(f"Security check: {check}")
            await asyncio.sleep(0.01)  # Simulate check time
        
        await logger.security("Security audit: All checks passed")
    
    async def on_shutdown(self, context: ApplicationContext) -> None:
        """Perform security cleanup on shutdown"""
        logger = context.get_dependency('logger')
        await logger.security("Security audit: Application shutting down")


class PerformanceMonitoringHook(LifecycleHook):
    """Performance monitoring lifecycle hook"""
    
    async def on_startup(self, context: ApplicationContext) -> None:
        """Setup performance monitoring"""
        monitoring = context.get_dependency('monitoring_system')
        
        # Add health checks
        monitoring.add_health_check('database', lambda: True)  # Simulate DB health
        monitoring.add_health_check('cache', lambda: True)     # Simulate cache health
        monitoring.add_health_check('ai_service', lambda: True)  # Simulate AI service health
        
        # Add alert rules
        monitoring.alerts.add_rule(AlertRule(
            name="high_error_rate",
            condition=lambda ctx: ctx.get('metrics', {}).get('counters', {}).get('errors', 0) > 10,
            severity=AlertSeverity.HIGH,
            message_template="High error rate detected: {errors} errors",
            cooldown_minutes=5
        ))
        
        monitoring.alerts.add_rule(AlertRule(
            name="memory_usage_high",
            condition=lambda ctx: ctx.get('metrics', {}).get('gauges', {}).get('system.memory.usage_percent', 0) > 80,
            severity=AlertSeverity.MEDIUM,
            message_template="High memory usage: {memory_percent}%",
            cooldown_minutes=10
        ))
        
        # Start monitoring
        await monitoring.start_monitoring(interval_seconds=30)
        
        logger = context.get_dependency('logger')
        await logger.info("Performance monitoring started")
    
    async def on_shutdown(self, context: ApplicationContext) -> None:
        """Stop performance monitoring"""
        monitoring = context.get_dependency('monitoring_system')
        await monitoring.stop_monitoring()
        
        logger = context.get_dependency('logger')
        await logger.info("Performance monitoring stopped")


async def setup_enhanced_application() -> ApplicationContext:
    """Setup the enhanced application with all patterns"""
    
    # Get application context
    context = get_application_context()
    
    # Setup dependencies
    container = DIContainer()
    
    # Setup monitoring system
    monitoring_system = MonitoringSystem()
    monitoring_system.setup_default_handlers()
    
    # Setup logger
    logger = StructuredLogger("enhanced_app")
    logger.add_handler(monitoring_system.logger.handlers[0])  # Share console handler
    logger.set_min_level(monitoring_system.logger.min_level)
    
    # Setup error manager
    error_manager = ErrorManager()
    error_manager.register_handler(monitoring_system.logger.handlers[0])  # Use logging handler
    
    # Setup cache system
    memory_backend = MemoryCacheBackend(max_size=1000, max_memory_mb=50)
    disk_backend = DiskCacheBackend(cache_dir="./cache", max_size_mb=100)
    
    # Create hierarchical cache
    hierarchical_cache = HierarchicalCache()
    hierarchical_cache.add_level(CacheLevel.L1_MEMORY, CacheManager(memory_backend))
    hierarchical_cache.add_level(CacheLevel.L2_DISK, CacheManager(disk_backend))
    
    cache_manager = CacheManager(memory_backend)  # Primary cache manager
    
    # Setup event bus
    event_bus = EventBus()
    
    # Setup circuit breaker
    circuit_breaker = CircuitBreaker(CircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout=30,
        expected_exception_types=[ApplicationError]
    ))
    
    # Register dependencies
    container.register('monitoring_system', monitoring_system)
    container.register('logger', logger)
    container.register('error_manager', error_manager)
    container.register('cache_manager', cache_manager)
    container.register('hierarchical_cache', hierarchical_cache)
    container.register('event_bus', event_bus)
    container.register('circuit_breaker', circuit_breaker)
    
    # Register services
    voice_chat_service = EnhancedVoiceChatService()
    analytics_service = ConversationAnalytics()
    
    container.register('voice_chat_service', voice_chat_service)
    container.register('analytics_service', analytics_service)
    
    # Setup application context
    context.set_container(container)
    context.set_event_bus(event_bus)
    
    # Add lifecycle hooks
    context.add_lifecycle_hook(SecurityAuditHook())
    context.add_lifecycle_hook(PerformanceMonitoringHook())
    
    return context


@application_lifecycle
async def demonstrate_enhanced_patterns():
    """Demonstrate all enhanced patterns working together"""
    
    print("🚀 Starting Enhanced TTBT5 Integration Demo")
    print("=" * 60)
    
    # Setup application
    context = await setup_enhanced_application()
    
    try:
        # Start application
        await context.startup()
        
        # Get services
        voice_chat = context.get_dependency('voice_chat_service')
        analytics = context.get_dependency('analytics_service')
        logger = context.get_dependency('logger')
        monitoring = context.get_dependency('monitoring_system')
        
        print("\n📊 Application started successfully!")
        print(f"Phase: {context.current_phase}")
        print(f"Dependencies: {len(context.container._instances)}")
        
        # Demonstrate conversation flow
        print("\n🗣️  Starting conversation demo...")
        
        # Start conversation
        session = await voice_chat.start_conversation("user123")
        print(f"Session started: {session['session_id']}")
        
        # Generate AI responses
        test_inputs = [
            "Hello, how are you?",
            "What's the weather like?",
            "Tell me a joke",
            "This should cause an error",  # Will trigger error handling
            "What are your capabilities?"
        ]
        
        for i, user_input in enumerate(test_inputs, 1):
            print(f"\n💬 Test {i}: {user_input}")
            
            try:
                response = await voice_chat.generate_ai_response(user_input, "user123")
                print(f"✅ Response: {response[:50]}...")
            except Exception as e:
                print(f"❌ Error handled: {type(e).__name__}: {e}")
        
        # Update user preferences
        print("\n⚙️  Updating user preferences...")
        await voice_chat.update_user_preferences("user123", {
            "language": "en",
            "voice_speed": "normal",
            "personality": "friendly"
        })
        
        # Wait a bit for monitoring to collect data
        await asyncio.sleep(2)
        
        # Show monitoring data
        print("\n📈 Monitoring Statistics:")
        stats = await monitoring.metrics.get_all_metrics()
        print(f"Counters: {stats.get('counters', {})}")
        print(f"Timers: {list(stats.get('timers', {}).keys())}")
        
        # Show cache statistics
        cache_manager = context.get_dependency('cache_manager')
        cache_stats = await cache_manager.get_stats()
        print(f"\n💾 Cache Statistics:")
        print(f"Hit rate: {cache_stats.hit_rate:.2%}")
        print(f"Entries: {cache_stats.entry_count}")
        print(f"Size: {cache_stats.size_bytes} bytes")
        
        # Show active alerts
        active_alerts = monitoring.alerts.get_active_alerts()
        print(f"\n🚨 Active Alerts: {len(active_alerts)}")
        for alert in active_alerts:
            print(f"  - {alert.severity.value}: {alert.message}")
        
        # Demonstrate error recovery
        print("\n🔄 Testing error recovery...")
        try:
            # This will fail but should be handled gracefully
            await voice_chat.generate_ai_response("", "")  # Invalid input
        except ValidationError as e:
            print(f"✅ Validation error caught and handled: {e.field}")
        
        print("\n🎉 Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger = context.get_dependency('logger')
        await logger.error(f"Demo failed: {e}", exc_info=True)
    
    finally:
        # Shutdown application
        await context.shutdown()
        print("\n🛑 Application shutdown complete")


async def demonstrate_caching_strategies():
    """Demonstrate different caching strategies"""
    
    print("\n💾 Caching Strategies Demo")
    print("-" * 40)
    
    # Memory cache
    memory_cache = CacheManager(MemoryCacheBackend(max_size=100))
    
    # Disk cache
    disk_cache = CacheManager(DiskCacheBackend(cache_dir="./demo_cache"))
    
    # Hierarchical cache
    hierarchical = HierarchicalCache()
    hierarchical.add_level(CacheLevel.L1_MEMORY, memory_cache)
    hierarchical.add_level(CacheLevel.L2_DISK, disk_cache)
    
    # Test data
    test_data = {
        "user:123": {"name": "John", "preferences": {"theme": "dark"}},
        "conversation:456": {"messages": ["Hello", "Hi there"]},
        "analytics:daily": {"conversations": 42, "users": 15}
    }
    
    # Store in hierarchical cache
    for key, value in test_data.items():
        await hierarchical.set(key, value)
        print(f"Stored: {key}")
    
    # Retrieve and show cache hits
    for key in test_data.keys():
        value = await hierarchical.get(key)
        print(f"Retrieved: {key} -> {value is not None}")
    
    # Show cache statistics
    memory_stats = await memory_cache.get_stats()
    disk_stats = await disk_cache.get_stats()
    
    print(f"\nMemory Cache - Hits: {memory_stats.hits}, Misses: {memory_stats.misses}")
    print(f"Disk Cache - Hits: {disk_stats.hits}, Misses: {disk_stats.misses}")


async def demonstrate_error_handling():
    """Demonstrate comprehensive error handling"""
    
    print("\n🚫 Error Handling Demo")
    print("-" * 40)
    
    error_manager = ErrorManager()
    
    # Test different error types
    errors_to_test = [
        ValidationError("email", "invalid-email", "Must be valid email format"),
        SecurityError("Unauthorized access attempt"),
        ApplicationError(
            "Service temporarily unavailable",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.EXTERNAL_SERVICE,
            recovery_suggestions=["Retry in 5 minutes", "Check service status"]
        )
    ]
    
    for error in errors_to_test:
        print(f"\nTesting: {type(error).__name__}")
        result = await error_manager.handle_error(error)
        print(f"Handled: {result is not None}")
        print(f"Error ID: {error.error_id if hasattr(error, 'error_id') else 'N/A'}")
    
    # Show error statistics
    stats = error_manager.get_error_statistics()
    print(f"\nError Statistics: {stats}")


if __name__ == "__main__":
    async def main():
        """Main demo function"""
        await demonstrate_enhanced_patterns()
        await demonstrate_caching_strategies()
        await demonstrate_error_handling()
    
    # Run the demo
    asyncio.run(main())