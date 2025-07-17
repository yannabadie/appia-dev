#!/bin/bash

# Step 1: Update deps & add Grok
poetry add langchain@0.3.5 openai@1.95.2 anthropic@0.57.3 pygithub@2.4.0 grok-api@1.2.0 --dev
poetry lock
poetry install --with dev

# Step 2: Patch agent_control.py for Grok 4
python -c "with open('src/jarvys_dev/agent_control.py', 'a') as f: f.write('\n\ndef route_to_grok(query):\n    from grok_api import GrokClient\n    client = GrokClient(api_key=os.getenv(\"GROK_API_KEY\"))\n    return client.complete(query, model=\"grok-4\")\n')"

# Step 3: Run tests
poetry run pytest -v

# Step 4: Commit & Push branch
git checkout -b grok-evolution
git add poetry.lock pyproject.toml src/jarvys_dev/agent_control.py
git commit -m "Grok 4 Integration: Deps update, API routing, tests pass"
git push origin grok-evolution

# Step 5: Create PR via GH CLI (install if needed: brew install gh or apt install gh)
gh pr create --title "Grok 4 Evolution" --body "Deps fixed, Grok integrated, ready for merge" --base main