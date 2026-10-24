"""Collaboration entre sous-agents.

Chaque agent peut solliciter un autre agent pour ce qui sort de son domaine.
Garde-fous : un agent ne peut pas être sollicité s'il travaille déjà sur la demande
(pas de boucle A -> B -> A), la chaîne est limitée en profondeur et en nombre d'appels.
"""
import functools
import importlib
import threading
from datetime import datetime

MAX_CHAINE = 3   # agents imbriqués au maximum (A -> B -> C)
MAX_APPELS = 5   # sollicitations maximales pour une même demande

REGISTRE = {
    "alpha": {"nom": "Alpha", "module": "alpha_agent", "fonction": "rechercher_avec_agent",
              "domaine": "recherche web, lecture de pages web, ouverture du navigateur"},
    "beta": {"nom": "Beta", "module": "beta_agent", "fonction": "gerer_fichiers",
             "domaine": "lecture, écriture et recherche de fichiers, Explorateur"},
    "grio": {"nom": "Grio", "module": "grio_agent", "fonction": "resoudre_mathematiques",
             "domaine": "mathématiques, calculs, statistiques, graphiques"},
    "delta": {"nom": "Delta", "module": "delta_agent", "fonction": "gerer_revisions",
              "domaine": "révisions : flashcards, QCM, planning, progression"},
    "gamma": {"nom": "Gamma", "module": "gamma_agent", "fonction": "gerer_agenda_temps",
              "domaine": "agenda, date et heure, fuseaux horaires, météo"},
    "lambda": {"nom": "Lambda", "module": "lambda_agent", "fonction": "gerer_documents",
               "domaine": "documents Word, Excel, PowerPoint et PDF"},
}

_etat = threading.local()


def _pile():
    if not hasattr(_etat, "pile"):
        _etat.pile = []
    return _etat.pile


def suivre_agent(nom):
    """Décorateur : signale quel agent travaille (sert à éviter les boucles)."""
    def decorateur(fonction):
        @functools.wraps(fonction)
        def enveloppe(*args, **kwargs):
            pile = _pile()
            pile.append(nom)
            try:
                return fonction(*args, **kwargs)
            finally:
                pile.pop()
                if not pile:
                    _etat.appels = 0
        return enveloppe
    return decorateur


def _journaliser(demandeur, cible, instruction, resultat):
    try:
        with open("delegations.log", "a", encoding="utf-8") as f:
            horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            extrait = str(resultat)[:150].replace("\n", " ")
            f.write(f"[{horodatage}] {demandeur} → {cible} ← {instruction[:150]}\n    → {extrait}...\n")
    except Exception:
        pass


def creer_outil_collaboration(nom_agent):
    def demander_a_un_agent(agent: str, instruction: str) -> str:
        cle = str(agent).strip().lower()
        if cle not in REGISTRE:
            return f"Erreur : agent inconnu ({agent}). Agents disponibles : {', '.join(REGISTRE)}."
        cible = REGISTRE[cle]["nom"]
        pile = _pile()
        if cible in pile:
            return (f"Erreur : {cible} travaille déjà sur cette demande ({' -> '.join(pile)}). "
                    f"Termine avec les informations dont tu disposes.")
        if len(pile) >= MAX_CHAINE:
            return "Erreur : chaîne de collaboration trop longue. Termine avec ce que tu as."
        if getattr(_etat, "appels", 0) >= MAX_APPELS:
            return "Erreur : limite de sollicitations atteinte pour cette demande. Termine avec ce que tu as."
        _etat.appels = getattr(_etat, "appels", 0) + 1
        try:
            module = importlib.import_module(REGISTRE[cle]["module"])
            resultat = getattr(module, REGISTRE[cle]["fonction"])(instruction)
        except Exception as e:
            resultat = f"Erreur : {cible} n'a pas pu répondre ({e})."
        _journaliser(nom_agent, cible, instruction, resultat)
        return str(resultat)
    return demander_a_un_agent


def schema_collaboration(nom_agent):
    autres = [cle for cle, v in REGISTRE.items() if v["nom"] != nom_agent]
    agents = " ; ".join(f"{cle} ({REGISTRE[cle]['domaine']})" for cle in autres)
    return {"type": "function", "function": {
        "name": "demander_a_un_agent",
        "description": ("Sollicite un autre agent spécialisé quand une partie de la tâche sort de ton domaine. "
                        "Donne-lui une instruction complète et autonome (il ne voit pas ta conversation). "
                        f"Agents : {agents}."),
        "parameters": {"type": "object", "properties": {
            "agent": {"type": "string", "enum": autres},
            "instruction": {"type": "string"}},
            "required": ["agent", "instruction"]}}}
