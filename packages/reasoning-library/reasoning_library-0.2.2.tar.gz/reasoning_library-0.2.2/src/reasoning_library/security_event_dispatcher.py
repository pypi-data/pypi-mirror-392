"""
Security Event Dispatcher

ARCH-001: This module provides a central dispatcher for security events that breaks
circular dependencies between sanitization.py and security_logging.py.

The dispatcher acts as a mediator that:
1. Receives security events from any component
2. Routes them to appropriate handlers
3. Provides a clean interface without circular dependencies
4. Supports lazy loading of the actual security logging implementation
"""

import logging
from typing import Dict, Any, Optional, Callable, List
from .security_events import SecurityEvent, SecurityEventType, SecuritySeverity


class SecurityEventDispatcher:
    """
    Central dispatcher for security events.

    This class provides a singleton-like dispatcher that can receive events
    from any component and route them to appropriate handlers without creating
    circular dependencies.
    """

    _instance: Optional['SecurityEventDispatcher'] = None
    _initialized: bool = False

    def __new__(cls) -> 'SecurityEventDispatcher':
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the dispatcher."""
        if not SecurityEventDispatcher._initialized:
            self._handlers: List[Callable[[SecurityEvent], None]] = []
            self._fallback_handler: Optional[Callable[[SecurityEvent], None]] = None
            self._logger = logging.getLogger(__name__)
            SecurityEventDispatcher._initialized = True

    def register_handler(self, handler: Callable[[SecurityEvent], None]) -> None:
        """
        Register a security event handler.

        Args:
            handler: Function that accepts SecurityEvent objects
        """
        if handler not in self._handlers:
            self._handlers.append(handler)
            self._logger.debug(f"Registered security event handler: {handler.__name__}")

    def register_fallback_handler(self, handler: Callable[[SecurityEvent], None]) -> None:
        """
        Register a fallback handler for when no other handlers are available.

        Args:
            handler: Function that accepts SecurityEvent objects
        """
        self._fallback_handler = handler
        self._logger.debug(f"Registered fallback security event handler: {handler.__name__}")

    def dispatch_event(self, event: SecurityEvent) -> None:
        """
        Dispatch a security event to all registered handlers.

        Args:
            event: SecurityEvent to dispatch
        """
        if self._handlers:
            for handler in self._handlers:
                try:
                    handler(event)
                except Exception as e:
                    self._logger.error(f"Security event handler {handler.__name__} failed: {e}")
        elif self._fallback_handler:
            try:
                self._fallback_handler(event)
            except Exception as e:
                self._logger.error(f"Fallback security event handler failed: {e}")
        else:
            # No handlers registered - log the security event directly
            security_logger = logging.getLogger('reasoning_library.security')

            # Sanitize the input preview to prevent log injection
            from .sanitization import sanitize_for_logging
            safe_preview = sanitize_for_logging(event.input_preview[:50] if event.input_preview else 'No preview')
            message = f"[SECURITY] {event.event_type.value.upper()} | Severity: {event.severity.value.upper()} | Source: {event.source} | Action: {event.action} | Details: {safe_preview}"

            # Log at appropriate severity level
            if event.severity.value == 'critical':
                security_logger.critical(message)
            elif event.severity.value == 'high':
                security_logger.error(message)
            elif event.severity.value == 'medium':
                security_logger.warning(message)
            else:  # low
                security_logger.info(message)

            # Also log that no handlers are registered for debugging
            self._logger.debug(f"No security event handlers registered. Event logged directly.")

    def clear_handlers(self) -> None:
        """Clear all registered handlers (useful for testing)."""
        self._handlers.clear()
        self._fallback_handler = None


# Global dispatcher instance
_dispatcher: Optional[SecurityEventDispatcher] = None


def get_security_event_dispatcher() -> SecurityEventDispatcher:
    """
    Get the global security event dispatcher.

    Returns:
        SecurityEventDispatcher instance
    """
    global _dispatcher
    if _dispatcher is None:
        _dispatcher = SecurityEventDispatcher()
    return _dispatcher


def dispatch_security_event(event: SecurityEvent) -> None:
    """
    Convenience function to dispatch a security event.

    Args:
        event: SecurityEvent to dispatch
    """
    get_security_event_dispatcher().dispatch_event(event)


def register_security_event_handler(handler: Callable[[SecurityEvent], None]) -> None:
    """
    Convenience function to register a security event handler.

    Args:
        handler: Function that accepts SecurityEvent objects
    """
    get_security_event_dispatcher().register_handler(handler)


# Backward compatibility functions that delegate to the factory pattern
# ARCH-002: These now use the factory pattern for better testability

def log_security_event(input_text: str,
                      source: str = "unknown",
                      context: Optional[Dict[str, Any]] = None,
                      block_action: bool = False) -> Dict[str, Any]:
    """
    Backward compatibility function for logging security events.

    This function creates and dispatches a security event using the factory pattern.
    It maintains the same interface as the original function from security_logging.py.

    Args:
        input_text: The suspicious input that triggered the event
        source: Source identifier (IP, user ID, module, etc.)
        context: Additional context information
        block_action: Whether the action was blocked

    Returns:
        Dict containing the event details (for backward compatibility)
    """
    from .security_events import SecurityEventType, SecuritySeverity, create_security_event

    # Default to reasoning_library if source is unknown
    if source == "unknown":
        source = "reasoning_library"

    # Create a basic event (the actual classification will happen in the handler)
    event = create_security_event(
        event_type=SecurityEventType.SUSPICIOUS_PATTERN,
        severity=SecuritySeverity.MEDIUM,
        input_text=input_text,
        source=source,
        context=context or {}
    )

    # Add action context
    event.action = "blocked" if block_action else "sanitized"

    # Dispatch the event
    dispatch_security_event(event)

    # Return event details for backward compatibility
    return event.to_dict()