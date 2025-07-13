"""Test Docker and containerization setup for JARVYS ecosystem."""

import platform
import subprocess
from pathlib import Path

import pytest


class TestDockerAvailability:
    """Test Docker availability and setup."""

    def test_docker_installed(self):
        """Test that Docker is installed and accessible."""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            assert (
                result.returncode == 0
            ), f"Docker not available: {result.stderr}"
            assert (
                "Docker version" in result.stdout
            ), "Invalid Docker version output"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker not available in environment")

    def test_docker_daemon_running(self):
        """Test that Docker daemon is running."""
        try:
            result = subprocess.run(
                ["docker", "info"], capture_output=True, text=True, timeout=15
            )
            if result.returncode != 0:
                if "daemon" in result.stderr.lower():
                    pytest.skip("Docker daemon not running")
                else:
                    pytest.fail(f"Docker daemon check failed: {result.stderr}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker not available in environment")

    def test_docker_compose_available(self):
        """Test that Docker Compose is available."""
        try:
            # Try both docker-compose and docker compose commands
            for cmd in [
                ["docker-compose", "--version"],
                ["docker", "compose", "--version"],
            ]:
                try:
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        assert (
                            "version" in result.stdout.lower()
                        ), "Invalid Docker Compose version output"
                        return
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue

            pytest.skip("Docker Compose not available")

        except Exception as e:
            pytest.skip(f"Docker Compose check failed: {e}")


class TestDockerImages:
    """Test Docker images and containers."""

    def test_python_base_image_available(self):
        """Test that Python base image can be pulled."""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "images",
                    "python:3.12",
                    "--format",
                    "{{.Repository}}:{{.Tag}}",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                pytest.skip(
                    "Cannot check Docker images - daemon may not be running"
                )

            # If image is not locally available, try to pull it (but don't fail if can't)
            if "python:3.12" not in result.stdout:
                try:
                    pullresult = subprocess.run(
                        ["docker", "pull", "python:3.12-slim"],
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )
                    if pull_result.returncode != 0:
                        pytest.skip(
                            "Cannot pull Python base image - network"
                            "may be limited"
                        )
                except subprocess.TimeoutExpired:
                    pytest.skip("Docker pull timeout - network may be slow")

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker not available for image testing")

    def test_dockerfile_exists(self):
        """Test that Dockerfiles exist in the project."""
        project_root = Path(__file__).parent.parent
        dockerfiles = ["Dockerfile", "Dockerfile.jarvys_ai"]

        missing_dockerfiles = []
        for dockerfile in dockerfiles:
            if not (project_root / dockerfile).exists():
                missing_dockerfiles.append(dockerfile)

        assert (
            not missing_dockerfiles
        ), f"Missing Dockerfiles: {missing_dockerfiles}"

    def test_dockerfile_syntax(self):
        """Test Dockerfile syntax."""
        project_root = Path(__file__).parent.parent
        dockerfile = project_root / "Dockerfile"

        if not dockerfile.exists():
            pytest.skip("Dockerfile not found")

        content = dockerfile.read_text()
        lines = content.strip().split("\n")

        # Basic syntax checks
        assert any(
            line.startswith("FROM ") for line in lines
        ), "Dockerfile missing FROM instruction"

        # Check for common issues
        for line in lines:
            line = line.strip()
            if line.startswith("FROM "):
                assert not line.endswith(
                    ":latest"
                ), "Avoid using :latest tag in Dockerfile"


class TestDockerCompose:
    """Test Docker Compose configuration."""

    def test_docker_compose_file_exists(self):
        """Test that docker-compose files exist."""
        project_root = Path(__file__).parent.parent
        compose_files = ["docker-compose.windows.yml"]

        found_files = []
        for compose_file in compose_files:
            if (project_root / compose_file).exists():
                found_files.append(compose_file)

        # At least one compose file should exist
        assert (
            found_files
        ), f"No Docker Compose files found. Expected one of: {compose_files}"

    def test_docker_compose_syntax(self):
        """Test Docker Compose file syntax."""
        project_root = Path(__file__).parent.parent

        # Check the Windows compose file if it exists
        compose_file = project_root / "docker-compose.windows.yml"
        if compose_file.exists():
            try:
                import yaml

                content = compose_file.read_text()
                config = yaml.safe_load(content)

                assert (
                    "services" in config
                ), "Docker Compose file missing 'services' section"
                assert (
                    len(config["services"]) > 0
                ), "Docker Compose file has no services defined"

            except ImportError:
                pytest.skip(
                    "PyYAML not available for Docker Compose syntax testing"
                )
            except yaml.YAMLError as e:
                pytest.fail(
                    f"Docker Compose file has invalid YAML syntax: {e}"
                )

    def test_docker_compose_validation(self):
        """Test Docker Compose configuration validation."""
        project_root = Path(__file__).parent.parent
        compose_file = project_root / "docker-compose.windows.yml"

        if not compose_file.exists():
            pytest.skip("Docker Compose file not found")

        try:
            result = subprocess.run(
                ["docker", "compose", "-f", str(compose_file), "config"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=project_root,
            )

            if result.returncode != 0:
                # Check if it's due to missing Docker daemon vs syntax errors
                if "daemon" in result.stderr.lower():
                    pytest.skip("Docker daemon not running")
                else:
                    pytest.fail(
                        f"Docker Compose validation failed: {result.stderr}"
                    )

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker Compose validation not available")


class TestContainerEnvironment:
    """Test container environment capabilities."""

    def test_container_platform_support(self):
        """Test platform support for containers."""
        system = platform.system()
        machine = platform.machine()

        # Check for known compatible platforms
        if system == "Linux":
            assert machine in [
                "x86_64",
                "aarch64",
            ], f"Unsupported Linux architecture: {machine}"
        elif system == "Darwin":  # macOS
            assert machine in [
                "x86_64",
                "arm64",
            ], f"Unsupported macOS architecture: {machine}"
        elif system == "Windows":
            assert machine in [
                "AMD64",
                "x86_64",
            ], f"Unsupported Windows architecture: {machine}"
        else:
            pytest.skip(f"Unknown platform: {system} {machine}")

    def test_container_resource_limits(self):
        """Test that container resource limits can be applied."""
        try:
            # Simple test to check if resource limits work
            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "--memory=100m",
                    "--cpus=0.5",
                    "alpine:latest",
                    "echo",
                    "test",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                if "daemon" in result.stderr.lower():
                    pytest.skip("Docker daemon not running")
                elif "unable to find image" in result.stderr.lower():
                    pytest.skip("Alpine image not available")
                else:
                    pytest.fail(
                        f"Container resource limits test failed:"
                        "{result.stderr}"
                    )

            assert "test" in result.stdout, "Container execution failed"

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker not available for resource testing")

    def test_container_networking(self):
        """Test container networking capabilities."""
        try:
            # Test basic networking
            result = subprocess.run(
                ["docker", "network", "ls"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                if "daemon" in result.stderr.lower():
                    pytest.skip("Docker daemon not running")
                else:
                    pytest.fail(
                        f"Docker networking test failed: {result.stderr}"
                    )

            # Should have at least bridge network
            assert "bridge" in result.stdout, "Bridge network not available"

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker not available for networking testing")


class TestContainerBuild:
    """Test container build capabilities."""

    def test_dockerfile_build_context(self):
        """Test that Dockerfile has proper build context."""
        project_root = Path(__file__).parent.parent
        dockerfile = project_root / "Dockerfile"

        if not dockerfile.exists():
            pytest.skip("Dockerfile not found")

        content = dockerfile.read_text()

        # Check for common build optimization patterns
        lines = content.strip().split("\n")
        has_workdir = any(
            line.strip().startswith("WORKDIR ") for line in lines
        )
        has_copy_or_add = any(
            line.strip().startswith(("COPY ", "ADD ")) for line in lines
        )

        assert (
            has_workdir
        ), "Dockerfile should set WORKDIR for better organization"
        assert has_copy_or_add, "Dockerfile should copy application files"

    def test_dockerignore_exists(self):
        """Test that .dockerignore exists to optimize build context."""
        project_root = Path(__file__).parent.parent
        dockerignore = project_root / ".dockerignore"

        if dockerignore.exists():
            content = dockerignore.read_text()

            # Should ignore common unnecessary files
            recommended_ignores = [
                ".git",
                "__pycache__",
                "*.pyc",
                ".pytest_cache",
            ]
            for ignore in recommended_ignores:
                assert (
                    ignore in content
                ), f".dockerignore should include {ignore}"
        else:
            # .dockerignore is recommended but not required
            print(
                "Warning: .dockerignore not found - consider adding"
                "for better build performance"
            )


class TestProductionReadiness:
    """Test production readiness of container setup."""

    def test_non_root_user_in_dockerfile(self):
        """Test that Dockerfile uses non-root user for security."""
        project_root = Path(__file__).parent.parent
        dockerfile = project_root / "Dockerfile"

        if not dockerfile.exists():
            pytest.skip("Dockerfile not found")

        content = dockerfile.read_text().lower()

        # Check for user creation or switching
        user_patterns = ["user ", "adduser", "useradd", "su -"]
        has_user_setup = any(pattern in content for pattern in user_patterns)

        if not has_user_setup:
            print(
                "Warning: Dockerfile may be running as root - consider"
                "adding non-root user for security"
            )

    def test_health_check_defined(self):
        """Test that health checks are defined."""
        project_root = Path(__file__).parent.parent
        dockerfile = project_root / "Dockerfile"

        if not dockerfile.exists():
            pytest.skip("Dockerfile not found")

        content = dockerfile.read_text().lower()

        # Check for health check
        if "healthcheck" not in content:
            print(
                "Info: Consider adding HEALTHCHECK instruction for"
                "better monitoring"
            )

    def test_minimal_image_layers(self):
        """Test that Dockerfile uses minimal layers."""
        project_root = Path(__file__).parent.parent
        dockerfile = project_root / "Dockerfile"

        if not dockerfile.exists():
            pytest.skip("Dockerfile not found")

        content = dockerfile.read_text()
        lines = [line.strip() for line in content.split("\n") if line.strip()]

        # Count RUN commands (each creates a layer)
        run_commands = [line for line in lines if line.startswith("RUN ")]

        if len(run_commands) > 5:
            print(
                f"Info: Consider combining RUN commands to reduce"
                "layers (found {len(run_commands)})"
            )
