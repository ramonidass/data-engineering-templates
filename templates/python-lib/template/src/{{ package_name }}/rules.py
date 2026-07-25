"""Composable business rules for domain-heavy coding exercises."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class RuleViolation:
    code: str
    message: str


@dataclass(frozen=True)
class Rule(Generic[T]):  # noqa: UP046 - supports generated projects on Python 3.11
    """A named predicate; valid values produce no violation."""

    code: str
    message: str
    is_valid: Callable[[T], bool]

    def evaluate(self, value: T) -> RuleViolation | None:
        if self.is_valid(value):
            return None
        return RuleViolation(code=self.code, message=self.message)


def evaluate_rules(  # noqa: UP047 - supports generated projects on Python 3.11
    value: T, rules: Iterable[Rule[T]]
) -> list[RuleViolation]:
    return [violation for rule in rules if (violation := rule.evaluate(value))]
