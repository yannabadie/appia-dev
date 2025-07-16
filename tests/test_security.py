from typing import Dict, List, Any, Optional
import json
import sys
import os
import importlib
import logging


def test_secret_filter_masks_tokens(monkeypatch, caplog):
    monkeypatch.setenv("SECRET_ACCESS_TOKEN", "tok")
    caplog.set_level(logging.INFO)
    module = importlib.reload(
        importlib.import_module(
            "jarvys_dev.langgraph_loop",
        ),
    )
    module.logger = logging.getLogger(__name__).info("should hide tok value")
    assert "tok" not in caplog.text
