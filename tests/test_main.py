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
    assert "from_jarvys_ai" in kwargs["labels"]
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
