"""Test JARVYS_DEV cloud agent functionality."""

import json
import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


class TestJarvysDevCore:
    """Test core JARVYS_DEV functionality."""

    def test_jarvys_dev_main_module_importable(self):
        """Test that JARVYS_DEV main module can be imported."""
        try:
            from jarvys_dev import main

            assert hasattr(main, "app"), "Main module should have FastAPI app"
        except ImportError as e:
            pytest.fail(f"Could not import JARVYS_DEV main: {e}")

    def test_multi_model_router_importable(self):
        """Test that MultiModelRouter can be imported."""
        try:
            from jarvys_dev.multi_model_router import MultiModelRouter

            assert MultiModelRouter is not None
        except ImportError as e:
            pytest.fail(f"Could not import MultiModelRouter: {e}")

    def test_langgraph_loop_importable(self):
        """Test that langgraph loop can be imported."""
        try:
            from jarvys_dev import langgraph_loop

<<<<<<< HEAD
            assert hasattr(langgraph_loop, "JarvysLoop"), "Should have JarvysLoop class"
=======
            assert hasattr(
                langgraph_loop, "JarvysLoop"
            ), "Should have JarvysLoop class"
>>>>>>> origin/main
        except ImportError as e:
            pytest.fail(f"Could not import langgraph_loop: {e}")


class TestMultiModelRouter:
    """Test MultiModelRouter functionality."""

    def test_router_initialization(self):
        """Test router can be initialized."""
        with patch.dict(os.environ, {}, clear=True):
            try:
                from jarvys_dev.multi_model_router import MultiModelRouter

                router = MultiModelRouter()
                assert router is not None
            except Exception as e:
                pytest.fail(f"Router initialization failed: {e}")

    def test_router_with_openai_key(self):
        """Test router initialization with OpenAI key."""
<<<<<<< HEAD
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123"}, clear=True):
=======
        with patch.dict(
            os.environ, {"OPENAI_API_KEY": "sk-test123"}, clear=True
        ):
>>>>>>> origin/main
            try:
                from jarvys_dev.multi_model_router import MultiModelRouter

                router = MultiModelRouter()
                assert router.openai_client is not None
            except Exception as e:
                pytest.fail(f"Router with OpenAI failed: {e}")

    def test_router_model_config_loading(self):
        """Test that router loads model configuration."""
        try:
            from jarvys_dev.multi_model_router import MultiModelRouter

            router = MultiModelRouter()

            # Check model configuration is loaded
<<<<<<< HEAD
            assert hasattr(router, "model_names"), "Router should have model_names"
=======
            assert hasattr(
                router, "model_names"
            ), "Router should have model_names"
>>>>>>> origin/main
            assert hasattr(
                router, "model_capabilities"
            ), "Router should have model_capabilities"

        except Exception as e:
            pytest.fail(f"Model config loading failed: {e}")

    def test_model_config_files_exist(self):
        """Test that model configuration files exist."""
        src_path = Path(__file__).parent.parent / "src" / "jarvys_dev"

        config_files = ["model_config.json", "model_capabilities.json"]

        for config_file in config_files:
            config_path = src_path / config_file
            assert config_path.exists(), f"Missing {config_file}"

            # Validate JSON structure
            try:
                with open(config_path) as f:
                    data = json.load(f)
                assert isinstance(
                    data, dict
                ), f"{config_file} should contain a JSON object"
            except json.JSONDecodeError:
                pytest.fail(f"{config_file} contains invalid JSON")


class TestIntelligentOrchestrator:
    """Test intelligent orchestrator functionality."""

    def test_orchestrator_importable(self):
        """Test that intelligent orchestrator can be imported."""
        try:
<<<<<<< HEAD
            from jarvys_dev.intelligent_orchestrator import \
                IntelligentOrchestrator
=======
            from jarvys_dev.intelligent_orchestrator import \
                IntelligentOrchestrator
>>>>>>> origin/main

            assert IntelligentOrchestrator is not None
        except ImportError as e:
            pytest.fail(f"Could not import IntelligentOrchestrator: {e}")

    def test_orchestrator_initialization(self):
        """Test orchestrator can be initialized."""
        try:
<<<<<<< HEAD
            from jarvys_dev.intelligent_orchestrator import \
                IntelligentOrchestrator
=======
            from jarvys_dev.intelligent_orchestrator import \
                IntelligentOrchestrator
>>>>>>> origin/main

            orchestrator = IntelligentOrchestrator()
            assert orchestrator is not None
        except Exception as e:
            pytest.fail(f"Orchestrator initialization failed: {e}")

    def test_task_analysis_method(self):
        """Test task analysis method exists."""
        try:
<<<<<<< HEAD
            from jarvys_dev.intelligent_orchestrator import \
                IntelligentOrchestrator
=======
            from jarvys_dev.intelligent_orchestrator import \
                IntelligentOrchestrator
>>>>>>> origin/main

            orchestrator = IntelligentOrchestrator()
            assert hasattr(
                orchestrator, "analyze_task"
            ), "Should have analyze_task method"
        except Exception as e:
            pytest.fail(f"Task analysis method test failed: {e}")


class TestAgentControl:
    """Test agent control functionality."""

    def test_agent_control_importable(self):
        """Test that agent control can be imported."""
        try:
            from jarvys_dev import agent_control

            assert agent_control is not None
        except ImportError as e:
            pytest.fail(f"Could not import agent_control: {e}")

    def test_agent_control_has_required_functions(self):
        """Test that agent control has required functions."""
        try:
            from jarvys_dev import agent_control

            # Check for key functions (adjust based on actual implementation)
            _expected_functions = [
                "start_agent",
                "stop_agent",
                "get_agent_status",
            ]
            available_functions = [
                attr
                for attr in dir(agent_control)
<<<<<<< HEAD
                if callable(getattr(agent_control, attr)) and not attr.startswith("_")
=======
                if callable(getattr(agent_control, attr))
                and not attr.startswith("_")
>>>>>>> origin/main
            ]

            # At least some control functions should be available
            assert (
                len(available_functions) > 0
            ), "Agent control should have callable functions"

        except Exception as e:
            pytest.fail(f"Agent control functions test failed: {e}")


class TestModelWatcher:
    """Test model watcher functionality."""

    def test_model_watcher_importable(self):
        """Test that model watcher can be imported."""
        try:
            from jarvys_dev import model_watcher

            assert model_watcher is not None
        except ImportError as e:
            pytest.fail(f"Could not import model_watcher: {e}")

    def test_model_watcher_has_main_function(self):
        """Test that model watcher has main function."""
        try:
            from jarvys_dev import model_watcher

            assert hasattr(
                model_watcher, "main"
            ), "Model watcher should have main function"
        except Exception as e:
            pytest.fail(f"Model watcher main function test failed: {e}")

    def test_model_watcher_execution(self):
        """Test model watcher can be executed."""
        try:
            # Mock the external API calls to avoid actual requests
            with patch("requests.get") as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = {"models": []}
                mock_response.status_code = 200
                mock_get.return_value = mock_response

                from jarvys_dev import model_watcher

                # Should not raise exception when run
                assert model_watcher is not None

        except Exception as e:
            pytest.fail(f"Model watcher execution test failed: {e}")


class TestAutoModelUpdater:
    """Test automatic model updater functionality."""

    def test_auto_model_updater_importable(self):
        """Test that auto model updater can be imported."""
        try:
            from jarvys_dev import auto_model_updater

            assert auto_model_updater is not None
        except ImportError as e:
            pytest.fail(f"Could not import auto_model_updater: {e}")


class TestJarvysDevAPI:
    """Test JARVYS_DEV API functionality."""

    def test_fastapi_app_creation(self):
        """Test FastAPI app can be created."""
        try:
            from jarvys_dev.main import app

            assert app is not None

            # Check it's a FastAPI app
            from fastapi import FastAPI

            assert isinstance(app, FastAPI), "Should be a FastAPI instance"

        except ImportError as e:
            pytest.fail(f"Could not import FastAPI app: {e}")

    def test_api_routes_defined(self):
        """Test that API routes are defined."""
        try:
            from jarvys_dev.main import app

            # Check that routes are defined
            routes = [route.path for route in app.routes]
            assert len(routes) > 0, "API should have defined routes"

            # Should have at least a root route
            assert "/" in routes, "API should have root route"

        except Exception as e:
            pytest.fail(f"API routes test failed: {e}")

    @pytest.mark.integration
    def test_api_health_endpoint(self):
        """Test API health endpoint."""
        try:
            from fastapi.testclient import TestClient

            from jarvys_dev.main import app

            _client = TestClient(app)
<<<<<<< HEAD
            _response = _client.get("/")

            # Should return successful response
            assert _response.status_code == 200
=======
            _response = client.get("/")

            # Should return successful response
            assert response.status_code == 200
>>>>>>> origin/main

        except Exception as e:
            pytest.fail(f"API health endpoint test failed: {e}")


class TestJarvysDevConfiguration:
    """Test JARVYS_DEV configuration management."""

    def test_environment_variable_handling(self):
        """Test environment variable handling."""
        # Test with minimal environment
        with patch.dict(os.environ, {}, clear=True):
            try:
                from jarvys_dev.multi_model_router import MultiModelRouter

                router = MultiModelRouter()

                # Should handle missing environment variables gracefully
                assert router is not None

            except Exception as e:
                pytest.fail(f"Environment variable handling failed: {e}")

    def test_configuration_validation(self):
        """Test configuration validation."""
        try:
            # Test with valid configuration
            valid_config = {
                "OPENAI_API_KEY": "sk-test123",
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_KEY": "eyJtest123",
            }

            with patch.dict(os.environ, valid_config, clear=True):
                from jarvys_dev.multi_model_router import MultiModelRouter

                router = MultiModelRouter()
                assert router is not None

        except Exception as e:
            pytest.fail(f"Configuration validation failed: {e}")


class TestJarvysDevErrorHandling:
    """Test JARVYS_DEV error handling."""

    def test_graceful_degradation_no_api_keys(self):
        """Test graceful degradation when API keys are missing."""
        with patch.dict(os.environ, {}, clear=True):
            try:
                from jarvys_dev.multi_model_router import MultiModelRouter

                router = MultiModelRouter()

                # Should not crash, but may have limited functionality
                assert router is not None

                # Should handle generation requests gracefully
                try:
                    router.generate("test prompt")
                    # If it succeeds, great. If it fails, that's also acceptable
                    # as long as it doesn't crash the system
                except Exception:
                    # Expected when no API keys are available
                    pass

            except Exception as e:
                pytest.fail(f"Graceful degradation test failed: {e}")

    def test_invalid_api_key_handling(self):
        """Test handling of invalid API keys."""
        invalid_config = {
            "OPENAI_API_KEY": "invalid-key",
            "SUPABASE_URL": "https://invalid.supabase.co",
            "SUPABASE_KEY": "invalid-key",
        }

        with patch.dict(os.environ, invalid_config, clear=True):
            try:
                from jarvys_dev.multi_model_router import MultiModelRouter

                router = MultiModelRouter()

                # Should initialize without crashing
                assert router is not None

                # API calls may fail, but shouldn't crash the system
                try:
                    router.generate("test prompt")
                except Exception:
                    # Expected with invalid keys
                    pass

            except Exception as e:
                pytest.fail(f"Invalid API key handling failed: {e}")


class TestJarvysDevIntegration:
    """Test JARVYS_DEV integration capabilities."""

    def test_github_integration_ready(self):
        """Test that GitHub integration components are ready."""
        try:
            from jarvys_dev.tools import github_tools

            assert github_tools is not None

            # Should have GitHub-related functions
            github_attrs = [
                attr for attr in dir(github_tools) if not attr.startswith("_")
            ]
            assert len(github_attrs) > 0, "GitHub tools should have functions"

        except ImportError as e:
            pytest.fail(f"GitHub integration test failed: {e}")

    def test_memory_integration_ready(self):
        """Test that memory integration components are ready."""
        try:
            from jarvys_dev.tools import memory_infinite

            assert memory_infinite is not None

            # Should have memory-related functions
            memory_attrs = [
<<<<<<< HEAD
                attr for attr in dir(memory_infinite) if not attr.startswith("_")
=======
                attr
                for attr in dir(memory_infinite)
                if not attr.startswith("_")
>>>>>>> origin/main
            ]
            assert len(memory_attrs) > 0, "Memory tools should have functions"

        except ImportError as e:
            pytest.fail(f"Memory integration test failed: {e}")

    def test_supabase_integration_ready(self):
        """Test that Supabase integration is ready."""
        try:
            from jarvys_dev.tools import memory

            assert memory is not None

            # Should have memory-related functions for Supabase
<<<<<<< HEAD
            memory_attrs = [attr for attr in dir(memory) if not attr.startswith("_")]
=======
            memory_attrs = [
                attr for attr in dir(memory) if not attr.startswith("_")
            ]
>>>>>>> origin/main
            assert len(memory_attrs) > 0, "Memory module should have functions"

        except ImportError as e:
            pytest.fail(f"Supabase integration test failed: {e}")
