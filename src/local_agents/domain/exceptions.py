class DomainError(Exception):
    """Base error for domain rules."""


class PolicyViolation(DomainError):
    """Action blocked by privacy or approval policy."""


class PathNotAllowed(DomainError):
    """Filesystem path is outside configured allowlist roots."""
