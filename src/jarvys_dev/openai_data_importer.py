"""
OpenAI Data Importer pour JARVYS
Module pour importer et traiter les données OpenAI dans l'écosystème JARVYS
"""

import json
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import openai
import requests
from openai import OpenAI

from supabase import Client, create_client


@dataclass
class OpenAIDataPoint:
    """Structure de données pour un point de données OpenAI"""

    timestamp: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    response_time_ms: float
    success: bool
    metadata: Dict[str, Any]
    user_context: str


class OpenAIDataImporter:
    """Importateur de données OpenAI pour JARVYS"""

    def __init__(self):
        """Initialise l'importateur avec les configurations nécessaires"""
        self.openai_client = None
        self.supabase_client = None
        self.setup_clients()

        # Configuration des modèles OpenAI et leurs coûts
        self.model_costs = {
            "gpt-4o": {"input": 0.0025, "output": 0.01},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "text-embedding-3-large": {"input": 0.00013, "output": 0},
            "text-embedding-3-small": {"input": 0.00002, "output": 0},
            "whisper-1": {"input": 0.006, "output": 0},  # per minute
        }

    def setup_clients(self):
        """Configure les clients OpenAI et Supabase"""
        try:
            # Configuration OpenAI
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self.openai_client = OpenAI(api_key=openai_key)
                print("✅ Client OpenAI configuré")
            else:
                print("⚠️ OPENAI_API_KEY non trouvé")

            # Configuration Supabase
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            if supabase_url and supabase_key:
                self.supabase_client = create_client(supabase_url, supabase_key)
                print("✅ Client Supabase configuré")
            else:
                print("⚠️ Variables Supabase non trouvées")

        except Exception as e:
            print(f"❌ Erreur configuration clients: {e}")

    def calculate_cost(
        self, model: str, prompt_tokens: int, completion_tokens: int
    ) -> float:
        """Calcule le coût d'une requête OpenAI"""
        if model not in self.model_costs:
            return 0.0

        costs = self.model_costs[model]
        input_cost = (prompt_tokens / 1000) * costs["input"]
        output_cost = (completion_tokens / 1000) * costs["output"]
        return input_cost + output_cost

    def import_chat_completion(
        self, model: str, messages: List[Dict], user_context: str = "unknown", **kwargs
    ) -> OpenAIDataPoint:
        """Importe une completion de chat et enregistre les métriques"""
        if not self.openai_client:
            raise ValueError("Client OpenAI non configuré")

        start_time = time.time()

        try:
            # Appel à l'API OpenAI
            response = self.openai_client.chat.completions.create(
                model=model, messages=messages, **kwargs
            )

            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            # Extraction des métriques
            usage = response.usage
            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else 0

            # Calcul du coût
            cost_usd = self.calculate_cost(model, prompt_tokens, completion_tokens)

            # Création du point de données
            data_point = OpenAIDataPoint(
                timestamp=datetime.now().isoformat(),
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_usd=cost_usd,
                response_time_ms=response_time_ms,
                success=True,
                metadata={
                    "response_id": response.id,
                    "messages_count": len(messages),
                    "finish_reason": (
                        response.choices[0].finish_reason if response.choices else None
                    ),
                    **kwargs,
                },
                user_context=user_context,
            )

            # Enregistrement dans Supabase
            self.save_to_supabase(data_point)

            return data_point

        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            # Enregistrement de l'erreur
            error_data_point = OpenAIDataPoint(
                timestamp=datetime.now().isoformat(),
                model=model,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost_usd=0.0,
                response_time_ms=response_time_ms,
                success=False,
                metadata={"error": str(e), "messages_count": len(messages)},
                user_context=user_context,
            )

            self.save_to_supabase(error_data_point)
            raise e

    def import_embedding(
        self, model: str, input_text: str, user_context: str = "unknown"
    ) -> OpenAIDataPoint:
        """Importe un embedding et enregistre les métriques"""
        if not self.openai_client:
            raise ValueError("Client OpenAI non configuré")

        start_time = time.time()

        try:
            # Appel à l'API OpenAI
            response = self.openai_client.embeddings.create(
                model=model, input=input_text
            )

            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            # Estimation des tokens (approximation)
            estimated_tokens = len(input_text.split()) * 1.3  # Approximation

            # Calcul du coût
            cost_usd = self.calculate_cost(model, int(estimated_tokens), 0)

            # Création du point de données
            data_point = OpenAIDataPoint(
                timestamp=datetime.now().isoformat(),
                model=model,
                prompt_tokens=int(estimated_tokens),
                completion_tokens=0,
                total_tokens=int(estimated_tokens),
                cost_usd=cost_usd,
                response_time_ms=response_time_ms,
                success=True,
                metadata={
                    "input_length": len(input_text),
                    "embedding_dimension": (
                        len(response.data[0].embedding) if response.data else 0
                    ),
                    "usage_estimate": True,
                },
                user_context=user_context,
            )

            # Enregistrement dans Supabase
            self.save_to_supabase(data_point)

            return data_point

        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            # Enregistrement de l'erreur
            error_data_point = OpenAIDataPoint(
                timestamp=datetime.now().isoformat(),
                model=model,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost_usd=0.0,
                response_time_ms=response_time_ms,
                success=False,
                metadata={"error": str(e), "input_length": len(input_text)},
                user_context=user_context,
            )

            self.save_to_supabase(error_data_point)
            raise e

    def save_to_supabase(self, data_point: OpenAIDataPoint):
        """Sauvegarde un point de données dans Supabase"""
        if not self.supabase_client:
            print("⚠️ Client Supabase non configuré, données non sauvegardées")
            return

        try:
            # Conversion en format Supabase
            supabase_data = {
                "timestamp": data_point.timestamp,
                "metric_type": "openai_api_call",
                "metric_value": asdict(data_point),
                "agent_id": "jarvys_dev",
                "session_id": f"session_{int(time.time())}",
            }

            # Insertion dans la table jarvys_metrics
            result = (
                self.supabase_client.table("jarvys_metrics")
                .insert(supabase_data)
                .execute()
            )

            if result.data:
                print(
                    f"✅ Données sauvegardées: {data_point.model} - {data_point.total_tokens} tokens"
                )
            else:
                print("⚠️ Aucune donnée retournée lors de la sauvegarde")

        except Exception as e:
            print(f"❌ Erreur sauvegarde Supabase: {e}")

    def import_usage_data(
        self, start_date: str, end_date: str
    ) -> List[OpenAIDataPoint]:
        """Importe les données d'usage depuis l'API OpenAI (si disponible)"""
        print("⚠️ Import direct des données d'usage OpenAI non encore implémenté")
        print("Utilisation recommandée: wrapper des appels API existants")
        return []

    def export_metrics_to_json(self, filepath: str = "openai_metrics.json"):
        """Exporte les métriques vers un fichier JSON"""
        if not self.supabase_client:
            print("⚠️ Client Supabase non configuré")
            return

        try:
            # Récupération des métriques OpenAI
            result = (
                self.supabase_client.table("jarvys_metrics")
                .select("*")
                .eq("metric_type", "openai_api_call")
                .order("timestamp", desc=True)
                .execute()
            )

            # Sauvegarde en JSON
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(result.data, f, indent=2, ensure_ascii=False)

            print(f"✅ Métriques exportées vers {filepath}: {len(result.data)} entrées")

        except Exception as e:
            print(f"❌ Erreur export JSON: {e}")

    def get_usage_summary(self, days: int = 7) -> Dict[str, Any]:
        """Récupère un résumé d'usage des derniers jours"""
        if not self.supabase_client:
            return {"error": "Client Supabase non configuré"}

        try:
            # Calcul de la date de début
            from datetime import datetime, timedelta

            start_date = (datetime.now() - timedelta(days=days)).isoformat()

            # Récupération des métriques
            result = (
                self.supabase_client.table("jarvys_metrics")
                .select("metric_value")
                .eq("metric_type", "openai_api_call")
                .gte("timestamp", start_date)
                .execute()
            )

            if not result.data:
                return {"message": "Aucune donnée trouvée", "days": days}

            # Calcul des statistiques
            total_calls = len(result.data)
            total_tokens = sum(
                item["metric_value"]["total_tokens"] for item in result.data
            )
            total_cost = sum(item["metric_value"]["cost_usd"] for item in result.data)
            successful_calls = sum(
                1 for item in result.data if item["metric_value"]["success"]
            )

            # Modèles utilisés
            models_used = {}
            for item in result.data:
                model = item["metric_value"]["model"]
                if model in models_used:
                    models_used[model] += 1
                else:
                    models_used[model] = 1

            return {
                "period_days": days,
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "success_rate": (
                    (successful_calls / total_calls * 100) if total_calls > 0 else 0
                ),
                "total_tokens": total_tokens,
                "total_cost_usd": round(total_cost, 4),
                "avg_tokens_per_call": (
                    round(total_tokens / total_calls) if total_calls > 0 else 0
                ),
                "models_used": models_used,
            }

        except Exception as e:
            return {"error": f"Erreur récupération résumé: {e}"}


def main():
    """Fonction principale pour tester l'importateur"""
    print("🔄 Test de l'OpenAI Data Importer pour JARVYS")

    importer = OpenAIDataImporter()

    # Test simple (nécessite OPENAI_API_KEY)
    if importer.openai_client:
        try:
            # Test d'embedding
            data_point = importer.import_embedding(
                model="text-embedding-3-small",
                input_text="Test d'embedding pour JARVYS",
                user_context="test_import",
            )
            print(f"✅ Test embedding réussi: {data_point.cost_usd} USD")

        except Exception as e:
            print(f"❌ Erreur test embedding: {e}")

    # Affichage du résumé d'usage
    summary = importer.get_usage_summary(days=30)
    print(f"\n📊 Résumé d'usage (30 derniers jours):")
    for key, value in summary.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
