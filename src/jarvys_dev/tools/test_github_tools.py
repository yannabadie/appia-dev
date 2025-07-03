# src/jarvys_dev/tools/test_github_tools.py
from unittest import mock

from jarvys_dev.tools.github_tools import github_create_issue


@mock.patch("jarvys_dev.tools.github_tools.Github")
def test_create_issue_new(MockGh, monkeypatch):
    """Crée une issue quand aucune n’existe."""
    repo = mock.Mock()
    repo.get_issues.return_value = []
    repo.create_issue.return_value.html_url = "https://example.com/42"
    MockGh.return_value.get_repo.return_value = repo

    monkeypatch.setenv("GH_TOKEN", "token")
    monkeypatch.setenv("GH_REPO", "owner/repo")
    url = github_create_issue("Titre A", "Corps", repo_fullname="owner/repo")
    assert url.endswith("/42")
    repo.create_issue.assert_called_once()


@mock.patch("jarvys_dev.tools.github_tools.Github")
def test_create_issue_duplicate(MockGh, monkeypatch):
    """Renvoie l’URL de l’issue existante si le titre est déjà utilisé."""
    existing = mock.Mock(html_url="https://example.com/99", title="Titre B")
    repo = mock.Mock()
    repo.get_issues.return_value = [existing]
    MockGh.return_value.get_repo.return_value = repo

    monkeypatch.setenv("GH_TOKEN", "token")
    monkeypatch.setenv("GH_REPO", "owner/repo")
    url = github_create_issue("Titre B", repo_fullname="owner/repo")
    assert url == "https://example.com/99"
    repo.create_issue.assert_not_called()
