#!/usr/bin/env python3
"""
Script simple pour lancer l'orchestrateur JARVYS
"""

import grok_orchestrator


def main():
    print("🚀 Démarrage de l'orchestrateur JARVYS...")

    # Test first that all APIs are working
    print("🔍 Validation des APIs...")
    grok_valid = grok_orchestrator.validate_grok_api()
    claude_valid = grok_orchestrator.validate_claude_api()
    memory_valid = grok_orchestrator.init_infinite_memory()

    print(f"✅ Grok API: {'✅' if grok_valid else '❌'}")
    print(f"✅ Claude API: {'✅' if claude_valid else '❌'}")
    print(f"✅ Memory System: {'✅' if memory_valid else '❌'}")

    if not (grok_valid and claude_valid and memory_valid):
        print(
            "❌ Certaines APIs ne sont pas disponibles. L'orchestrateur peut quand même fonctionner en mode dégradé."
        )

    # Build and test the orchestrator graph
    print("📊 Construction du graphique LangGraph...")
    try:
        graph = grok_orchestrator.build_orchestrator_graph()
        print("✅ Graphique orchestrateur construit avec succès!")

        # Run a single test cycle
        print("🔄 Test d'un cycle autonome...")
        initial_state = grok_orchestrator.AgentState(
            task="",
            sub_agent="",
            repo_dir="",
            repo_obj=None,
            code_generated="",
            test_result="",
            reflection="",
            doc_update="",
            log_entry={},
            lint_fixed=False,
        )

        result = graph.invoke(initial_state)
        print("✅ Cycle autonome terminé!")
        print(f"📋 Tâche identifiée: {result.get('task', 'Aucune')}")
        print(f"🤖 Agent: {result.get('sub_agent', 'Aucun')}")

        # Ask user if they want to continue with full orchestration
        user_input = input("\n🤔 Voulez-vous lancer l'orchestrateur complet ? (y/N): ")
        if user_input.lower() in ["y", "yes", "oui"]:
            print("🚀 Lancement de l'orchestrateur complet...")
            grok_orchestrator.run_orchestrator()
        else:
            print("👋 Test terminé. L'orchestrateur est prêt!")

    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
