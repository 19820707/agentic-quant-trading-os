"""Order management boundary.

Current implementation is limited to local deterministic state validation. It
does not submit, cancel, replace or execute orders.
"""

from .state_machine import (
    ALLOWED_TRANSITIONS,
    TERMINAL_STATUSES,
    OrderStateTransition,
    OrderStateTransitionError,
    allowed_next_statuses,
    assert_transition_allowed,
)

__all__ = [
    "ALLOWED_TRANSITIONS",
    "TERMINAL_STATUSES",
    "OrderStateTransition",
    "OrderStateTransitionError",
    "allowed_next_statuses",
    "assert_transition_allowed",
]
