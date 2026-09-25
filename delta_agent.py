from groq import Groq
import os
import json
from dotenv import load_dotenv
from outils import creer_flashcard, suivre_progression, voir_progression, planifier_revisions, generer_qcm

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

OUTILS_DELTA = {
    "creer_flashcard": creer_flashcard,
    "suivre_progression": suivre_progression,
    "voir_progression": voir_progression,
    "planifier_revisions": planifier_revisions,
    "generer_qcm": generer_qcm,
}

SCHEMA_DELTA = [
    {
        "type": "function",
        "function": {
            "name": "creer_flashcard",
            "description": "Crée une flashcard de révision avec une question et sa réponse",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "reponse": {"type": "string"}
                },
                "required": ["question", "reponse"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "suivre_progression",
            "description": "Enregistre l'avancement de révision d'une matière",
            "parameters": {
                "type": "object",
                "properties": {
                    "matiere": {"type": "string"},
                    "statut": {"type": "string"}
                },
                "required": ["matiere", "statut"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "voir_progression",
            "description": "Affiche l'historique de progression des révisions",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "planifier_revisions",
            "description": "Crée un planning de révision réparti jusqu'à une date d'examen donnée",
            "parameters": {
                "type": "object",
                "properties": {
                    "sujets": {"type": "string", "description": "Liste des sujets séparés par des virgules"},
                    "date_examen": {"type": "string", "description": "Date au format AAAA-MM-JJ"}
                },
                "required": ["sujets", "date_examen"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generer_qcm",
            "description": "Génère un QCM à partir d'un texte donné",
            "parameters": {
                "type": "object",
                "properties": {
                    "texte": {"type": "string"},
                    "nombre_questions": {"type": "integer"}
                },
                "required": ["texte"]
            }
        }
    }
]

def gerer_revisions(instruction: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "Tu es Delta, un agent spécialisé dans l'accompagnement des révisions : création de "
                "flashcards, suivi et consultation de la progression, planification de révisions jusqu'à "
                "une date d'examen, et génération de QCM. Utilise les outils disponibles pour accomplir "
                "précisément la demande, puis donne une réponse claire et synthétique. "
                "Si un contexte sur Monsieur Farnèse t'est fourni, cherche-y activement toute date "
                "d'examen ou information pertinente pour la demande en cours, même si le sujet mentionné "
                "n'est pas formulé exactement à l'identique (ex: 'génie biomédical' peut être lié à "
                "'anatomie' ou 'physiologie'). Ne redemande une information que si elle est vraiment absente du contexte."
            )
        },
        {"role": "user", "content": instruction}
    ]

    for _ in range(5):
        reponse = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=SCHEMA_DELTA,
            max_tokens=1024
        )
        message = reponse.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content or "Delta n'a pas pu produire de réponse."

        for appel in message.tool_calls:
            nom = appel.function.name
            try:
                params = json.loads(appel.function.arguments)
            except json.JSONDecodeError:
                resultat = "Erreur : arguments non valides."
                messages.append({"role": "tool", "tool_call_id": appel.id, "content": resultat})
                continue

            fonction = OUTILS_DELTA.get(nom)
            if not fonction:
                resultat = f"Outil inconnu : {nom}"
            else:
                try:
                    resultat = fonction(**params)
                except Exception as e:
                    resultat = f"Erreur : {e}"

            messages.append({"role": "tool", "tool_call_id": appel.id, "content": str(resultat)})

    return "Delta a atteint la limite d'itérations sans conclure."