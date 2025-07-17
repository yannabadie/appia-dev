#!/bin/bash
# Quick setup script for xAI API key

echo "🔧 xAI API Key Setup Helper"
echo "=========================="

# Check current status
echo "Current XAI_API_KEY status:"
if [ -z "$XAI_API_KEY" ]; then
    echo "❌ XAI_API_KEY is empty or not set"
else
    echo "✅ XAI_API_KEY is set (length: ${#XAI_API_KEY} chars)"
    echo "   Preview: ${XAI_API_KEY:0:8}...${XAI_API_KEY: -4}"
fi

echo ""
echo "📋 To fix this:"
echo "1. Get your API key from: https://console.x.ai/team/default/api-keys"
echo "2. Set it with: export XAI_API_KEY='your-real-key-here'"
echo "3. Test with: python -c 'from grok_orchestrator import validate_grok_api; validate_grok_api()'"
echo ""
echo "🚀 Once set, run: poetry run python grok_orchestrator.py"
