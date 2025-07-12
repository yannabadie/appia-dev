#!/bin/bash
# 🚀 JARVYS Dashboard - Manual Deployment Script for Supabase
#
# This script manually deploys the JARVYS Dashboard to Supabase Edge Functions
# Use this when you need to deploy outside of the automated GitHub Actions

set -e

echo "🚀 JARVYS Dashboard - Manual Deployment to Supabase"
echo "=" * 55

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Supabase CLI is installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v supabase &> /dev/null; then
        print_error "Supabase CLI not found. Installing..."
        npm install -g supabase@latest
    fi
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is required but not installed."
        exit 1
    fi
    
    print_success "Dependencies verified"
}

# Verify project structure
verify_structure() {
    print_status "Verifying project structure..."
    
    if [ ! -f "supabase/functions/jarvys-dashboard/index.ts" ]; then
        print_error "Edge Function file not found: supabase/functions/jarvys-dashboard/index.ts"
        exit 1
    fi
    
    if [ ! -f "supabase/config.toml" ]; then
        print_warning "supabase/config.toml not found, but continuing..."
    fi
    
    print_success "Project structure verified"
}

# Authenticate with Supabase
authenticate() {
    print_status "Authenticating with Supabase..."
    
    if [ -z "$SUPABASE_SERVICE_ROLE" ]; then
        print_warning "SUPABASE_SERVICE_ROLE not set as environment variable"
        echo "Please enter your Supabase service role token:"
        read -s SUPABASE_SERVICE_ROLE
        export SUPABASE_SERVICE_ROLE
    fi
    
    if [ -z "$SUPABASE_PROJECT_ID" ]; then
        print_warning "SUPABASE_PROJECT_ID not set as environment variable"
        echo "Please enter your Supabase project ID:"
        read SUPABASE_PROJECT_ID
        export SUPABASE_PROJECT_ID
    fi
    
    echo "$SUPABASE_SERVICE_ROLE" | supabase auth login --token -
    print_success "Authentication successful"
}

# Deploy the Edge Function
deploy_function() {
    print_status "Deploying JARVYS Dashboard Edge Function..."
    
    supabase functions deploy jarvys-dashboard \
        --project-ref "$SUPABASE_PROJECT_ID" \
        --no-verify-jwt
    
    print_success "Edge Function deployed successfully"
}

# Configure secrets
configure_secrets() {
    print_status "Configuring secrets..."
    
    if [ ! -z "$SPB_EDGE_FUNCTIONS" ]; then
        supabase secrets set SPB_EDGE_FUNCTIONS="$SPB_EDGE_FUNCTIONS" \
            --project-ref "$SUPABASE_PROJECT_ID"
        print_success "Secret SPB_EDGE_FUNCTIONS configured"
    else
        print_warning "SPB_EDGE_FUNCTIONS not set. Dashboard will use default configuration."
        # Set a default secret
        DEFAULT_SECRET="dHx8o@3?G4!QT86C"
        supabase secrets set SPB_EDGE_FUNCTIONS="$DEFAULT_SECRET" \
            --project-ref "$SUPABASE_PROJECT_ID"
        print_success "Default secret configured"
    fi
}

# Test the deployment
test_deployment() {
    print_status "Testing deployment..."
    
    FUNCTION_URL="https://$SUPABASE_PROJECT_ID.supabase.co/functions/v1/jarvys-dashboard"
    
    # Wait a moment for deployment to be effective
    sleep 5
    
    # Test health endpoint
    print_status "Testing health endpoint..."
    if curl -f -s "$FUNCTION_URL/health" > /dev/null; then
        print_success "Health check passed"
    else
        print_error "Health check failed"
        return 1
    fi
    
    # Test API status
    print_status "Testing API status endpoint..."
    if curl -f -s "$FUNCTION_URL/api/status" > /dev/null; then
        print_success "API status check passed"
    else
        print_warning "API status check failed (may be normal for first deployment)"
    fi
    
    print_success "Deployment tests completed"
}

# Display summary
show_summary() {
    echo ""
    echo "🎉 JARVYS Dashboard Successfully Deployed!"
    echo "=" * 50
    echo ""
    echo "🌐 Dashboard URL:"
    echo "   https://$SUPABASE_PROJECT_ID.supabase.co/functions/v1/jarvys-dashboard"
    echo ""
    echo "📚 Available API Endpoints:"
    echo "   GET  /                - Dashboard main page"
    echo "   GET  /api/status      - System status"
    echo "   GET  /api/metrics     - Performance metrics"
    echo "   GET  /api/data        - Complete dashboard data"
    echo "   GET  /api/tasks       - Recent tasks"
    echo "   POST /api/chat        - Chat with JARVYS"
    echo "   GET  /health          - Health check"
    echo ""
    echo "🔐 Secrets configured:"
    echo "   ✅ SPB_EDGE_FUNCTIONS"
    echo ""
    echo "📈 Dashboard is now online and operational!"
    echo ""
    echo "🔗 Access your dashboard: https://$SUPABASE_PROJECT_ID.supabase.co/functions/v1/jarvys-dashboard"
}

# Main execution
main() {
    echo "Starting manual deployment process..."
    echo ""
    
    check_dependencies
    verify_structure
    authenticate
    deploy_function
    configure_secrets
    test_deployment
    show_summary
    
    print_success "Manual deployment completed successfully!"
}

# Run main function
main "$@"
