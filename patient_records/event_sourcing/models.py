"""Event sourcing models module."""

# Remove duplicate EventStore model and import from audit
from ..models.audit.events import EventStore

__all__ = ['EventStore']