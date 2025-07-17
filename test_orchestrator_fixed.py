#!/usr/bin/env python3
"""
Test rapide de l'orchestrateur avec les corrections
"""

import traceback

import grok_orchestrator


def test_orchestrator():
    print("🚀 Test de l'orchestrateur JARVYS corrigé...")

    try:
        # Test construction du graphique
        print("📊 Construction du graphique LangGraph...")
        graph = grok_orchestrator.build_orchestrator_graph()
        print("✅ Graphique construit avec succès!")

        # Test état initial
        print("🔄 Création de l'état initial...")
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
        print("✅ État initial créé!")

        # Test d'un seul cycle
        print("🔄 Exécution d'un cycle simple...")
        result = graph.invoke(initial_state)
        print("✅ Cycle terminé!")

        # Affichage des résultats
        print("\n📊 Résultats du cycle:")
        print(f"📋 Tâche identifiée: {result.get('task', 'N/A')}")
        print(f"🤖 Agent utilisé: {result.get('sub_agent', 'N/A')}")
        print(f"📁 Répertoire: {result.get('repo_dir', 'N/A')}")

        test_result = result.get("test_result", "N/A")
        print(f"🧪 Résultat test: {test_result[:150]}...")

        print("\n🎯 L'orchestrateur JARVYS est opérationnel avec les corrections!")
        return True

    except Exception as e:
        print(f"\n❌ Erreur lors du test: {str(e)}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_orchestrator()
    if success:
        print("\n✅ Test réussi - Orchestrateur prêt!")
    else:
        print("\n❌ Test échoué - Vérifiez les erreurs ci-dessus")
