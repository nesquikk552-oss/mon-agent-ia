from outils import lire_fichier, ecrire_fichier, lister_fichiers, compter_mots
from sous_agent_commun import executer_sous_agent

OUTILS_BETA = {
    "lire_fichier": lire_fichier,
    "ecrire_fichier": ecrire_fichier,
    "lister_fichiers": lister_fichiers,
    "compter_mots": compter_mots,
}

SCHEMA_BETA = [
    {"type": "function", "function": {"name": "lire_fichier", "description": "Lit le contenu d'un fichier texte", "parameters": {"type": "object", "properties": {"chemin": {"type": "string"}}, "required": ["chemin"]}}},
    {"type": "function", "function": {"name": "ecrire_fichier", "description": "Écrit du contenu dans un fichier (le crée s'il n'existe pas)", "parameters": {"type": "object", "properties": {"chemin": {"type": "string"}, "contenu": {"type": "string"}}, "required": ["chemin", "contenu"]}}},
    {"type": "function", "function": {"name": "lister_fichiers", "description": "Liste les fichiers d'un dossier", "parameters": {"type": "object", "properties": {"dossier": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {"name": "compter_mots", "description": "Compte le nombre de mots et de caractères d'un texte", "parameters": {"type": "object", "properties": {"texte": {"type": "string"}}, "required": ["texte"]}}},
]

def gerer_fichiers(instruction: str) -> str:
    instructions_systeme = "Tu es Beta, un agent spécialisé dans la gestion de fichiers : lecture, écriture, listage et comptage de mots. Utilise les outils disponibles pour accomplir précisément la demande, puis donne une réponse claire et synthétique."
    return executer_sous_agent("Beta", instructions_systeme, OUTILS_BETA, SCHEMA_BETA, instruction)