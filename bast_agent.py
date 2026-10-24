"""Bast — Agent de sécurité et de protection de Christiane.

Surveillance continue (toutes les 1 minute) + validation des actions sensibles
via code d'autorisation « Wakanda forever ».
"""
import os
import threading
import time
from datetime import datetime
from collaboration import suivre_agent, creer_outil_collaboration, schema_collaboration
from sous_agent_commun import executer_sous_agent

CODE_AUTORISATION = "wakanda forever"
INTERVALLE_SURVEILLANCE = 60  # secondes

OUTILS_BAST = {}
SCHEMA_BAST = []

# État de surveillance
_surveillance_active = False
_thread_surveillance = None
_evenements_securite = []


def _journaliser_securite(message: str):
    horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ligne = f"[{horodatage}] {message}"
    _evenements_securite.append(ligne)
    if len(_evenements_securite) > 200:
        _evenements_securite.pop(0)
    try:
        with open("securite.log", "a", encoding="utf-8") as f:
            f.write(ligne + "\n")
    except Exception:
        pass


def _verifier_integrite():
    """Contrôles légers exécutés périodiquement."""
    problemes = []
    if not os.path.exists(".env"):
        problemes.append("Fichier .env absent")
    for log in ("erreurs.log", "delegations.log"):
        if os.path.exists(log) and os.path.getsize(log) > 5_000_000:
            problemes.append(f"{log} très volumineux")
    if problemes:
        _journaliser_securite("ALERTE : " + " | ".join(problemes))
    else:
        _journaliser_securite("Surveillance OK")


def _boucle_surveillance():
    while _surveillance_active:
        try:
            _verifier_integrite()
        except Exception as e:
            _journaliser_securite(f"Erreur surveillance : {e}")
        time.sleep(INTERVALLE_SURVEILLANCE)


def demarrer_surveillance():
    """Lance la surveillance en arrière-plan (idempotent)."""
    global _surveillance_active, _thread_surveillance
    if _surveillance_active:
        return "Surveillance déjà active."
    _surveillance_active = True
    _thread_surveillance = threading.Thread(target=_boucle_surveillance, daemon=True)
    _thread_surveillance.start()
    _journaliser_securite("Surveillance Bast démarrée (intervalle 60s)")
    return "Surveillance Bast démarrée."


def arreter_surveillance():
    global _surveillance_active
    _surveillance_active = False
    _journaliser_securite("Surveillance Bast arrêtée")
    return "Surveillance Bast arrêtée."


def verifier_code(code: str) -> bool:
    """Vérifie le code d'autorisation (insensible à la casse et aux espaces)."""
    if not code:
        return False
    return code.strip().lower() == CODE_AUTORISATION


def demander_autorisation(action: str, details: str = "") -> str:
    """Demande l'autorisation pour une action sensible.
    Retourne un message à afficher à l'utilisateur.
    """
    _journaliser_securite(f"Demande d'autorisation : {action} — {details[:100]}")
    return (
        f"🛡️ Bast : Action sensible détectée ({action}).\n"
        f"Pour autoriser, répondez avec le code : **Wakanda forever**\n"
        f"(écrit ou vocal)."
    )


@suivre_agent("Bast")
def gerer_securite(instruction: str) -> str:
    instructions_systeme = (
        "Tu es Bast, agent de sécurité et de protection de Christiane. "
        "Tu surveilles l'intégrité du système, protèges les actions sensibles "
        "et réponds de façon posée et vigilante. "
        "Tu ne bloques jamais une action sans demander l'autorisation de Monsieur "
        "via le code « Wakanda forever »."
    )
    return executer_sous_agent(
        "Bast", instructions_systeme, OUTILS_BAST, SCHEMA_BAST, instruction, max_tokens=1024
    )


# Démarrage automatique de la surveillance à l'import
demarrer_surveillance()
