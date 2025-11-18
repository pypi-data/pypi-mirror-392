"""
Security Factory and Dependency Injection

ARCH-002: This module provides factory patterns and dependency injection
to replace global singletons and improve testability.

This replaces the global _security_logger singleton with a proper
factory pattern that supports:
1. Dependency injection for testing
2. Multiple logger instances
3. Configuration-based creation
4. Clean lifecycle management
"""

import logging
from typing import Dict, Any, Optional, Protocol, Union
from abc import ABC, abstractmethod
from threading import Lock
from .security_events import SecurityEvent, SecurityEventType, SecuritySeverity
from .security_event_dispatcher import SecurityEventDispatcher


class SecurityLoggerInterface(Protocol):
    """Protocol for security logger implementations."""

    def log_security_event(self,
                          input_text: str,
                          source: str = "unknown",
                          context: Optional[Dict[str, Any]] = None,
                          block_action: bool = False) -> Dict[str, Any]:
        """Log a security event."""
        ...

    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics."""
        ...

    def security_context(self, source: str = "unknown"):
        """Get security context manager."""
        ...


class SecurityLoggerFactory(ABC):
    """Abstract factory for creating security loggers."""

    @abstractmethod
    def create_logger(self, name: str = "reasoning_library.security", **kwargs) -> SecurityLoggerInterface:
        """Create a security logger instance."""
        pass

    @abstractmethod
    def create_dispatcher(self) -> SecurityEventDispatcher:
        """Create a security event dispatcher."""
        pass


class DefaultSecurityLoggerFactory(SecurityLoggerFactory):
    """Default factory implementation that creates standard security loggers."""

    def __init__(self):
        self._dispatcher: Optional[SecurityEventDispatcher] = None
        self._lock = Lock()

    def create_logger(self, name: str = "reasoning_library.security", **kwargs) -> SecurityLoggerInterface:
        """Create a standard security logger."""
        from .security_logging import SecurityLogger
        return SecurityLogger(name)

    def create_dispatcher(self) -> SecurityEventDispatcher:
        """Create or get the singleton dispatcher."""
        if self._dispatcher is None:
            with self._lock:
                if self._dispatcher is None:
                    self._dispatcher = SecurityEventDispatcher()
        return self._dispatcher


class TestSecurityLoggerFactory(SecurityLoggerFactory):
    """Factory for testing that creates mock/in-memory loggers."""

    def __init__(self):
        self.events: list[SecurityEvent] = []
        self.metrics = {
            "total_events": 0,
            "events_by_type": {},
            "active_sources": 0,
            "rate_limited_sources": 0,
            "correlation_patterns": 0,
            "last_activity": None
        }

    def create_logger(self, name: str = "test.security", **kwargs) -> SecurityLoggerInterface:
        """Create a test security logger that stores events in memory."""
        return TestSecurityLogger(self)

    def create_dispatcher(self) -> SecurityEventDispatcher:
        """Create a test dispatcher."""
        return TestSecurityEventDispatcher(self)


class TestSecurityLogger:
    """Test implementation of security logger for unit tests."""

    def __init__(self, factory: 'TestSecurityLoggerFactory'):
        self.factory = factory
        self.name = "test.security"

    def log_security_event(self,
                          input_text: str,
                          source: str = "unknown",
                          context: Optional[Dict[str, Any]] = None,
                          block_action: bool = False) -> Dict[str, Any]:
        """Log a security event to the in-memory store."""
        from .security_events import create_security_event, SecurityEventType, SecuritySeverity

        event = create_security_event(
            event_type=SecurityEventType.SUSPICIOUS_PATTERN,
            severity=SecuritySeverity.MEDIUM,
            input_text=input_text,
            source=source,
            context=context or {}
        )
        event.action = "blocked" if block_action else "sanitized"

        self.factory.events.append(event)
        self.factory.metrics["total_events"] += 1
        self.factory.metrics["events_by_type"][event.event_type.value] = \
            self.factory.metrics["events_by_type"].get(event.event_type.value, 0) + 1

        return event.to_dict()

    def get_security_metrics(self) -> Dict[str, Any]:
        """Get test metrics."""
        return self.factory.metrics.copy()

    def security_context(self, source: str = "unknown"):
        """Return a no-op context manager for testing."""
        from contextlib import nullcontext
        return nullcontext()


class TestSecurityEventDispatcher(SecurityEventDispatcher):
    """Test implementation of security event dispatcher."""

    def __init__(self, factory: 'TestSecurityLoggerFactory'):
        self.factory = factory
        self._handlers = []

    def register_handler(self, handler) -> None:
        """Register a handler."""
        self._handlers.append(handler)

    def dispatch_event(self, event: SecurityEvent) -> None:
        """Dispatch event to registered handlers."""
        self.factory.events.append(event)
        for handler in self._handlers:
            try:
                handler(event)
            except Exception:
                pass  # Ignore handler errors in tests


class SecurityLoggerRegistry:
    """
    Registry for managing security logger factory instances.

    This provides a centralized way to manage different factory implementations
    and supports dependency injection for testing.
    """

    _instance: Optional['SecurityLoggerRegistry'] = None
    _lock = Lock()

    def __new__(cls) -> 'SecurityLoggerRegistry':
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the registry."""
        if not hasattr(self, '_initialized'):
            self._factory: Optional[SecurityLoggerFactory] = None
            self._default_factory = DefaultSecurityLoggerFactory()
            self._initialized = True

    def register_factory(self, factory: SecurityLoggerFactory) -> None:
        """
        Register a custom factory implementation.

        This is useful for dependency injection in tests.

        Args:
            factory: Factory implementation to use
        """
        with self._lock:
            self._factory = factory

    def get_factory(self) -> SecurityLoggerFactory:
        """
        Get the current factory.

        Returns:
            Current factory implementation (custom or default)
        """
        if self._factory is not None:
            return self._factory
        return self._default_factory

    def reset_to_default(self) -> None:
        """Reset to the default factory (useful for testing)."""
        with self._lock:
            self._factory = None

    def create_logger(self, name: str = "reasoning_library.security", **kwargs) -> SecurityLoggerInterface:
        """
        Create a security logger using the current factory.

        Args:
            name: Logger name
            **kwargs: Additional arguments for the factory

        Returns:
            Security logger instance
        """
        return self.get_factory().create_logger(name, **kwargs)

    def create_dispatcher(self) -> SecurityEventDispatcher:
        """
        Create a security event dispatcher using the current factory.

        Returns:
            Security event dispatcher instance
        """
        return self.get_factory().create_dispatcher()


# Global registry instance
_registry: Optional[SecurityLoggerRegistry] = None


def get_security_logger_registry() -> SecurityLoggerRegistry:
    """
    Get the global security logger registry.

    Returns:
        SecurityLoggerRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = SecurityLoggerRegistry()
    return _registry


def create_security_logger(name: str = "reasoning_library.security", **kwargs) -> SecurityLoggerInterface:
    """
    Create a security logger using the factory pattern.

    This replaces the global singleton with proper dependency injection.

    Args:
        name: Logger name
        **kwargs: Additional arguments for the factory

    Returns:
        Security logger instance
    """
    return get_security_logger_registry().create_logger(name, **kwargs)


def create_security_event_dispatcher() -> SecurityEventDispatcher:
    """
    Create a security event dispatcher using the factory pattern.

    Args:
        None

    Returns:
        Security event dispatcher instance
    """
    return get_security_logger_registry().create_dispatcher()


def register_security_logger_factory(factory: SecurityLoggerFactory) -> None:
    """
    Register a custom security logger factory.

    This enables dependency injection for testing.

    Args:
        factory: Factory implementation to use
    """
    get_security_logger_registry().register_factory(factory)


def reset_security_logger_factory() -> None:
    """
    Reset to the default security logger factory.

    This is useful for cleaning up after tests.
    """
    get_security_logger_registry().reset_to_default()


# Context manager for testing
class TestSecurityLoggerContext:
    """Context manager for using test security loggers."""

    def __init__(self):
        self.test_factory = TestSecurityLoggerFactory()
        self.original_factory = None

    def __enter__(self) -> TestSecurityLoggerFactory:
        """Enter the test context."""
        registry = get_security_logger_registry()
        self.original_factory = registry.get_factory()
        registry.register_factory(self.test_factory)
        return self.test_factory

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the test context and restore original factory."""
        get_security_logger_registry().register_factory(self.original_factory)


def use_test_security_logger() -> TestSecurityLoggerContext:
    """
    Get a context manager for using test security loggers.

    Usage:
        with use_test_security_logger() as test_factory:
            logger = create_security_logger("test")
            # ... test code ...

    Returns:
        TestSecurityLoggerContext
    """
    return TestSecurityLoggerContext()