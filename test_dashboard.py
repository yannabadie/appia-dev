import json
import os
#!/usr/bin/env python3
"""
Script de test pour le JARVYS Dashboard déployé sur Supabase
Teste tous les endpoints et vérifie le bon fonctionnement.
"""

import sys
import time
from typing import Any, Dict

import requests


class DashboardTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.results = []

    def test_endpoint(
        self, endpoint: str, method: str = "GET", data: Dict = None
    ) -> Dict[str, Any]:
        """Teste un endpoint spécifique."""
        url = f"{self.base_url}{endpoint}"

        try:
            start_time = time.time()

            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                raise ValueError(f"Méthode {method} non supportée")

            end_time = time.time()
            duration = round((end_time - start_time) * 1000, 2)

            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "duration_ms": duration,
                "success": 200 <= response.status_code < 300,
                "content_type": response.headers.get("Content-Type", ""),
                "content_length": len(response.content),
            }

            if result["success"]:
                # Tentative de parsing JSON pour les API
                if "application/json" in result["content_type"]:
                    try:
                        result["json_data"] = response.json()
                    except Exception:
                        result["json_data"] = None

                # Pour HTML, vérifier la présence de contenu clé
                elif "text/html" in result["content_type"]:
                    content = response.text
                    result["has_title"] = "JARVYS" in content
                    result["has_dashboard"] = "dashboard" in content.lower()

            return result

        except Exception as e:
            return {
                "endpoint": endpoint,
                "method": method,
                "success": False,
                "error": str(e),
                "duration_ms": 0,
            }

    def run_all_tests(self):
        """Exécute tous les tests du dashboard."""
        print("🧪 Test du JARVYS Dashboard sur Supabase")
        print(f"🌐 URL de base: {self.base_url}")
        print("-" * 60)

        # Liste des endpoints à tester
        endpoints = [
            ("/", "GET"),
            ("/health", "GET"),
            ("/api/status", "GET"),
            ("/api/metrics", "GET"),
            ("/api/data", "GET"),
            ("/api/tasks", "GET"),
            (
                "/api/chat",
                "POST",
                {"message": "Hello JARVYS, what is your status?"},
            ),
        ]

        for test_data in endpoints:
            endpoint = test_data[0]
            method = test_data[1]
            data = test_data[2] if len(test_data) > 2 else None

            print(f"Testing {method} {endpoint}...", end=" ")
            result = self.test_endpoint(endpoint, method, data)
            self.results.append(result)

            if result["success"]:
                print(f"✅ {result['status_code']} ({result['duration_ms']}ms)")
            else:
                print(f"❌ {result.get('status_code', 'ERROR')}")
                if "error" in result:
                    print(f"   Error: {result['error']}")

        print()
        self.print_summary()

    def print_summary(self):
        """Affiche le résumé des tests."""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r["success"])

        print("📊 Résumé des Tests")
        print("-" * 30)
        print(f"Total: {total_tests}")
        print(f"Réussis: {successful_tests}")
        print(f"Échoués: {total_tests - successful_tests}")
        print(f"Taux de réussite: {(successful_tests/total_tests)*100:.1f}%")

        if successful_tests == total_tests:
            print("\n🎉 Tous les tests sont passés avec succès!")
            print("✅ Le dashboard JARVYS est opérationnel")
        else:
            print("\n⚠️ Certains tests ont échoué")
            print("🔧 Vérifiez la configuration et le déploiement")

        # Détails des tests échoués
        failed_tests = [r for r in self.results if not r["success"]]
        if failed_tests:
            print("\n❌ Tests échoués:")
            for test in failed_tests:
                print(f"   {test['method']} {test['endpoint']}")
                if "error" in test:
                    print(f"      Error: {test['error']}")

        # Statistiques de performance
        successful_durations = [r["duration_ms"] for r in self.results if r["success"]]
        if successful_durations:
            avg_duration = sum(successful_durations) / len(successful_durations)
            max_duration = max(successful_durations)
            print("\n⚡ Performance:")
            print(f"   Temps de réponse moyen: {avg_duration:.2f}ms")
            print(f"   Temps de réponse max: {max_duration:.2f}ms")


def main():
    """Fonction principale."""
    if len(sys.argv) != 2:
        print("Usage: python test_dashboard.py <SUPABASE_URL>")
        print(
            "Exemple: python test_dashboard.py https://abc123.supabase.co/functions/v1/jarvys-dashboard"
        )
        sys.exit(1)

    base_url = sys.argv[1]
    tester = DashboardTester(base_url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
