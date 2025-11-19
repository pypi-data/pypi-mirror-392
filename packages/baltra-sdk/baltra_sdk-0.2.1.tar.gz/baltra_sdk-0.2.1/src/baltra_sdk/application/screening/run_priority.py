from __future__ import annotations

from typing import Optional


def should_cancel_active_run(active_priority: Optional[str], incoming_priority: Optional[str]) -> bool:
    """Return True when the active OpenAI run should be canceled before processing the incoming batch."""

    # Text runs never take priority: any new message should cancel them immediately.
    if active_priority == "text_grouped":
        return True

    # Interactive runs stay alive unless we cannot determine their priority.
    if active_priority == "interactive_solo":
        return False

    # If the currently active priority is unknown (None), cancel whenever an interactive arrives.
    if incoming_priority == "interactive_solo":
        return True

    # Otherwise, keep the active run.
    return False
