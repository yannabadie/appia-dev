from typing import Dict, List, Any, Optional
import json
import sys
import os
import subprocess


def test_mkdocs_build(tmp_path):
    build_dir = tmp_path / "site"
    subprocess.check_call(
        [
            "mkdocs",
            "build",
            "-q",
            "-d",
            str(build_dir),
        ]
    )
    assert (build_dir / "index.html").exists()
