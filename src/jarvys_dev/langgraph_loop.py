"""LangGraph-based observe-plan-act-reflect loop."""

from __future__ import annotations

import json
import logging
from typing import TypedDict

from langgraph.graph import END, StateGraph

from .main import confidence_score, send_to_jarvys_ai
from .tools.memory import upsert_embedding

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    planned = f"Handle {state['observation']}"
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
    compiled = build_graph().compile()
    state: LoopState = {}
    for _ in range(steps):
        state = compiled.invoke(state)
        if confidence_score() < 0.85:
            state["waiting_for_human_review"] = True
            break
    return state


__all__ = ["run_loop", "build_graph", "LoopState"]

if __name__ == "__main__":  # pragma: no cover
    final_state = run_loop(steps=1)
    print(json.dumps(final_state, indent=2))
