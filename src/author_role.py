import math
import sys
import uuid
from typing import override
from datetime import datetime


class AuthorRole:
    def __init__(
        self,
        unit_id: int,
        comment_id: uuid.UUID,
        author_name: str,
        role: str,
        severity: float,
        timestamp: datetime | None,
    ) -> None:
        self.unit_id: int = unit_id
        self.comment_id: uuid.UUID = comment_id
        self.author_name: str = author_name
        self.severity = severity
        self.role = role
        self.timestamp: datetime | None = timestamp

    @property
    def role(self) -> str:
        return self._role

    @role.setter
    def role(self, value: str) -> None:
        self._role: str = value

    @property
    def severity(self) -> float:
        return self._severity

    @severity.setter
    def severity(self, value: float) -> None:
        if 0 <= value <= 3.0:
            self._severity = value
        else:
            raise ValueError("severity must be between 0.0 to 3.0 (inclusive)")

    def compute_time_delta(self, other: "AuthorRole") -> float:
        if other.timestamp is not None and self.timestamp is not None:
            delta = (self.timestamp - other.timestamp).total_seconds()
            # The math.log function defaults to natural log.
            try:
                log_delta = math.log(1.0 + delta)
            except ValueError:
                raise ValueError(f"Time delta value is {delta}")
            return log_delta
        else:
            return 0.0

    def should_add_edge(self, other: "AuthorRole") -> bool:
        CUTOFF = sys.maxsize
        return True

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AuthorRole):
            return NotImplemented
        return self.author_name == other.author_name and self.role == other.role

    @override
    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @override
    def __hash__(self) -> int:
        return hash((self.author_name, self.role))

    @override
    def __str__(self) -> str:
        return str({"author_name": self.author_name, "role": self.role})

    @override
    def __repr__(self) -> str:
        return self.__str__()
