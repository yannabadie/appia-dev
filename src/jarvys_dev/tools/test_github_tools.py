from typing import Dict, List, Any, Optional
import json
import sys
import os
# src/jarvys_dev/tools/test_github_tools.py
from unittest import mock

import pytest

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
    url = github_create_issue("Titre A", "Corps")
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
    url = github_create_issue("Titre B")
    assert url == "https://example.com/99"
    repo.create_issue.assert_not_called()


@mock.patch("jarvys_dev.tools.github_tools.Github")
def test_create_pull_request(MockGh, monkeypatch):
    repo = mock.Mock()
    repo.default_branch = "feat"
    repo.create_pull.return_value.html_url = "https://example.com/pr1"
    MockGh.return_value.get_repo.return_value = repo

    monkeypatch.setenv("GH_TOKEN", "tok")
    monkeypatch.setenv("GH_REPO", "owner/repo")
    from jarvys_dev.tools.github_tools import create_pull_request

    url = create_pull_request("PR", head="feat")
    assert url.endswith("pr1")
    repo.create_pull.assert_called_once_with(
        title="PR", body="", head="feat", base="dev"
    )


@mock.patch("jarvys_dev.tools.github_tools.Github")
def test_create_pull_request_wrong_base(MockGh, monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "tok")
    monkeypatch.setenv("GH_REPO", "owner/repo")
    from jarvys_dev.tools.github_tools import create_pull_request

    with pytest.raises(ValueError):
        create_pull_request("bad", base="main")
