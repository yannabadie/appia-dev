"""Main control loop for JARVYS_DEV."""

from __future__ import annotations

import json
import os

from .tools.github_tools import github_create_issue
from .tools.memory import upsert_embedding

# FastAPI app export
try:
    # Try different import paths
    import os
    import sys

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    from app.main import app
except ImportError:
    try:
        from app.main import app
    except ImportError:
        app  # To be initialized

# ---------------------------------------------------------------------------
# Inter-agent communication


def send_to_jarvys_ai(
    task_dict: dict,
    repo_fullname: str | None = None,
) -> str:
    """Create an issue for JARVYS_AI with JSON payload."""
    body = f"```json\n{json.dumps(task_dict, indent=2)}\n```"
    return github_create_issue(
        title=task_dict.get("title", "Task from JARVYS_DEV"),
        body=body,
        labels=["from_jarvys_dev"],
        repo_fullname=repo_fullname,
    )


# ---------------------------------------------------------------------------
# Simple observe-plan-act-reflect loop


class LoopState(dict):
    """Mutable state for the control loop."""


def observe(state: LoopState) -> LoopState:
    return {"observation": state.get("observation", "initial")}


def plan(state: LoopState) -> LoopState:
    return {"plan": f"Handle: {state['observation']}"}


def act(state: LoopState) -> LoopState:
    task = {"title": "Automated task", "detail": state["plan"]}
    url = send_to_jarvys_ai(task)
    return {"action_url": url}


def reflect(state: LoopState) -> LoopState:
    txt = json.dumps(state)
    upsert_embedding(txt)
    return {"reflected": True}


def run_once(state: LoopState | None = None) -> LoopState:
    """Run a single observe-plan-act-reflect cycle."""
    state = state or LoopState()
    state.update(observe(state))
    state.update(plan(state))
    state.update(act(state))
    state.update(reflect(state))
    return state


def confidence_score() -> float:
    """Return an external confidence score (env or default 1.0)."""
    return float(os.getenv("CONFIDENCE_SCORE", "1.0"))


def run_loop(steps: int = 1) -> LoopState:
    """Run multiple cycles and stop if confidence is too low."""
    state = LoopState()
    for _ in range(steps):
        state = run_once(state)
        if confidence_score() < 0.85:
            state["waiting_for_human_review"] = True
            break
    return state


__all__ = [
    "send_to_jarvys_ai",
    "run_once",
    "run_loop",
    "app",
]
