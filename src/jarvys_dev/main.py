"""Main control loop for JARVYS_DEV."""

from __future__ import annotations

import json

from langgraph.graph import END, StateGraph

from .tools.github_tools import github_create_issue
from .tools.memory import upsert_embedding

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
        labels=["from_jarvys_ai"],
        repo_fullname=repo_fullname,
    )


# ---------------------------------------------------------------------------
# Simple observe-plan-act-reflect loop


class LoopState(dict):
    """Mutable state for the control loop."""


def observe(state: LoopState) -> LoopState:
    state["observation"] = state.get("observation", "initial")
    return state


def plan(state: LoopState) -> LoopState:
    state["plan"] = f"Handle: {state['observation']}"
    return state


def act(state: LoopState) -> LoopState:
    task = {"title": "Automated task", "detail": state["plan"]}
    url = send_to_jarvys_ai(task)
    state["action_url"] = url
    return state


def reflect(state: LoopState) -> LoopState:
    txt = json.dumps(state)
    upsert_embedding(txt)
    state["reflected"] = True
    return state


def run_once() -> LoopState:
    """Run a single observe-plan-act-reflect cycle."""
    sg = StateGraph(LoopState)
    sg.add_node("observe", observe)
    sg.add_node("plan", plan)
    sg.add_node("act", act)
    sg.add_node("reflect", reflect)
    sg.add_edge("observe", "plan")
    sg.add_edge("plan", "act")
    sg.add_edge("act", "reflect")
    sg.add_edge("reflect", END)
    graph = sg.compile()
    return graph.invoke(LoopState())


__all__ = [
    "send_to_jarvys_ai",
    "run_once",
]
