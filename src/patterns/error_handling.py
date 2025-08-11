"""
Enhanced Error Handling and Validation System

This module provides comprehensive error handling, validation,
and error recovery mechanisms for robust application behavior.
"""

import functools
import inspect
import traceback
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union, get_type_hints
import logging


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification"""
    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    SYSTEM = "system"
    SECURITY = "security"
    PERFORMANCE = "performance"


@dataclass
class ErrorContext:
    """Context information for errors"""
    timestamp: datetime = field(default_factory=datetime.now)
    function_name: str = ""
    module_name: str = ""
    line_number: int = 0
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorInfo:
    """Comprehensive error information"""
    error_id: str
    message: str
    error_type: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: ErrorContext
    stack_trace: str
    is_recoverable: bool = True
    recovery_suggestions: List[str] = field(default_factory=list)
    user_message: Optional[str] = None


class ApplicationError(Exception):
    """Base application error with enhanced information"""
    
    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.BUSINESS_LOGIC,
        is_recoverable: bool = True,
        recovery_suggestions: Optional[List[str]] = None,
        user_message: Optional[str] = None,
        context: Optional[ErrorContext] = None
    ):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.category = category
        self.is_recoverable = is_recoverable
        self.recovery_suggestions = recovery_suggestions or []
        self.user_message = user_message
        self.context = context or ErrorContext()
        self.error_id = self._generate_error_id()
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        import uuid
        return f"ERR_{self.category.value.upper()}_{uuid.uuid4().hex[:8]}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary"""
        return {
            'error_id': self.error_id,
            'message': self.message,
            'error_type': self.__class__.__name__,
            'severity': self.severity.value,
            'category': self.category.value,
            'is_recoverable': self.is_recoverable,
            'recovery_suggestions': self.recovery_suggestions,
            'user_message': self.user_message,
            'context': {
                'timestamp': self.context.timestamp.isoformat(),
                'function_name': self.context.function_name,
                'module_name': self.context.module_name,
                'line_number': self.context.line_number,
                'additional_data': self.context.additional_data
            }
        }


class ValidationError(ApplicationError):
    """Validation-specific error"""
    
    def __init__(self, field: str, value: Any, constraint: str, **kwargs):
        message = f"Validation failed for field '{field}': {constraint}"
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            **kwargs
        )
        self.field = field
        self.value = value
        self.constraint = constraint


class ExternalServiceError(ApplicationError):
    """External service error"""
    
    def __init__(self, service_name: str, operation: str, **kwargs):
        message = f"External service '{service_name}' failed during '{operation}'"
        super().__init__(
            message=message,
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
        self.service_name = service_name
        self.operation = operation


class SecurityError(ApplicationError):
    """Security-related error"""
    
    def __init__(self, security_issue: str, **kwargs):
        super().__init__(
            message=f"Security violation: {security_issue}",
            category=ErrorCategory.SECURITY,
            severity=ErrorSeverity.CRITICAL,
            is_recoverable=False,
            **kwargs
        )


class ErrorHandler(ABC):
    """Abstract error handler"""
    
    @abstractmethod
    def can_handle(self, error: Exception) -> bool:
        """Check if this handler can handle the error"""
        pass
    
    @abstractmethod
    async def handle(self, error: Exception, context: ErrorContext) -> Optional[Any]:
        """Handle the error and optionally return a result"""
        pass


class LoggingErrorHandler(ErrorHandler):
    """Error handler that logs errors"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def can_handle(self, error: Exception) -> bool:
        """Can handle any error for logging"""
        return True
    
    async def handle(self, error: Exception, context: ErrorContext) -> None:
        """Log the error"""
        if isinstance(error, ApplicationError):
            log_level = {
                ErrorSeverity.LOW: logging.INFO,
                ErrorSeverity.MEDIUM: logging.WARNING,
                ErrorSeverity.HIGH: logging.ERROR,
                ErrorSeverity.CRITICAL: logging.CRITICAL
            }.get(error.severity, logging.ERROR)
            
            self.logger.log(log_level, f"Application Error: {error.to_dict()}")
        else:
            self.logger.error(f"Unhandled Error: {error}", exc_info=True)


class RetryErrorHandler(ErrorHandler):
    """Error handler that implements retry logic"""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_counts: Dict[str, int] = {}
    
    def can_handle(self, error: Exception) -> bool:
        """Can handle recoverable application errors"""
        return isinstance(error, ApplicationError) and error.is_recoverable
    
    async def handle(self, error: Exception, context: ErrorContext) -> Optional[bool]:
        """Handle error with retry logic"""
        if not isinstance(error, ApplicationError):
            return None
        
        error_key = f"{context.function_name}_{error.error_id}"
        retry_count = self.retry_counts.get(error_key, 0)
        
        if retry_count < self.max_retries:
            self.retry_counts[error_key] = retry_count + 1
            
            # Calculate backoff delay
            import asyncio
            delay = self.backoff_factor * (2 ** retry_count)
            await asyncio.sleep(delay)
            
            return True  # Indicate retry should happen
        
        # Max retries exceeded
        self.retry_counts.pop(error_key, None)
        return False


class ErrorManager:
    """Central error management system"""
    
    def __init__(self):
        self.handlers: List[ErrorHandler] = []
        self.error_history: List[ErrorInfo] = []
        self.max_history_size = 1000
    
    def register_handler(self, handler: ErrorHandler) -> None:
        """Register an error handler"""
        self.handlers.append(handler)
    
    async def handle_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> Optional[Any]:
        """Handle an error using registered handlers"""
        if context is None:
            context = self._create_context_from_stack()
        
        # Create error info
        error_info = self._create_error_info(error, context)
        self._add_to_history(error_info)
        
        # Try each handler
        for handler in self.handlers:
            if handler.can_handle(error):
                try:
                    result = await handler.handle(error, context)
                    if result is not None:
                        return result
                except Exception as handler_error:
                    # Handler itself failed, log and continue
                    print(f"Error handler failed: {handler_error}")
        
        # No handler could resolve the error
        return None
    
    def _create_context_from_stack(self) -> ErrorContext:
        """Create error context from current stack"""
        frame = inspect.currentframe()
        try:
            # Go up the stack to find the actual error location
            while frame and frame.f_code.co_filename == __file__:
                frame = frame.f_back
            
            if frame:
                return ErrorContext(
                    function_name=frame.f_code.co_name,
                    module_name=frame.f_globals.get('__name__', ''),
                    line_number=frame.f_lineno
                )
        finally:
            del frame
        
        return ErrorContext()
    
    def _create_error_info(self, error: Exception, context: ErrorContext) -> ErrorInfo:
        """Create comprehensive error information"""
        if isinstance(error, ApplicationError):
            return ErrorInfo(
                error_id=error.error_id,
                message=error.message,
                error_type=type(error).__name__,
                severity=error.severity,
                category=error.category,
                context=context,
                stack_trace=traceback.format_exc(),
                is_recoverable=error.is_recoverable,
                recovery_suggestions=error.recovery_suggestions,
                user_message=error.user_message
            )
        else:
            return ErrorInfo(
                error_id=f"SYS_{hash(str(error)) % 100000:05d}",
                message=str(error),
                error_type=type(error).__name__,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.SYSTEM,
                context=context,
                stack_trace=traceback.format_exc(),
                is_recoverable=False
            )
    
    def _add_to_history(self, error_info: ErrorInfo) -> None:
        """Add error to history with size limit"""
        self.error_history.append(error_info)
        if len(self.error_history) > self.max_history_size:
            self.error_history.pop(0)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        if not self.error_history:
            return {'total_errors': 0}
        
        total_errors = len(self.error_history)
        severity_counts = {}
        category_counts = {}
        
        for error in self.error_history:
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
            category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
        
        return {
            'total_errors': total_errors,
            'severity_distribution': severity_counts,
            'category_distribution': category_counts,
            'recent_errors': [error.error_id for error in self.error_history[-10:]]
        }


class Validator:
    """Enhanced validation system"""
    
    @staticmethod
    def validate_type(value: Any, expected_type: Type, field_name: str = "value") -> None:
        """Validate value type"""
        if not isinstance(value, expected_type):
            raise ValidationError(
                field=field_name,
                value=value,
                constraint=f"Expected type {expected_type.__name__}, got {type(value).__name__}"
            )
    
    @staticmethod
    def validate_range(value: Union[int, float], min_val: Optional[Union[int, float]] = None,
                      max_val: Optional[Union[int, float]] = None, field_name: str = "value") -> None:
        """Validate numeric range"""
        if min_val is not None and value < min_val:
            raise ValidationError(
                field=field_name,
                value=value,
                constraint=f"Value must be >= {min_val}"
            )
        
        if max_val is not None and value > max_val:
            raise ValidationError(
                field=field_name,
                value=value,
                constraint=f"Value must be <= {max_val}"
            )
    
    @staticmethod
    def validate_length(value: str, min_length: Optional[int] = None,
                       max_length: Optional[int] = None, field_name: str = "value") -> None:
        """Validate string length"""
        length = len(value)
        
        if min_length is not None and length < min_length:
            raise ValidationError(
                field=field_name,
                value=value,
                constraint=f"Length must be >= {min_length}"
            )
        
        if max_length is not None and length > max_length:
            raise ValidationError(
                field=field_name,
                value=value,
                constraint=f"Length must be <= {max_length}"
            )
    
    @staticmethod
    def validate_email(email: str, field_name: str = "email") -> None:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError(
                field=field_name,
                value=email,
                constraint="Invalid email format"
            )
    
    @staticmethod
    def validate_url(url: str, field_name: str = "url") -> None:
        """Validate URL format"""
        import re
        pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
        if not re.match(pattern, url):
            raise ValidationError(
                field=field_name,
                value=url,
                constraint="Invalid URL format"
            )


# Decorators for easy error handling
def handle_errors(error_manager: Optional[ErrorManager] = None):
    """Decorator for automatic error handling"""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if error_manager:
                    result = await error_manager.handle_error(e)
                    if result is not None:
                        return result
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if error_manager:
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                        result = loop.run_until_complete(error_manager.handle_error(e))
                        if result is not None:
                            return result
                    except:
                        pass
                raise
        
        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
    return decorator


def validate_parameters(**validators):
    """Decorator for parameter validation"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate parameters
            for param_name, validator_func in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    validator_func(value, param_name)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


@contextmanager
def error_context(**context_data):
    """Context manager for adding error context"""
    # This would integrate with the error manager to add context
    try:
        yield
    except Exception as e:
        if isinstance(e, ApplicationError) and e.context:
            e.context.additional_data.update(context_data)
        raise


# Global error manager instance
_global_error_manager: Optional[ErrorManager] = None


def get_error_manager() -> ErrorManager:
    """Get the global error manager"""
    global _global_error_manager
    if _global_error_manager is None:
        _global_error_manager = ErrorManager()
    return _global_error_manager