#!/usr/bin/env python3
"""
Quick test script for xAI API key validation
"""

import os

from grok_orchestrator import GROK_MODEL, XAI_API_KEY, validate_grok_api


def test_xai_setup():
    print("🔍 xAI API Setup Diagnostics")
    print("=" * 50)

    print(
        f"📊 XAI_API_KEY: {XAI_API_KEY[:8]}...{XAI_API_KEY[-4:] if len(XAI_API_KEY) > 12 else XAI_API_KEY}"
    )
    print(f"🤖 GROK_MODEL: {GROK_MODEL}")
    print(
        f"🔧 SDK Available: {os.path.exists('.venv/lib/python3.12/site-packages/xai_sdk')}"
    )

    print("\n🧪 Testing API Connection...")

    if XAI_API_KEY == "test-key":
        print("❌ ISSUE: Still using test-key!")
        print("🔧 SOLUTION: Set real API key from console.x.ai")
        print("   export XAI_API_KEY='your-real-key-here'")
        return False

    result = validate_grok_api()

    if result:
        print("✅ SUCCESS: xAI API is working!")
        print("🚀 Ready to run: poetry run python grok_orchestrator.py")
    else:
        print("❌ FAILED: Check your API key and internet connection")
        print("🔧 Verify: https://console.x.ai/team/default/api-keys")

    return result


if __name__ == "__main__":
    test_xai_setup()
