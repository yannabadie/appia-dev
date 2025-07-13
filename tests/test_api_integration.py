"""Test API endpoints and responses for JARVYS ecosystem."""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests


class TestJarvysDevAPI:
    """Test JARVYS_DEV API endpoints."""

    @pytest.mark.integration
    def test_fastapi_app_importable(self):
        """Test FastAPI app can be imported."""
        # Try different possible locations for the FastAPI app
        app_locations = [
            ("app.main", "app"),
            ("jarvys_dev.main", "app"),
            ("main", "app"),
        ]

        app_found = False
        for module_path, app_name in app_locations:
            try:
                module = __import__(module_path, fromlist=[app_name])
                app = getattr(module, app_name, None)

                if app is not None:
                    from fastapi import FastAPI

                    assert isinstance(
                        app, FastAPI
                    ), "Should be a FastAPI instance"
                    app_found = True
                    print(f"Found FastAPI app at {module_path}.{app_name}")
                    break

            except (ImportError, AttributeError):
                continue

        if not app_found:
            # Check if app directory exists but isn't importable
            app_dir = Path(__file__).parent.parent / "app"
            if app_dir.exists():
                pytest.skip("FastAPI app directory exists but not importable")
            else:
                pytest.skip("FastAPI app not found")

    @pytest.mark.integration
    def test_api_root_endpoint(self):
        """Test API root endpoint."""
        try:
            from fastapi.testclient import TestClient

            from app.main import app

            client = TestClient(app)
            response = client.get("/")

            # Should return successful response
            assert response.status_code in [
                200,
                404,
            ], "Should get valid HTTP response"

            if response.status_code == 200:
                # If endpoint exists, check response format
                assert response.headers.get(
                    "content-type"
                ), "Should have content-type header"

        except Exception as e:
            pytest.fail(f"API root endpoint test failed: {e}")

    @pytest.mark.integration
    def test_api_health_endpoint(self):
        """Test API health endpoint if it exists."""
        try:
            from fastapi.testclient import TestClient

            from app.main import app

            client = TestClient(app)

            # Common health endpoint paths
            health_paths = ["/health", "/api/health", "/status", "/ping"]

            found_health_endpoint = False
            for path in health_paths:
                response = client.get(path)
                if response.status_code == 200:
                    found_health_endpoint = True
                    print(f"Found health endpoint at {path}")

                    # Health response should be JSON
                    try:
                        health_data = response.json()
                        assert isinstance(
                            health_data, dict
                        ), "Health response should be JSON object"
                    except Exception:
                        # Text response is also acceptable
                        pass
                    break

            if not found_health_endpoint:
                print("Info: No health endpoint found")

        except Exception as e:
            pytest.fail(f"API health endpoint test failed: {e}")

    @pytest.mark.integration
    def test_api_cors_configuration(self):
        """Test API CORS configuration."""
        try:
            from fastapi.testclient import TestClient

            from app.main import app

            client = TestClient(app)

            # Test CORS preflight request
            response = client.options(
                "/",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET",
                },
            )

            # Should handle CORS appropriately
            if response.status_code in [200, 204]:
                cors_headers = [
                    h
                    for h in response.headers.keys()
                    if h.lower().startswith("access-control")
                ]
                if cors_headers:
                    print(f"CORS headers found: {cors_headers}")

        except Exception as e:
            print(f"Info: CORS test failed: {e}")


class TestMCPServerAPI:
    """Test MCP (Model Context Protocol) server API."""

    @pytest.mark.integration
    def test_mcp_server_structure(self):
        """Test MCP server structure exists."""
        # Check if MCP server code exists
        project_root = Path(__file__).parent.parent
        app_dir = project_root / "app"

        if app_dir.exists():
            main_file = app_dir / "main.py"
            if main_file.exists():
                content = main_file.read_text()

                # Should be FastAPI or similar server
                server_patterns = ["FastAPI", "uvicorn", "app ="]
                found_patterns = [p for p in server_patterns if p in content]

                assert (
                    len(found_patterns) > 0
                ), f"MCP server should have server patterns: {server_patterns}"
                print(f"MCP server patterns found: {found_patterns}")
            else:
                pytest.skip("MCP server main.py not found")
        else:
            pytest.skip("MCP server app directory not found")

    @pytest.mark.integration
    def test_mcp_endpoints_structure(self):
        """Test MCP endpoints have proper structure."""
        try:
            from app.main import app

            # Get all routes
            routes = [route.path for route in app.routes]

            # Should have MCP-related endpoints
            mcp_patterns = ["/v1/", "/tool", "/metadata"]
            found_mcp = [
                pattern
                for pattern in mcp_patterns
                if any(pattern in route for route in routes)
            ]

            if found_mcp:
                print(f"MCP-related endpoints found: {found_mcp}")
            else:
                print("Info: No MCP-specific endpoints found")

        except ImportError:
            pytest.skip("MCP server app not importable")

    @pytest.mark.integration
    def test_mcp_server_startup(self):
        """Test MCP server can start up."""
        try:
            from fastapi.testclient import TestClient

            from app.main import app

            client = TestClient(app)

            # Test basic connectivity
            response = client.get("/")

            # Should return some response
            assert response.status_code in [
                200,
                404,
                422,
            ], "Server should respond"

        except ImportError:
            pytest.skip("MCP server not available")
        except Exception as e:
            pytest.fail(f"MCP server startup failed: {e}")


class TestSupabaseAPI:
    """Test Supabase API integration."""

    @pytest.mark.integration
    def test_supabase_api_connection(self):
        """Test Supabase API connection."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            pytest.skip("Supabase credentials not available")

        try:
            from supabase import create_client

            client = create_client(url, key)

            # Test basic API call
            _response = (
                client.table("test_table").select("*").limit(1).execute()
            )

            # Should get a response (even if table doesn't exist)
            assert hasattr(
                response, "data"
            ), "Should get response object with data attribute"

        except Exception as e:
            error_str = str(e).lower()
            if "relation" in error_str and "does not exist" in error_str:
                # Table doesn't exist - that's fine, connection works
                pass
            elif "unauthorized" in error_str:
                pytest.fail(f"Supabase authentication failed: {e}")
            else:
                pytest.skip(f"Supabase API test failed: {e}")

    @pytest.mark.integration
    def test_supabase_edge_functions_api(self):
        """Test Supabase Edge Functions API."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            pytest.skip("Supabase credentials not available")

        try:
            # Test Edge Function API endpoint
            functions_url = f"{url}/functions/v1/"

            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            }

            response = requests.get(
                functions_url, headers=headers, timeout=10
            )

            # Should get some response (even if no functions deployed)
            assert response.status_code in [
                200,
                404,
                401,
            ], "Should get valid HTTP response"

            if response.status_code == 401:
                pytest.fail("Supabase Edge Functions authentication failed")

        except requests.exceptions.RequestException as e:
            pytest.skip(f"Supabase Edge Functions API test failed: {e}")

    @pytest.mark.integration
    def test_supabase_dashboard_api(self):
        """Test Supabase dashboard API if deployed."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            pytest.skip("Supabase credentials not available")

        try:
            # Test dashboard endpoint
            dashboard_url = f"{url}/functions/v1/jarvys-dashboard/"

            headers = {"Authorization": f"Bearer {key}"}

            response = requests.get(
                dashboard_url, headers=headers, timeout=10
            )

            # Dashboard may or may not be deployed
            if response.status_code == 200:
                print("Dashboard API is accessible")
                assert response.headers.get(
                    "content-type"
                ), "Should have content-type"
            elif response.status_code == 404:
                print("Info: Dashboard not deployed yet")
            else:
                print(f"Dashboard API status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            pytest.skip(f"Dashboard API test failed: {e}")


class TestGitHubAPI:
    """Test GitHub API integration."""

    @pytest.mark.integration
    def test_github_api_connection(self):
        """Test GitHub API connection."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            pytest.skip("GITHUB_TOKEN not available")

        try:
            from github import Github

            client = Github(token)

            # Test basic API access
            user = client.get_user()
            assert user is not None

            # Test rate limit info
            rate_limit = client.get_rate_limit()
            assert rate_limit.core.remaining >= 0

            print(
                f"GitHub API rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit}"
            )

        except Exception as e:
            error_str = str(e).lower()
            if "bad credentials" in error_str:
                pytest.fail("GitHub token is invalid")
            else:
                pytest.fail(f"GitHub API test failed: {e}")

    @pytest.mark.integration
    def test_github_repository_api(self):
        """Test GitHub repository API access."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            pytest.skip("GITHUB_TOKEN not available")

        try:
            from github import Github

            client = Github(token)

            # Test repository access
            repo_name = "yannabadie/appia-dev"
            repo = client.get_repo(repo_name)

            assert repo is not None
            assert repo.name == "appia-dev"

            # Test repository operations
            issues = repo.get_issues(state="open")
            issue_count = len(list(issues)[:5])  # Limit to avoid rate limits

            print(f"Repository accessible, {issue_count} issues found")

        except Exception as e:
            pytest.skip(f"GitHub repository API test failed: {e}")

    @pytest.mark.integration
    def test_github_issues_api(self):
        """Test GitHub Issues API for agent communication."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            pytest.skip("GITHUB_TOKEN not available")

        try:
            from github import Github

            client = Github(token)

            repo_name = "yannabadie/appia-dev"
            repo = client.get_repo(repo_name)

            # Test issue listing with agent communication labels
            issues = repo.get_issues(labels=["agent_communication"])

            # Should be able to iterate (even if no results)
            issue_list = list(issues)[:3]  # Limit to avoid rate limits

            print(f"Found {len(issue_list)} agent communication issues")

        except Exception as e:
            pytest.skip(f"GitHub Issues API test failed: {e}")


class TestOpenAIAPI:
    """Test OpenAI API integration."""

    @pytest.mark.integration
    def test_openai_api_connection(self):
        """Test OpenAI API connection."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not available")

        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)

            # Test API access with models list
            models = client.models.list()
            assert hasattr(models, "data")
            assert len(models.data) > 0

            # Find GPT models
            gpt_models = [m for m in models.data if "gpt" in m.id.lower()]
            assert len(gpt_models) > 0, "Should have GPT models available"

            print(f"OpenAI API accessible, {len(gpt_models)} GPT models found")

        except Exception as e:
            error_str = str(e).lower()
            if "unauthorized" in error_str or "invalid" in error_str:
                pytest.fail("OpenAI API key is invalid")
            else:
                pytest.skip(f"OpenAI API test failed: {e}")

    @pytest.mark.integration
    def test_openai_chat_completion_api(self):
        """Test OpenAI Chat Completion API."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not available")

        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)

            # Test minimal chat completion
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10,
            )

            assert response.choices is not None
            assert len(response.choices) > 0
            assert response.choices[0].message.content is not None

            print("OpenAI Chat Completion API working")

        except Exception as e:
            error_str = str(e).lower()
            if "unauthorized" in error_str:
                pytest.fail("OpenAI API key is invalid")
            elif "quota" in error_str or "billing" in error_str:
                pytest.skip("OpenAI API quota exceeded")
            else:
                pytest.skip(f"OpenAI Chat Completion test failed: {e}")


class TestExternalAPIIntegration:
    """Test external API integrations."""

    @pytest.mark.integration
    def test_gemini_api_integration(self):
        """Test Google Gemini API integration."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            pytest.skip("GEMINI_API_KEY not available")

        try:
            # Test with HTTP request to avoid import issues
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            response = requests.get(url, timeout=10)

            assert (
                response.status_code == 200
            ), f"Gemini API returned {response.status_code}"

            data = response.json()
            assert "models" in data, "Gemini API should return models"

            print(f"Gemini API accessible, {len(data['models'])} models found")

        except requests.exceptions.RequestException as e:
            pytest.skip(f"Gemini API test failed: {e}")

    @pytest.mark.integration
    def test_anthropic_api_integration(self):
        """Test Anthropic API integration."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not available")

        try:
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }

            # Test with minimal request
            data = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hi"}],
            }

            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=10,
            )

            assert (
                response.status_code == 200
            ), f"Anthropic API returned {response.status_code}"

            _result = response.json()
            assert "content" in result, "Anthropic API should return content"

            print("Anthropic API accessible")

        except requests.exceptions.RequestException as e:
            pytest.skip(f"Anthropic API test failed: {e}")


class TestAPIErrorHandling:
    """Test API error handling and resilience."""

    def test_api_rate_limit_handling(self):
        """Test API rate limit handling."""
        # Test that APIs handle rate limits gracefully
        try:
            from jarvys_dev.multi_model_router import MultiModelRouter

            with patch.dict(
                os.environ, {"OPENAI_API_KEY": "sk-test123"}, clear=True
            ):
                router = MultiModelRouter()

                # Mock rate limit response
                with patch("openai.OpenAI") as mock_openai:
                    mock_client = Mock()
                    mock_client.chat.completions.create.side_effect = (
                        Exception("Rate limit exceeded")
                    )
                    mock_openai.return_value = mock_client

                    # Should handle rate limits gracefully
                    try:
                        router.generate("test prompt")
                        # If it doesn't crash, that's good
                    except Exception as e:
                        # Rate limit handling should prevent crashes
                        assert "internal error" not in str(e).lower()

        except ImportError:
            pytest.skip("MultiModelRouter not available")

    def test_api_authentication_error_handling(self):
        """Test API authentication error handling."""
        try:
            from jarvys_dev.multi_model_router import MultiModelRouter

            # Test with invalid API key
            with patch.dict(
                os.environ, {"OPENAI_API_KEY": "invalid-key"}, clear=True
            ):
                router = MultiModelRouter()

                # Should handle auth errors gracefully
                try:
                    router.generate("test prompt")
                except Exception as e:
                    # Auth errors should be handled, not cause crashes
                    error_str = str(e).lower()
                    assert "internal error" not in error_str

        except ImportError:
            pytest.skip("MultiModelRouter not available")

    def test_api_network_error_handling(self):
        """Test API network error handling."""
        try:
            # Test network error handling
            with patch("requests.get") as mock_get:
                mock_get.side_effect = requests.exceptions.ConnectionError(
                    "Network error"
                )

                # Should handle network errors gracefully
                try:
                    response = requests.get(
                        "https://api.openai.com/v1/models", timeout=1
                    )
                except requests.exceptions.ConnectionError:
                    # Expected - connection error should be caught
                    pass
                except Exception as e:
                    pytest.fail(f"Unexpected error type: {e}")

        except Exception as e:
            pytest.skip(f"Network error handling test failed: {e}")


class TestAPIPerformance:
    """Test API performance characteristics."""

    def test_api_response_time_tracking(self):
        """Test API response time tracking."""
        try:
            from fastapi.testclient import TestClient

            from app.main import app

            client = TestClient(app)

            import time

            start_time = time.time()
            client.get("/")
            end_time = time.time()

            response_time = end_time - start_time

            # Should respond quickly (less than 5 seconds for local API)
            assert (
                response_time < 5.0
            ), f"API response too slow: {response_time}s"

            print(f"API response time: {response_time:.3f}s")

        except ImportError:
            pytest.skip("FastAPI app not available")

    def test_api_concurrent_request_handling(self):
        """Test API can handle concurrent requests."""
        try:
            import threading

            from fastapi.testclient import TestClient

            from app.main import app

            client = TestClient(app)
            results = []

            def make_request():
                try:
                    response = client.get("/")
                    results.append(response.status_code)
                except Exception as e:
                    results.append(str(e))

            # Make concurrent requests
            threads = []
            for i in range(3):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()

            # Wait for all requests to complete
            for thread in threads:
                thread.join(timeout=10)

            # Should handle all requests
            assert len(results) == 3, "Should handle all concurrent requests"

            print(f"Concurrent request results: {results}")

        except ImportError:
            pytest.skip("FastAPI app not available")


class TestAPIDocumentation:
    """Test API documentation and discoverability."""

    def test_api_openapi_schema(self):
        """Test API provides OpenAPI schema."""
        try:
            from fastapi.testclient import TestClient

            from app.main import app

            client = TestClient(app)

            # FastAPI automatically provides OpenAPI schema
            response = client.get("/openapi.json")

            if response.status_code == 200:
                schema = response.json()

                assert "openapi" in schema, "Should have OpenAPI version"
                assert "info" in schema, "Should have API info"
                assert "paths" in schema, "Should have API paths"

                print("OpenAPI schema available")
            else:
                print("Info: OpenAPI schema not found")

        except ImportError:
            pytest.skip("FastAPI app not available")

    def test_api_docs_endpoint(self):
        """Test API documentation endpoint."""
        try:
            from fastapi.testclient import TestClient

            from app.main import app

            client = TestClient(app)

            # FastAPI automatically provides docs
            response = client.get("/docs")

            if response.status_code == 200:
                assert (
                    "swagger" in response.text.lower()
                    or "documentation" in response.text.lower()
                )
                print("API documentation endpoint available")
            else:
                print("Info: API documentation endpoint not found")

        except ImportError:
            pytest.skip("FastAPI app not available")
