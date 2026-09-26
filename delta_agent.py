from outils import creer_flashcard, suivre_progression, voir_progression, planifier_revisions, generer_qcm
from sous_agent_commun import executer_sous_agent

OUTILS_DELTA = {
    "creer_flashcard": creer_flashcard,
    "suivre_progression": suivre_progression,
    "voir_progression": voir_progression,
    "planifier_revisions": planifier_revisions,
    "generer_qcm": generer_qcm,
}

SCHEMA_DELTA = [
    {"type": "function", "function": {"name": "creer_flashcard", "description": "Crée une flashcard de révision avec une question et sa réponse", "parameters": {"type": "object", "properties": {"question": {"type": "string"}, "reponse": {"type": "string"}}, "required": ["question", "reponse"]}}},
    {"type": "function", "function": {"name": "suivre_progression", "description": "Enregistre l'avancement de révision d'une matière", "parameters": {"type": "object", "properties": {"matiere": {"type": "string"}, "statut": {"type": "string"}}, "required": ["matiere", "statut"]}}},
    {"type": "function", "function": {"name": "voir_progression", "description": "Affiche l'historique de progression des révisions", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "planifier_revisions", "description": "Crée un planning de révision réparti jusqu'à une date d'examen donnée", "parameters": {"type": "object", "properties": {"sujets": {"type": "string", "description": "Liste des sujets séparés par des virgules"}, "date_examen": {"type": "string", "description": "Date au format AAAA-MM-JJ"}}, "required": ["sujets", "date_examen"]}}},
    {"type": "function", "function": {"name": "generer_qcm", "description": "Génère un QCM à partir d'un texte donné", "parameters": {"type": "object", "properties": {"texte": {"type": "string"}, "nombre_questions": {"type": "integer"}}, "required": ["texte"]}}},
]

def gerer_revisions(instruction: str) -> str:
    instructions_systeme = (
        "Tu es Delta, un agent spécialisé dans l'accompagnement des révisions : création de flashcards, "
        "suivi et consultation de la progression, planification de révisions jusqu'à une date d'examen, "
        "et génération de QCM. Utilise les outils disponibles pour accomplir précisément la demande, puis "
        "donne une réponse claire et synthétique. Si un contexte sur Monsieur Farnèse t'est fourni, "
        "cherche-y activement toute date d'examen ou information pertinente pour la demande en cours, "
        "même si le sujet mentionné n'est pas formulé exactement à l'identique. Ne redemande une "
        "information que si elle est vraiment absente du contexte."
    )
    return executer_sous_agent("Delta", instructions_systeme, OUTILS_DELTA, SCHEMA_DELTA, instruction)