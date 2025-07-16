"""Test environment setup validation for JARVYS ecosystem."""

import os
import platform
import subprocess
import sys
from pathlib import Path

import pytest


class TestEnvironmentSetup:
    """Test environment setup and validation."""

    def test_python_version(self):
        """Test that Python version meets requirements."""
        version = sys.version_info
        assert version.major == 3, f"Python 3 required, got {version.major}"
        assert (
            version.minor >= 12
        ), f"Python 3.12+ required, got {version.major}.{version.minor}"

    def test_platform_compatibility(self):
        """Test platform compatibility."""
        system = platform.system()
        assert system in [
            "Linux",
            "Darwin",
            "Windows",
        ], f"Unsupported platform: {system}"

    def test_required_environment_variables(self):
        """Test that required environment variables are available."""
        # These are the core secrets needed for JARVYS operation
        required_vars = [
            "OPENAI_API_KEY",
            "SUPABASE_URL",
            "SUPABASE_KEY",
        ]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
<<<<<<< HEAD
            pytest.skip(f"Missing environment variables: {', '.join(missing_vars)}")
=======
            pytest.skip(
                f"Missing environment variables: {', '.join(missing_vars)}"
            )
>>>>>>> origin/main

    def test_optional_environment_variables(self):
        """Test optional environment variables for full functionality."""
        optional_vars = [
            "GITHUB_TOKEN",
            "GEMINI_API_KEY",
            "ANTHROPIC_API_KEY",
            "GCP_SA_JSON",
            "SUPABASE_PROJECT_REF",
            "SUPABASE_SERVICE_ROLE",
        ]

        available_vars = []
        missing_vars = []

        for var in optional_vars:
            if os.getenv(var):
                available_vars.append(var)
            else:
                missing_vars.append(var)

        # Log what's available vs missing for information
        # In testing environments, it's OK to have no optional vars

        # Log what's available vs missing
        print(f"Available optional vars: {available_vars}")
        print(f"Missing optional vars: {missing_vars}")

    def test_core_dependencies_importable(self):
        """Test that core dependencies can be imported."""
        core_deps = [
            "requests",
            "openai",
            "supabase",
            "fastapi",
            "uvicorn",
            "pytest",
            "github",  # PyGithub
        ]

        import_errors = []
        for dep in core_deps:
            try:
                __import__(dep)
            except ImportError as e:
                import_errors.append((dep, str(e)))

<<<<<<< HEAD
        assert not import_errors, f"Failed to import dependencies: {import_errors}"
=======
        assert (
            not import_errors
        ), f"Failed to import dependencies: {import_errors}"
>>>>>>> origin/main

    def test_jarvys_dev_module_structure(self):
        """Test that JARVYS dev module has correct structure."""
        src_path = Path(__file__).parent.parent / "src" / "jarvys_dev"
        assert src_path.exists(), f"JARVYS dev source not found at {src_path}"

        expected_files = [
            "__init__.py",
            "main.py",
            "multi_model_router.py",
            "langgraph_loop.py",
        ]

        missing_files = []
        for file in expected_files:
            if not (src_path / file).exists():
                missing_files.append(file)

        assert not missing_files, f"Missing core files: {missing_files}"

    def test_tools_module_structure(self):
        """Test that tools module has correct structure."""
<<<<<<< HEAD
        tools_path = Path(__file__).parent.parent / "src" / "jarvys_dev" / "tools"
=======
        tools_path = (
            Path(__file__).parent.parent / "src" / "jarvys_dev" / "tools"
        )
>>>>>>> origin/main
        assert tools_path.exists(), f"Tools module not found at {tools_path}"

        expected_files = ["memory.py", "memory_infinite.py", "github_tools.py"]

        missing_files = []
        for file in expected_files:
            if not (tools_path / file).exists():
                missing_files.append(file)

        assert not missing_files, f"Missing tool files: {missing_files}"

    def test_config_files_present(self):
        """Test that configuration files are present."""
        project_root = Path(__file__).parent.parent
        config_files = [
            "pyproject.toml",
            "pytest.ini",
            ".pre-commit-config.yaml",
        ]

        missing_configs = []
        for config in config_files:
            if not (project_root / config).exists():
                missing_configs.append(config)

<<<<<<< HEAD
        assert not missing_configs, f"Missing configuration files: {missing_configs}"
=======
        assert (
            not missing_configs
        ), f"Missing configuration files: {missing_configs}"
>>>>>>> origin/main

    def test_poetry_environment(self):
        """Test that poetry environment is properly set up."""
        try:
            _result = subprocess.run(
                ["poetry", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
<<<<<<< HEAD
            assert result.returncode == 0, f"Poetry not available: {result.stderr}"
=======
            assert (
                result.returncode == 0
            ), f"Poetry not available: {result.stderr}"
>>>>>>> origin/main
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Poetry not available in environment")

    def test_git_availability(self):
        """Test that git is available."""
        try:
            _result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
<<<<<<< HEAD
            assert result.returncode == 0, f"Git not available: {result.stderr}"
=======
            assert (
                result.returncode == 0
            ), f"Git not available: {result.stderr}"
>>>>>>> origin/main
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Git not available in environment")

    def test_project_structure_integrity(self):
        """Test overall project structure integrity."""
        project_root = Path(__file__).parent.parent

        expected_dirs = ["src", "tests", ".github", "supabase"]

        missing_dirs = []
        for directory in expected_dirs:
            if not (project_root / directory).exists():
                missing_dirs.append(directory)

        assert not missing_dirs, f"Missing project directories: {missing_dirs}"


class TestGitHubWorkflowStructure:
    """Test GitHub workflow structure."""

    def test_workflows_directory_exists(self):
        """Test that workflows directory exists."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        assert workflows_path.exists(), "GitHub workflows directory not found"

    def test_core_workflows_present(self):
        """Test that core workflows are present."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"

        expected_workflows = [
            "ci.yml",
            "agent.yml",
            "jarvys-cloud.yml",
            "model-detection.yml",
        ]

        missing_workflows = []
        for workflow in expected_workflows:
            if not (workflows_path / workflow).exists():
                missing_workflows.append(workflow)

<<<<<<< HEAD
        assert not missing_workflows, f"Missing core workflows: {missing_workflows}"
=======
        assert (
            not missing_workflows
        ), f"Missing core workflows: {missing_workflows}"
>>>>>>> origin/main


class TestSupabaseStructure:
    """Test Supabase structure."""

    def test_supabase_directory_exists(self):
        """Test that supabase directory exists."""
        supabase_path = Path(__file__).parent.parent / "supabase"
        assert supabase_path.exists(), "Supabase directory not found"

    def test_supabase_config_files(self):
        """Test that supabase configuration files exist."""
        supabase_path = Path(__file__).parent.parent / "supabase"

        expected_files = ["config.toml", "schema.sql"]

        missing_files = []
        for file in expected_files:
            if not (supabase_path / file).exists():
                missing_files.append(file)

        assert not missing_files, f"Missing Supabase files: {missing_files}"
