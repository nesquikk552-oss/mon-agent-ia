from groq import Groq
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from outils import OUTILS_DISPONIBLES
from tools_schema import TOOLS_SCHEMA

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MAX_ITERATIONS = 10

def enregistrer_erreur(nom_outil, params, message):
    try:
        with open("erreurs.log", "a", encoding="utf-8") as f:
            horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{horodatage}] {nom_outil}({params}) → {message}\n")
    except Exception:
        pass

def executer_outil(nom, params):
    fonction = OUTILS_DISPONIBLES.get(nom)
    if not fonction:
        message = f"Outil inconnu : {nom}"
        enregistrer_erreur(nom, params, message)
        return message
    try:
        return fonction(**params)
    except Exception as e:
        message = f"Erreur lors de l'exécution de {nom} : {e}"
        enregistrer_erreur(nom, params, message)
        return message

def lancer_agent(objectif: str, confirmer_action=None):
    if confirmer_action is None:
        confirmer_action = lambda: input("Confirmer l'écriture ? (o/n) : ").lower() == "o"

    messages = [{"role": "user", "content": objectif}]
    compteur_echecs = {}
    journal = []
    reponse_finale = ""
    for i in range(MAX_ITERATIONS):
        reponse = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=TOOLS_SCHEMA,
            max_tokens=1024
        )

        message = reponse.choices[0].message
        messages.append(message)

        if message.content:
            journal.append(f"[Agent] {message.content}")
            reponse_finale = message.content

        if not message.tool_calls:
            journal.append("--- Terminé ---")
            break

        for appel in message.tool_calls:
            nom = appel.function.name
            params = json.loads(appel.function.arguments)
            journal.append(f"[Outil] {nom}({params})")

            if compteur_echecs.get(nom, 0) >= 3:
                resultat = f"L'outil {nom} a échoué 3 fois, abandon de cette action."
            elif nom == "ecrire_fichier" or nom == "envoyer_email":
                if confirmer_action():
                    resultat = executer_outil(nom, params)
                else:
                    resultat = "Action refusée par l'utilisateur."
            else:
                resultat = executer_outil(nom, params)

            if str(resultat).startswith("Erreur"):
                compteur_echecs[nom] = compteur_echecs.get(nom, 0) + 1

            messages.append({
                "role": "tool",
                "tool_call_id": appel.id,
                "content": str(resultat)
            })
    else:
        journal.append("Limite d'itérations atteinte.")

    return {
        "reponse": reponse_finale,
        "journal": "\n".join(journal)
    }
if __name__ == "__main__":
    try:
        with open("memoire.txt", "r", encoding="utf-8") as f:
            memoire = f.read()
    except FileNotFoundError:
        memoire = "Aucune information mémorisée pour l'instant."

    objectif = input("Que dois-je faire ? ")
    objectif_complet = (
        f"Voici ce que tu sais déjà sur moi :\n{memoire}\n\n"
        f"Si je te donne une nouvelle information importante sur moi pendant cette conversation "
        f"(mes études, mes préférences, mes projets...), utilise l'outil ajouter_a_memoire pour la sauvegarder.\n\n"
        f"Ma demande : {objectif}"
    )

    resultat = lancer_agent(objectif_complet)
    print(resultat["reponse"])