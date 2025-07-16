"""
OpenAI Data Importer pour JARVYS
Module pour importer les données réelles des conversations ChatGPT
"""

import json
import os
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from supabase import create_client


@dataclass
class ChatGPTConversation:
    """Structure de données pour une conversation ChatGPT"""

    conversation_id: str
    title: str
    create_time: float
    update_time: float
    messages: List[Dict[str, Any]]
    model: str
    total_tokens_estimated: int
    cost_estimated_usd: float
    user_email: str


class OpenAIDataImporter:
    """Importateur de données ChatGPT réelles pour JARVYS"""

    def __init__(self):
        """Initialise l'importateur avec les configurations nécessaires"""
        self.supabase_client = None
        self.setup_clients()

        # Configuration des modèles OpenAI et leurs coûts (2024 mis à jour)
        self.model_costs = {
            # GPT-4 Models
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-0314": {"input": 0.03, "output": 0.06},
            "gpt-4-0613": {"input": 0.03, "output": 0.06},
            "gpt-4-32k": {"input": 0.06, "output": 0.12},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
            "gpt-4-0125-preview": {"input": 0.01, "output": 0.03},
            "gpt-4-1106-preview": {"input": 0.01, "output": 0.03},
            "gpt-4-vision-preview": {"input": 0.01, "output": 0.03},
            # GPT-4o Models (latest)
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4o-2024-05-13": {"input": 0.005, "output": 0.015},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4o-mini-2024-07-18": {"input": 0.00015, "output": 0.0006},
            # GPT-3.5 Models
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "gpt-3.5-turbo-0301": {"input": 0.0015, "output": 0.002},
            "gpt-3.5-turbo-0613": {"input": 0.0015, "output": 0.002},
            "gpt-3.5-turbo-1106": {"input": 0.001, "output": 0.002},
            "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},
            # Embedding Models
            "text-embedding-3-large": {"input": 0.00013, "output": 0},
            "text-embedding-3-small": {"input": 0.00002, "output": 0},
            "text-embedding-ada-002": {"input": 0.0001, "output": 0},
            # Other Models
            "whisper-1": {"input": 0.006, "output": 0},  # per minute
            "tts-1": {"input": 0.015, "output": 0},  # per 1K characters
            "tts-1-hd": {"input": 0.030, "output": 0},  # per 1K characters
            "dall-e-2": {"input": 0.020, "output": 0},  # per image 1024x1024
            "dall-e-3": {"input": 0.040, "output": 0},  # per image 1024x1024
        }

        # Default model mapping for conversations without explicit model info
        self.default_model_by_date = {
            "2024-05-01": "gpt-4o",
            "2024-01-01": "gpt-4-turbo",
            "2023-11-01": "gpt-4-1106-preview",
            "2023-06-01": "gpt-4",
            "2022-11-01": "gpt-3.5-turbo",
        }

    def setup_clients(self):
        """Configure le client Supabase"""
        try:
            # Configuration Supabase
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_ROLE") or os.getenv(
                "SUPABASE_KEY"
            )
            if supabase_url and supabase_key:
<<<<<<< HEAD
                self.supabase_client = create_client(supabase_url, supabase_key)
=======
                self.supabase_client = create_client(
                    supabase_url, supabase_key
                )
>>>>>>> origin/main
                print("✅ Client Supabase configuré")
            else:
                print("⚠️ Variables Supabase non trouvées")

        except Exception as e:
            print(f"❌ Erreur configuration clients: {e}")

    def estimate_tokens(self, text: str) -> int:
        """Estime le nombre de tokens dans un texte"""
        # Approximation: 1 token ≈ 4 caractères en anglais, 3.5 en français
        return max(1, len(text) // 4)

    def determine_model_from_date(self, timestamp: float) -> str:
        """Détermine le modèle probable basé sur la date"""
<<<<<<< HEAD
        conversation_date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
=======
        conversation_date = datetime.fromtimestamp(timestamp).strftime(
            "%Y-%m-%d"
        )
>>>>>>> origin/main

        for date_threshold, model in sorted(
            self.default_model_by_date.items(), reverse=True
        ):
            if conversation_date >= date_threshold:
                return model

        return "gpt-3.5-turbo"  # Fallback

    def calculate_conversation_cost(self, conversation: Dict) -> tuple:
        """Calcule le coût estimé d'une conversation"""
        total_tokens = 0
        total_cost = 0.0

        # Déterminer le modèle
        model = conversation.get(
            "model",
            self.determine_model_from_date(
                conversation.get("create_time", time.time())
            ),
        )

        if "mapping" in conversation:
            for message_id, message_data in conversation["mapping"].items():
                if message_data and "message" in message_data:
                    message = message_data["message"]
                    if (
                        message
                        and "content" in message
                        and "parts" in message["content"]
                    ):
                        for part in message["content"]["parts"]:
                            if isinstance(part, str):
                                tokens = self.estimate_tokens(part)
                                total_tokens += tokens

                                # Calcul du coût
                                if model in self.model_costs:
                                    # Approximation: 70% input, 30% output
                                    input_tokens = int(tokens * 0.7)
                                    output_tokens = int(tokens * 0.3)

                                    cost = (
                                        input_tokens
                                        / 1000
                                        * self.model_costs[model]["input"]
                                        + output_tokens
                                        / 1000
                                        * self.model_costs[model]["output"]
                                    )
                                    total_cost += cost

        return total_tokens, total_cost, model

    def import_from_chatgpt_export(
        self, export_file_path: str, user_email: str = "unknown"
    ) -> List[ChatGPTConversation]:
        """Importe les données depuis un export ChatGPT (fichier JSON)"""
        conversations = []

        try:
            # Si c'est un ZIP, l'extraire
            if export_file_path.endswith(".zip"):
                with zipfile.ZipFile(export_file_path, "r") as zip_ref:
                    zip_ref.extractall(os.path.dirname(export_file_path))
                    # Chercher le fichier conversations.json
                    json_files = [
                        f
                        for f in zip_ref.namelist()
                        if f.endswith("conversations.json")
                    ]
                    if json_files:
                        export_file_path = os.path.join(
                            os.path.dirname(export_file_path), json_files[0]
                        )

            # Lire le fichier JSON
            with open(export_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            print(f"📊 Traitement de {len(data)} conversations...")

            for conversation_data in data:
                try:
                    tokens_estimated, cost_estimated, model = (
                        self.calculate_conversation_cost(conversation_data)
                    )

                    # Extraire les messages
                    messages = []
                    if "mapping" in conversation_data:
                        for message_id, message_data in conversation_data[
                            "mapping"
                        ].items():
                            if message_data and "message" in message_data:
                                message = message_data["message"]
                                if message and message.get("content"):
                                    messages.append(
                                        {
                                            "id": message_id,
<<<<<<< HEAD
                                            "role": message.get("author", {}).get(
                                                "role", "unknown"
                                            ),
                                            "content": message.get("content", {}),
                                            "create_time": message.get("create_time"),
=======
                                            "role": message.get(
                                                "author", {}
                                            ).get("role", "unknown"),
                                            "content": message.get(
                                                "content", {}
                                            ),
                                            "create_time": message.get(
                                                "create_time"
                                            ),
>>>>>>> origin/main
                                            "tokens_estimated": self.estimate_tokens(
                                                str(message.get("content", ""))
                                            ),
                                        }
                                    )

                    conversation = ChatGPTConversation(
                        conversation_id=conversation_data.get("id", "unknown"),
                        title=conversation_data.get("title", "Untitled"),
                        create_time=conversation_data.get("create_time", 0),
                        update_time=conversation_data.get("update_time", 0),
                        messages=messages,
                        model=model,
                        total_tokens_estimated=tokens_estimated,
                        cost_estimated_usd=cost_estimated,
                        user_email=user_email,
                    )

                    conversations.append(conversation)

                except Exception as e:
                    print(
                        f"⚠️ Erreur traitement conversation {conversation_data.get('id', 'unknown')}: {e}"
                    )

            print(f"✅ {len(conversations)} conversations traitées")

            # Sauvegarder dans Supabase
            self.save_conversations_to_supabase(conversations)

            return conversations

        except Exception as e:
            print(f"❌ Erreur import fichier: {e}")
            return []

<<<<<<< HEAD
    def save_conversations_to_supabase(self, conversations: List[ChatGPTConversation]):
=======
    def save_conversations_to_supabase(
        self, conversations: List[ChatGPTConversation]
    ):
>>>>>>> origin/main
        """Sauvegarde les conversations dans Supabase"""
        if not self.supabase_client:
            print("⚠️ Client Supabase non configuré")
            return

        try:
            for conversation in conversations:
                # Données pour jarvys_metrics
                metric_data = {
                    "agent_type": "chatgpt",
                    "event_type": "conversation_import",
                    "service": "openai",
                    "model": conversation.model,
                    "tokens_used": conversation.total_tokens_estimated,
                    "cost_usd": conversation.cost_estimated_usd,
                    "response_time_ms": 0,  # Non applicable pour import
                    "success": True,
                    "metadata": {
                        "conversation_id": conversation.conversation_id,
                        "title": conversation.title,
                        "messages_count": len(conversation.messages),
                        "user_email": conversation.user_email,
                        "import_timestamp": datetime.now().isoformat(),
                    },
                    "user_context": conversation.user_email,
                    "created_at": datetime.fromtimestamp(
                        conversation.create_time
                    ).isoformat(),
                }

                # Insérer dans jarvys_metrics
                _result = (
                    self.supabase_client.table("jarvys_metrics")
                    .insert(metric_data)
                    .execute()
                )

                # Sauvegarder dans jarvys_memory pour les conversations importantes
                if (
                    conversation.total_tokens_estimated > 100
                ):  # Seulement les conversations substantielles
                    memory_content = f"Conversation: {conversation.title}\n"
                    memory_content += f"Modèle: {conversation.model}\n"
<<<<<<< HEAD
                    memory_content += f"Messages: {len(conversation.messages)}\n"
                    memory_content += f"Tokens: {conversation.total_tokens_estimated}\n"
=======
                    memory_content += (
                        f"Messages: {len(conversation.messages)}\n"
                    )
                    memory_content += (
                        f"Tokens: {conversation.total_tokens_estimated}\n"
                    )
>>>>>>> origin/main

                    # Ajouter un extrait des premiers messages
                    for i, msg in enumerate(conversation.messages[:3]):
                        if msg["role"] in ["user", "assistant"]:
                            content_str = (
                                str(msg.get("content", ""))
                                .replace("'", "")
                                .replace('"', "")[:200]
                            )
<<<<<<< HEAD
                            memory_content += f"{msg['role']}: {content_str}...\n"
=======
                            memory_content += (
                                f"{msg['role']}: {content_str}...\n"
                            )
>>>>>>> origin/main

                    memory_data = {
                        "content": memory_content,
                        "agent_source": "chatgpt_import",
                        "memory_type": "conversation_history",
                        "user_context": conversation.user_email,
                        "importance_score": min(
                            1.0, conversation.total_tokens_estimated / 1000
                        ),
                        "created_at": datetime.fromtimestamp(
                            conversation.create_time
                        ).isoformat(),
                    }

                    self.supabase_client.table("jarvys_memory").insert(
                        memory_data
                    ).execute()

<<<<<<< HEAD
            print(f"✅ {len(conversations)} conversations sauvegardées dans Supabase")
=======
            print(
                f"✅ {len(conversations)} conversations sauvegardées dans Supabase"
            )
>>>>>>> origin/main

        except Exception as e:
            print(f"❌ Erreur sauvegarde Supabase: {e}")

    def download_chatgpt_data_instructions(self):
        """Affiche les instructions pour télécharger les données ChatGPT"""
        instructions = """
📥 INSTRUCTIONS POUR TÉLÉCHARGER VOS DONNÉES CHATGPT:

1. Connectez-vous à ChatGPT (https://chat.openai.com)
2. Cliquez sur votre profil (en bas à gauche)
3. Allez dans "Settings" → "Data controls"
4. Cliquez sur "Export data"
5. Confirmez votre demande d'export
6. Attendez l'email de confirmation (peut prendre quelques heures)
7. Téléchargez le fichier ZIP depuis l'email
8. Utilisez ce script avec le fichier téléchargé

⚠️ IMPORTANT:
- Répétez cette opération pour chaque compte:
  - yann.abadie@gmail.com
  - yann.abadie.exakis@gmail.com
- Les exports contiennent TOUTES vos conversations
- Le fichier à utiliser sera "conversations.json" dans le ZIP
        """

        print(instructions)
        return instructions

    def get_usage_summary_from_imports(
        self, user_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Récupère un résumé des données importées"""
        if not self.supabase_client:
            return {"error": "Client Supabase non configuré"}

        try:
<<<<<<< HEAD
            query = self.supabase.table("openai_imported_data").select("*")

            result = query.execute()
=======
            query = (
                self.supabase_client.table("jarvys_metrics")
                .select("*")
                .eq("event_type", "conversation_import")
            )

            if user_email:
                query = query.eq("user_context", user_email)

            _result = query.execute()
>>>>>>> origin/main

            if not result.data:
                return {"message": "Aucune donnée importée trouvée"}

            # Calcul des statistiques
            total_conversations = len(result.data)
<<<<<<< HEAD
            total_tokens = sum(item["tokens_used"] or 0 for item in result.data)
=======
            total_tokens = sum(
                item["tokens_used"] or 0 for item in result.data
            )
>>>>>>> origin/main
            total_cost = sum(item["cost_usd"] or 0 for item in result.data)

            # Modèles utilisés
            models_used = {}
            users = {}
            for item in result.data:
                model = item["model"] or "unknown"
                user = item["user_context"] or "unknown"

                models_used[model] = models_used.get(model, 0) + 1
                users[user] = users.get(user, 0) + 1

            # Coût par utilisateur
            cost_by_user = {}
            for item in result.data:
                user = item["user_context"] or "unknown"
<<<<<<< HEAD
                cost_by_user[user] = cost_by_user.get(user, 0) + (item["cost_usd"] or 0)
=======
                cost_by_user[user] = cost_by_user.get(user, 0) + (
                    item["cost_usd"] or 0
                )
>>>>>>> origin/main

            return {
                "total_conversations": total_conversations,
                "total_tokens": total_tokens,
                "total_cost_usd": round(total_cost, 4),
                "avg_tokens_per_conversation": (
                    round(total_tokens / total_conversations)
                    if total_conversations > 0
                    else 0
                ),
                "avg_cost_per_conversation": (
                    round(total_cost / total_conversations, 4)
                    if total_conversations > 0
                    else 0
                ),
                "models_used": models_used,
                "users": users,
<<<<<<< HEAD
                "cost_by_user": {k: round(v, 4) for k, v in cost_by_user.items()},
=======
                "cost_by_user": {
                    k: round(v, 4) for k, v in cost_by_user.items()
                },
>>>>>>> origin/main
            }

        except Exception as e:
            return {"error": f"Erreur récupération résumé: {e}"}


def main():
    """Fonction principale pour importer les données ChatGPT"""
<<<<<<< HEAD
    print("🔄 OpenAI Data Importer pour JARVYS - Import données ChatGPT réelles")
=======
    print(
        "🔄 OpenAI Data Importer pour JARVYS - Import données ChatGPT réelles"
    )
>>>>>>> origin/main

    importer = OpenAIDataImporter()

    # Afficher les instructions
    importer.download_chatgpt_data_instructions()

    # Demander les fichiers d'export
    print("\n" + "=" * 60)
    print("📁 IMPORTATION DES DONNÉES")

    # Import pour yann.abadie@gmail.com
    gmail_file = input(
        "\n📎 Chemin vers l'export ChatGPT pour yann.abadie@gmail.com (ou 'skip'): "
    ).strip()
<<<<<<< HEAD
    if gmail_file and gmail_file.lower() != "skip" and os.path.exists(gmail_file):
=======
    if (
        gmail_file
        and gmail_file.lower() != "skip"
        and os.path.exists(gmail_file)
    ):
>>>>>>> origin/main
        print("🔄 Import en cours pour yann.abadie@gmail.com...")
        conversations_gmail = importer.import_from_chatgpt_export(
            gmail_file, "yann.abadie@gmail.com"
        )
<<<<<<< HEAD
        print(f"✅ {len(conversations_gmail)} conversations importées pour Gmail")
=======
        print(
            f"✅ {len(conversations_gmail)} conversations importées pour Gmail"
        )
>>>>>>> origin/main

    # Import pour yann.abadie.exakis@gmail.com
    exakis_file = input(
        "\n📎 Chemin vers l'export ChatGPT pour yann.abadie.exakis@gmail.com (ou 'skip'): "
    ).strip()
<<<<<<< HEAD
    if exakis_file and exakis_file.lower() != "skip" and os.path.exists(exakis_file):
=======
    if (
        exakis_file
        and exakis_file.lower() != "skip"
        and os.path.exists(exakis_file)
    ):
>>>>>>> origin/main
        print("🔄 Import en cours pour yann.abadie.exakis@gmail.com...")
        conversations_exakis = importer.import_from_chatgpt_export(
            exakis_file, "yann.abadie.exakis@gmail.com"
        )
<<<<<<< HEAD
        print(f"✅ {len(conversations_exakis)} conversations importées pour Exakis")
=======
        print(
            f"✅ {len(conversations_exakis)} conversations importées pour Exakis"
        )
>>>>>>> origin/main

    # Affichage du résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ GLOBAL DES IMPORTS")

    summary = importer.get_usage_summary_from_imports()
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("\n🎉 Import terminé! Données disponibles dans le dashboard JARVYS.")


if __name__ == "__main__":
    main()
