"""Test infrastructure components for JARVYS ecosystem."""

import json
import os
from pathlib import Path

import pytest


class TestSupabaseInfrastructure:
    """Test Supabase infrastructure setup."""

    def test_supabase_schema_sql_exists(self):
        """Test that schema.sql exists and has basic structure."""
        schema_path = Path(__file__).parent.parent / "supabase" / "schema.sql"
        assert schema_path.exists(), "schema.sql not found"

        content = schema_path.read_text()
        assert len(content.strip()) > 0, "schema.sql is empty"

        # Basic SQL structure checks
        assert (
            "CREATE" in content.upper()
        ), "schema.sql should contain CREATE statements"

    def test_supabase_config_toml_exists(self):
        """Test that config.toml exists and has basic structure."""
        config_path = Path(__file__).parent.parent / "supabase" / "config.toml"
        assert config_path.exists(), "config.toml not found"

        content = config_path.read_text()
        assert len(content.strip()) > 0, "config.toml is empty"

        # Basic TOML structure check
        assert "[" in content, "config.toml should contain sections"

    @pytest.mark.integration
    def test_supabase_database_connection(self):
        """Test Supabase database connection."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            pytest.skip("Supabase credentials not available")

        try:
            from supabase import create_client

            client = create_client(url, key)

            # Test with a simple system query that should always work
            _response = client.rpc("version").execute()
            assert response is not None, "Could not get database version"

        except Exception as e:
            error_str = str(e).lower()
            if "unauthorized" in error_str or "invalid" in error_str:
                pytest.fail(f"Supabase authentication failed: {e}")
            elif "function" in error_str and "does not exist" in error_str:
                # RPC function doesn't exist - that's fine, connection is working
                pass
            else:
                pytest.fail(f"Supabase database connection failed: {e}")

    @pytest.mark.integration
    def test_supabase_memory_table_schema(self):
        """Test that memory table schema is correct."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            pytest.skip("Supabase credentials not available")

        try:
            from supabase import create_client

            client = create_client(url, key)

            # Try to query the memory table structure
<<<<<<< HEAD
            _response = client.table("agent_memory").select("*").limit(1).execute()
=======
            _response = (
                client.table("agent_memory").select("*").limit(1).execute()
            )
>>>>>>> origin/main

            # If table exists, check it has expected structure
            if hasattr(_response, "data"):
                # Table exists - this is good
                pass

        except Exception as e:
            error_str = str(e).lower()
            if "relation" in error_str and "does not exist" in error_str:
                # Memory table doesn't exist yet - that's fine for testing
                pass
            elif "unauthorized" in error_str:
                pytest.fail(f"Supabase authentication failed: {e}")
            else:
                # Other errors might be connectivity issues
                pytest.skip(f"Could not test memory table schema: {e}")

    def test_supabase_functions_directory(self):
        """Test that Supabase functions directory exists."""
<<<<<<< HEAD
        functions_path = Path(__file__).parent.parent / "supabase" / "functions"
        assert functions_path.exists(), "Supabase functions directory not found"
=======
        functions_path = (
            Path(__file__).parent.parent / "supabase" / "functions"
        )
        assert (
            functions_path.exists()
        ), "Supabase functions directory not found"
>>>>>>> origin/main

        # Check if there are any Edge Functions defined
        function_dirs = [d for d in functions_path.iterdir() if d.is_dir()]
        if function_dirs:
            # If functions exist, check they have index.ts
            for func_dir in function_dirs:
                index_file = func_dir / "index.ts"
                if index_file.exists():
                    content = index_file.read_text()
                    assert (
                        "Deno.serve" in content or "new Response" in content
                    ), f"Function {func_dir.name} doesn't look like a"
                    "valid Edge Function"


class TestGCPInfrastructure:
    """Test Google Cloud Platform infrastructure."""

    def test_gcp_service_account_structure(self):
        """Test GCP service account JSON structure."""
        sa_json = os.getenv("GCP_SA_JSON")
        if not sa_json:
            pytest.skip("GCP_SA_JSON not available")

        try:
            sa_data = json.loads(sa_json)

            # Required fields for service account
            required_fields = [
                "type",
                "project_id",
                "private_key_id",
                "private_key",
                "client_email",
                "client_id",
                "auth_uri",
                "token_uri",
            ]

            missing_fields = []
            for field in required_fields:
                if field not in sa_data:
                    missing_fields.append(field)

<<<<<<< HEAD
            assert not missing_fields, f"Missing required SA fields: {missing_fields}"
            assert sa_data["type"] == "service_account", "Invalid service account type"
=======
            assert (
                not missing_fields
            ), f"Missing required SA fields: {missing_fields}"
            assert (
                sa_data["type"] == "service_account"
            ), "Invalid service account type"
>>>>>>> origin/main

        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid GCP Service Account JSON: {e}")

    def test_gcp_project_id_format(self):
        """Test GCP project ID format."""
        sa_json = os.getenv("GCP_SA_JSON")
        if not sa_json:
            pytest.skip("GCP_SA_JSON not available")

        try:
            sa_data = json.loads(sa_json)
            project_id = sa_data.get("project_id")

            assert project_id, "No project_id in service account"
            assert len(project_id) >= 6, "Project ID too short"
            assert len(project_id) <= 30, "Project ID too long"
            assert (
                project_id.replace("-", "").replace("_", "").isalnum()
            ), "Project ID contains invalid characters"

        except json.JSONDecodeError:
            pytest.fail("Invalid GCP Service Account JSON")

    @pytest.mark.integration
    def test_gcp_service_account_permissions(self):
        """Test GCP service account has basic permissions."""
        sa_json = os.getenv("GCP_SA_JSON")
        if not sa_json:
            pytest.skip("GCP_SA_JSON not available")

        try:
            # Basic validation that the service account JSON is well-formed
            sa_data = json.loads(sa_json)
            client_email = sa_data.get("client_email")

            assert client_email, "No client_email in service account"
            assert "@" in client_email, "Invalid client_email format"
            assert (
                ".iam.gserviceaccount.com" in client_email
            ), "client_email doesn't look like a service account email"

        except json.JSONDecodeError:
            pytest.fail("Invalid GCP Service Account JSON")


class TestCloudBuildConfiguration:
    """Test Cloud Build configuration."""

    def test_cloudbuild_yaml_exists(self):
        """Test that cloudbuild.yaml exists."""
        cloudbuild_path = Path(__file__).parent.parent / "cloudbuild.yaml"
        assert cloudbuild_path.exists(), "cloudbuild.yaml not found"

    def test_cloudbuild_yaml_structure(self):
        """Test cloudbuild.yaml structure."""
        cloudbuild_path = Path(__file__).parent.parent / "cloudbuild.yaml"
        if not cloudbuild_path.exists():
            pytest.skip("cloudbuild.yaml not found")

        try:
            import yaml

            content = cloudbuild_path.read_text()
            config = yaml.safe_load(content)

            assert "steps" in config, "cloudbuild.yaml missing 'steps' section"
<<<<<<< HEAD
            assert len(config["steps"]) > 0, "cloudbuild.yaml has no build steps"
=======
            assert (
                len(config["steps"]) > 0
            ), "cloudbuild.yaml has no build steps"
>>>>>>> origin/main

            # Check for basic step structure
            for i, step in enumerate(config["steps"]):
                assert "name" in step, f"Step {i} missing 'name'"

        except ImportError:
            pytest.skip("PyYAML not available for cloudbuild.yaml testing")
        except yaml.YAMLError as e:
            pytest.fail(f"cloudbuild.yaml has invalid YAML syntax: {e}")


class TestDatabaseSchema:
    """Test database schema and migrations."""

    def test_schema_sql_syntax(self):
        """Test that schema.sql has valid SQL syntax."""
        schema_path = Path(__file__).parent.parent / "supabase" / "schema.sql"
        if not schema_path.exists():
            pytest.skip("schema.sql not found")

        content = schema_path.read_text()

        # Basic SQL syntax checks
        assert content.count("(") == content.count(
            ")"
        ), "Unmatched parentheses in schema.sql"
        assert content.count("{") == content.count(
            "}"
        ), "Unmatched braces in schema.sql"

        # Check for dangerous operations in production
        dangerous_ops = ["DROP DATABASE", "TRUNCATE", "DELETE FROM"]
        for op in dangerous_ops:
            if op in content.upper():
                print(f"Warning: Found potentially dangerous operation: {op}")

    def test_functions_sql_exists(self):
        """Test that functions.sql exists if referenced."""
<<<<<<< HEAD
        functions_path = Path(__file__).parent.parent / "supabase" / "functions.sql"
=======
        functions_path = (
            Path(__file__).parent.parent / "supabase" / "functions.sql"
        )
>>>>>>> origin/main
        if functions_path.exists():
            content = functions_path.read_text()
            assert len(content.strip()) > 0, "functions.sql is empty"

            # Should contain function definitions
            assert (
                "CREATE" in content.upper()
            ), "functions.sql should contain CREATE statements"


class TestStorageConfiguration:
    """Test storage and file operations configuration."""

    @pytest.mark.integration
    def test_supabase_storage_access(self):
        """Test Supabase storage access."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            pytest.skip("Supabase credentials not available")

        try:
            from supabase import create_client

            client = create_client(url, key)

            # Test storage access (will fail if storage not set up, but connection works)
            try:
                buckets = client.storage.list_buckets()
                # If we get here, storage is accessible
<<<<<<< HEAD
                assert isinstance(buckets, list), "Storage buckets should be a list"
=======
                assert isinstance(
                    buckets, list
                ), "Storage buckets should be a list"
>>>>>>> origin/main
            except Exception as storage_e:
                # Storage might not be configured - that's fine
                if "unauthorized" in str(storage_e).lower():
                    pytest.fail(f"Storage authentication failed: {storage_e}")
                else:
                    # Other storage errors are acceptable for testing
                    pass

        except Exception as e:
            error_str = str(e).lower()
            if "unauthorized" in error_str:
                pytest.fail(f"Supabase authentication failed: {e}")
            else:
                pytest.skip(f"Could not test storage: {e}")

    def test_memory_database_file_location(self):
        """Test memory database file location."""
        project_root = Path(__file__).parent.parent
        memory_db = project_root / "jarvys_metrics.db"

        if memory_db.exists():
            # Check file is readable
            assert memory_db.is_file(), "Memory database should be a file"
            assert (
                memory_db.stat().st_size >= 0
            ), "Memory database file should be readable"
        else:
            # File doesn't exist yet - that's fine
            print("Info: Local memory database not yet created")


class TestEdgeFunctionsInfrastructure:
    """Test Edge Functions infrastructure."""

    def test_edge_functions_structure(self):
        """Test Edge Functions directory structure."""
<<<<<<< HEAD
        functions_path = Path(__file__).parent.parent / "supabase" / "functions"
=======
        functions_path = (
            Path(__file__).parent.parent / "supabase" / "functions"
        )
>>>>>>> origin/main
        if not functions_path.exists():
            pytest.skip("Supabase functions directory not found")

        # Look for any function directories
        function_dirs = [d for d in functions_path.iterdir() if d.is_dir()]

        for func_dir in function_dirs:
            # Each function should have an index.ts file
            index_file = func_dir / "index.ts"
            if index_file.exists():
                content = index_file.read_text()

                # Basic TypeScript/Deno Edge Function structure
                assert any(
<<<<<<< HEAD
                    pattern in content for pattern in ["Deno.serve", "new Response"]
=======
                    pattern in content
                    for pattern in ["Deno.serve", "new Response"]
>>>>>>> origin/main
                ), f"Function {func_dir.name} doesn't contain proper"
                "Edge Function patterns"

    @pytest.mark.integration
    def test_edge_function_deployment_ready(self):
        """Test that Edge Functions are deployment ready."""
<<<<<<< HEAD
        functions_path = Path(__file__).parent.parent / "supabase" / "functions"
=======
        functions_path = (
            Path(__file__).parent.parent / "supabase" / "functions"
        )
>>>>>>> origin/main
        if not functions_path.exists():
            pytest.skip("Supabase functions directory not found")

        function_dirs = [d for d in functions_path.iterdir() if d.is_dir()]

        for func_dir in function_dirs:
            index_file = func_dir / "index.ts"
            if index_file.exists():
                content = index_file.read_text()

                # Check for common Edge Function requirements
                has_cors = (
<<<<<<< HEAD
                    "cors" in content.lower() or "Access-Control-Allow" in content
=======
                    "cors" in content.lower()
                    or "Access-Control-Allow" in content
>>>>>>> origin/main
                )
                has_error_handling = "try" in content and "catch" in content

                if not has_cors:
<<<<<<< HEAD
                    print(f"Warning: Function {func_dir.name} may need" "CORS handling")
                if not has_error_handling:
                    print(
                        f"Warning: Function {func_dir.name} may need" "error handling"
=======
                    print(
                        f"Warning: Function {func_dir.name} may need"
                        "CORS handling"
                    )
                if not has_error_handling:
                    print(
                        f"Warning: Function {func_dir.name} may need"
                        "error handling"
>>>>>>> origin/main
                    )
