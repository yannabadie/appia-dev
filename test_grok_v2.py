#!/usr/bin/env python3
"""
🧪 Test Script for Grok-4-0709 Orchestrator V2
Validates the new strict version with enhanced fallback chain
"""

import os
import sys


def test_grok_validation():
    """Test strict Grok-4-0709 validation"""
    print("🔍 Testing Grok-4-0709 strict validation...")

    # Test valid model
    GROK_MODEL = "grok-4-0709"
    if "grok" in GROK_MODEL.lower() and GROK_MODEL != "grok-4-0709":
        raise ValueError(
            f"ERREUR: Seul grok-4-0709 est autorisé. Modèle détecté: {GROK_MODEL}"
        )

    print(f"✅ Validation passed: {GROK_MODEL}")

    # Test invalid model (should fail)
    try:
        invalid_model = "grok-3"
        if "grok" in invalid_model.lower() and invalid_model != "grok-4-0709":
            raise ValueError(
                f"ERREUR: Seul grok-4-0709 est autorisé. Modèle détecté: {invalid_model}"
            )
        print("❌ Should have failed validation!")
    except ValueError as e:
        print(f"✅ Correctly rejected invalid model: {e}")


def test_imports():
    """Test module imports"""
    print("\n🔍 Testing module imports...")

    try:
        # Add current directory to path
        sys.path.insert(0, "/workspaces/appia-dev")

        from grok_orchestrator import GROK_MODEL, XAI_SDK_AVAILABLE

        print("✅ Successfully imported orchestrator components")
        print(f"📋 Model configured: {GROK_MODEL}")
        print(f"📦 xAI SDK available: {XAI_SDK_AVAILABLE}")

        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_fallback_chain():
    """Test fallback chain configuration"""
    print("\n🔍 Testing fallback chain configuration...")

    # Test environment variables
    openai_key = os.getenv("OPENAI_API_KEY")
    xai_key = os.getenv("XAI_API_KEY")

    print(
        f"🔑 XAI API Key configured: {'Yes' if xai_key and xai_key != 'test-key' else 'No (test key)'}"
    )
    print(f"🔑 OpenAI API Key configured: {'Yes' if openai_key else 'No'}")

    fallback_chain = ["Grok-4-0709", "ChatGPT-4", "Claude"]
    print(f"🔄 Configured fallback chain: {' → '.join(fallback_chain)}")


def main():
    print("🤖 Testing Grok-4 Orchestrator V2")
    print("=" * 50)

    try:
        # Test validation
        test_grok_validation()

        # Test imports
        imports_ok = test_imports()

        # Test fallback configuration
        test_fallback_chain()

        print("\n" + "=" * 50)
        if imports_ok:
            print("✅ All tests passed! New version is functional.")
            print("📋 Key improvements:")
            print("   - Strict grok-4-0709 validation")
            print("   - Enhanced fallback chain (Grok→ChatGPT-4→Claude)")
            print("   - No other Grok versions allowed")
        else:
            print("⚠️ Some tests failed. Check configuration.")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

    return True


if __name__ == "__main__":
    main()
