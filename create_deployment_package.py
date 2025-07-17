#!/usr/bin/env python3
"""
📦 JARVYS_AI Deployment Package Creator
Creates a complete deployment package with all necessary files
"""

import json
import logging
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class JarvysDeploymentPackager:
    """Creates comprehensive deployment packages for JARVYS_AI"""

    def __init__(self):
        self.workspace_path = Path("/workspaces/appia-dev")
        self.jarvys_ai_path = self.workspace_path / "jarvys_ai"
        self.output_path = self.workspace_path / "deployment_packages"

    def create_deployment_package(self):
        """Create a complete deployment package"""
        try:
            # Create output directory
            self.output_path.mkdir(exist_ok=True)

            # Create package directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            package_name = f"jarvys_ai_complete_{timestamp}"
            package_path = self.output_path / package_name
            package_path.mkdir(exist_ok=True)

            logging.getLogger(__name__).info(
                f"📦 Creating deployment package: {package_name}"
            )

            # Copy JARVYS_AI core files
            self._copy_jarvys_ai_core(package_path)

            # Copy Docker and deployment files
            self._copy_deployment_files(package_path)

            # Copy documentation
            self._copy_documentation(package_path)

            # Create configuration files
            self._create_configuration_files(package_path)

            # Create deployment scripts
            self._create_deployment_scripts(package_path)

            # Create README
            self._create_package_readme(package_path)

            # Create ZIP archive
            zip_path = self._create_zip_archive(package_path, package_name)

            logging.getLogger(__name__).info(
                f"✅ Deployment package created: {zip_path}"
            )
            return zip_path

        except Exception as e:
            logging.getLogger(__name__).error(
                f"❌ Error creating deployment package: {e}"
            )
            return None

    def _copy_jarvys_ai_core(self, package_path: Path):
        """Copy JARVYS_AI core modules"""
        logging.getLogger(__name__).info("📁 Copying JARVYS_AI core modules...")

        jarvys_target = package_path / "jarvys_ai"
        jarvys_target.mkdir(exist_ok=True)

        # Copy all Python files except __pycache__
        for item in self.jarvys_ai_path.rglob("*"):
            if (
                item.is_file()
                and not item.name.endswith(".pyc")
                and "__pycache__" not in str(item)
            ):
                relative_path = item.relative_to(self.jarvys_ai_path)
                target_file = jarvys_target / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target_file)

        logging.getLogger(__name__).info("✅ JARVYS_AI core modules copied")

    def _copy_deployment_files(self, package_path: Path):
        """Copy Docker and deployment files"""
        logging.getLogger(__name__).info("🐳 Copying deployment files...")

        files_to_copy = [
            "requirements-jarvys-ai.txt",
            "Dockerfile.jarvys_ai",
            "docker-compose.windows.yml",
            "test_jarvys_ai_complete.py",
        ]

        for file_name in files_to_copy:
            source_file = self.workspace_path / file_name
            if source_file.exists():
                shutil.copy2(source_file, package_path / file_name)

        # Copy docker directory
        docker_source = self.workspace_path / "docker"
        if docker_source.exists():
            docker_target = package_path / "docker"
            shutil.copytree(docker_source, docker_target)

        logging.getLogger(__name__).info("✅ Deployment files copied")

    def _copy_documentation(self, package_path: Path):
        """Copy documentation files"""
        logging.getLogger(__name__).info("📚 Copying documentation...")

        docs_to_copy = [
            "WINDOWS11_DOCKER_SETUP.md",
            "DEPLOY_ECOSYSTEM_COMPLETE.md",
            "DASHBOARD_CLOUD.md",
            "DEPLOYMENT_FIX_SUMMARY.md",
        ]

        docs_dir = package_path / "docs"
        docs_dir.mkdir(exist_ok=True)

        for doc_name in docs_to_copy:
            source_doc = self.workspace_path / doc_name
            if source_doc.exists():
                shutil.copy2(source_doc, docs_dir / doc_name)

        logging.getLogger(__name__).info("✅ Documentation copied")

    def _create_configuration_files(self, package_path: Path):
        """Create configuration files"""
        logging.getLogger(__name__).info("⚙️ Creating configuration files...")

        # Main configuration
        config = {
            "jarvys_ai": {
                "version": "1.0.0",
                "build_date": datetime.now().isoformat(),
                "deployment": {
                    "mode": "production",
                    "supported_platforms": [
                        "windows",
                        "linux",
                        "docker",
                        "cloud_run",
                    ],
                    "requirements": {
                        "python": ">=3.9",
                        "docker": ">=20.0",
                        "memory": "4GB",
                        "storage": "10GB",
                    },
                },
                "features": {
                    "voice_interface": True,
                    "email_management": True,
                    "cloud_integration": True,
                    "file_management": True,
                    "digital_twin": True,
                    "continuous_improvement": True,
                    "fallback_engine": True,
                    "dashboard_integration": True,
                },
                "integrations": {
                    "supabase_dashboard": "https://kzcswopokvknxmxczilu.supabase.co/functions/v1/jarvys-dashboard",
                    "github_repo": "yannabadie/appIA",
                    "cloud_run": {
                        "region": "us-central1",
                        "service_name": "jarvys-ai-fallback",
                    },
                },
            }
        }

        config_file = package_path / "jarvys_config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        # Environment template
        env_template = """# JARVYS_AI Environment Configuration
# Copy this file to .env and update with your actual values

# Basic Configuration
JARVYS_MODE=production
JARVYS_LOG_LEVEL=INFO
JARVYS_DEBUG=false

# API Keys (replace with actual values)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Cloud Provider Configurations (optional)
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
AZURE_SUBSCRIPTION_ID=your_azure_subscription_id
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# Email Configuration (optional)
OUTLOOK_CLIENT_ID=your_outlook_client_id
OUTLOOK_CLIENT_SECRET=your_outlook_client_secret
GMAIL_CREDENTIALS_PATH=./config/gmail_credentials.json

# Supabase Integration
SUPABASE_URL=https://kzcswopokvknxmxczilu.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key

# GitHub Integration (for continuous improvement)
GITHUB_TOKEN=your_github_token
GITHUB_REPO=yannabadie/appIA

# Voice Interface (Windows only)
VOICE_ENABLED=true
VOICE_LANGUAGE=en-US
"""

        env_file = package_path / ".env.template"
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_template)

        logging.getLogger(__name__).info("✅ Configuration files created")

    def _create_deployment_scripts(self, package_path: Path):
        """Create deployment scripts"""
        logging.getLogger(__name__).info("📝 Creating deployment scripts...")

        # Windows deployment script
        windows_script = """@echo off
REM JARVYS_AI Windows Deployment Script

echo Starting JARVYS_AI Windows Deployment...

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

REM Check for .env file
if not exist .env (
    echo Creating .env file from template...
    copy .env.template .env
    echo.
    echo IMPORTANT: Please edit .env file with your API keys before continuing.
    echo Press any key when you have updated the .env file...
    pause
)

REM Build and run JARVYS_AI
echo Building JARVYS_AI Docker image...
docker build -f Dockerfile.jarvys_ai -t jarvys_ai:latest .

if %errorlevel% neq 0 (
    echo Error: Docker build failed.
    pause
    exit /b 1
)

echo Starting JARVYS_AI...
docker-compose -f docker-compose.windows.yml up -d

if %errorlevel% neq 0 (
    echo Error: Failed to start JARVYS_AI.
    pause
    exit /b 1
)

echo.
echo ✅ JARVYS_AI deployed successfully!
echo 🌐 Web interface: http://localhost:8000
echo 🎤 Voice interface will be available on your audio devices
echo 📝 Check logs: docker-compose -f docker-compose.windows.yml logs -f
echo.
pause
"""

        windows_script_path = package_path / "deploy_windows.bat"
        with open(windows_script_path, "w", encoding="utf-8") as f:
            f.write(windows_script)

        # Linux/Mac deployment script
        linux_script = """#!/bin/bash
# JARVYS_AI Linux/Mac Deployment Script

set -e

echo "🚀 Starting JARVYS_AI Deployment..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.template .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your API keys before continuing."
    echo "Press Enter when you have updated the .env file..."
    read
fi

# Build JARVYS_AI image
echo "🏗️  Building JARVYS_AI Docker image..."
docker build -f Dockerfile.jarvys_ai -t jarvys_ai:latest .

# Start JARVYS_AI
echo "🎯 Starting JARVYS_AI..."
docker-compose -f docker-compose.windows.yml up -d

echo ""
echo "✅ JARVYS_AI deployed successfully!"
echo "🌐 Web interface: http://localhost:8000"
echo "📝 Check logs: docker-compose -f docker-compose.windows.yml logs -"
echo "🛑 Stop JARVYS_AI: docker-compose -f docker-compose.windows.yml down"
"""

        linux_script_path = package_path / "deploy_linux.sh"
        with open(linux_script_path, "w", encoding="utf-8") as f:
            f.write(linux_script)
        os.chmod(linux_script_path, 0o755)

        # Cloud deployment script
        cloud_script = """#!/bin/bash
# JARVYS_AI Cloud Deployment Script (Google Cloud Run)

set -e

echo "☁️  Starting JARVYS_AI Cloud Deployment..."

# Check required tools
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK is not installed."
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    exit 1
fi

# Configuration
read -p "Enter your Google Cloud Project ID: " PROJECT_ID
read -p "Enter region (default: us-central1): " REGION
REGION=${REGION:-us-central1}
SERVICE_NAME="jarvys-ai"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Build and deploy
echo "🏗️  Building and deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \\
    --source . \\
    --platform managed \\
    --region $REGION \\
    --allow-unauthenticated \\
    --memory 2Gi \\
    --cpu 2 \\
    --max-instances 10 \\
    --set-env-vars="JARVYS_MODE=production"

echo ""
echo "✅ JARVYS_AI deployed to Cloud Run successfully!"
echo "🌐 Access your deployment at the URL shown above"
"""

        cloud_script_path = package_path / "deploy_cloud.sh"
        with open(cloud_script_path, "w", encoding="utf-8") as f:
            f.write(cloud_script)
        os.chmod(cloud_script_path, 0o755)

        logging.getLogger(__name__).info("✅ Deployment scripts created")

    def _create_package_readme(self, package_path: Path):
        """Create comprehensive README for the package"""
        logging.getLogger(__name__).info("📄 Creating package README...")

        readme_content = """# JARVYS_AI - Complete Deployment Package

This package contains everything needed to deploy JARVYS_AI, your unlimited digital twin assistant.

## 🚀 Quick Start

### Windows (with Docker Desktop)
1. Ensure Docker Desktop is running
2. Double-click `deploy_windows.bat`
3. Follow the prompts to configure your API keys
4. Access JARVYS_AI at http://localhost:8000

### Linux/Mac
1. Ensure Docker is installed and running
2. Run `./deploy_linux.sh`
3. Follow the prompts to configure your API keys
4. Access JARVYS_AI at http://localhost:8000

### Cloud Deployment (Google Cloud Run)
1. Install Google Cloud SDK
2. Run `./deploy_cloud.sh`
3. Follow the prompts
4. Access your cloud deployment

## 📁 Package Contents

```
jarvys_ai/                     # Core JARVYS_AI modules
├── main.py                    # Main orchestrator
├── intelligence_core.py       # AI intelligence engine
├── digital_twin.py           # Digital twin personality
├── continuous_improvement.py  # Self-improvement system
├── fallback_engine.py        # Cloud Run fallback
├── dashboard_integration.py   # Supabase integration
└── extensions/               # Feature extensions
    ├── voice_interface.py    # Voice/speech capabilities
    ├── email_manager.py      # Email automation
    ├── cloud_manager.py      # Multi-cloud operations
    └── file_manager.py       # File management

docker/                       # Docker support files
├── start.sh                 # Container startup script
└── healthcheck.sh           # Health monitoring

docs/                        # Documentation
├── WINDOWS11_DOCKER_SETUP.md
├── DEPLOY_ECOSYSTEM_COMPLETE.md
└── ... other documentation

Dockerfile.jarvys_ai         # Docker image definition
docker-compose.windows.yml   # Docker Compose configuration
requirements-jarvys-ai.txt   # Python dependencies
jarvys_config.json          # JARVYS_AI configuration
.env.template               # Environment variables template

deploy_windows.bat          # Windows deployment script
deploy_linux.sh             # Linux/Mac deployment script
deploy_cloud.sh             # Cloud deployment script
```

## ⚙️ Configuration

### Required Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for AI capabilities
- `JARVYS_MODE`: Set to 'production' for deployment

### Optional Configuration
- `GOOGLE_CLOUD_PROJECT`: For cloud integration
- `OUTLOOK_CLIENT_ID`: For email management
- `SUPABASE_URL`: For dashboard integration

See `.env.template` for complete configuration options.

## 🎯 Features

### Core Capabilities
- **Digital Twin Intelligence**: Full personality simulation of Yann Abadie
- **Voice Interface**: Natural speech interaction (Windows with audio support)
- **Email Management**: Automated Outlook/Gmail integration
- **Cloud Integration**: GCP, Azure, AWS support
- **File Management**: Local and cloud file operations
- **Continuous Improvement**: Self-updating from GitHub repository
- **Fallback Engine**: Automatic Cloud Run deployment when needed

### Dashboard Integration
- Real-time monitoring via Supabase dashboard
- Performance metrics and health status
- Task management and chat interface
- Continuous improvement tracking

Dashboard URL: https://kzcswopokvknxmxczilu.supabase.co/functions/v1/jarvys-dashboard/

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_jarvys_ai_complete.py
```

## 📊 Monitoring

### Local Monitoring
- Health endpoint: http://localhost:8000/health
- Metrics endpoint: http://localhost:8000/metrics
- Logs: `docker-compose logs -f`

### Cloud Monitoring
- Google Cloud Console for Cloud Run deployments
- Supabase dashboard for real-time status

## 🔄 Continuous Improvement

JARVYS_AI automatically:
1. Checks for updates from the GitHub repository
2. Applies safe code improvements
3. Reports performance metrics
4. Manages GitHub Actions quota
5. Falls back to Cloud Run when needed

## 🛠️ Troubleshooting

### Common Issues

**Docker build fails:**
- Ensure Docker Desktop is running
- Check available disk space (need ~10GB)
- Verify internet connection for downloading dependencies

**Voice interface not working:**
- Ensure you're on Windows with audio devices
- Check Docker Desktop audio passthrough settings
- Verify microphone permissions

**API errors:**
- Check your API keys in `.env` file
- Ensure APIs have sufficient quota/credits
- Verify network connectivity

**Cloud deployment fails:**
- Ensure Google Cloud SDK is authenticated: `gcloud auth login`
- Verify billing is enabled on your GCP project
- Check project permissions for Cloud Run

### Getting Help

1. Check the logs: `docker-compose logs -f`
2. Review the documentation in the `docs/` folder
3. Visit the dashboard for real-time status
4. Check GitHub repository for updates

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

JARVYS_AI continuously improves itself, but manual contributions are welcome:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

**JARVYS_AI** - Your unlimited digital twin assistant, now ready to deploy anywhere.

For support and updates: https://github.com/yannabadie/appIA
"""

        readme_path = package_path / "README.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        logging.getLogger(__name__).info("✅ Package README created")

    def _create_zip_archive(self, package_path: Path, package_name: str) -> Path:
        """Create ZIP archive of the deployment package"""
        logging.getLogger(__name__).info("🗜️ Creating ZIP archive...")

        zip_path = self.output_path / f"{package_name}.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in package_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(package_path)
                    zipf.write(file_path, arcname)

        # Calculate size
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        logging.getLogger(__name__).info(
            f"✅ ZIP archive created: {zip_path.name} ({size_mb:.1f} MB)"
        )

        return zip_path


def main():
    """Main function"""
    packager = JarvysDeploymentPackager()

    print("📦 JARVYS_AI Deployment Package Creator")
    print("=" * 50)

    zip_path = packager.create_deployment_package()

    if zip_path:
        print("\n🎉 Deployment package created successfully!")
        print(f"📁 Location: {zip_path}")
        print(f"📏 Size: {zip_path.stat().st_size / (1024 * 1024):.1f} MB")
        print("\n📋 Next Steps:")
        print("1. Extract the ZIP file to your deployment location")
        print("2. Follow the README.md instructions")
        print("3. Run the appropriate deployment script for your platform")
        print(
            "\n🌐 Dashboard: https://kzcswopokvknxmxczilu.supabase.co/functions/v1/jarvys-dashboard/"
        )
    else:
        print("\n❌ Failed to create deployment package")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
