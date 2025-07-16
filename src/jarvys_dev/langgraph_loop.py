"""LangGraph-based observe-plan-act-reflect loop."""

from __future__ import annotations

import json
import logging
import os
from typing import TypedDict

from langgraph.graph import END, StateGraph

from .main import confidence_score, send_to_jarvys_ai
from .multi_model_router import MultiModelRouter
from .tools.memory import upsert_embedding

logger = logging.getLogger(__name__)

SECRET_ENV_KEYS = [
    "GH_TOKEN",
    "SECRET_ACCESS_TOKEN",
    "SUPABASE_KEY",
]


class _SecretFilter(logging.Filter):
    """Mask configured secrets in log messages."""

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover
        msg = record.getMessage()
        for key in SECRET_ENV_KEYS:
            val = os.getenv(key)
            if val and val in msg:
                record.msg = record.msg.replace(val, "***")
        return True


logger.addFilter(_SecretFilter())

_router = MultiModelRouter()

CONFIDENCE_THRESHOLD = 0.85


class LoopState(TypedDict, total=False):
    """State handled by the LangGraph loop."""

    observation: str
    plan: str
    action_url: str
    reflected: bool
    waiting_for_human_review: bool


def observe(state: LoopState) -> LoopState:
    observation = state.get("observation", "initial observation")
    logger.info("observe: %s", observation)
    return {"observation": observation}


def plan(state: LoopState) -> LoopState:
    prompt = f"Plan how to handle: {state['observation']}"
    planned = _router.generate(prompt, task_type="reasoning")
    logger.info("plan: %s", planned)
    return {"plan": planned}


def act(state: LoopState) -> LoopState:
    task = {"title": "Automated task", "detail": state["plan"]}
    url = send_to_jarvys_ai(task)
    logger.info("act: created %s", url)
    return {"action_url": url}


def reflect(state: LoopState) -> LoopState:
    upsert_embedding(json.dumps(state))
    logger.info("reflect: state stored")
    return {"reflected": True}


def build_graph() -> StateGraph:
    graph = StateGraph(LoopState)
    graph.add_node("observe_step", observe)
    graph.add_node("plan_step", plan)
    graph.add_node("act_step", act)
    graph.add_node("reflect_step", reflect)
    graph.set_entry_point("observe_step")
    graph.add_edge("observe_step", "plan_step")
    graph.add_edge("plan_step", "act_step")
    graph.add_edge("act_step", "reflect_step")
    graph.add_edge("reflect_step", END)
    return graph


def run_loop(steps: int = 1) -> LoopState:
    """Execute the loop for the given number of ``steps``.

    Parameters
    ----------
    steps:
        Number of iterations to execute.

    Returns
    -------
    LoopState
        Final state after execution. The state includes
        ``waiting_for_human_review`` if ``confidence_score``
        falls below :data:`CONFIDENCE_THRESHOLD`.
    """
    compiled = build_graph().compile()
    state: LoopState = {}
    for _ in range(steps):
        state = compiled.invoke(state)
        if confidence_score() < CONFIDENCE_THRESHOLD:
            state["waiting_for_human_review"] = True
            break
    if _router.benchmarks:
        logger.info("benchmarks: %s", _router.benchmarks[-1])
    return state


class JarvysLoop:
    """Minimaliste wrapper pour le loop LangGraph."""

    def __init__(self):
        """Initialize the loop."""
<<<<<<< HEAD
        pass

    def run(self, initial_state):
        # This is a placeholder for the actual loop execution
        pass
=======

    def run(self, steps: int = 1) -> dict:
        """Run the loop and delegate to run_loop function."""
        return run_loop(steps)
>>>>>>> origin/main


__all__ = ["run_loop", "build_graph", "LoopState", "JarvysLoop"]

if __name__ == "__main__":  # pragma: no cover
    final_state = run_loop(steps=1)
    print(json.dumps(final_state, indent=2))
