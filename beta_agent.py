from groq import Groq
import os
import json
from dotenv import load_dotenv
from outils import lire_fichier, ecrire_fichier, lister_fichiers, compter_mots

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

OUTILS_BETA = {
    "lire_fichier": lire_fichier,
    "ecrire_fichier": ecrire_fichier,
    "lister_fichiers": lister_fichiers,
    "compter_mots": compter_mots,
}

SCHEMA_BETA = [
    {
        "type": "function",
        "function": {
            "name": "lire_fichier",
            "description": "Lit le contenu d'un fichier texte",
            "parameters": {
                "type": "object",
                "properties": {"chemin": {"type": "string"}},
                "required": ["chemin"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ecrire_fichier",
            "description": "Écrit du contenu dans un fichier (le crée s'il n'existe pas)",
            "parameters": {
                "type": "object",
                "properties": {
                    "chemin": {"type": "string"},
                    "contenu": {"type": "string"}
                },
                "required": ["chemin", "contenu"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lister_fichiers",
            "description": "Liste les fichiers d'un dossier",
            "parameters": {
                "type": "object",
                "properties": {"dossier": {"type": "string"}},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compter_mots",
            "description": "Compte le nombre de mots et de caractères d'un texte",
            "parameters": {
                "type": "object",
                "properties": {"texte": {"type": "string"}},
                "required": ["texte"]
            }
        }
    }
]

def gerer_fichiers(instruction: str, confirmer_ecriture=None) -> str:
    if confirmer_ecriture is None:
        confirmer_ecriture = lambda: True

    messages = [
        {
            "role": "system",
            "content": "Tu es Beta, un agent spécialisé dans la gestion de fichiers : lecture, écriture, listage et comptage de mots. Utilise les outils disponibles pour accomplir précisément la demande, puis donne une réponse claire et synthétique."
        },
        {"role": "user", "content": instruction}
    ]

    for _ in range(5):
        reponse = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=SCHEMA_BETA,
            max_tokens=1024
        )
        message = reponse.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content or "Beta n'a pas pu produire de réponse."

        for appel in message.tool_calls:
            nom = appel.function.name
            try:
                params = json.loads(appel.function.arguments)
            except json.JSONDecodeError:
                resultat = "Erreur : arguments non valides."
                messages.append({"role": "tool", "tool_call_id": appel.id, "content": resultat})
                continue

            fonction = OUTILS_BETA.get(nom)
            if not fonction:
                resultat = f"Outil inconnu : {nom}"
            elif nom == "ecrire_fichier" and not confirmer_ecriture():
                resultat = "Action refusée : écriture non autorisée."
            else:
                try:
                    resultat = fonction(**params)
                except Exception as e:
                    resultat = f"Erreur : {e}"

            messages.append({"role": "tool", "tool_call_id": appel.id, "content": str(resultat)})

    return "Beta a atteint la limite d'itérations sans conclure."