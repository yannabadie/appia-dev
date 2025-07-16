#!/usr/bin/env python3
"""
Test des variables d'environnement GitHub
"""

import os

from dotenv import load_dotenv

# Charger le .env (qui référence les variables d'environnement)
load_dotenv()

print("🔍 Test des Variables d'Environnement")
print("=" * 50)

# Variables à tester
vars_to_check = [
    "CLAUDE_API_KEY",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "XAI_API_KEY",
    "GH_TOKEN",
    "GITHUB_TOKEN",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE",
    "SUPABASE_KEY",
]

print("\n📋 Résultats:")
for var in vars_to_check:
    value = os.getenv(var)
    if value:
        # Masquer partiellement la valeur
        masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
        print(f"✅ {var}: {masked}")
    else:
        print(f"❌ {var}: Non trouvé")

# Test spécifique pour Claude
claude_key = os.getenv("CLAUDE_API_KEY")
if claude_key and claude_key.startswith("sk-ant-"):
    print("\n✅ CLAUDE_API_KEY semble valide")
else:
    print("\n⚠️  CLAUDE_API_KEY manquante ou invalide")
    print("   Ajoutez-la dans les secrets GitHub de votre Codespace")
