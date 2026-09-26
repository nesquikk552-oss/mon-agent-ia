from outils import obtenir_date_heure_fuseau, obtenir_meteo, ajouter_evenement, lister_evenements, supprimer_evenement
from sous_agent_commun import executer_sous_agent

OUTILS_GAMMA = {
    "obtenir_date_heure_fuseau": obtenir_date_heure_fuseau,
    "obtenir_meteo": obtenir_meteo,
    "ajouter_evenement": ajouter_evenement,
    "lister_evenements": lister_evenements,
    "supprimer_evenement": supprimer_evenement,
}

SCHEMA_GAMMA = [
    {"type": "function", "function": {"name": "obtenir_date_heure_fuseau", "description": "Donne la date et l'heure actuelles dans un fuseau horaire donné", "parameters": {"type": "object", "properties": {"fuseau": {"type": "string", "description": "Fuseau au format IANA, ex: Europe/Paris"}}, "required": []}}},
    {"type": "function", "function": {"name": "obtenir_meteo", "description": "Donne la météo actuelle d'une ville, n'importe où dans le monde", "parameters": {"type": "object", "properties": {"ville": {"type": "string"}}, "required": ["ville"]}}},
    {"type": "function", "function": {"name": "ajouter_evenement", "description": "Ajoute un événement à l'agenda", "parameters": {"type": "object", "properties": {"titre": {"type": "string"}, "date_heure": {"type": "string"}, "description": {"type": "string"}}, "required": ["titre", "date_heure"]}}},
    {"type": "function", "function": {"name": "lister_evenements", "description": "Liste tous les événements de l'agenda", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "supprimer_evenement", "description": "Supprime un événement de l'agenda par son titre", "parameters": {"type": "object", "properties": {"titre": {"type": "string"}}, "required": ["titre"]}}},
]

def gerer_agenda_temps(instruction: str) -> str:
    instructions_systeme = "Tu es Gamma, un agent spécialisé dans la gestion de l'agenda, de la date et de l'heure dans n'importe quel fuseau horaire, et de la météo n'importe où dans le monde. Utilise les outils disponibles pour accomplir précisément la demande, puis donne une réponse claire et synthétique."
    return executer_sous_agent("Gamma", instructions_systeme, OUTILS_GAMMA, SCHEMA_GAMMA, instruction)