#!/usr/bin/env python3
"""
JARVYS_AI Sync and Deployment Script
Syncs JARVYS_AI code to appIA repository and implements continuous improvement
"""

import json
import logging
import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class JarvysAISync:
    def __init__(self):
        self.workspace_path = Path("/workspaces/appia-dev")
        self.jarvys_ai_path = self.workspace_path / "jarvys_ai"
        self.target_repo = "yannabadie/appIA"
        self.temp_dir = None

    def create_temp_workspace(self):
        """Create temporary workspace for appIA repo"""
        self.temp_dir = tempfile.mkdtemp(prefix="jarvys_sync_")
        logger = logging.getLogger(__name__).info(
            f"Created temporary workspace: {self.temp_dir}"
        )
        return self.temp_dir

    def clone_target_repo(self):
        """Clone the appIA repository"""
        try:
            cmd = f"gh repo clone {self.target_repo} {self.temp_dir}/appIA"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger = logging.getLogger(__name__).error(
                    f"Failed to clone repo: {result.stderr}"
                )
                return False
            logger = logging.getLogger(__name__).info(
                "Successfully cloned appIA repository"
            )
            return True
        except Exception as e:
            logger = logging.getLogger(__name__).error(f"Error cloning repo: {e}")
            return False

    def sync_jarvys_ai_code(self):
        """Sync JARVYS_AI code to appIA repository"""
        try:
            target_path = Path(self.temp_dir) / "appIA"

            # Create main directory structure
            jarvys_target = target_path / "jarvys_ai"
            jarvys_target.mkdir(exist_ok=True)

            # Copy all JARVYS_AI files
            for item in self.jarvys_ai_path.rglob("*"):
                if item.is_file() and not item.name.endswith(".pyc"):
                    relative_path = item.relative_to(self.jarvys_ai_path)
                    target_file = jarvys_target / relative_path
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target_file)
                    logger = logging.getLogger(__name__).info(
                        f"Copied: {relative_path}"
                    )

            # Copy related files
            files_to_copy = [
                "requirements-jarvys-ai.txt",
                "Dockerfile.jarvys_ai",
                "docker-compose.windows.yml",
                "test_jarvys_ai_complete.py",
                "WINDOWS11_DOCKER_SETUP.md",
                "DEPLOY_ECOSYSTEM_COMPLETE.md",
            ]

            for file_name in files_to_copy:
                source_file = self.workspace_path / file_name
                if source_file.exists():
                    shutil.copy2(source_file, target_path / file_name)
                    logger = logging.getLogger(__name__).info(f"Copied: {file_name}")

            # Copy docker directory
            docker_source = self.workspace_path / "docker"
            if docker_source.exists():
                docker_target = target_path / "docker"
                if docker_target.exists():
                    shutil.rmtree(docker_target)
                shutil.copytree(docker_source, docker_target)
                logger = logging.getLogger(__name__).info("Copied docker directory")

            return True
        except Exception as e:
            logger = logging.getLogger(__name__).error(f"Error syncing code: {e}")
            return False

    def create_readme(self):
        """Create comprehensive README for appIA repository"""
        readme_content = """# JARVYS_AI - Digital Twin Assistant

JARVYS_AI is a comprehensive digital twin of Yann Abadie, designed to provide unlimited human-like capabilities including voice/text interaction, email management, cloud integration, and file management.

## 🚀 Features

- **Digital Twin Intelligence**: Full digital representation with personality, preferences, and knowledge
- **Voice & Text Interface**: Natural conversation capabilities with speech synthesis and recognition
- **Email Management**: Automated Outlook/Gmail integration with intelligent responses
- **Cloud Integration**: GCP, Azure, AWS, and MCP (Model Context Protocol) support
- **File Management**: Local and cloud file operations with intelligent organization
- **Continuous Improvement**: Self-updating capabilities via JARVYS_DEV integration
- **Fallback Engine**: Automatic Cloud Run deployment when GitHub Actions quotas are exhausted

## 🏗️ Architecture

```
jarvys_ai/
├── main.py                    # Main orchestrator
├── intelligence_core.py       # Core AI intelligence
├── digital_twin.py           # Digital twin personality and knowledge
├── continuous_improvement.py  # Self-improvement mechanisms
├── fallback_engine.py        # Cloud Run fallback system
├── dashboard_integration.py   # Supabase dashboard integration
└── extensions/
    ├── email_manager.py       # Email automation
    ├── voice_interface.py     # Voice/speech capabilities
    ├── cloud_manager.py       # Multi-cloud operations
    └── file_manager.py        # File system operations
```

## 🐳 Windows 11 Docker Setup

### Prerequisites
- Docker Desktop for Windows
- WSL2 enabled
- Windows 11 with audio support

### Quick Start
```bash
# Clone repository
git clone https://github.com/yannabadie/appIA.git
cd appIA

# Build and run with Docker Compose
docker-compose -f docker-compose.windows.yml up --build

# Access JARVYS_AI
# Voice interface will be available on audio devices
# Web interface on http://localhost:8000
```

### Manual Docker Build
```bash
# Build image
docker build -f Dockerfile.jarvys_ai -t jarvys_ai .

# Run with audio support
docker run -it --rm \
  --device /dev/snd \
  -p 8000:8000 \
  -e JARVYS_MODE=production \
  jarvys_ai
```

## 🔧 Configuration

### Environment Variables
```bash
# Core Configuration
JARVYS_MODE=development|production
JARVYS_LOG_LEVEL=INFO|DEBUG|WARNING|ERROR

# API Keys (set via GitHub secrets or local .env)
OPENAI_API_KEY=your_openai_key
GOOGLE_CLOUD_PROJECT=your_gcp_project
AZURE_SUBSCRIPTION_ID=your_azure_subscription
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# Email Configuration
OUTLOOK_CLIENT_ID=your_outlook_client_id
OUTLOOK_CLIENT_SECRET=your_outlook_client_secret
GMAIL_CREDENTIALS_PATH=path_to_gmail_credentials.json

# Supabase Integration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

## 🧪 Testing

```bash
# Run comprehensive test suite
python test_jarvys_ai_complete.py

# Run specific module tests
python -m pytest tests/ -v

# Test Docker container
docker run --rm jarvys_ai python -m pytest tests/ -v
```

## 📊 Dashboard Integration

JARVYS_AI integrates with the JARVYS_DEV dashboard for monitoring and control:

- **Real-time Status**: Current operations and health metrics
- **Task Management**: View and manage ongoing tasks
- **Performance Metrics**: CPU, memory, and operation statistics
- **Chat Interface**: Direct communication with JARVYS_AI
- **Continuous Improvement**: Track self-improvement progress

Dashboard URL: https://kzcswopokvknxmxczilu.supabase.co/functions/v1/jarvys-dashboard/

## 🔄 Continuous Improvement

JARVYS_AI continuously improves through:

1. **Learning from Interactions**: Adapts based on user feedback and patterns
2. **Code Self-Modification**: Updates its own algorithms and responses
3. **External Integration**: Learns from JARVYS_DEV dashboard and external APIs
4. **Fallback Learning**: Optimizes performance based on Cloud Run experiences

## 🌤️ Cloud Run Fallback

When GitHub Actions quotas are exhausted, JARVYS_AI automatically deploys to Google Cloud Run:

1. **Automatic Detection**: Monitors GitHub Actions quota usage
2. **Seamless Migration**: Deploys to Cloud Run without data loss
3. **Continued Operation**: Maintains all functionality in cloud environment
4. **Cost Optimization**: Automatically scales down when not in use

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, please open an issue or contact the development team through the JARVYS_DEV dashboard.

---

**JARVYS_AI** - Your unlimited digital twin assistant, powered by advanced AI and continuous improvement.
"""

        try:
            target_path = Path(self.temp_dir) / "appIA" / "README.md"
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
            logger = logging.getLogger(__name__).info("Created comprehensive README.md")
            return True
        except Exception as e:
            logger = logging.getLogger(__name__).error(f"Error creating README: {e}")
            return False

    def create_deployment_script(self):
        """Create deployment script for appIA"""
        deploy_script = """#!/bin/bash
# JARVYS_AI Deployment Script for appIA

set -e

echo "🚀 JARVYS_AI Deployment Starting..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop for Windows."
    exit 1
fi

# Check if running on Windows with WSL2
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "✅ Running on WSL2"
else
    echo "⚠️  Not running on WSL2. Audio features may not work properly."
fi

# Build JARVYS_AI image
echo "🏗️  Building JARVYS_AI Docker image..."
docker build -f Dockerfile.jarvys_ai -t jarvys_ai:latest .

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file template..."
    cat > .env << EOL
# JARVYS_AI Configuration
JARVYS_MODE=development
JARVYS_LOG_LEVEL=INFO

# API Keys (replace with actual values)
OPENAI_API_KEY=your_openai_key_here
GOOGLE_CLOUD_PROJECT=your_gcp_project_here

# Optional: Email Configuration
OUTLOOK_CLIENT_ID=your_outlook_client_id
GMAIL_CREDENTIALS_PATH=./config/gmail_credentials.json

# Supabase Integration
SUPABASE_URL=https://kzcswopokvknxmxczilu.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
EOL
    echo "⚠️  Please update .env file with your actual API keys before running JARVYS_AI"
fi

# Run JARVYS_AI with Docker Compose
echo "🎯 Starting JARVYS_AI..."
docker-compose -f docker-compose.windows.yml up -d

echo "✅ JARVYS_AI deployed successfully!"
echo "📊 Dashboard: http://localhost:8000"
echo "🎤 Voice interface will be available on your audio devices"
echo "📝 Check logs: docker-compose -f docker-compose.windows.yml logs -"
"""

        try:
            target_path = Path(self.temp_dir) / "appIA" / "deploy.sh"
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(deploy_script)
            os.chmod(target_path, 0o755)
            logger = logging.getLogger(__name__).info("Created deployment script")
            return True
        except Exception as e:
            logger = logging.getLogger(__name__).error(
                f"Error creating deployment script: {e}"
            )
            return False

    def create_continuous_improvement_config(self):
        """Create configuration for continuous improvement"""
        config = {
            "jarvys_ai": {
                "version": "1.0.0",
                "last_sync": datetime.now().isoformat(),
                "continuous_improvement": {
                    "enabled": True,
                    "sync_interval_hours": 24,
                    "dashboard_url": "https://kzcswopokvknxmxczilu.supabase.co/functions/v1/jarvys-dashboard",
                    "fallback_cloud_run": {
                        "enabled": True,
                        "project_id": "your-gcp-project",
                        "region": "us-central1",
                        "service_name": "jarvys-ai-fallback",
                    },
                },
                "features": {
                    "voice_interface": True,
                    "email_management": True,
                    "cloud_integration": True,
                    "file_management": True,
                    "digital_twin": True,
                    "dashboard_integration": True,
                },
                "api_integrations": {
                    "openai": "required",
                    "google_cloud": "optional",
                    "azure": "optional",
                    "aws": "optional",
                    "outlook": "optional",
                    "gmail": "optional",
                },
            }
        }

        try:
            target_path = Path(self.temp_dir) / "appIA" / "jarvys_config.json"
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            logger.info(f"Created continuous improvement config: {config}")
            return True
        except Exception as e:
            logger.error(f"Error creating config: {e}")
            return False

    def commit_and_push(self):
        """Commit and push changes to appIA repository"""
        try:
            repo_path = Path(self.temp_dir) / "appIA"
            os.chdir(repo_path)

            # Configure git
            subprocess.run(
                ["git", "config", "user.name", "JARVYS_DEV"], check=True
            )
            subprocess.run(
                ["git", "config", "user.email", "jarvys@appia-dev.ai"],
                check=True,
            )

            # Add all files
            subprocess.run(["git", "add", "."], check=True)

            # Check if there are changes to commit
            result = subprocess.run(
                ["git", "dif", "--staged", "--quiet"], capture_output=True
            )
            if result.returncode == 0:
                logger = logging.getLogger(__name__).info("No changes to commit")
                return True

            # Commit changes
            commit_message = (
                f"JARVYS_AI Sync - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            subprocess.run(["git", "commit", "-m", commit_message], check=True)

            # Push changes
            subprocess.run(["git", "push", "origin", "main"], check=True)

            logger = logging.getLogger(__name__).info(
                "Successfully committed and pushed changes to appIA repository"
            )
            return True
        except subprocess.CalledProcessError as e:
            logger = logging.getLogger(__name__).error(f"Git operation failed: {e}")
            return False
        except Exception as e:
            logger = logging.getLogger(__name__).error(
                f"Error committing and pushing: {e}"
            )
            return False

    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger = logging.getLogger(__name__).info("Cleaned up temporary workspace")

    def run_sync(self):
        """Run the complete sync process"""
        try:
            logger = logging.getLogger(__name__).info(
                "🚀 Starting JARVYS_AI sync to appIA repository..."
            )

            # Create temporary workspace
            self.create_temp_workspace()

            # Clone target repository
            if not self.clone_target_repo():
                return False

            # Sync JARVYS_AI code
            if not self.sync_jarvys_ai_code():
                return False

            # Create documentation and configuration
            if not self.create_readme():
                return False

            if not self.create_deployment_script():
                return False

            if not self.create_continuous_improvement_config():
                return False

            # Commit and push changes
            if not self.commit_and_push():
                return False

            logger = logging.getLogger(__name__).info(
                "✅ JARVYS_AI sync completed successfully!"
            )
            logger = logging.getLogger(__name__).info(
                f"📍 Repository: https://github.com/{self.target_repo}"
            )
            return True

        except Exception as e:
            logger = logging.getLogger(__name__).error(f"Sync process failed: {e}")
            return False
        finally:
            self.cleanup()


def main():
    """Main function"""
    sync = JarvysAISync()
    success = sync.run_sync()

    if success:
        print("\n🎉 JARVYS_AI has been successfully synced to the appIA repository!")
        print("🔗 Repository: https://github.com/yannabadie/appIA")
        print("📚 Check the README.md for deployment instructions")
        print("🐳 Use deploy.sh for quick Windows 11 Docker setup")
    else:
        print("\n❌ Sync process failed. Check the logs for details.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
