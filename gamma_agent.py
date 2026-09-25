from groq import Groq
import os
import json
from dotenv import load_dotenv
from outils import obtenir_date_heure_fuseau, obtenir_meteo, ajouter_evenement, lister_evenements, supprimer_evenement

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

OUTILS_GAMMA = {
    "obtenir_date_heure_fuseau": obtenir_date_heure_fuseau,
    "obtenir_meteo": obtenir_meteo,
    "ajouter_evenement": ajouter_evenement,
    "lister_evenements": lister_evenements,
    "supprimer_evenement": supprimer_evenement,
}

SCHEMA_GAMMA = [
    {
        "type": "function",
        "function": {
            "name": "obtenir_date_heure_fuseau",
            "description": "Donne la date et l'heure actuelles dans un fuseau horaire donné",
            "parameters": {
                "type": "object",
                "properties": {
                    "fuseau": {"type": "string", "description": "Fuseau au format IANA, ex: Europe/Paris, Asia/Tokyo, America/New_York"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obtenir_meteo",
            "description": "Donne la météo actuelle d'une ville, n'importe où dans le monde",
            "parameters": {
                "type": "object",
                "properties": {"ville": {"type": "string"}},
                "required": ["ville"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ajouter_evenement",
            "description": "Ajoute un événement à l'agenda",
            "parameters": {
                "type": "object",
                "properties": {
                    "titre": {"type": "string"},
                    "date_heure": {"type": "string", "description": "Date et heure, ex: 2026-11-15 14:00"},
                    "description": {"type": "string"}
                },
                "required": ["titre", "date_heure"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lister_evenements",
            "description": "Liste tous les événements de l'agenda",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "supprimer_evenement",
            "description": "Supprime un événement de l'agenda par son titre",
            "parameters": {
                "type": "object",
                "properties": {"titre": {"type": "string"}},
                "required": ["titre"]
            }
        }
    }
]

def gerer_agenda_temps(instruction: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "Tu es Gamma, un agent spécialisé dans la gestion de l'agenda, de la date et de l'heure "
                "dans n'importe quel fuseau horaire, et de la météo n'importe où dans le monde. "
                "Utilise les outils disponibles pour accomplir précisément la demande, puis donne une "
                "réponse claire et synthétique."
            )
        },
        {"role": "user", "content": instruction}
    ]

    for _ in range(5):
        reponse = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=SCHEMA_GAMMA,
            max_tokens=1024
        )
        message = reponse.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content or "Gamma n'a pas pu produire de réponse."

        for appel in message.tool_calls:
            nom = appel.function.name
            try:
                params = json.loads(appel.function.arguments)
            except json.JSONDecodeError:
                resultat = "Erreur : arguments non valides."
                messages.append({"role": "tool", "tool_call_id": appel.id, "content": resultat})
                continue

            fonction = OUTILS_GAMMA.get(nom)
            if not fonction:
                resultat = f"Outil inconnu : {nom}"
            else:
                try:
                    resultat = fonction(**params)
                except Exception as e:
                    resultat = f"Erreur : {e}"

            messages.append({"role": "tool", "tool_call_id": appel.id, "content": str(resultat)})

    return "Gamma a atteint la limite d'itérations sans conclure."