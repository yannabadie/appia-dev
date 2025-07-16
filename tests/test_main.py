from typing import Dict, List, Any, Optional
import json
import sys
import os
from unittest import mock

from jarvys_dev.main import send_to_jarvys_ai


@mock.patch("jarvys_dev.main.github_create_issue")
def test_send_to_jarvys_ai_creates_issue(create_issue):
    create_issue.return_value = "https://example.com/1"
    task = {"title": "Do", "data": {"a": 1}}
    url = send_to_jarvys_ai(task)
    assert url.endswith("/1")
    create_issue.assert_called_once()
    _, kwargs = create_issue.call_args
    assert "from_jarvys_dev" in kwargs["labels"]
    assert "```json" in kwargs["body"]


@mock.patch("jarvys_dev.tools.github_tools.OpenAI")
def test_copilot_generate_patch(OpenAI):
    dummy = mock.Mock()
    dummy.chat.completions.create.return_value.choices = [
        mock.Mock(
            message=mock.Mock(
                content='{"files": {"a.py": "new"}, "message": "msg"}'
            )  # noqa: E501
        )
    ]
    OpenAI.return_value = dummy

    from jarvys_dev.tools.github_tools import copilot_generate_patch

    with mock.patch.dict(os.environ, {"GH_TOKEN": "x", "OPENAI_API_KEY": "k"}):
        files, msg = copilot_generate_patch({"a.py": "old"}, "prompt")
    assert files == {"a.py": "new"}
    assert msg == "msg"


@mock.patch("jarvys_dev.main.upsert_embedding")
@mock.patch("jarvys_dev.main.send_to_jarvys_ai")
def test_run_loop_flags_waiting(send_issue, _upsert):
    send_issue.return_value = "url"
    with mock.patch.dict(os.environ, {"CONFIDENCE_SCORE": "0.8"}):
        from jarvys_dev.main import run_loop

        state = run_loop(steps=2)
    assert state["waiting_for_human_review"] is True
    send_issue.assert_called_once()


@mock.patch("jarvys_dev.tools.github_tools.subprocess.check_call")
@mock.patch("jarvys_dev.tools.github_tools.subprocess.check_output")
@mock.patch("jarvys_dev.tools.github_tools.copilot_generate_patch")
def test_copilot_commit_patch(gen, chk_out, chk_call, tmp_path, monkeypatch):
    gen.return_value = ({"f.txt": "new"}, "msg")
    chk_out.return_value = b"dev\n"
    from jarvys_dev.tools.github_tools import copilot_commit_patch

    monkeypatch.chdir(tmp_path)
    (tmp_path / "f.txt").write_text("old")
    message = copilot_commit_patch({"f.txt": "old"}, "prompt")
    assert message == "msg"
    chk_call.assert_any_call(["git", "add", "f.txt"])
    chk_call.assert_any_call(["git", "commit", "-m", "msg"])
