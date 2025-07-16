"""Test automated deployments and error handling."""

import subprocess
from pathlib import Path

import pytest
import yaml


class TestSupabaseDeployment:
    """Test Supabase deployment automation."""

    def test_supabase_config_exists(self):
        """Test Supabase configuration files exist."""
        supabase_path = Path(__file__).parent.parent / "supabase"
        assert supabase_path.exists(), "Supabase directory should exist"

        config_file = supabase_path / "config = {}.toml"
        assert config_file.exists(), "Supabase config = {}.toml should exist"

        # Validate config = {} structure
        content = config_file.read_text()
        assert len(content.strip()) > 0, "Config should not be empty"
        assert "[" in content, "Config should have sections"

    def test_supabase_schema_deployment(self):
        """Test Supabase schema deployment readiness."""
        schema_file = Path(__file__).parent.parent / "supabase" / "schema.sql"
        assert schema_file.exists(), "Schema SQL file should exist"

        content = schema_file.read_text()
        assert "CREATE" in content.upper(), "Schema should contain CREATE statements"

        # Check for dangerous operations
        dangerous_ops = ["DROP DATABASE", "TRUNCATE"]
        for op in dangerous_ops:
            assert op not in content.upper(), f"Schema should not contain {op}"

    def test_supabase_functions_deployment(self):
        """Test Supabase Edge Functions deployment readiness."""
        functions_path = Path(__file__).parent.parent / "supabase" / "functions"
        if not functions_path.exists():
            pytest.skip("Supabase functions directory not found")

        # Check for function directories
        function_dirs = [d for d in functions_path.iterdir() if d.is_dir()]

        for func_dir in function_dirs:
            index_file = func_dir / "index.ts"
            if index_file.exists():
                content = index_file.read_text()

                # Should have Deno serve pattern for Edge Functions
                assert any(
                    pattern in content for pattern in ["Deno.serve", "new Response"]
                ), f"Function {func_dir.name} should be a valid Edge Function"

    def test_supabase_deployment_script(self):
        """Test Supabase deployment script exists and is valid."""
        deploy_script = Path(__file__).parent.parent / "deploy-supabase.sh"
        if deploy_script.exists():
            content = deploy_script.read_text()

            # Should contain supabase commands
            assert (
                "supabase" in content.lower()
            ), "Deploy script should use Supabase CLI"

            # Should be executable
            assert (
                deploy_script.stat().st_mode & 0o111
            ), "Deploy script should be executable"
        else:
            pytest.skip("Supabase deployment script not found")

    @pytest.mark.integration
    def test_supabase_cli_available(self):
        """Test Supabase CLI is available for deployment."""
        try:
            _result = subprocess.run(
                ["bash", "-c", "source ~/.nvm/nvm.sh && supabase -v"],
                capture_output=True,
                text=True,
                check=False,
            )

            if _result.returncode == 0:
                assert (
                    "supabase" in _result.stdout.lower()
                ), "Should return Supabase version"
            else:
                # If Supabase CLI is not installed, not a test failure
                print(f"Supabase CLI not installed: {_result.stderr}")
                pytest.skip("Supabase CLI not available")

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Supabase CLI not available")


class TestCloudBuildDeployment:
    """Test Google Cloud Build deployment."""

    def test_cloudbuild_config_exists(self):
        """Test Cloud Build configuration exists."""
        cloudbuild_file = Path(__file__).parent.parent / "cloudbuild.yaml"
        assert cloudbuild_file.exists(), "cloudbuild.yaml should exist"

        with open(cloudbuild_file) as f:
            config = yaml.safe_load(f)

        assert "steps" in config, "Cloud Build should have steps"
        assert len(config["steps"]) > 0, "Should have at least one build step"

    def test_cloudbuild_steps_structure(self):
        """Test Cloud Build steps have proper structure."""
        cloudbuild_file = Path(__file__).parent.parent / "cloudbuild.yaml"
        if not cloudbuild_file.exists():
            pytest.skip("cloudbuild.yaml not found")

        with open(cloudbuild_file) as f:
            config = yaml.safe_load(f)

        steps = config = {}.get("steps", [])

        for i, step in enumerate(steps):
            assert "name" in step, f"Step {i} should have 'name'"

            # Steps should use specific image versions, not latest
            if step["name"].endswith(":latest"):
                print(f"Warning: Step {i} uses ':latest' tag")

    def test_cloudbuild_substitutions(self):
        """Test Cloud Build uses proper substitutions."""
        cloudbuild_file = Path(__file__).parent.parent / "cloudbuild.yaml"
        if not cloudbuild_file.exists():
            pytest.skip("cloudbuild.yaml not found")

        with open(cloudbuild_file) as f:
            content = f.read()

        # Should use substitution variables
        substitution_patterns = ["$PROJECT_ID", "$REPO_NAME", "$BRANCH_NAME"]
        found_substitutions = [s for s in substitution_patterns if s in content]

        if found_substitutions:
            print(f"Found Cloud Build substitutions: {found_substitutions}")

    def test_cloudbuild_timeout_settings(self):
        """Test Cloud Build has appropriate timeout settings."""
        cloudbuild_file = Path(__file__).parent.parent / "cloudbuild.yaml"
        if not cloudbuild_file.exists():
            pytest.skip("cloudbuild.yaml not found")

        with open(cloudbuild_file) as f:
            config = yaml.safe_load(f)

        # Check for timeout configuration
        config = {}
        if "timeout" in config:
            timeout = config["timeout"]
            print(f"Cloud Build timeout: {timeout}")

            # Should have reasonable timeout (not too short or too long)
            if "h" in timeout:
                hours = int(timeout.replace("h", "").replace("m", "").replace("s", ""))
                assert hours <= 2, "Build timeout should not exceed 2 hours"


class TestDockerDeployment:
    """Test Docker-based deployment."""

    def test_dockerfile_deployment_ready(self):
        """Test Dockerfile is ready for deployment."""
        dockerfile = Path(__file__).parent.parent / "Dockerfile"
        assert dockerfile.exists(), "Dockerfile should exist"

        content = dockerfile.read_text()
        lines = content.strip().split("\n")

        # Should have proper structure
        assert any(
            line.startswith("FROM ") for line in lines
        ), "Should have FROM instruction"
        assert any(
            line.startswith("WORKDIR ") for line in lines
        ), "Should set working directory"

        # Should not use latest tag
        from_lines = [line for line in lines if line.startswith("FROM ")]
        for from_line in from_lines:
            assert ":latest" not in from_line, "Should not use :latest tag"

    def test_docker_compose_deployment(self):
        """Test Docker Compose deployment configuration."""
        compose_file = Path(__file__).parent.parent / "docker-compose.windows.yml"
        if not compose_file.exists():
            pytest.skip("Docker Compose file not found")

        with open(compose_file) as f:
            config = yaml.safe_load(f)

        assert "services" in config, "Compose should define services"
        assert len(config["services"]) > 0, "Should have at least one service"

        # Check service configurations
        for service_name, service_config in config["services"].items():
            if "build" in service_config:
                print(f"Service {service_name} has build configuration")
            if "image" in service_config:
                print(f"Service {service_name} uses image: {service_config['image']}")

    def test_dockerignore_exists(self):
        """Test .dockerignore exists for efficient builds."""
        dockerignore = Path(__file__).parent.parent / ".dockerignore"
        if dockerignore.exists():
            content = dockerignore.read_text()

            # Should ignore common unnecessary files
            recommended_ignores = [
                ".git",
                "__pycache__",
                "*.pyc",
                ".pytest_cache",
            ]
            found_ignores = [
                ignore for ignore in recommended_ignores if ignore in content
            ]

            assert (
                len(found_ignores) > 0
            ), f"Should ignore some common files: {recommended_ignores}"
        else:
            print(
                "Info: .dockerignore not found - consider adding for better build performance"
            )

    def test_multi_stage_build_optimization(self):
        """Test Dockerfile uses multi-stage builds for optimization."""
        dockerfile = Path(__file__).parent.parent / "Dockerfile"
        if not dockerfile.exists():
            pytest.skip("Dockerfile not found")

        content = dockerfile.read_text()

        # Count FROM statements (indicates multi-stage)
        from_count = content.count("FROM ")

        if from_count > 1:
            print(f"Multi-stage build detected with {from_count} stages")
        else:
            print("Info: Single-stage build - consider multi-stage for optimization")


class TestGitHubPagesDeployment:
    """Test GitHub Pages deployment for documentation."""

    def test_pages_workflow_exists(self):
        """Test GitHub Pages deployment workflow exists."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        pages_workflows = []
        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                content = f.read()

            if any(
                keyword in content.lower()
                for keyword in ["pages", "github-pages", "docs"]
            ):
                pages_workflows.append(workflow_file.name)

        if pages_workflows:
            print(f"Found GitHub Pages workflows: {pages_workflows}")
        else:
            print("Info: GitHub Pages deployment not found")

    def test_mkdocs_deployment_ready(self):
        """Test MkDocs deployment readiness."""
        mkdocs_config = Path(__file__).parent.parent / "mkdocs.yml"
        if mkdocs_config.exists():
            with open(mkdocs_config) as f:
                config = yaml.safe_load(f)

            assert "site_name" in config, "MkDocs should have site name"
            assert "docs_dir" in config.get("docs_dir", "") or "docs" in str(
                config
            ), "Should specify docs directory"

            print("MkDocs configuration found - docs deployment ready")
        else:
            print("Info: MkDocs configuration not found")


class TestDeploymentErrorHandling:
    """Test deployment error handling and recovery."""

    def test_deployment_rollback_capability(self):
        """Test deployment rollback capability."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        rollback_patterns = ["rollback", "revert", "previous", "backup"]

        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                content = f.read()

            found_rollback = [
                pattern for pattern in rollback_patterns if pattern in content.lower()
            ]
            if found_rollback:
                print(f"Rollback capability in {workflow_file.name}: {found_rollback}")

    def test_deployment_health_checks(self):
        """Test deployment includes health checks."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        health_patterns = ["health", "status", "ping", "ready"]

        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                content = f.read()

            if any(
                keyword in workflow_file.name.lower() for keyword in ["deploy", "build"]
            ):
                found_health = [
                    pattern for pattern in health_patterns if pattern in content.lower()
                ]
                if found_health:
                    print(f"Health checks in {workflow_file.name}: {found_health}")
                else:
                    print(f"Info: {workflow_file.name} may lack health checks")

    def test_deployment_notification_on_failure(self):
        """Test deployment failure notifications."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        notification_patterns = ["slack", "email", "webhook", "notification"]

        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                content = f.read()

            if any(
                keyword in workflow_file.name.lower() for keyword in ["deploy", "build"]
            ):
                found_notifications = [
                    pattern
                    for pattern in notification_patterns
                    if pattern in content.lower()
                ]
                if found_notifications:
                    print(
                        f"Notifications in {workflow_file.name}: {found_notifications}"
                    )

    def test_deployment_retry_logic(self):
        """Test deployment retry logic for transient failures."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                workflow_config = yaml.safe_load(f)

            # Look for retry mechanisms
            jobs = workflow_config.get("jobs", {})
            for job_name, job_config in jobs.items():
                steps = job_config.get("steps", [])

                for step in steps:
                    if isinstance(step, dict) and "uses" in step:
                        if "retry" in step.get("with", {}):
                            print(
                                f"Retry logic found in {workflow_file.name}, step: {step.get('name', 'unnamed')}"
                            )


class TestDeploymentSecurity:
    """Test deployment security measures."""

    def test_deployment_secrets_protection(self):
        """Test deployment protects secrets properly."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                content = f.read()

            # Should not contain hardcoded secrets
            secret_patterns = ["sk-", "eyJ", "AIza", "ghp_"]
            found_secrets = [
                pattern for pattern in secret_patterns if pattern in content
            ]

            assert (
                not found_secrets
            ), f"Hardcoded secrets found in {workflow_file.name}: {found_secrets}"

    def test_deployment_environment_protection(self):
        """Test deployment uses environment protection."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                workflow_config = yaml.safe_load(f)

            # Check for environment protection
            jobs = workflow_config.get("jobs", {})
            for job_name, job_config in jobs.items():
                if "environment" in job_config:
                    environment = job_config["environment"]
                    print(
                        f"Environment protection in {workflow_file.name}: {environment}"
                    )

    def test_deployment_permission_restrictions(self):
        """Test deployment has appropriate permission restrictions."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                workflow_config = yaml.safe_load(f)

            # Check for permission restrictions
            if "permissions" in workflow_config:
                permissions = workflow_config["permissions"]

                # Should not grant excessive permissions
                if permissions == "write-all" or permissions == {}:
                    print(
                        f"Warning: {workflow_file.name} may have excessive permissions"
                    )
                else:
                    print(
                        f"Permission restrictions in {workflow_file.name}: {permissions}"
                    )


class TestDeploymentMonitoring:
    """Test deployment monitoring and observability."""

    def test_deployment_logging(self):
        """Test deployment includes proper logging."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                content = f.read()

            if any(
                keyword in workflow_file.name.lower() for keyword in ["deploy", "build"]
            ):
                # Should have logging statements
                logging_patterns = ["echo", "log", "print"]
                found_logging = [
                    pattern
                    for pattern in logging_patterns
                    if pattern in content.lower()
                ]

                if found_logging:
                    print(f"Logging in {workflow_file.name}: {found_logging}")
                else:
                    print(f"Info: {workflow_file.name} may lack logging")

    def test_deployment_metrics_collection(self):
        """Test deployment collects metrics."""
        # Check for metrics collection in deployment
        project_root = Path(__file__).parent.parent

        # Look for metrics-related files or scripts
        metrics_files = list(project_root.glob("*metric*")) + list(
            project_root.glob("*monitor*")
        )

        if metrics_files:
            print(f"Deployment metrics collection: {[f.name for f in metrics_files]}")
        else:
            print("Info: Deployment metrics collection not found")

    def test_deployment_status_reporting(self):
        """Test deployment reports status appropriately."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                workflow_config = yaml.safe_load(f)

            # Check for status reporting
            jobs = workflow_config.get("jobs", {})
            for job_name, job_config in jobs.items():
                steps = job_config.get("steps", [])

                status_steps = [
                    step
                    for step in steps
                    if isinstance(step, dict)
                    and any(
                        keyword in str(step).lower()
                        for keyword in ["status", "report", "notify"]
                    )
                ]

                if status_steps:
                    print(
                        f"Status reporting in {workflow_file.name}: {len(status_steps)} steps"
                    )


class TestDeploymentPerformance:
    """Test deployment performance optimization."""

    def test_deployment_caching(self):
        """Test deployment uses caching for performance."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                content = f.read()

            # Look for caching mechanisms
            cache_patterns = ["cache", "restore", "save"]
            found_caching = [
                pattern for pattern in cache_patterns if pattern in content.lower()
            ]

            if found_caching:
                print(f"Caching in {workflow_file.name}: {found_caching}")

    def test_deployment_parallelization(self):
        """Test deployment uses parallelization where possible."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                workflow_config = yaml.safe_load(f)

            # Check for parallel jobs
            jobs = workflow_config.get("jobs", {})

            if len(jobs) > 1:
                # Check for dependencies between jobs
                dependent_jobs = []
                for job_name, job_config in jobs.items():
                    if "needs" in job_config:
                        dependent_jobs.append(job_name)

                parallel_jobs = len(jobs) - len(dependent_jobs)
                if parallel_jobs > 1:
                    print(
                        f"Parallel execution in {workflow_file.name}: {parallel_jobs} parallel jobs"
                    )

    def test_deployment_resource_optimization(self):
        """Test deployment optimizes resource usage."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        for workflow_file in workflows_path.glob("*.yml"):
            with open(workflow_file) as f:
                workflow_config = yaml.safe_load(f)

            # Check for resource optimization
            jobs = workflow_config.get("jobs", {})
            for job_name, job_config in jobs.items():
                # Check for timeout settings (prevents resource waste)
                if "timeout-minutes" in job_config:
                    timeout = job_config["timeout-minutes"]
                    print(
                        f"Resource timeout in {workflow_file.name}: {timeout} minutes"
                    )

                # Check for runner selection
                if "runs-on" in job_config:
                    runner = job_config["runs-on"]
                    if "ubuntu-latest" in str(runner):
                        print(
                            f"Using optimized runner in {workflow_file.name}: {runner}"
                        )
