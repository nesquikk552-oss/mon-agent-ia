from groq import Groq
import os
import json
from dotenv import load_dotenv
from outils import lire_fichier, ecrire_fichier, lire_pdf, lire_docx, ecrire_docx, lire_excel, ecrire_excel, lire_pptx, creer_pptx

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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
    {"type": "function", "function": {"name": "ecrire_excel", "description": "Crée un fichier Excel (.xlsx) à partir de données au format lignes séparées par des retours à la ligne, colonnes séparées par des virgules", "parameters": {"type": "object", "properties": {"chemin": {"type": "string"}, "donnees": {"type": "string"}, "feuille": {"type": "string"}}, "required": ["chemin", "donnees"]}}},
    {"type": "function", "function": {"name": "lire_pptx", "description": "Lit le contenu d'une présentation PowerPoint (.pptx)", "parameters": {"type": "object", "properties": {"chemin": {"type": "string"}}, "required": ["chemin"]}}},
    {"type": "function", "function": {"name": "creer_pptx", "description": "Crée une présentation PowerPoint (.pptx) simple avec un titre et du contenu", "parameters": {"type": "object", "properties": {"chemin": {"type": "string"}, "titre": {"type": "string"}, "contenu": {"type": "string"}}, "required": ["chemin", "titre", "contenu"]}}},
]

def gerer_documents(instruction: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "Tu es Lambda, un agent spécialisé dans la gestion de documents : fichiers texte, PDF, "
                "Word, Excel et PowerPoint. Utilise les outils disponibles pour lire, créer ou modifier "
                "ces documents selon la demande, puis donne une réponse claire et synthétique."
            )
        },
        {"role": "user", "content": instruction}
    ]

    for _ in range(5):
        reponse = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=SCHEMA_LAMBDA,
            max_tokens=1024
        )
        message = reponse.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content or "Lambda n'a pas pu produire de réponse."

        for appel in message.tool_calls:
            nom = appel.function.name
            try:
                params = json.loads(appel.function.arguments)
            except json.JSONDecodeError:
                resultat = "Erreur : arguments non valides."
                messages.append({"role": "tool", "tool_call_id": appel.id, "content": resultat})
                continue

            fonction = OUTILS_LAMBDA.get(nom)
            if not fonction:
                resultat = f"Outil inconnu : {nom}"
            else:
                try:
                    resultat = fonction(**params)
                except Exception as e:
                    resultat = f"Erreur : {e}"

            messages.append({"role": "tool", "tool_call_id": appel.id, "content": str(resultat)})

    return "Lambda a atteint la limite d'itérations sans conclure."