# TTBT5 API Reference

## 🎯 Overview

This document provides a comprehensive API reference for all enhanced patterns, components, and utilities in the TTBT5 Voice Chat system.

## 📚 Table of Contents

1. [Application Context](#application-context)
2. [Dependency Injection](#dependency-injection)
3. [Observer Pattern](#observer-pattern)
4. [Factory Pattern](#factory-pattern)
5. [Error Handling](#error-handling)
6. [Caching System](#caching-system)
7. [Logging & Monitoring](#logging--monitoring)
8. [Circuit Breaker](#circuit-breaker)
9. [Retry Mechanism](#retry-mechanism)
10. [Advanced Configuration](#advanced-configuration)
11. [Testing Framework](#testing-framework)
12. [Code Quality Analyzer](#code-quality-analyzer)

---

## Application Context

### `ApplicationContext`

Central application state and lifecycle manager.

```python
from src.patterns.application_context import ApplicationContext, get_context

# Get singleton instance
context = get_context()

# Initialize application
await context.initialize()

# Register services
context.register_service("voice_chat", voice_chat_service)

# Get services
voice_chat = context.get_service("voice_chat")

# Shutdown
await context.shutdown()
```

#### Methods

- `initialize() -> None`: Initialize application context
- `shutdown() -> None`: Shutdown and cleanup resources
- `register_service(name: str, service: Any) -> None`: Register a service
- `get_service(name: str) -> Any`: Get a registered service
- `add_lifecycle_hook(hook: LifecycleHook) -> None`: Add lifecycle hook

### `@requires_context`

Decorator for functions requiring application context.

```python
@requires_context
async def my_function():
    context = get_context()
    # Use context...
```

---

## Dependency Injection

### `DIContainer`

Dependency injection container for managing services and dependencies.

```python
from src.patterns.dependency_injection import DIContainer, inject

# Create container
container = DIContainer()

# Register services
container.register("config", Config, singleton=True)
container.register("logger", Logger, factory=lambda: Logger("app"))

# Get services
config = container.get("config")
logger = container.get("logger")
```

#### Methods

- `register(name: str, service_class: Type, **kwargs) -> None`: Register service
- `get(name: str) -> Any`: Get service instance
- `create_child() -> DIContainer`: Create child container

### `@inject`

Decorator for automatic dependency injection.

```python
@inject
def my_function(config: Config, logger: Logger):
    # Dependencies automatically injected
    pass
```

---

## Observer Pattern

### `EventBus`

Event-driven communication system.

```python
from src.patterns.observer import EventBus, Observer

# Create event bus
event_bus = EventBus()

# Subscribe to events
@event_bus.subscribe("user_message")
async def handle_message(event_data):
    print(f"Received: {event_data}")

# Publish events
await event_bus.publish("user_message", {"text": "Hello"})
```

#### Methods

- `subscribe(event_type: str, handler: Callable) -> None`: Subscribe to events
- `unsubscribe(event_type: str, handler: Callable) -> None`: Unsubscribe from events
- `publish(event_type: str, data: Any) -> None`: Publish event

---

## Factory Pattern

### `ServiceFactory`

Factory for creating service instances with dependency injection.

```python
from src.patterns.factory import ServiceFactory

# Create factory
factory = ServiceFactory(container)

# Register creators
factory.register("voice_chat", VoiceChatService)

# Create instances
voice_chat = factory.create("voice_chat", config=config)
```

#### Methods

- `register(name: str, creator: Callable) -> None`: Register service creator
- `create(name: str, **kwargs) -> Any`: Create service instance

---

## Error Handling

### `ErrorManager`

Central error handling and management system.

```python
from src.patterns.error_handling import ErrorManager, ValidationError

# Create error manager
error_manager = ErrorManager()

# Handle errors
try:
    # Some operation
    pass
except Exception as e:
    await error_manager.handle_error(e, context={"user_id": "123"})
```

### Error Types

- `ValidationError`: Input validation errors
- `ExternalServiceError`: External service failures
- `SecurityError`: Security-related errors
- `ConfigurationError`: Configuration issues

### `@handle_errors`

Decorator for automatic error handling.

```python
@handle_errors(error_manager)
async def risky_operation():
    # Operation that might fail
    pass
```

### `Validator`

Input validation utilities.

```python
from src.patterns.error_handling import Validator

# Validate inputs
Validator.validate_type(value, str, "username")
Validator.validate_email("user@example.com")
Validator.validate_url("https://example.com")
```

---

## Caching System

### `CacheManager`

Multi-level caching system with various strategies.

```python
from src.patterns.caching import CacheManager, CacheStrategy

# Create cache manager
cache = CacheManager(
    strategy=CacheStrategy.LRU,
    max_size=1000,
    ttl=3600
)

# Cache operations
await cache.set("key", "value")
value = await cache.get("key")
await cache.delete("key")
```

### `@cached`

Decorator for automatic function result caching.

```python
@cached(cache_manager, ttl=300)
async def expensive_operation(param):
    # Expensive computation
    return result
```

### Cache Strategies

- `LRU`: Least Recently Used
- `LFU`: Least Frequently Used
- `FIFO`: First In, First Out
- `TTL`: Time To Live
- `ADAPTIVE`: Adaptive strategy

---

## Logging & Monitoring

### `StructuredLogger`

Advanced logging with structured data and context.

```python
from src.patterns.logging_monitoring import StructuredLogger

# Create logger
logger = StructuredLogger("voice_chat")

# Log with context
logger.info("User message received", {
    "user_id": "123",
    "message_length": 50,
    "timestamp": datetime.now()
})
```

### `MonitoringSystem`

Comprehensive system monitoring and metrics collection.

```python
from src.patterns.logging_monitoring import MonitoringSystem

# Create monitoring system
monitor = MonitoringSystem()

# Collect metrics
monitor.record_metric("response_time", 150.5, {"endpoint": "/chat"})
monitor.record_metric("memory_usage", 120.0, {"component": "voice_chat"})

# Health checks
health = await monitor.get_health_status()
```

### `@monitor_performance`

Decorator for automatic performance monitoring.

```python
@monitor_performance(monitor)
async def chat_operation():
    # Operation to monitor
    pass
```

---

## Circuit Breaker

### `CircuitBreaker`

Protection against cascading failures.

```python
from src.resilience.circuit_breaker import CircuitBreaker

# Create circuit breaker
breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30,
    expected_exception=ExternalServiceError
)

# Use circuit breaker
@breaker
async def external_api_call():
    # Call to external service
    pass
```

#### States

- `CLOSED`: Normal operation
- `OPEN`: Circuit is open, calls fail fast
- `HALF_OPEN`: Testing if service recovered

---

## Retry Mechanism

### `RetryPolicy`

Configurable retry mechanism for transient failures.

```python
from src.resilience.retry import RetryPolicy, BackoffStrategy

# Create retry policy
retry_policy = RetryPolicy(
    max_attempts=3,
    backoff_strategy=BackoffStrategy.EXPONENTIAL,
    base_delay=1.0
)

# Use retry
@retry_policy
async def unreliable_operation():
    # Operation that might fail
    pass
```

### Backoff Strategies

- `FIXED`: Fixed delay between retries
- `LINEAR`: Linear increase in delay
- `EXPONENTIAL`: Exponential backoff

---

## Advanced Configuration

### `ConfigManager`

Hierarchical configuration management with validation.

```python
from src.config.advanced_config import ConfigManager

# Create config manager
config = ConfigManager("config/base.json")

# Load environment-specific config
await config.load_environment_config("development")

# Get configuration values
api_key = config.get("api.key")
timeout = config.get("network.timeout", default=30)

# Validate configuration
config.validate()
```

#### Features

- Environment-specific configurations
- Schema validation
- Hot-reloading
- Encrypted values

---

## Testing Framework

### `TestFramework`

Comprehensive testing utilities and fixtures.

```python
from src.testing.test_framework import TestFramework

# Create test framework
test_framework = TestFramework()

# Generate test data
user_data = test_framework.generate_test_data("user")
message_data = test_framework.generate_test_data("message")

# Create mocks
mock_service = test_framework.create_mock("voice_chat_service")
```

### Test Data Generation

```python
# Generate various test data types
user = test_framework.generate_user()
message = test_framework.generate_message()
config = test_framework.generate_config()
```

---

## Code Quality Analyzer

### `CodeAnalyzer`

Static code analysis and quality metrics.

```python
from src.quality.code_analyzer import CodeAnalyzer

# Create analyzer
analyzer = CodeAnalyzer()

# Analyze code
results = analyzer.analyze_file("src/voice_chat.py")
project_results = analyzer.analyze_project("src/")

# Get metrics
complexity = results.complexity_metrics
style_issues = results.style_issues
security_issues = results.security_issues
```

#### Analysis Types

- Complexity analysis (cyclomatic, cognitive)
- Style checking
- Security vulnerability detection
- Documentation coverage
- Performance analysis

---

## Usage Examples

### Complete Integration Example

```python
import asyncio
from src.patterns.application_context import get_context
from src.patterns.dependency_injection import inject
from src.patterns.error_handling import handle_errors
from src.patterns.caching import cached
from src.patterns.logging_monitoring import monitor_performance

@inject
@handle_errors
@cached(ttl=300)
@monitor_performance
async def enhanced_voice_chat_operation(
    config: Config,
    logger: StructuredLogger,
    cache: CacheManager
):
    """Enhanced voice chat operation with all patterns."""
    
    # Get application context
    context = get_context()
    
    # Log operation start
    logger.info("Starting voice chat operation", {
        "operation": "chat_processing",
        "user_id": context.get_current_user_id()
    })
    
    # Process with caching
    result = await process_voice_input()
    
    return result

# Initialize and run
async def main():
    context = get_context()
    await context.initialize()
    
    try:
        result = await enhanced_voice_chat_operation()
        print(f"Result: {result}")
    finally:
        await context.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

### Error Handling Example

```python
from src.patterns.error_handling import ErrorManager, ValidationError, error_context

async def process_user_input(user_input: str):
    error_manager = ErrorManager()
    
    with error_context("user_input_processing"):
        try:
            # Validate input
            if not user_input or len(user_input) > 1000:
                raise ValidationError(
                    "Invalid input length",
                    details={"length": len(user_input), "max_length": 1000}
                )
            
            # Process input
            result = await process_input(user_input)
            return result
            
        except Exception as e:
            await error_manager.handle_error(e, context={
                "user_input_length": len(user_input),
                "processing_stage": "validation"
            })
            raise
```

### Caching Example

```python
from src.patterns.caching import CacheManager, CacheStrategy

# Multi-level caching
cache = CacheManager(
    strategy=CacheStrategy.ADAPTIVE,
    levels=[
        {"type": "memory", "max_size": 1000},
        {"type": "disk", "max_size": 10000},
        {"type": "distributed", "nodes": ["redis://localhost:6379"]}
    ]
)

@cached(cache, ttl=3600, key_prefix="voice_response")
async def generate_voice_response(text: str, voice_id: str):
    """Generate voice response with multi-level caching."""
    # Expensive voice generation
    return await voice_synthesis_api.generate(text, voice_id)
```

---

## Configuration Reference

### Environment Variables

```bash
# Application
TTBT5_ENV=development
TTBT5_LOG_LEVEL=INFO
TTBT5_DEBUG=true

# Database
DATABASE_URL=postgresql://user:pass@localhost/ttbt5
REDIS_URL=redis://localhost:6379

# External Services
ELEVENLABS_API_KEY=your_api_key
ANTHROPIC_API_KEY=your_api_key

# Security
SECRET_KEY=your_secret_key
ENCRYPTION_KEY=your_encryption_key
```

### Configuration Files

#### `config/base.json`
```json
{
  "application": {
    "name": "TTBT5",
    "version": "2.0.0",
    "debug": false
  },
  "logging": {
    "level": "INFO",
    "format": "structured",
    "handlers": ["console", "file"]
  },
  "cache": {
    "strategy": "adaptive",
    "ttl": 3600,
    "max_size": 1000
  },
  "monitoring": {
    "enabled": true,
    "metrics_interval": 60,
    "health_check_interval": 30
  }
}
```

---

## Best Practices

### 1. Dependency Injection
- Register all services in the DI container
- Use interfaces for better testability
- Avoid circular dependencies

### 2. Error Handling
- Use specific error types for different scenarios
- Always provide context with errors
- Implement proper error recovery strategies

### 3. Caching
- Choose appropriate cache strategies for your use case
- Set reasonable TTL values
- Monitor cache hit rates

### 4. Monitoring
- Log structured data with context
- Monitor key performance metrics
- Set up alerts for critical issues

### 5. Testing
- Use the testing framework for consistent test data
- Mock external dependencies
- Test error scenarios

---

## Performance Guidelines

### Memory Usage
- Use appropriate cache sizes
- Clean up resources properly
- Monitor memory consumption

### Response Times
- Cache frequently accessed data
- Use async operations where possible
- Monitor and optimize slow operations

### Scalability
- Design for horizontal scaling
- Use distributed caching for multi-instance deployments
- Implement proper load balancing

---

## Security Considerations

### Input Validation
- Validate all user inputs
- Use the Validator class for common validations
- Sanitize data before processing

### Error Handling
- Don't expose sensitive information in error messages
- Log security events for auditing
- Implement rate limiting

### Configuration
- Use environment variables for sensitive data
- Encrypt configuration files
- Implement proper access controls

---

## Troubleshooting

### Common Issues

1. **Dependency Injection Errors**
   - Check service registration
   - Verify dependency graph
   - Look for circular dependencies

2. **Cache Performance Issues**
   - Monitor cache hit rates
   - Adjust cache sizes
   - Review TTL settings

3. **Circuit Breaker Triggering**
   - Check external service health
   - Review failure thresholds
   - Monitor recovery times

4. **Memory Leaks**
   - Check resource cleanup
   - Monitor object references
   - Review cache eviction policies

### Debug Mode

Enable debug mode for detailed logging:

```python
import os
os.environ["TTBT5_DEBUG"] = "true"
```

### Health Checks

Monitor system health:

```python
from src.patterns.logging_monitoring import MonitoringSystem

monitor = MonitoringSystem()
health = await monitor.get_health_status()
print(f"System Health: {health}")
```

---

This API reference provides comprehensive documentation for all enhanced patterns and components in the TTBT5 system. For more examples and detailed usage, refer to the files in the `examples/` directory.