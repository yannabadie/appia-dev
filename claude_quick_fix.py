import asyncio
import os

import anthropic


async def quick_analyze():
    claude = anthropic.AsyncAnthropic(api_key=os.getenv("CLAUDE_API_KEY"))

    # Analyser grok_orchestrator.py
    with open("grok_orchestrator.py", "r") as f:
        code = f.read()

    response = await claude.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"Identifie les 3 problèmes principaux dans ce code:\n\n{code[:2000]}",
            }
        ],
    )

    print("🤖 Analyse Claude:")
    print(response.content[0].text)


asyncio.run(quick_analyze())
