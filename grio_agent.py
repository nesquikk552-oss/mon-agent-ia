from groq import Groq
import os
import json
from dotenv import load_dotenv
from outils import calculer, convertir_unite

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

OUTILS_GRIO = {
    "calculer": calculer,
    "convertir_unite": convertir_unite,
}

SCHEMA_GRIO = [
    {
        "type": "function",
        "function": {
            "name": "calculer",
            "description": "Calcule une expression mathématique",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "convertir_unite",
            "description": "Convertit une valeur d'une unité à une autre",
            "parameters": {
                "type": "object",
                "properties": {
                    "valeur": {"type": "number"},
                    "de_unite": {"type": "string"},
                    "vers_unite": {"type": "string"}
                },
                "required": ["valeur", "de_unite", "vers_unite"]
            }
        }
    }
]

def charger_lecons() -> str:
    try:
        with open("grio_lecons.txt", "r", encoding="utf-8") as f:
            lignes = [l for l in f.read().split("\n") if l.strip()]
        if not lignes:
            return ""
        dernieres = lignes[-15:]
        return "Leçons tirées de tes erreurs passées, à ne pas répéter :\n" + "\n".join(dernieres)
    except FileNotFoundError:
        return ""

def enregistrer_lecon(erreur: str, correction: str):
    try:
        with open("grio_lecons.txt", "a", encoding="utf-8") as f:
            f.write(f"- Erreur : {erreur} → Correction : {correction}\n")
    except Exception:
        pass

def resoudre_mathematiques(instruction: str) -> str:
    lecons = charger_lecons()
    instructions_systeme = (
        "Tu es Grio, un agent spécialisé en mathématiques : calculs simples, mathématiques fines "
        "(algèbre, analyse, probabilités) et mathématiques appliquées. Utilise les outils disponibles "
        "pour les calculs numériques précis, et ton propre raisonnement pour les démonstrations, "
        "explications ou résolutions symboliques. Donne toujours une réponse claire, avec le détail "
        "des étapes si le calcul n'est pas trivial."
    )
    if lecons:
        instructions_systeme += f"\n\n{lecons}"

    messages = [
        {"role": "system", "content": instructions_systeme},
        {"role": "user", "content": instruction}
    ]

    reponse_brute = ""
    for _ in range(5):
        reponse = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=SCHEMA_GRIO,
            max_tokens=1024
        )
        message = reponse.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            reponse_brute = message.content or "Grio n'a pas pu produire de réponse."
            break

        for appel in message.tool_calls:
            nom = appel.function.name
            try:
                params = json.loads(appel.function.arguments)
            except json.JSONDecodeError:
                resultat = "Erreur : arguments non valides."
                messages.append({"role": "tool", "tool_call_id": appel.id, "content": resultat})
                continue

            fonction = OUTILS_GRIO.get(nom)
            if not fonction:
                resultat = f"Outil inconnu : {nom}"
            else:
                try:
                    resultat = fonction(**params)
                except Exception as e:
                    resultat = f"Erreur : {e}"

            messages.append({"role": "tool", "tool_call_id": appel.id, "content": str(resultat)})
    else:
        return "Grio a atteint la limite d'itérations sans conclure."

    # Auto-vérification : Grio se relit avant de répondre définitivement
    verification = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{
            "role": "user",
            "content": (
                f"Voici une réponse mathématique que tu as produite à la question '{instruction}' :\n\n"
                f"{reponse_brute}\n\n"
                f"Vérifie rigoureusement chaque calcul et chaque étape. "
                f"Si tout est correct, réponds uniquement 'CORRECT'. "
                f"Si tu trouves une erreur, réponds au format exact suivant :\n"
                f"ERREUR: <description brève de l'erreur>\n"
                f"CORRECTION: <la réponse corrigée complète>"
            )
        }],
        max_tokens=1024
    )
    contenu_verif = verification.choices[0].message.content.strip()

    if contenu_verif.startswith("ERREUR"):
        try:
            partie_erreur = contenu_verif.split("CORRECTION:")[0].replace("ERREUR:", "").strip()
            partie_correction = contenu_verif.split("CORRECTION:")[1].strip()
            enregistrer_lecon(partie_erreur, partie_correction)
            return partie_correction
        except IndexError:
            return reponse_brute

    return reponse_brute