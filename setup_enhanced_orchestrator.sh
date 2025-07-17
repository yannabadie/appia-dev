#!/bin/bash

# 🚀 Enhanced GROK-4 Orchestrator - Quick Setup Script
# Version: 2025-07-17 with Claude 4 + Infinite Memory
# Description: Automated setup for the complete orchestrator environment

set -e  # Exit on any error

echo "🤖 Enhanced GROK-4 Orchestrator Setup"
echo "======================================"
echo "🎯 Setting up complete environment with Claude 4 integration"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
print_status "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    print_success "Python $PYTHON_VERSION detected (>= $REQUIRED_VERSION required)"
else
    print_error "Python $PYTHON_VERSION detected. Minimum required: $REQUIRED_VERSION"
    exit 1
fi

# Upgrade pip and core tools
print_status "Upgrading pip and core tools..."
python3 -m pip install --upgrade pip setuptools wheel
print_success "Core tools upgraded"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv .venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate
print_success "Virtual environment activated"

# Install Poetry if not present
if ! command -v poetry &> /dev/null; then
    print_status "Installing Poetry..."
    pip install poetry
    print_success "Poetry installed"
else
    print_success "Poetry already installed"
fi

# Install enhanced requirements
print_status "Installing enhanced requirements..."
if [ -f "requirements-enhanced.txt" ]; then
    pip install -r requirements-enhanced.txt
    print_success "Enhanced requirements installed"
else
    print_warning "requirements-enhanced.txt not found, installing basic requirements"
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
fi

# Install additional AI/ML packages that might fail individually
print_status "Installing additional AI packages..."
pip install --no-deps sentence-transformers || print_warning "sentence-transformers installation failed"
pip install torch --index-url https://download.pytorch.org/whl/cpu || print_warning "torch CPU installation failed"

# Poetry install if pyproject.toml exists
if [ -f "pyproject.toml" ]; then
    print_status "Running Poetry install..."
    poetry install --with dev || print_warning "Poetry install had some issues"
    print_success "Poetry dependencies processed"
fi

# Check critical environment variables
print_status "Checking environment variables..."

check_env_var() {
    if [ -z "${!1}" ]; then
        print_warning "$1 not set"
        return 1
    else
        print_success "$1 is set"
        return 0
    fi
}

ENV_OK=true
check_env_var "XAI_API_KEY" || ENV_OK=false
check_env_var "SUPABASE_URL" || ENV_OK=false
check_env_var "SUPABASE_KEY" || ENV_OK=false
check_env_var "GITHUB_TOKEN" || ENV_OK=false

# Optional but recommended
check_env_var "ANTHROPIC_API_KEY" || check_env_var "CLAUDE_API_KEY" || print_warning "Claude API key not set (optional)"
check_env_var "OPENAI_API_KEY" || print_warning "OpenAI API key not set (optional fallback)"

# Create .env template if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env template..."
    cat > .env << 'EOF'
# 🤖 Enhanced GROK-4 Orchestrator Environment Variables
# Copy this to .env and fill in your actual values

# Primary AI (Required)
XAI_API_KEY=your_xai_api_key_here

# Code Validation AI (Recommended) 
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# OR
CLAUDE_API_KEY=your_claude_api_key_here

# Fallback AI (Optional)
OPENAI_API_KEY=your_openai_api_key_here

# Infinite Memory System (Required)
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE=your_supabase_service_role_key_here

# Repository Management (Required)
GITHUB_TOKEN=your_github_token_here
GH_TOKEN=your_github_token_here

# Repository URLs (Default values)
GH_REPO_DEV=yannabadie/appia-dev
GH_REPO_AI=yannabadie/appIA

# Google Cloud Platform (Optional)
GCP_SA_JSON={"type":"service_account","project_id":"your_project"}

# Workspace Configuration
WORKSPACE_DIR=/workspaces/appia-dev
JARVYS_OBSERVATION_MODE=false
EOF
    print_success ".env template created"
else
    print_warning ".env already exists"
fi

# Test basic imports
print_status "Testing critical imports..."
python3 -c "
try:
    import xai_sdk
    print('✅ xAI SDK import successful')
except ImportError as e:
    print(f'❌ xAI SDK import failed: {e}')

try:
    import anthropic
    print('✅ Anthropic (Claude) import successful')
except ImportError as e:
    print(f'❌ Anthropic import failed: {e}')

try:
    import langgraph
    print('✅ LangGraph import successful')
except ImportError as e:
    print(f'❌ LangGraph import failed: {e}')

try:
    import supabase
    print('✅ Supabase import successful')
except ImportError as e:
    print(f'❌ Supabase import failed: {e}')

try:
    from github import Github
    print('✅ PyGithub import successful')
except ImportError as e:
    print(f'❌ PyGithub import failed: {e}')
"

# Run the enhanced test
if [ -f "test_enhanced_orchestrator.py" ]; then
    print_status "Running enhanced orchestrator test..."
    python3 test_enhanced_orchestrator.py || print_warning "Test completed with some warnings"
else
    print_warning "test_enhanced_orchestrator.py not found"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
print_success "Environment setup finished"
echo ""
echo "📋 Next Steps:"
echo "1. 📝 Edit .env file with your actual API keys"
echo "2. 🔧 Run: source .venv/bin/activate"
echo "3. 🧪 Test: python3 test_enhanced_orchestrator.py"
echo "4. 🚀 Launch: python3 grok_orchestrator.py"
echo ""
echo "📚 Features Available:"
echo "  🤖 Grok-4-0709 primary AI"
echo "  🔍 Claude 4 code validation"
echo "  🧠 Infinite memory system"
echo "  🌐 Technology verification"
echo "  🔄 Auto-sync repositories"
echo ""
echo "⚠️  Remember to set your environment variables in .env!"

if [ "$ENV_OK" = false ]; then
    echo ""
    print_warning "Some environment variables are missing. Check .env file!"
    exit 1
fi

print_success "🎯 Ready for autonomous operation!"
