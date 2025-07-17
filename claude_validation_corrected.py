# Enhanced Claude code validation function - CORRECTED VERSION
import json
import re
import time

try:
    import anthropic  # noqa: F401

    CLAUDE_AVAILABLE = True
    CLAUDE_MODELS = {
        "opus": "claude-opus-4-20250514",
        "sonnet": "claude-sonnet-4-20250514",
        "haiku": "claude-3-haiku-20240307",
    }
except ImportError:
    CLAUDE_AVAILABLE = False
    CLAUDE_MODELS = {}

try:
    from enhanced_system_prompts import get_enhanced_prompts

    enhanced_prompts = get_enhanced_prompts()
    ENHANCED_PROMPTS_AVAILABLE = True
except ImportError:
    enhanced_prompts = None
    ENHANCED_PROMPTS_AVAILABLE = False

import os

CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")


def store_memory(
    memory_type: str, content: dict, importance: float = 0.5, tags: list = None
):
    """Fallback store_memory function"""
    print(f"📝 Memory stored: {memory_type} (importance: {importance})")


def validate_code_with_claude_enhanced(
    code: str, task_description: str, grok_metadata: dict = None
) -> dict:
    """Use Claude 4 to validate and improve generated code with enhanced analysis and contextual prompts"""
    if not CLAUDE_AVAILABLE or not CLAUDE_API_KEY:
        return {"validated": False, "message": "Claude not available"}

    try:
        print("🔍 Validating code with enhanced Claude 4 analysis...")

        import anthropic

        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

        # Use Claude 4 Opus for complex code analysis or Sonnet for faster validation
        model = CLAUDE_MODELS.get(
            "opus", CLAUDE_MODELS.get("sonnet", "claude-3-haiku-20240307")
        )

        # Use enhanced prompts if available
        if enhanced_prompts and ENHANCED_PROMPTS_AVAILABLE:
            try:
                validation_prompt = enhanced_prompts.get_claude_validation_prompt(
                    code=code,
                    task_description=task_description,
                    grok_metadata=grok_metadata or {},
                )

                print(
                    "🎯 Using enhanced Claude validation prompt with full security analysis"
                )

                # Store prompt usage for learning
                store_memory(
                    "prompt_usage",
                    {
                        "prompt_type": "enhanced_claude_validation",
                        "task": task_description[:100],
                        "code_length": len(code),
                        "enhanced_features": [
                            "security_analysis",
                            "performance_metrics",
                            "jarvys_integration",
                        ],
                    },
                    importance=0.7,
                    tags=["prompts", "claude", "validation", "enhancement"],
                )

            except Exception as e:
                print(f"⚠️ Enhanced Claude prompt failed, using fallback: {e}")
                validation_prompt = f"""You are Claude 4, an expert code reviewer. Analyze this Python code:

Task: {task_description}

Code:
```python
{code}
```

Provide JSON analysis with is_valid, confidence, issues, and suggestions."""
        else:
            validation_prompt = f"""You are Claude 4, an expert code reviewer. Analyze this Python code:

Task: {task_description}

Code:
```python
{code}
```

Provide JSON analysis with is_valid, confidence, issues, and suggestions."""

        response = client.messages.create(
            model=model,
            max_tokens=6000,
            temperature=0.1,
            messages=[{"role": "user", "content": validation_prompt}],
        )

        result_text = response.content[0].text if response.content else ""

        # Extract JSON from response
        try:
            if "```json" in result_text:
                json_match = re.search(r"```json\n(.*?)\n```", result_text, re.DOTALL)
                if json_match:
                    result_json = json.loads(json_match.group(1))
                else:
                    result_json = {
                        "validated": False,
                        "message": "Could not parse Claude response",
                    }
            else:
                # Try to find JSON in the response
                json_start = result_text.find("{")
                json_end = result_text.rfind("}")
                if json_start != -1 and json_end != -1:
                    json_str = result_text[json_start : json_end + 1]
                    result_json = json.loads(json_str)
                else:
                    result_json = {
                        "validated": False,
                        "message": "No JSON found in Claude response",
                    }

        except json.JSONDecodeError as e:
            result_json = {
                "validated": False,
                "message": f"Invalid JSON from Claude: {str(e)}",
            }

        # Enhanced logging and memory storage
        if hasattr(response, "usage"):
            usage = response.usage
            print(f"📊 Claude 4 Validation - Model: {model}")
            print(
                f"📊 Tokens - Input: {usage.input_tokens}, Output: {usage.output_tokens}"
            )

        # Store comprehensive validation result in memory for learning
        store_memory(
            "code_validation",
            {
                "task": task_description,
                "validation_result": result_json,
                "claude_model": model,
                "code_snippet": code[:500],
                "validation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "token_usage": {
                    "input": (
                        getattr(response.usage, "input_tokens", 0)
                        if hasattr(response, "usage")
                        else 0
                    ),
                    "output": (
                        getattr(response.usage, "output_tokens", 0)
                        if hasattr(response, "usage")
                        else 0
                    ),
                },
            },
            importance=0.9,
            tags=["validation", "claude4", "code_quality", "learning"],
        )

        is_valid = result_json.get("is_valid", False)
        confidence = result_json.get("confidence", 0)
        severity = result_json.get("severity_score", 10)

        print("✅ Claude 4 validation completed:")
        print(
            f"   Valid: {is_valid} | Confidence: {confidence:.2f} | Severity: {severity}/10"
        )

        if not is_valid:
            issues = result_json.get("issues", [])
            print(f"   Issues found: {len(issues)}")
            for issue in issues[:3]:
                print(
                    f"   - {issue.get('severity', 'unknown')}: {issue.get('description', 'No description')}"
                )

        return result_json

    except Exception as e:
        print(f"❌ Claude validation failed: {str(e)}")
        store_memory(
            "validation_error",
            {
                "task": task_description,
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            importance=0.7,
            tags=["error", "claude", "validation"],
        )
        return {"validated": False, "message": f"Claude error: {str(e)}"}
