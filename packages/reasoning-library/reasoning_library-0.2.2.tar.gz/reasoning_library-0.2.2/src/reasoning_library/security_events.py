"""
Security Events Interface and Abstraction Layer

ARCH-001: This module provides the abstraction layer needed to break circular dependencies
between sanitization.py and security_logging.py. It defines interfaces and event structures
that both modules can depend on without creating circular imports.

This module contains:
1. Event type definitions and enums
2. Security event data structures
3. Abstract interfaces for security event handling
4. Event severity classifications
5. Correlation data structures

Key Design Principles:
- No dependencies on other internal modules
- Pure data structures and interfaces
- Forward compatibility for event processing
- Serialization-friendly for persistent storage
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional, List, Set, Protocol
import json


class SecurityEventType(Enum):
    """Classification of security events for proper monitoring."""
    CODE_INJECTION = "code_injection"
    SQL_INJECTION = "sql_injection"
    XSS_ATTEMPT = "xss_attempt"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    LDAP_INJECTION = "ldap_injection"
    LOG_INJECTION = "log_injection"
    TEMPLATE_INJECTION = "template_injection"
    SIZE_LIMIT_EXCEEDED = "size_limit_exceeded"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    ENCODED_ATTACK = "encoded_attack"
    NESTED_INJECTION = "nested_injection"
    UNICODE_BYPASS = "unicode_bypass"
    SANITIZATION_BLOCKED = "sanitization_blocked"
    VALIDATION_FAILED = "validation_failed"
    AUTHENTICATION_FAILED = "authentication_failed"
    AUTHORIZATION_FAILED = "authorization_failed"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    SENSITIVE_DATA_DETECTED = "sensitive_data_detected"
    INJECTION_ATTEMPT = "injection_attempt"
    ENCODED_INJECTION_DECODED = "encoded_injection_decoded"
    OVERSIZE_INPUT_TRUNCATED = "oversize_input_truncated"
    UNICODE_EXPANSION = "unicode_expansion"


class SecuritySeverity(Enum):
    """Severity levels for security events."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """
    Core security event data structure.

    This is the canonical representation of a security event that can be
    serialized, stored, and processed by any component in the system.
    """
    timestamp: str
    event_id: str
    event_type: SecurityEventType
    severity: SecuritySeverity
    source: str
    input_preview: str
    input_hash: str
    context: Dict[str, Any] = field(default_factory=dict)
    detection_patterns: List[str] = field(default_factory=list)
    action: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "source": self.source,
            "input_preview": self.input_preview,
            "input_hash": self.input_hash,
            "context": self.context,
            "detection_patterns": self.detection_patterns,
            "action": self.action
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecurityEvent':
        """Create from dictionary for deserialization."""
        return cls(
            timestamp=data["timestamp"],
            event_id=data["event_id"],
            event_type=SecurityEventType(data["event_type"]),
            severity=SecuritySeverity(data["severity"]),
            source=data["source"],
            input_preview=data["input_preview"],
            input_hash=data["input_hash"],
            context=data.get("context", {}),
            detection_patterns=data.get("detection_patterns", []),
            action=data.get("action", "unknown")
        )

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> 'SecurityEvent':
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))


@dataclass
class RateLimitInfo:
    """Rate limiting information for security events."""
    source: str
    event_timestamps: List[float] = field(default_factory=list)
    window_seconds: int = 300  # 5 minutes
    threshold: int = 100  # events per window

    def is_rate_limited(self, current_time: float) -> bool:
        """Check if source has exceeded rate limits."""
        # Clean old entries
        cutoff_time = current_time - self.window_seconds
        self.event_timestamps = [
            ts for ts in self.event_timestamps if ts > cutoff_time
        ]

        # Check current rate
        self.event_timestamps.append(current_time)

        return len(self.event_timestamps) > self.threshold


@dataclass
class EventCorrelation:
    """Event correlation data for attack pattern analysis."""
    event_type: str
    source: str
    count: int = 0
    first_seen: str = ""
    last_seen: str = ""
    severity_levels: Set[str] = field(default_factory=set)

    def update(self, event: SecurityEvent) -> None:
        """Update correlation data with new event."""
        self.count += 1
        self.last_seen = event.timestamp
        self.severity_levels.add(event.severity.value)

        if not self.first_seen:
            self.first_seen = event.timestamp


@dataclass
class SecurityMetrics:
    """Security metrics for monitoring and reporting."""
    total_events: int = 0
    events_by_type: Dict[str, int] = field(default_factory=dict)
    active_sources: int = 0
    rate_limited_sources: int = 0
    correlation_patterns: int = 0
    last_activity: Optional[str] = None


class SecurityEventHandler(Protocol):
    """
    Protocol for security event handling.

    This defines the interface that any security event handler must implement.
    Components can depend on this protocol rather than concrete implementations.
    """

    def handle_security_event(self, event: SecurityEvent) -> None:
        """Handle a security event."""
        ...

    def get_metrics(self) -> SecurityMetrics:
        """Get current security metrics."""
        ...


class SecurityEventClassifier(ABC):
    """
    Abstract base class for security event classification.

    This provides the interface for classifying security events without
    depending on concrete implementations.
    """

    @abstractmethod
    def classify_attack(self, input_text: str) -> SecurityEventType:
        """Classify the type of attack based on input patterns."""
        pass

    @abstractmethod
    def determine_severity(self, event_type: SecurityEventType, context: Dict[str, Any]) -> SecuritySeverity:
        """Determine severity level based on event type and context."""
        pass


class SecurityEventLogger(ABC):
    """
    Abstract base class for security event logging.

    This provides the interface for logging security events without
    depending on concrete implementations.
    """

    @abstractmethod
    def log_event(self, event: SecurityEvent) -> None:
        """Log a security event."""
        pass

    @abstractmethod
    def create_security_event(self,
                            event_type: SecurityEventType,
                            severity: SecuritySeverity,
                            input_text: str,
                            source: str = "unknown",
                            context: Optional[Dict[str, Any]] = None) -> SecurityEvent:
        """Create a security event with proper structure."""
        pass


class SecurityEventFilter(ABC):
    """
    Abstract base class for security event filtering.

    This provides the interface for filtering security events without
    depending on concrete implementations.
    """

    @abstractmethod
    def should_log_event(self, event: SecurityEvent) -> bool:
        """Determine if an event should be logged."""
        pass

    @abstractmethod
    def filter_sensitive_data(self, text: str) -> str:
        """Filter sensitive data from text."""
        pass


# Event factory functions for creating common events
def create_security_event(event_type: SecurityEventType,
                         severity: SecuritySeverity,
                         input_text: str,
                         source: str = "unknown",
                         context: Optional[Dict[str, Any]] = None,
                         event_id: Optional[str] = None) -> SecurityEvent:
    """
    Factory function to create a security event.

    Args:
        event_type: Type of security event
        severity: Severity level
        input_text: The input that triggered the event
        source: Source identifier
        context: Additional context
        event_id: Optional event ID (will be generated if not provided)

    Returns:
        SecurityEvent instance
    """
    import hashlib
    import time

    if event_id is None:
        content = f"{input_text}:{source}:{time.time()}"
        event_id = hashlib.sha256(content.encode()).hexdigest()[:16]

    return SecurityEvent(
        timestamp=datetime.now(timezone.utc).isoformat(),
        event_id=event_id,
        event_type=event_type,
        severity=severity,
        source=source,
        input_preview=input_text[:100],
        input_hash=hashlib.sha256(input_text.encode()).hexdigest()[:16],
        context=context or {}
    )


def create_rate_limit_event(source: str, original_input: str) -> SecurityEvent:
    """Create a rate limit exceeded event."""
    return create_security_event(
        event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
        severity=SecuritySeverity.CRITICAL,
        input_text=f"Rate limit exceeded for source: {source}",
        source=source,
        context={"original_input": original_input[:100]}
    )


# Utility functions for event processing
def sanitize_input_preview(input_text: str, max_length: int = 100) -> str:
    """
    Sanitize input preview for logging to prevent injection.

    This is a minimal sanitization function specifically for creating
    safe input previews in security events. It's designed to be
    dependency-free to avoid circular imports.

    Args:
        input_text: Input text to sanitize
        max_length: Maximum length for preview

    Returns:
        Sanitized input preview
    """
    import re

    # Truncate
    sanitized = input_text[:max_length]

    # Remove control characters that could cause log injection
    sanitized = re.sub(r'[\n\r\t]', ' ', sanitized)

    # Mark potential log level injection patterns
    sanitized = re.sub(
        r'\[(ERROR|WARN|INFO|DEBUG|CRITICAL)\]',
        r'[\1_LEVEL_BLOCKED]',
        sanitized,
        flags=re.IGNORECASE
    )

    # Block timestamp patterns
    sanitized = re.sub(
        r'(2024-\d{2}-\d{2}|FAKE_EVENT)',
        r'[\1_BLOCKED]',
        sanitized
    )

    return sanitized