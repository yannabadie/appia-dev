#!/usr/bin/env python3
"""
Test du système de prompts corrigé - Style concis et direct
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_system_prompts import EnhancedPromptSystem, extract_system_prompt_for_grok
    
    def test_corrected_prompts():
        print("🧪 Test du système de prompts CORRIGÉ")
        print("=" * 50)
        
        # Initialize
        enhanced_prompts = EnhancedPromptSystem()
        enhanced_prompts.environment_info = {
            'secrets_summary': {
                'github': True,
                'supabase': True, 
                'xai_grok': True,
                'claude': True,
                'gcp': False
            }
        }
        
        # Test system prompt pour Grok
        system_prompt = enhanced_prompts.get_grok_orchestrator_system_prompt(
            agent_type="DEV",
            collaboration_mode=True
        )
        
        print("📝 System Prompt pour Grok (échantillon):")
        print("-" * 40)
        print(system_prompt[:300] + "...")
        print()
        
        # Vérifications de style
        checks = [
            ("Concis et direct", "PhD-level autonomous AI orchestrator" in system_prompt),
            ("Mission claire", "CORE MISSION:" in system_prompt),
            ("Requirements techniques", "TECHNICAL REQUIREMENTS:" in system_prompt),
            ("Format output", "OUTPUT FORMAT:" in system_prompt),
            ("Pas de markdown excessif", system_prompt.count("#") < 5),
            ("Longueur raisonnable", len(system_prompt) < 3000)
        ]
        
        print("✅ Vérifications de qualité:")
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
        
        # Test fonction utilitaire
        system_prompt_direct = extract_system_prompt_for_grok(enhanced_prompts, "DEV", True)
        print(f"\n🔧 Fonction utilitaire: {len(system_prompt_direct)} caractères")
        
        print("\n✅ Test terminé - Prompts corrigés et optimisés!")
        
        return system_prompt
    
    if __name__ == "__main__":
        test_corrected_prompts()
        
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    sys.exit(1)
