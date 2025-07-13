"""Test connectivity to external services for JARVYS ecosystem."""

import json
import os

import pytest
import requests


class TestOpenAIConnectivity:
    """Test OpenAI API connectivity."""

    @pytest.mark.integration
    def test_openai_api_key_format(self):
        """Test OpenAI API key format."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not available")

        assert api_key.startswith(
            "sk-"
        ), "OpenAI API key should start with 'sk-'"
        assert len(api_key) > 20, "OpenAI API key seems too short"

    @pytest.mark.integration
    def test_openai_connectivity(self):
        """Test actual OpenAI API connectivity."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not available")

        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)

            # Test with a minimal request
            response = client.models.list()
            assert hasattr(response, "data"), "Invalid OpenAI API response"
            assert len(response.data) > 0, "No models available from OpenAI"

        except Exception as e:
            pytest.fail(f"OpenAI connectivity test failed: {e}")

    @pytest.mark.integration
    def test_openai_import_availability(self):
        """Test that OpenAI library can be imported."""
        try:
            import openai

            assert hasattr(openai, "OpenAI"), "OpenAI class not available"
        except ImportError:
            pytest.fail("OpenAI library not available")


class TestSupabaseConnectivity:
    """Test Supabase connectivity."""

    @pytest.mark.integration
    def test_supabase_url_format(self):
        """Test Supabase URL format."""
        url = os.getenv("SUPABASE_URL")
        if not url:
            pytest.skip("SUPABASE_URL not available")

        assert url.startswith(
            "https://"
        ), "Supabase URL should start with https://"
        assert (
            ".supabase.co" in url
        ), "Supabase URL should contain .supabase.co"

    @pytest.mark.integration
    def test_supabase_key_format(self):
        """Test Supabase key format."""
        key = os.getenv("SUPABASE_KEY")
        if not key:
            pytest.skip("SUPABASE_KEY not available")

        assert key.startswith(
            "eyJ"
        ), "Supabase key should start with 'eyJ' (JWT format)"
        assert len(key) > 100, "Supabase key seems too short"

    @pytest.mark.integration
    def test_supabase_connectivity(self):
        """Test actual Supabase connectivity."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            pytest.skip("Supabase credentials not available")

        try:
            from supabase import create_client

            client = create_client(url, key)

            # Test basic connectivity with a simple query
            # This will fail if credentials are invalid
            response = (
                client.table("test_connectivity_check")
                .select("*")
                .limit(1)
                .execute()
            )
            # We don't care if the table exists, just that we can connect
            assert hasattr(response, "data"), "Invalid Supabase response"

        except Exception as e:
            # Check if it's a table not found error (acceptable) vs auth error
            error_str = str(e).lower()
            if "relation" in error_str and "does not exist" in error_str:
                # Table doesn't exist - that's fine, connection is working
                pass
            elif "unauthorized" in error_str or "invalid" in error_str:
                pytest.fail(f"Supabase authentication failed: {e}")
            else:
                pytest.fail(f"Supabase connectivity test failed: {e}")

    @pytest.mark.integration
    def test_supabase_import_availability(self):
        """Test that Supabase library can be imported."""
        try:
            import supabase

            assert hasattr(
                supabase, "create_client"
            ), "Supabase create_client not available"
        except ImportError:
            pytest.fail("Supabase library not available")


class TestGeminiConnectivity:
    """Test Google Gemini API connectivity."""

    @pytest.mark.integration
    def test_gemini_api_key_format(self):
        """Test Gemini API key format."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            pytest.skip("GEMINI_API_KEY not available")

        assert api_key.startswith(
            "AIza"
        ), "Gemini API key should start with 'AIza'"
        assert len(api_key) > 30, "Gemini API key seems too short"

    @pytest.mark.integration
    def test_gemini_connectivity(self):
        """Test actual Gemini API connectivity."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            pytest.skip("GEMINI_API_KEY not available")

        try:
            # Test with a simple HTTP request to avoid import issues
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            response = requests.get(url, timeout=10)

            if response.status_code == 401:
                pytest.fail("Gemini API key is invalid")
            elif response.status_code == 403:
                pytest.fail("Gemini API access forbidden")
            elif response.status_code != 200:
                pytest.fail(
                    f"Gemini API returned status {response.status_code}"
                )

            data = response.json()
            assert "models" in data, "Invalid Gemini API response format"

        except requests.exceptions.RequestException as e:
            pytest.fail(f"Gemini connectivity test failed: {e}")


class TestAnthropicConnectivity:
    """Test Anthropic API connectivity."""

    @pytest.mark.integration
    def test_anthropic_api_key_format(self):
        """Test Anthropic API key format."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not available")

        assert api_key.startswith(
            "sk-ant-"
        ), "Anthropic API key should start with 'sk-ant-'"
        assert len(api_key) > 50, "Anthropic API key seems too short"

    @pytest.mark.integration
    def test_anthropic_connectivity(self):
        """Test actual Anthropic API connectivity."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not available")

        try:
            # Test with a simple HTTP request
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }

            # Test a minimal request
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

            if response.status_code == 401:
                pytest.fail("Anthropic API key is invalid")
            elif response.status_code == 403:
                pytest.fail("Anthropic API access forbidden")
            elif response.status_code != 200:
                pytest.fail(
                    f"Anthropic API returned status {response.status_code}"
                )

        except requests.exceptions.RequestException as e:
            pytest.fail(f"Anthropic connectivity test failed: {e}")


class TestGitHubConnectivity:
    """Test GitHub API connectivity."""

    @pytest.mark.integration
    def test_github_token_format(self):
        """Test GitHub token format."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            pytest.skip("GITHUB_TOKEN not available")

        # GitHub tokens can be various formats
        valid_prefixes = ["ghp_", "gho_", "ghu_", "ghs_", "ghr_"]
        assert any(
            token.startswith(prefix) for prefix in valid_prefixes
        ), f"GitHub token should start with one of: {valid_prefixes}"

    @pytest.mark.integration
    def test_github_connectivity(self):
        """Test actual GitHub API connectivity."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            pytest.skip("GITHUB_TOKEN not available")

        try:
            from github import Github

            g = Github(token)

            # Test basic connectivity
            user = g.get_user()
            assert user is not None, "Could not get GitHub user info"

            # Test rate limit to ensure token is working
            rate_limit = g.get_rate_limit()
            assert (
                rate_limit.core.remaining >= 0
            ), "Invalid rate limit response"

        except Exception as e:
            error_str = str(e).lower()
            if "bad credentials" in error_str:
                pytest.fail("GitHub token is invalid")
            else:
                pytest.fail(f"GitHub connectivity test failed: {e}")

    @pytest.mark.integration
    def test_github_import_availability(self):
        """Test that PyGithub library can be imported."""
        try:
            import github

            assert hasattr(github, "Github"), "Github class not available"
        except ImportError:
            pytest.fail("PyGithub library not available")


class TestGCPConnectivity:
    """Test Google Cloud Platform connectivity."""

    @pytest.mark.integration
    def test_gcp_service_account_json_format(self):
        """Test GCP Service Account JSON format."""
        sa_json = os.getenv("GCP_SA_JSON")
        if not sa_json:
            pytest.skip("GCP_SA_JSON not available")

        try:
            sa_data = json.loads(sa_json)
            required_fields = [
                "type",
                "project_id",
                "private_key_id",
                "private_key",
                "client_email",
            ]
            missing_fields = [
                field for field in required_fields if field not in sa_data
            ]
            assert (
                not missing_fields
            ), f"Missing GCP SA fields: {missing_fields}"
            assert (
                sa_data["type"] == "service_account"
            ), "GCP SA type should be 'service_account'"
        except json.JSONDecodeError:
            pytest.fail("GCP_SA_JSON is not valid JSON")

    @pytest.mark.integration
    def test_gcp_connectivity(self):
        """Test actual GCP connectivity."""
        sa_json = os.getenv("GCP_SA_JSON")
        if not sa_json:
            pytest.skip("GCP_SA_JSON not available")

        # This is a basic test - more specific GCP tests should be in infrastructure tests
        try:
            sa_data = json.loads(sa_json)
            project_id = sa_data.get("project_id")
            assert project_id, "No project_id in GCP Service Account"

            # Basic validation that the JSON structure is correct
            assert (
                "private_key" in sa_data
            ), "No private_key in GCP Service Account"
            assert (
                "client_email" in sa_data
            ), "No client_email in GCP Service Account"

        except Exception as e:
            pytest.fail(f"GCP Service Account validation failed: {e}")


class TestNetworkConnectivity:
    """Test general network connectivity."""

    @pytest.mark.integration
    def test_internet_connectivity(self):
        """Test basic internet connectivity."""
        try:
            response = requests.get("https://httpbin.org/get", timeout=10)
            assert (
                response.status_code == 200
            ), "Internet connectivity check failed"
        except requests.exceptions.RequestException:
            pytest.skip("No internet connectivity available")

    @pytest.mark.integration
    def test_dns_resolution(self):
        """Test DNS resolution for key services."""
        import socket

        services = [
            "api.openai.com",
            "api.anthropic.com",
            "generativelanguage.googleapis.com",
            "github.com",
        ]

        failed_resolutions = []
        for service in services:
            try:
                socket.gethostbyname(service)
            except socket.gaierror:
                failed_resolutions.append(service)

        if failed_resolutions:
            pytest.skip(f"DNS resolution failed for: {failed_resolutions}")
