import os
from typing import Any, Dict, List, Optional

#!/usr/bin/env python3
"""
🧪 JARVYS_AI - Script de Test Complet
Test de toutes les fonctionnalités en mode démo
"""

import asyncio
import logging
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from jarvys_ai.main import JarvysAI

# Configuration logging pour tests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - TEST - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__) = logging.getLogger(__name__)


class JarvysAITester:
    """Testeur complet pour JARVYS_AI"""

    def __init__(self):
        """Initialiser le testeur"""
        self.config = {
            "demo_mode": True,
            "debug": True,
            "auto_improve": False,  # Désactiver pour tests
            "voice_enabled": True,
            "email_enabled": True,
            "cloud_enabled": True,
        }

        self.jarvys = None
        self.test_results = {}

    async def run_all_tests(self):
        """Exécuter tous les tests"""
        logger = logging.getLogger(__name__).info("🧪 Démarrage des tests JARVYS_AI")
        logger = logging.getLogger(__name__).info("=" * 60)

        try:
            # 1. Test d'initialisation
            await self._test_initialization()

            # 2. Test composants principaux
            await self._test_core_components()

            # 3. Test extensions
            await self._test_extensions()

            # 4. Test commandes
            await self._test_commands()

            # 5. Test amélioration continue
            await self._test_continuous_improvement()

            # 6. Test fallback engine
            await self._test_fallback_engine()

            # 7. Rapport final
            await self._generate_final_report()

        except Exception as e:
            logger = logging.getLogger(__name__).error(f"❌ Erreur critique during tests: {e}")
            self.test_results["critical_error"] = str(e)

        finally:
            if self.jarvys:
                await self.jarvys.stop()

    async def _test_initialization(self):
        """Test d'initialisation"""
        logger = logging.getLogger(__name__).info("🔧 Test initialisation...")

        try:
            self.jarvys = JarvysAI(self.config)
            self.test_results["initialization"] = {
                "status": "success",
                "details": "JARVYS_AI créé",
            }
            logger = logging.getLogger(__name__).info("✅ Initialisation réussie")

        except Exception as e:
            self.test_results["initialization"] = {
                "status": "failed",
                "error": str(e),
            }
            logger = logging.getLogger(__name__).error(f"❌ Erreur initialisation: {e}")
            raise

    async def _test_core_components(self):
        """Test composants principaux"""
        logger = logging.getLogger(__name__).info("🧠 Test composants principaux...")

        # Test Intelligence Core
        try:
            await self.jarvys.intelligence_core.initialize()
            self.test_results["intelligence_core"] = {"status": "success"}
            logger = logging.getLogger(__name__).info("✅ Intelligence Core OK")
        except Exception as e:
            self.test_results["intelligence_core"] = {
                "status": "failed",
                "error": str(e),
            }
            logger = logging.getLogger(__name__).error(f"❌ Intelligence Core: {e}")

        # Test Digital Twin
        try:
            await self.jarvys.digital_twin.initialize()
            self.test_results["digital_twin"] = {"status": "success"}
            logger = logging.getLogger(__name__).info("✅ Digital Twin OK")
        except Exception as e:
            self.test_results["digital_twin"] = {
                "status": "failed",
                "error": str(e),
            }
            logger = logging.getLogger(__name__).error(f"❌ Digital Twin: {e}")

        # Test Continuous Improvement
        try:
            await self.jarvys.continuous_improvement.initialize()
            self.test_results["continuous_improvement"] = {"status": "success"}
            logger = logging.getLogger(__name__).info("✅ Continuous Improvement OK")
        except Exception as e:
            self.test_results["continuous_improvement"] = {
                "status": "failed",
                "error": str(e),
            }
            logger = logging.getLogger(__name__).error(f"❌ Continuous Improvement: {e}")

        # Test Fallback Engine
        try:
            await self.jarvys.fallback_engine.initialize()
            self.test_results["fallback_engine"] = {"status": "success"}
            logger = logging.getLogger(__name__).info("✅ Fallback Engine OK")
        except Exception as e:
            self.test_results["fallback_engine"] = {
                "status": "failed",
                "error": str(e),
            }
            logger = logging.getLogger(__name__).error(f"❌ Fallback Engine: {e}")

    async def _test_extensions(self):
        """Test extensions"""
        logger = logging.getLogger(__name__).info("🔌 Test extensions...")

        for name, extension in self.jarvys.extensions.items():
            try:
                await extension.initialize()
                self.test_results[f"extension_{name}"] = {"status": "success"}
                logger = logging.getLogger(__name__).info(f"✅ Extension {name} OK")
            except Exception as e:
                self.test_results[f"extension_{name}"] = {
                    "status": "failed",
                    "error": str(e),
                }
                logger = logging.getLogger(__name__).error(f"❌ Extension {name}: {e}")

    async def _test_commands(self):
        """Test commandes"""
        logger = logging.getLogger(__name__).info("💬 Test commandes...")

        test_commands = [
            "Bonjour JARVYS",
            "Lis mes emails",
            "Chercher fichier projet",
            "Status cloud",
            "Dire bonjour",
            "Aide",
        ]

        for command in test_commands:
            try:
                _response = await self.jarvys.process_command(command, "test")
                self.test_results[f"command_{command}"] = {
                    "status": "success",
                    "response_length": len(response),
                }
                logger = logging.getLogger(__name__).info(
                    f"✅ Commande '{command}' OK ({len(response)} chars)"
                )

            except Exception as e:
                self.test_results[f"command_{command}"] = {
                    "status": "failed",
                    "error": str(e),
                }
                logger = logging.getLogger(__name__).error(f"❌ Commande '{command}': {e}")

    async def _test_continuous_improvement(self):
        """Test amélioration continue"""
        logger = logging.getLogger(__name__).info("🔄 Test amélioration continue...")

        try:
            # Test synchronisation
            updates_count = (
                await self.jarvys.continuous_improvement.sync_with_jarvys_dev()
            )

            # Test status
            status = (
                self.jarvys.continuous_improvement.get_improvement_status()
            )

            self.test_results["continuous_improvement_sync"] = {
                "status": "success",
                "updates_found": updates_count,
                "device_id": status["device_id"],
            }
            logger = logging.getLogger(__name__).info(
                f"✅ Amélioration continue OK ({updates_count} updates)"
            )

        except Exception as e:
            self.test_results["continuous_improvement_sync"] = {
                "status": "failed",
                "error": str(e),
            }
            logger = logging.getLogger(__name__).error(f"❌ Amélioration continue: {e}")

    async def _test_fallback_engine(self):
        """Test moteur de fallback"""
        logger = logging.getLogger(__name__).info("🚨 Test fallback engine...")

        try:
            # Test status
            status = await self.jarvys.fallback_engine.get_fallback_status()

            # Test fallback manuel
            test_result = (
                await self.jarvys.fallback_engine.force_fallback_test()
            )

            self.test_results["fallback_engine_test"] = {
                "status": "success",
                "test_successful": test_result["test_successful"],
                "fallback_active": status["fallback_active"],
            }
            logger = logging.getLogger(__name__).info(
                f"✅ Fallback Engine OK (test: {test_result['test_successful']})"
            )

        except Exception as e:
            self.test_results["fallback_engine_test"] = {
                "status": "failed",
                "error": str(e),
            }
            logger = logging.getLogger(__name__).error(f"❌ Fallback Engine: {e}")

    async def _generate_final_report(self):
        """Générer rapport final"""
        logger = logging.getLogger(__name__).info("📊 Génération rapport final...")
        logger = logging.getLogger(__name__).info("=" * 60)

        total_tests = len(self.test_results)
        successful_tests = len(
            [
                r
                for r in self.test_results.values()
                if r.get("status") == "success"
            ]
        )
        failed_tests = total_tests - successful_tests
        success_rate = (
            (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        )

        logger = logging.getLogger(__name__).info("📈 RAPPORT DE TESTS JARVYS_AI")
        logger = logging.getLogger(__name__).info(f"📊 Tests totaux: {total_tests}")
        logger = logging.getLogger(__name__).info(f"✅ Tests réussis: {successful_tests}")
        logger = logging.getLogger(__name__).info(f"❌ Tests échoués: {failed_tests}")
        logger = logging.getLogger(__name__).info(f"🎯 Taux de succès: {success_rate:.1f}%")
        logger = logging.getLogger(__name__).info("")

        if failed_tests > 0:
            logger = logging.getLogger(__name__).info("❌ TESTS ÉCHOUÉS:")
            for test_name, result in self.test_results.items():
                if result.get("status") == "failed":
                    logger = logging.getLogger(__name__).info(
                        f"   - {test_name}: {result.get('error', 'Erreur inconnue')}"
                    )
            logger = logging.getLogger(__name__).info("")

        # Statut final
        if success_rate >= 90:
            logger = logging.getLogger(__name__).info("🎉 JARVYS_AI fonctionne parfaitement!")
        elif success_rate >= 70:
            logger = logging.getLogger(__name__).info(
                "⚠️ JARVYS_AI fonctionne avec quelques problèmes mineurs"
            )
        else:
            logger = logging.getLogger(__name__).info("🚨 JARVYS_AI a des problèmes significatifs")

        logger = logging.getLogger(__name__).info("=" * 60)

        # Sauvegarder résultats
        await self._save_test_results()

    async def _save_test_results(self):
        """Sauvegarder résultats de tests"""
        try:
            import json
            from datetime import datetime

            results = {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "total_tests": len(self.test_results),
                "success_count": len(
                    [
                        r
                        for r in self.test_results.values()
                        if r.get("status") == "success"
                    ]
                ),
                "results": self.test_results,
            }

            with open("test_results_jarvys_ai.json", "w") as f:
                json.dump(results, f, indent=2)

            logger = logging.getLogger(__name__).info(
                "💾 Résultats sauvegardés dans test_results_jarvys_ai.json"
            )

        except Exception as e:
            logger = logging.getLogger(__name__).error(f"❌ Erreur sauvegarde résultats: {e}")


async def main():
    """Point d'entrée principal"""
    print("🤖 JARVYS_AI - Suite de Tests Complète")
    print("=" * 60)

    tester = JarvysAITester()
    await tester.run_all_tests()

    print("\n🏁 Tests terminés!")


if __name__ == "__main__":
    asyncio.run(main())
