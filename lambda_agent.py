from outils import lire_fichier, ecrire_fichier, lire_pdf, lire_docx, ecrire_docx, lire_excel, ecrire_excel, lire_pptx, creer_pptx
from sous_agent_commun import executer_sous_agent

OUTILS_LAMBDA = {
    "lire_fichier": lire_fichier,
    "ecrire_fichier": ecrire_fichier,
    "lire_pdf": lire_pdf,
    "lire_docx": lire_docx,
    "ecrire_docx": ecrire_docx,
    "lire_excel": lire_excel,
    "ecrire_excel": ecrire_excel,
    "lire_pptx": lire_pptx,
    "creer_pptx": creer_pptx,
}

SCHEMA_LAMBDA = [
    {"type": "function", "function": {"name": "lire_fichier", "description": "Lit un fichier texte", "parameters": {"type": "object", "properties": {"chemin": {"type": "string"}}, "required": ["chemin"]}}},
    {"type": "function", "function": {"name": "ecrire_fichier", "description": "Écrit dans un fichier texte", "parameters": {"type": "object", "properties": {"chemin": {"type": "string"}, "contenu": {"type": "string"}}, "required": ["chemin", "contenu"]}}},
    {"type": "function", "function": {"name": "lire_pdf", "description": "Lit le contenu d'un fichier PDF", "parameters": {"type": "object", "properties": {"chemin": {"type": "string"}}, "required": ["chemin"]}}},
    {"type": "function", "function": {"name": "lire_docx", "description": "Lit le contenu d'un document Word (.docx)", "parameters": {"type": "object", "properties": {"chemin": {"type": "string"}}, "required": ["chemin"]}}},
    {"type": "function", "function": {"name": "ecrire_docx", "description": "Crée un document Word (.docx) avec un titre et du contenu", "parameters": {"type": "object", "properties": {"chemin": {"type": "string"}, "contenu": {"type": "string"}, "titre": {"type": "string"}}, "required": ["chemin", "contenu"]}}},
    {"type": "function", "function": {"name": "lire_excel", "description": "Lit le contenu d'un fichier Excel (.xlsx)", "parameters": {"type": "object", "properties": {"chemin": {"type": "string"}}, "required": ["chemin"]}}},
    {"type": "function", "function": {"name": "ecrire_excel", "description": "Crée un fichier Excel (.xlsx)", "parameters": {"type": "object", "properties": {"chemin": {"type": "string"}, "donnees": {"type": "string"}, "feuille": {"type": "string"}}, "required": ["chemin", "donnees"]}}},
    {"type": "function", "function": {"name": "lire_pptx", "description": "Lit le contenu d'une présentation PowerPoint (.pptx)", "parameters": {"type": "object", "properties": {"chemin": {"type": "string"}}, "required": ["chemin"]}}},
    {"type": "function", "function": {"name": "creer_pptx", "description": "Crée une présentation PowerPoint (.pptx) simple", "parameters": {"type": "object", "properties": {"chemin": {"type": "string"}, "titre": {"type": "string"}, "contenu": {"type": "string"}}, "required": ["chemin", "titre", "contenu"]}}},
]

def gerer_documents(instruction: str) -> str:
    instructions_systeme = "Tu es Lambda, un agent spécialisé dans la gestion de documents : fichiers texte, PDF, Word, Excel et PowerPoint. Utilise les outils disponibles pour lire, créer ou modifier ces documents selon la demande, puis donne une réponse claire et synthétique."
    return executer_sous_agent("Lambda", instructions_systeme, OUTILS_LAMBDA, SCHEMA_LAMBDA, instruction)