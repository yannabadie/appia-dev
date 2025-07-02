import os
from unittest import mock
from jarvys_dev.tools.github_tools import github_create_issue


@mock.patch("jarvys_dev.tools.github_tools.Github")
def test_create_issue_new(mock_github):
    fake_repo = mock.Mock()
    fake_repo.get_issues.return_value = []
    fake_issue = mock.Mock(number=123)
    fake_repo.create_issue.return_value = fake_issue
    mock_github.return_value.get_repo.return_value = fake_repo

    os.environ["GH_TOKEN"] = "x"
    os.environ["GH_REPO"]  = "owner/repo"

    num = github_create_issue("Hello", "Body")
    assert num == 123
    fake_repo.create_issue.assert_called_once()


@mock.patch("jarvys_dev.tools.github_tools.Github")
def test_create_issue_duplicate(mock_github):
    dup = mock.Mock(title="Hello", number=99)
    fake_repo = mock.Mock()
    fake_repo.get_issues.return_value = [dup]
    mock_github.return_value.get_repo.return_value = fake_repo

    os.environ["GH_TOKEN"] = "x"
    os.environ["GH_REPO"]  = "owner/repo"

    num = github_create_issue("Hello")
    assert num == 99
    fake_repo.create_issue.assert_not_called()
