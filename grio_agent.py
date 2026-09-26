from groq import Groq
import os
import json
from dotenv import load_dotenv
from outils import calculer, convertir_unite, resoudre_equation, calculer_statistiques, tracer_graphique, calcul_matriciel

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

OUTILS_GRIO = {
    "calculer": calculer,
    "convertir_unite": convertir_unite,
    "resoudre_equation": resoudre_equation,
    "calculer_statistiques": calculer_statistiques,
    "tracer_graphique": tracer_graphique,
    "calcul_matriciel": calcul_matriciel
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
    },
    {
        "type": "function",
        "function": {
            "name": "resoudre_equation",
            "description": "Résout une équation mathématique symbolique (ex: '2*x + 5 = 15') et renvoie la ou les solutions exactes",
            "parameters": {
                "type": "object",
                "properties": {
                    "equation": {"type": "string", "description": "L'équation à résoudre, ex: '2*x + 5 = 15' ou 'x**2 - 4'"},
                    "variable": {"type": "string", "description": "La variable à isoler, par défaut 'x'"}
                },
                "required": ["equation"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculer_statistiques",
            "description": "Calcule la moyenne, médiane, écart-type, minimum et maximum d'une liste de valeurs numériques",
            "parameters": {
                "type": "object",
                "properties": {
                    "valeurs": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "La liste des valeurs numériques à analyser"
                    }
                },
                "required": ["valeurs"]
            }
        }
    },
   {
        "type": "function",
        "function": {
            "name": "tracer_graphique",
            "description": "Trace le graphique d'une fonction mathématique et l'enregistre en image",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "L'expression de la fonction, ex: 'x**2 - 3*x + 2'"},
                    "variable": {"type": "string", "description": "La variable de la fonction, par défaut 'x'"},
                    "x_min": {"type": "number", "description": "Borne minimale de l'axe x, par défaut -10"},
                    "x_max": {"type": "number", "description": "Borne maximale de l'axe x, par défaut 10"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calcul_matriciel",
            "description": "Effectue une opération sur des matrices : déterminant, inverse, multiplication ou transposée",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "description": "L'opération à effectuer : 'determinant', 'inverse', 'multiplication' ou 'transposee'"},
                    "matrice_a": {
                        "type": "array",
                        "items": {"type": "array", "items": {"type": "number"}},
                        "description": "La première matrice, ex: [[1, 2], [3, 4]]"
                    },
                    "matrice_b": {
                        "type": "array",
                        "items": {"type": "array", "items": {"type": "number"}},
                        "description": "La seconde matrice, requise uniquement pour la multiplication"
                    }
                },
                "required": ["operation", "matrice_a"]
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