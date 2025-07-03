from unittest import mock


@mock.patch("jarvys_dev.langgraph_loop.upsert_embedding")
@mock.patch("jarvys_dev.langgraph_loop.send_to_jarvys_ai")
def test_run_loop_invokes_tools(send_issue, upsert, monkeypatch):
    send_issue.return_value = "url"
    monkeypatch.setenv("CONFIDENCE_SCORE", "1.0")
    from jarvys_dev.langgraph_loop import run_loop

    state = run_loop(steps=1)
    assert state["action_url"] == "url"
    send_issue.assert_called_once()
    upsert.assert_called_once()
    assert state["reflected"] is True


@mock.patch("jarvys_dev.langgraph_loop.upsert_embedding")
@mock.patch("jarvys_dev.langgraph_loop.send_to_jarvys_ai")
def test_run_loop_flags_waiting(send_issue, _upsert, monkeypatch):
    send_issue.return_value = "url"
    monkeypatch.setenv("CONFIDENCE_SCORE", "0.5")
    from jarvys_dev.langgraph_loop import run_loop

    state = run_loop(steps=2)
    assert state["waiting_for_human_review"] is True
    send_issue.assert_called_once()
