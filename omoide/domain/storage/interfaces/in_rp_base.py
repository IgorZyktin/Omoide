"""Base repository class.
"""
import abc
from typing import Any


# TODO - write custom wrapper for the db
class AbsBaseRepository(abc.ABC):
    """Base repository class."""

    def __init__(self, db: Any) -> None:
        """Initialize instance."""
        self.db = db

    def transaction(self) -> Any:
        """Start transaction."""
        return self.db.transaction()
