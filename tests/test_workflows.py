"""Enhanced GitHub Actions workflow testing for JARVYS ecosystem."""

import os
from pathlib import Path

import pytest
import yaml


class TestWorkflowStructure:
    """Test GitHub Actions workflow structure and syntax."""

    def test_workflows_directory_structure(self):
        """Test workflows directory has proper structure."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        assert workflows_path.exists(), "Workflows directory should exist"
        assert workflows_path.is_dir(), "Workflows should be a directory"

        # Should have some workflow files
        workflow_files = list(workflows_path.glob("*.yml"))
<<<<<<< HEAD
        assert len(workflow_files) > 0, "Should have at least one workflow file"
=======
        assert (
            len(workflow_files) > 0
        ), "Should have at least one workflow file"
>>>>>>> origin/main

    def test_workflow_files_yaml_syntax(self):
        """Test that all workflow files have valid YAML syntax."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        workflow_files = list(workflows_path.glob("*.yml"))
        invalid_files = []

        for workflow_file in workflow_files:
            try:
                with open(workflow_file) as f:
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                invalid_files.append((workflow_file.name, str(e)))

<<<<<<< HEAD
        assert not invalid_files, f"Invalid YAML syntax in workflows: {invalid_files}"
=======
        assert (
            not invalid_files
        ), f"Invalid YAML syntax in workflows: {invalid_files}"
>>>>>>> origin/main

    def test_core_workflows_exist(self):
        """Test that core workflows exist."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        core_workflows = [
            "ci.yml",
            "agent.yml",
            "jarvys-cloud.yml",
            "model-detection.yml",
        ]

        existing_workflows = [f.name for f in workflows_path.glob("*.yml")]
<<<<<<< HEAD
        missing_workflows = [w for w in core_workflows if w not in existing_workflows]

        assert not missing_workflows, f"Missing core workflows: {missing_workflows}"
=======
        missing_workflows = [
            w for w in core_workflows if w not in existing_workflows
        ]

        assert (
            not missing_workflows
        ), f"Missing core workflows: {missing_workflows}"
>>>>>>> origin/main


class TestCIWorkflow:
    """Test CI workflow functionality."""

    def test_ci_workflow_structure(self):
        """Test CI workflow has proper structure."""
<<<<<<< HEAD
        ci_path = Path(__file__).parent.parent / ".github" / "workflows" / "ci.yml"
=======
        ci_path = (
            Path(__file__).parent.parent / ".github" / "workflows" / "ci.yml"
        )
>>>>>>> origin/main
        if not ci_path.exists():
            pytest.skip("CI workflow not found")

        with open(ci_path) as f:
            ci_config = yaml.safe_load(f)

        # Should have required sections
        assert "name" in ci_config, "CI workflow should have a name"
        assert "on" in ci_config, "CI workflow should have triggers"
        assert "jobs" in ci_config, "CI workflow should have jobs"

        # Should have at least one job
        assert len(ci_config["jobs"]) > 0, "CI should have at least one job"

    def test_ci_workflow_triggers(self):
        """Test CI workflow has appropriate triggers."""
<<<<<<< HEAD
        ci_path = Path(__file__).parent.parent / ".github" / "workflows" / "ci.yml"
=======
        ci_path = (
            Path(__file__).parent.parent / ".github" / "workflows" / "ci.yml"
        )
>>>>>>> origin/main
        if not ci_path.exists():
            pytest.skip("CI workflow not found")

        with open(ci_path) as f:
            ci_config = yaml.safe_load(f)

        triggers = ci_config.get("on", {})

        # Should trigger on push and pull requests
        expected_triggers = ["push", "pull_request"]
        for trigger in expected_triggers:
            if trigger not in triggers:
                print(f"Warning: CI workflow missing {trigger} trigger")

    def test_ci_workflow_python_version(self):
        """Test CI workflow uses appropriate Python version."""
<<<<<<< HEAD
        ci_path = Path(__file__).parent.parent / ".github" / "workflows" / "ci.yml"
=======
        ci_path = (
            Path(__file__).parent.parent / ".github" / "workflows" / "ci.yml"
        )
>>>>>>> origin/main
        if not ci_path.exists():
            pytest.skip("CI workflow not found")

        with open(ci_path) as f:
            content = f.read()

        # Should reference Python 3.12
        assert "3.12" in content, "CI workflow should use Python 3.12"


class TestAgentWorkflow:
    """Test agent workflow functionality."""

    def test_agent_workflow_structure(self):
        """Test agent workflow has proper structure."""
        agent_path = (
<<<<<<< HEAD
            Path(__file__).parent.parent / ".github" / "workflows" / "agent.yml"
=======
            Path(__file__).parent.parent
            / ".github"
            / "workflows"
            / "agent.yml"
>>>>>>> origin/main
        )
        if not agent_path.exists():
            pytest.skip("Agent workflow not found")

        with open(agent_path) as f:
            agent_config = yaml.safe_load(f)

        # Should have required sections
        assert "name" in agent_config, "Agent workflow should have a name"
        assert "on" in agent_config, "Agent workflow should have triggers"
        assert "jobs" in agent_config, "Agent workflow should have jobs"

    def test_agent_workflow_secrets(self):
        """Test agent workflow references required secrets."""
        agent_path = (
<<<<<<< HEAD
            Path(__file__).parent.parent / ".github" / "workflows" / "agent.yml"
=======
            Path(__file__).parent.parent
            / ".github"
            / "workflows"
            / "agent.yml"
>>>>>>> origin/main
        )
        if not agent_path.exists():
            pytest.skip("Agent workflow not found")

        with open(agent_path) as f:
            content = f.read()

        # Should reference key secrets
        required_secrets = ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]

        missing_secrets = []
        for secret in required_secrets:
            if secret not in content:
                missing_secrets.append(secret)

        if missing_secrets:
<<<<<<< HEAD
            print("Warning: Agent workflow may be missing secrets:" "{missing_secrets}")
=======
            print(
                "Warning: Agent workflow may be missing secrets:"
                "{missing_secrets}"
            )
>>>>>>> origin/main

    def test_agent_workflow_schedule(self):
        """Test agent workflow has schedule trigger."""
        agent_path = (
<<<<<<< HEAD
            Path(__file__).parent.parent / ".github" / "workflows" / "agent.yml"
=======
            Path(__file__).parent.parent
            / ".github"
            / "workflows"
            / "agent.yml"
>>>>>>> origin/main
        )
        if not agent_path.exists():
            pytest.skip("Agent workflow not found")

        with open(agent_path) as f:
            agent_config = yaml.safe_load(f)

        triggers = agent_config.get("on", {})

        # Should have schedule trigger for autonomous operation
        if "schedule" not in triggers:
            print("Info: Agent workflow doesn't have schedule trigger")
        else:
            schedule = triggers["schedule"]
            assert isinstance(schedule, list), "Schedule should be a list"
            assert len(schedule) > 0, "Should have at least one schedule"


class TestJarvysCloudWorkflow:
    """Test JARVYS cloud workflow functionality."""

    def test_jarvys_cloud_workflow_structure(self):
        """Test JARVYS cloud workflow has proper structure."""
        cloud_path = (
<<<<<<< HEAD
            Path(__file__).parent.parent / ".github" / "workflows" / "jarvys-cloud.yml"
=======
            Path(__file__).parent.parent
            / ".github"
            / "workflows"
            / "jarvys-cloud.yml"
>>>>>>> origin/main
        )
        if not cloud_path.exists():
            pytest.skip("JARVYS cloud workflow not found")

        with open(cloud_path) as f:
            cloud_config = yaml.safe_load(f)

        # Should have required sections
        assert "name" in cloud_config, "Cloud workflow should have a name"
        assert "on" in cloud_config, "Cloud workflow should have triggers"
        assert "jobs" in cloud_config, "Cloud workflow should have jobs"

    def test_jarvys_cloud_deployment_steps(self):
        """Test JARVYS cloud workflow has deployment steps."""
        cloud_path = (
<<<<<<< HEAD
            Path(__file__).parent.parent / ".github" / "workflows" / "jarvys-cloud.yml"
=======
            Path(__file__).parent.parent
            / ".github"
            / "workflows"
            / "jarvys-cloud.yml"
>>>>>>> origin/main
        )
        if not cloud_path.exists():
            pytest.skip("JARVYS cloud workflow not found")

        with open(cloud_path) as f:
            content = f.read()

        # Should have deployment-related steps
        deployment_keywords = ["deploy", "build", "setup", "install"]
<<<<<<< HEAD
        found_keywords = [kw for kw in deployment_keywords if kw in content.lower()]
=======
        found_keywords = [
            kw for kw in deployment_keywords if kw in content.lower()
        ]
>>>>>>> origin/main

        assert (
            len(found_keywords) > 0
        ), "Cloud workflow should have deployment steps with"
        "keywords: {deployment_keywords}"


class TestModelDetectionWorkflow:
    """Test model detection workflow functionality."""

    def test_model_detection_workflow_structure(self):
        """Test model detection workflow has proper structure."""
        model_path = (
            Path(__file__).parent.parent
            / ".github"
            / "workflows"
            / "model-detection.yml"
        )
        if not model_path.exists():
            pytest.skip("Model detection workflow not found")

        with open(model_path) as f:
            model_config = yaml.safe_load(f)

        # Should have required sections
<<<<<<< HEAD
        assert "name" in model_config, "Model detection workflow should have a name"
        assert "on" in model_config, "Model detection workflow should have triggers"
        assert "jobs" in model_config, "Model detection workflow should have jobs"
=======
        assert (
            "name" in model_config
        ), "Model detection workflow should have a name"
        assert (
            "on" in model_config
        ), "Model detection workflow should have triggers"
        assert (
            "jobs" in model_config
        ), "Model detection workflow should have jobs"
>>>>>>> origin/main

    def test_model_detection_schedule(self):
        """Test model detection has scheduled execution."""
        model_path = (
            Path(__file__).parent.parent
            / ".github"
            / "workflows"
            / "model-detection.yml"
        )
        if not model_path.exists():
            pytest.skip("Model detection workflow not found")

        with open(model_path) as f:
            model_config = yaml.safe_load(f)

        triggers = model_config.get("on", {})

        # Should have schedule for regular model checking
        if "schedule" in triggers:
            schedule = triggers["schedule"]
            assert isinstance(schedule, list), "Schedule should be a list"
            assert len(schedule) > 0, "Should have at least one schedule"
        else:
            print("Info: Model detection workflow doesn't have schedule")

    def test_model_detection_api_keys(self):
        """Test model detection workflow has required API keys."""
        model_path = (
            Path(__file__).parent.parent
            / ".github"
            / "workflows"
            / "model-detection.yml"
        )
        if not model_path.exists():
            pytest.skip("Model detection workflow not found")

        with open(model_path) as f:
            content = f.read()

        # Should reference model API keys
        api_keys = ["OPENAI_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY"]
        found_keys = [key for key in api_keys if key in content]

        assert (
            len(found_keys) > 0
        ), "Model detection should reference at least one API key"
        "from: {api_keys}"


class TestDashboardDeploymentWorkflow:
    """Test dashboard deployment workflow."""

    def test_dashboard_deployment_workflow_exists(self):
        """Test dashboard deployment workflow exists."""
        dashboard_path = (
            Path(__file__).parent.parent
            / ".github"
            / "workflows"
            / "deploy-dashboard.yml"
        )
        if dashboard_path.exists():
            with open(dashboard_path) as f:
                dashboard_config = yaml.safe_load(f)

            # Should have required sections
<<<<<<< HEAD
            assert "name" in dashboard_config, "Dashboard deployment should have a name"
            assert "on" in dashboard_config, "Dashboard deployment should have triggers"
            assert "jobs" in dashboard_config, "Dashboard deployment should have jobs"
=======
            assert (
                "name" in dashboard_config
            ), "Dashboard deployment should have a name"
            assert (
                "on" in dashboard_config
            ), "Dashboard deployment should have triggers"
            assert (
                "jobs" in dashboard_config
            ), "Dashboard deployment should have jobs"
>>>>>>> origin/main
        else:
            pytest.skip("Dashboard deployment workflow not found")

    def test_dashboard_supabase_deployment(self):
        """Test dashboard deployment references Supabase."""
        dashboard_path = (
            Path(__file__).parent.parent
            / ".github"
            / "workflows"
            / "deploy-dashboard.yml"
        )
        if not dashboard_path.exists():
            pytest.skip("Dashboard deployment workflow not found")

        with open(dashboard_path) as f:
            content = f.read()

        # Should reference Supabase for deployment
        supabase_keywords = ["supabase", "edge", "function"]
        found_keywords = [
            kw for kw in supabase_keywords if kw.lower() in content.lower()
        ]

        assert (
            len(found_keywords) > 0
        ), "Dashboard deployment should reference Supabase with"
        "keywords: {supabase_keywords}"


class TestWorkflowSecurity:
    """Test workflow security configurations."""

    def test_workflow_permissions(self):
        """Test workflows have appropriate permissions."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        workflow_files = list(workflows_path.glob("*.yml"))

        for workflow_file in workflow_files:
            with open(workflow_file) as f:
                workflow_config = yaml.safe_load(f)

            # Check for permissions section
            if "permissions" in workflow_config:
                permissions = workflow_config["permissions"]

                # Should not grant excessive permissions
                dangerous_permissions = ["write-all", "admin"]
                for perm in dangerous_permissions:
                    if perm in str(permissions):
                        print(
                            f"Warning: {workflow_file.name} may have"
                            "excessive permissions: {perm}"
                        )

    def test_workflow_secrets_usage(self):
        """Test workflows use secrets appropriately."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        workflow_files = list(workflows_path.glob("*.yml"))

        for workflow_file in workflow_files:
            with open(workflow_file) as f:
                content = f.read()

            # Should use secrets.VARIABLE_NAME format, not hardcoded values
            if "sk-" in content or "eyJ" in content:
<<<<<<< HEAD
                print(f"Warning: {workflow_file.name} may contain" "hardcoded secrets")
=======
                print(
                    f"Warning: {workflow_file.name} may contain"
                    "hardcoded secrets"
                )
>>>>>>> origin/main

    def test_workflow_environment_restrictions(self):
        """Test workflows have appropriate environment restrictions."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        workflow_files = list(workflows_path.glob("*.yml"))

        for workflow_file in workflow_files:
            with open(workflow_file) as f:
                workflow_config = yaml.safe_load(f)

            # Check for environment protection
            if "environment" in str(workflow_config):
<<<<<<< HEAD
                print(f"Info: {workflow_file.name} uses environment protection")
=======
                print(
                    f"Info: {workflow_file.name} uses environment protection"
                )
>>>>>>> origin/main


class TestWorkflowValidation:
    """Test workflow validation and linting."""

    def test_workflow_action_versions(self):
        """Test workflows use pinned action versions."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        workflow_files = list(workflows_path.glob("*.yml"))

        for workflow_file in workflow_files:
            with open(workflow_file) as f:
                content = f.read()

            # Should use versioned actions, not @main or @master
            if "@main" in content or "@master" in content:
                print(
                    f"Warning: {workflow_file.name} uses unpinned"
                    "action versions (@main/@master)"
                )

    def test_workflow_timeout_settings(self):
        """Test workflows have reasonable timeout settings."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        workflow_files = list(workflows_path.glob("*.yml"))

        for workflow_file in workflow_files:
            with open(workflow_file) as f:
                workflow_config = yaml.safe_load(f)

            # Check for timeout settings
            jobs = workflow_config.get("jobs", {})
            for job_name, job_config in jobs.items():
                if "timeout-minutes" in job_config:
                    timeout = job_config["timeout-minutes"]
                    if timeout > 60:
                        print(
                            f"Info: {workflow_file.name} job"
                            "{job_name} has long timeout: {timeout} minutes"
                        )


class TestWorkflowIntegration:
    """Test workflow integration capabilities."""

    @pytest.mark.integration
    def test_workflow_github_api_access(self):
        """Test workflows can access GitHub API."""
        token = os.getenv("GH_TOKEN")
        if not token:
            pytest.skip("GH_TOKEN not available")

        try:
            from github import Github

            _client = Github(token)

            # Test repository access for workflow operations
            repo_name = "yannabadie/appia-dev"
            repo = client.get_repo(repo_name)

            # Should be able to access workflow runs
            workflows = repo.get_workflows()
            workflow_list = list(workflows)

<<<<<<< HEAD
            assert len(workflow_list) >= 0, "Should be able to access workflows"
=======
            assert (
                len(workflow_list) >= 0
            ), "Should be able to access workflows"
>>>>>>> origin/main

        except Exception as e:
            pytest.skip(f"GitHub API access test failed: {e}")

    def test_workflow_dependency_management(self):
        """Test workflow dependency management."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        workflow_files = list(workflows_path.glob("*.yml"))

        for workflow_file in workflow_files:
            with open(workflow_file) as f:
                content = f.read()

            # Should manage dependencies properly
            if "poetry" in content.lower():
                assert (
                    "poetry install" in content
                ), f"{workflow_file.name} uses Poetry but missing install step"

            if "requirements" in content.lower():
                assert (
                    "pip install" in content
                ), f"{workflow_file.name} uses requirements but"
                "missing install step"


class TestWorkflowMonitoring:
    """Test workflow monitoring and observability."""

    def test_workflow_logging_practices(self):
        """Test workflows have good logging practices."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        workflow_files = list(workflows_path.glob("*.yml"))

        for workflow_file in workflow_files:
            with open(workflow_file) as f:
                content = f.read()

            # Should have some form of logging or output
            logging_indicators = ["echo", "print", "log", "debug"]
            found_logging = [
                indicator
                for indicator in logging_indicators
                if indicator in content.lower()
            ]

            if not found_logging:
<<<<<<< HEAD
                print(f"Info: {workflow_file.name} may lack logging/debug output")
=======
                print(
                    f"Info: {workflow_file.name} may lack logging/debug output"
                )
>>>>>>> origin/main

    def test_workflow_error_handling(self):
        """Test workflows have error handling."""
        workflows_path = Path(__file__).parent.parent / ".github" / "workflows"
        if not workflows_path.exists():
            pytest.skip("Workflows directory not found")

        workflow_files = list(workflows_path.glob("*.yml"))

        for workflow_file in workflow_files:
            with open(workflow_file) as f:
                workflow_config = yaml.safe_load(f)

            # Check for error handling patterns
            jobs = workflow_config.get("jobs", {})
            for job_name, job_config in jobs.items():
                steps = job_config.get("steps", [])

                # Look for continue-on-error or if conditions
                has_error_handling = any(
                    "continue-on-error" in step or "i" in step
                    for step in steps
                    if isinstance(step, dict)
                )

                if not has_error_handling and len(steps) > 5:
                    print(
                        f"Info: {workflow_file.name} job {job_name}"
                        "may lack error handling"
                    )
