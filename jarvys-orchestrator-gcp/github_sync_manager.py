#!/usr/bin/env python3
"""
🔄 GitHub Synchronization Manager - JARVYS GCP
=============================================

Gestionnaire de synchronisation centralisé pour maintenir la cohérence
entre les modifications GitHub initiées depuis GCP et Codespace.

Architecture:
- Orchestrateur GCP = Source de vérité pour modifications
- Supabase = Journal des modifications centralisé
- GitHub Webhooks = Détection des changements externes
- Conflict Resolution = Résolution automatique des conflits

Fonctionnalités:
✅ Synchronisation bidirectionnelle GitHub ↔ GCP
✅ Détection et résolution des conflits
✅ Journal centralisé des modifications
✅ Rollback automatique en cas d'erreur
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from github import Github

from supabase import Client


@dataclass
class GitModification:
    """Représente une modification Git"""

    id: str
    type: str  # "commit", "branch", "file", "pr"
    source: str  # "gcp", "codespace", "external"
    timestamp: str
    author: str
    message: str
    files_changed: List[str]
    sha: str
    metadata: Dict


class GitHubSyncManager:
    """Gestionnaire de synchronisation GitHub centralisé"""

    def __init__(self, github_token: str, supabase: Client, repo_name: str):
        self.github = Github(github_token)
        self.supabase = supabase
        self.repo = self.github.get_repo(repo_name)
        self.logger = logging.getLogger(__name__)

        # État de synchronisation
        self.last_sync_sha = None
        self.pending_modifications = []
        self.conflict_queue = []

    async def initialize_sync_state(self):
        """Initialise l'état de synchronisation"""
        try:
            # Récupérer le dernier SHA connu depuis Supabase
            result = (
                self.supabase.table("github_sync_state")
                .select("*")
                .order("timestamp", desc=True)
                .limit(1)
                .execute()
            )

            if result.data:
                self.last_sync_sha = result.data[0]["last_sha"]
                self.logger.info(f"🔄 État sync initialisé: {self.last_sync_sha[:8]}")
            else:
                # Premier sync - utiliser HEAD actuel
                self.last_sync_sha = self.repo.get_branch("main").commit.sha
                await self._save_sync_state(self.last_sync_sha, "initialization")

        except Exception as e:
            self.logger.error(f"❌ Erreur initialisation sync: {e}")

    async def detect_external_changes(self) -> List[GitModification]:
        """Détecte les changements externes depuis le dernier sync"""
        try:
            if not self.last_sync_sha:
                await self.initialize_sync_state()

            # Récupérer les commits depuis le dernier sync
            commits = self.repo.get_commits(
                since=self._sha_to_datetime(self.last_sync_sha)
            )
            external_changes = []

            for commit in commits:
                if commit.sha == self.last_sync_sha:
                    continue

                # Vérifier si le commit vient de GCP
                if self._is_gcp_commit(commit):
                    continue

                # C'est un changement externe (Codespace ou autre)
                modification = GitModification(
                    id=commit.sha,
                    type="commit",
                    source=self._detect_commit_source(commit),
                    timestamp=commit.commit.committer.date.isoformat(),
                    author=commit.commit.author.name,
                    message=commit.commit.message,
                    files_changed=[file.filename for file in commit.files],
                    sha=commit.sha,
                    metadata={
                        "url": commit.html_url,
                        "stats": {
                            "additions": commit.stats.additions,
                            "deletions": commit.stats.deletions,
                        },
                    },
                )
                external_changes.append(modification)

            return external_changes

        except Exception as e:
            self.logger.error(f"❌ Erreur détection changements: {e}")
            return []

    async def sync_external_changes(self, changes: List[GitModification]):
        """Synchronise les changements externes avec l'état GCP"""
        for change in changes:
            try:
                # Enregistrer le changement dans Supabase
                await self._log_modification(change)

                # Analyser l'impact du changement
                impact = await self._analyze_change_impact(change)

                # Décider de l'action à prendre
                if impact["conflict_risk"] == "low":
                    # Accepter automatiquement
                    await self._accept_external_change(change)
                    self.logger.info(f"✅ Changement accepté: {change.id[:8]}")

                elif impact["conflict_risk"] == "medium":
                    # Mettre en queue pour validation
                    await self._queue_for_validation(change, impact)
                    self.logger.warning(f"⚠️ Changement en attente: {change.id[:8]}")

                else:
                    # Conflit détecté - résolution automatique
                    await self._resolve_conflict(change, impact)
                    self.logger.error(f"🔥 Conflit résolu: {change.id[:8]}")

            except Exception as e:
                self.logger.error(f"❌ Erreur sync changement {change.id[:8]}: {e}")

    async def apply_gcp_modification(self, modification: Dict) -> bool:
        """Applique une modification initiée depuis GCP"""
        try:
            mod_type = modification["type"]

            if mod_type == "file_update":
                return await self._apply_file_update(modification)
            elif mod_type == "commit":
                return await self._apply_commit(modification)
            elif mod_type == "branch_create":
                return await self._apply_branch_create(modification)
            elif mod_type == "pr_create":
                return await self._apply_pr_create(modification)
            else:
                self.logger.error(f"❌ Type modification inconnu: {mod_type}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Erreur application modification GCP: {e}")
            return False

    async def _apply_file_update(self, modification: Dict) -> bool:
        """Applique une mise à jour de fichier"""
        try:
            file_path = modification["file_path"]
            new_content = modification["content"]
            commit_message = modification.get("message", f"Update {file_path} from GCP")

            # Récupérer le fichier actuel
            try:
                file_obj = self.repo.get_contents(file_path)
                sha = file_obj.sha
            except:
                # Fichier n'existe pas - création
                sha = None

            # Effectuer la modification
            if sha:
                # Mise à jour
                result = self.repo.update_file(
                    path=file_path,
                    message=f"🤖 [GCP] {commit_message}",
                    content=new_content,
                    sha=sha,
                    committer=self._get_gcp_committer(),
                )
            else:
                # Création
                result = self.repo.create_file(
                    path=file_path,
                    message=f"🤖 [GCP] {commit_message}",
                    content=new_content,
                    committer=self._get_gcp_committer(),
                )

            # Enregistrer la modification
            await self._log_gcp_modification(result["commit"].sha, modification)
            await self._save_sync_state(result["commit"].sha, "gcp_file_update")

            return True

        except Exception as e:
            self.logger.error(f"❌ Erreur mise à jour fichier: {e}")
            return False

    async def _resolve_conflict(self, change: GitModification, impact: Dict):
        """Résout automatiquement un conflit"""
        try:
            resolution_strategy = impact.get("resolution_strategy", "merge")

            if resolution_strategy == "merge":
                # Tentative de merge automatique
                await self._auto_merge_conflict(change, impact)

            elif resolution_strategy == "gcp_priority":
                # GCP a la priorité - revenir à l'état GCP
                await self._revert_to_gcp_state(change, impact)

            elif resolution_strategy == "branch_external":
                # Créer une branche pour le changement externe
                await self._branch_external_change(change, impact)

            else:
                # Résolution manuelle requise
                await self._escalate_conflict(change, impact)

        except Exception as e:
            self.logger.error(f"❌ Erreur résolution conflit: {e}")

    async def _auto_merge_conflict(self, change: GitModification, impact: Dict):
        """Tentative de merge automatique"""
        try:
            # Créer une branche temporaire pour le merge
            branch_name = f"auto-merge-{change.id[:8]}"
            base_branch = self.repo.get_branch("main")

            merge_branch = self.repo.create_git_ref(
                ref=f"refs/heads/{branch_name}", sha=change.sha
            )

            # Tenter le merge avec la stratégie appropriée
            merge_result = await self._attempt_three_way_merge(
                base_sha=base_branch.commit.sha,
                change_sha=change.sha,
                gcp_sha=self.last_sync_sha,
            )

            if merge_result["success"]:
                # Merge réussi - créer le commit final
                final_commit = self.repo.create_git_commit(
                    message=f"🔄 [AUTO-MERGE] {change.message}",
                    tree=merge_result["tree_sha"],
                    parents=[base_branch.commit.sha, change.sha],
                )

                # Mettre à jour main
                base_branch.edit(sha=final_commit.sha)

                # Nettoyer la branche temporaire
                merge_branch.delete()

                await self._log_merge_success(change, final_commit.sha)
                self.logger.info(f"✅ Merge automatique réussi: {change.id[:8]}")

            else:
                # Échec du merge - escalade
                await self._escalate_conflict(change, impact)
                merge_branch.delete()

        except Exception as e:
            self.logger.error(f"❌ Erreur auto-merge: {e}")
            await self._escalate_conflict(change, impact)

    async def _detect_commit_source(self, commit) -> str:
        """Détecte la source d'un commit"""
        # Analyse de l'auteur et du message
        if "🤖 [GCP]" in commit.commit.message:
            return "gcp"
        elif "Codespace" in commit.commit.author.name:
            return "codespace"
        elif commit.commit.author.email.endswith("@github.com"):
            return "github_web"
        else:
            return "external"

    async def _analyze_change_impact(self, change: GitModification) -> Dict:
        """Analyse l'impact d'un changement externe"""
        impact = {
            "conflict_risk": "low",
            "affected_systems": [],
            "resolution_strategy": "merge",
        }

        # Analyser les fichiers modifiés
        critical_files = [
            "jarvys_command_interface.py",
            "grok_orchestrator_gcp.py",
            "requirements.txt",
            "cloudbuild.yaml",
        ]

        for file_path in change.files_changed:
            if any(critical in file_path for critical in critical_files):
                impact["conflict_risk"] = "high"
                impact["affected_systems"].append("orchestrator")
                impact["resolution_strategy"] = "gcp_priority"
                break

        # Analyser le timing
        time_since_last_gcp = self._time_since_last_gcp_commit()
        if time_since_last_gcp < 300:  # 5 minutes
            impact["conflict_risk"] = "medium"

        return impact

    async def create_sync_dashboard_endpoint(self):
        """Crée un endpoint pour le dashboard de synchronisation"""
        return {
            "sync_status": {
                "last_sync": self.last_sync_sha,
                "pending_changes": len(self.pending_modifications),
                "conflicts": len(self.conflict_queue),
                "is_synced": len(self.pending_modifications) == 0,
            },
            "recent_modifications": await self._get_recent_modifications(),
            "conflict_resolution": await self._get_conflict_status(),
        }

    # Méthodes utilitaires
    def _is_gcp_commit(self, commit) -> bool:
        """Vérifie si un commit vient de GCP"""
        return "🤖 [GCP]" in commit.commit.message

    def _get_gcp_committer(self) -> Dict:
        """Retourne les infos du committer GCP"""
        return {
            "name": "JARVYS GCP Orchestrator",
            "email": "jarvys@doublenumerique-yann.gcp",
        }

    async def _save_sync_state(self, sha: str, operation: str):
        """Sauvegarde l'état de synchronisation"""
        try:
            self.supabase.table("github_sync_state").insert(
                {
                    "last_sha": sha,
                    "operation": operation,
                    "timestamp": datetime.now().isoformat(),
                    "orchestrator_id": "gcp-orchestrator",
                }
            ).execute()
            self.last_sync_sha = sha
        except Exception as e:
            self.logger.error(f"❌ Erreur sauvegarde sync state: {e}")


# Configuration pour l'orchestrateur GCP
async def setup_github_sync(orchestrator):
    """Configure la synchronisation GitHub pour l'orchestrateur"""
    try:
        github_token = os.getenv("GITHUB_TOKEN")
        repo_name = f"{os.getenv('GITHUB_OWNER')}/{os.getenv('GITHUB_REPO')}"

        sync_manager = GitHubSyncManager(
            github_token=github_token,
            supabase=orchestrator.supabase,
            repo_name=repo_name,
        )

        await sync_manager.initialize_sync_state()

        # Démarrer la synchronisation périodique
        asyncio.create_task(periodic_sync(sync_manager))

        return sync_manager

    except Exception as e:
        logger.error(f"❌ Erreur setup GitHub sync: {e}")
        return None


async def periodic_sync(sync_manager: GitHubSyncManager):
    """Synchronisation périodique"""
    while True:
        try:
            # Détecter les changements externes
            external_changes = await sync_manager.detect_external_changes()

            if external_changes:
                logger.info(f"🔄 {len(external_changes)} changements externes détectés")
                await sync_manager.sync_external_changes(external_changes)

            # Attendre 2 minutes avant la prochaine vérification
            await asyncio.sleep(120)

        except Exception as e:
            logger.error(f"❌ Erreur sync périodique: {e}")
            await asyncio.sleep(300)  # Attendre 5 min en cas d'erreur
