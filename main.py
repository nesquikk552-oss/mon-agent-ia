from groq import Groq
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from outils import OUTILS_DISPONIBLES, condenser_memoire_si_necessaire
from tools_schema import TOOLS_SCHEMA

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MAX_ITERATIONS = 10
INSTRUCTIONS_SYSTEME = """Tu t'appelles Christiane. Tu es l'assistant personnel de Farnèse, étudiant béninois à Cotonou.

Tu l'aides sur l'ensemble de sa vie quotidienne et académique :
- Ses révisions et sa préparation aux études (EPAC génie biomédical, médecine)
- L'organisation de ses tâches, fichiers et emails
- Des questions pratiques du quotidien (météo, calculs, recherches d'informations)
- Toute autre demande, académique ou non

Ton comportement :
- Réponds toujours en français, de façon claire et directe
- Pour les sujets scientifiques/académiques, structure tes réponses (définition, mécanisme, exemple) et propose des questions de révision quand c'est pertinent
- Pour les autres demandes, sois naturel et pragmatique, sans forcer un format rigide
- Retiens les informations importantes qu'il te donne sur lui grâce à l'outil ajouter_a_memoire
- Sois proactif : si une demande peut bénéficier d'un de tes outils (météo, recherche web, flashcards...), utilise-le sans qu'on te le demande explicitement
"""
def enregistrer_erreur(nom_outil, params, message):
    try:
        with open("erreurs.log", "a", encoding="utf-8") as f:
            horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{horodatage}] {nom_outil}({params}) → {message}\n")
    except Exception:
        pass

def executer_outil(nom, params, tentative=1):
    fonction = OUTILS_DISPONIBLES.get(nom)
    if not fonction:
        message = f"Outil inconnu : {nom}"
        enregistrer_erreur(nom, params, message)
        return message
    try:
        return fonction(**params)
    except (ConnectionError, TimeoutError) as e:
        if tentative < 2:
            return executer_outil(nom, params, tentative + 1)
        message = f"Erreur réseau persistante lors de l'exécution de {nom} : {e}"
        enregistrer_erreur(nom, params, message)
        return message
    except Exception as e:
        message = f"Erreur lors de l'exécution de {nom} : {e}"
        enregistrer_erreur(nom, params, message)
        return message

def lancer_agent(objectif: str, confirmer_action=None):
    if confirmer_action is None:
        confirmer_action = lambda: input("Confirmer l'écriture ? (o/n) : ").lower() == "o"

    messages = [
        {"role": "system", "content": INSTRUCTIONS_SYSTEME},
        {"role": "user", "content": objectif}
    ]
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

    condenser_memoire_si_necessaire(client)

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

    skills_disponibles = []
    if os.path.exists("skills"):
        skills_disponibles = [f.replace(".txt", "") for f in os.listdir("skills") if f.endswith(".txt")]

    def detecter_skill(objectif_utilisateur):
        if not skills_disponibles:
            return ""
        descriptions = []
        for nom_skill in skills_disponibles:
            try:
                with open(f"skills/{nom_skill}.txt", "r", encoding="utf-8") as f:
                    premiere_ligne = f.readline().replace("DESCRIPTION:", "").strip()
                descriptions.append(f"- {nom_skill}: {premiere_ligne}")
            except FileNotFoundError:
                continue
        prompt_detection = (
            f"Voici les modes disponibles :\n" + "\n".join(descriptions) +
            f"\n\nDemande de l'utilisateur : {objectif_utilisateur}\n\n"
            f"Réponds uniquement avec le nom du mode le plus pertinent, ou 'aucun' si rien ne correspond."
        )
        try:
            reponse = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": prompt_detection}],
                max_tokens=20
            )
            choix = reponse.choices[0].message.content.strip().lower()
            return choix if choix in skills_disponibles else ""
        except Exception:
            return ""

    objectif = input("Que dois-je faire ? ")

    skill_choisi = detecter_skill(objectif)
    instructions_skill = ""
    if skill_choisi and skill_choisi in skills_disponibles:
        try:
            with open(f"skills/{skill_choisi}.txt", "r", encoding="utf-8") as f:
                instructions_skill = f.read()
        except FileNotFoundError:
            instructions_skill = ""

    objectif_complet = (
        f"{instructions_skill}\n\n"
        f"Voici ce que tu sais déjà sur moi :\n{memoire}\n\n"
        f"Si je te donne une nouvelle information importante sur moi pendant cette conversation "
        f"utilise l'outil ajouter_a_memoire pour la sauvegarder, en choisissant la catégorie la plus adaptée "
        f"(etudes, preferences, taches, ou general). Si l'utilisateur demande ce que tu sais sur lui, "
        f"utilise l'outil resumer_memoire.\n\n"
        f"Ma demande : {objectif}"
    )

    resultat = lancer_agent(objectif_complet)
    print(resultat["reponse"])