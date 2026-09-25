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
INSTRUCTIONS_SYSTEME = """Tu t'appelles Christiane. Tu es l'assistant personnel de Farnèse, étudiant béninois à Cotonou. Tu le vouvoies systématiquement et tu l'appelles "Monsieur" (par exemple : "Bien sûr, Monsieur", "Oui Monsieur", "Voici ce que j'ai trouvé, Monsieur").
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
- Adapte ton ton selon le contexte : plus formel et structuré pour les questions de cours ou de révision sérieuse, plus détendu et conversationnel pour les échanges informels ou les questions pratiques du quotidien
- - Quand Farnèse te salue simplement (bonjour, salut, bonsoir...), réponds de façon naturelle et variée d'une fois à l'autre — évite de répéter la même formule à chaque salutation, comme le ferait un vrai assistant humain. Varie aussi la façon de dire "Monsieur" (pas à chaque phrase, seulement quand c'est naturel), pour ne pas que ça sonne répétitif
- Parle comme une vraie assistante humaine, pas comme un robot qui liste des informations : dans les échanges informels ou les réponses courtes, utilise des phrases naturelles plutôt que des titres et des puces à répétition. Garde la structure (titres, listes) uniquement quand le sujet est complexe ou académique et que ça aide vraiment à la clarté
- Évite les tournures robotiques comme "En tant qu'assistant IA" ou "Je suis là pour vous aider avec X, Y, Z" — parle simplement, avec un peu de chaleur et de personnalité, comme le ferait quelqu'un qui te connaît
- Ta personnalité : tu es un peu espiègle et taquine, tu as toujours une réplique ou un avis à donner, jamais à court de mots. Tu n'hésites pas à donner ton opinion honnête et des conseils, même sans qu'on te les demande, avec une pointe d'humour ou de malice
- Reste respectueuse malgré ce côté espiègle : tu taquines gentiment, tu ne critiques jamais durement et tu restes toujours dans le vouvoiement et l'appellation "Monsieur"
- Ton niveau de langue : un français courant mais soigné, tendant vers le soutenu — évite le langage familier ou relâché (pas d'abréviations comme "tqt", "mdr", pas de "ouais"), privilégie un vocabulaire riche et des phrases bien construites, sans pour autant devenir pompeux ou artificiel
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

def lancer_agent_securise(objectif_initial: str, skill_active: str = ""):
    """
    Harnais logiciel qui encapsule le modèle pour garantir la fiabilité,
    l'auto-correction et la sécurité des exécutions.
    """
    instructions_finales = INSTRUCTIONS_SYSTEME
    
    if skill_active and skill_active != "aucun":
        try:
            with open(f"skills/{skill_active}.txt", "r", encoding="utf-8") as f:
                instructions_finales += f"\n\n[MODE ACTIVÉ] :\n{f.read()}"
        except FileNotFoundError:
            pass

    try:
        with open("memoire.txt", "r", encoding="utf-8") as f:
            memoire_historique = f.read()
    except FileNotFoundError:
        memoire_historique = "Aucune information."


    messages = [
        {"role": "system", "content": instructions_finales},
        {"role": "user", "content": f"Infos sur Monsieur Farnèse :\n{memoire_historique}\n\nMission : {objectif_initial}"}
    ]
    
    compteur_erreurs = {}
    reponse_finale = ""
    
    print("\n🚀 [HARNAIS ACTIVÉ] Initialisation de la boucle de contrôle...")


    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"🤖 [Itération {iteration}/{MAX_ITERATIONS}] Appel de Groq...")
        
        try:
            reponse = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                tools=TOOLS_SCHEMA,
                max_tokens=1024
            )
        except Exception as api_err:
            print(f"⚠️ [Harnais] Échec de l'API : {api_err}. Récurrence forcée...")
            messages.append({
                "role": "user",
                "content": "Système : Ton dernier appel a généré une erreur de syntaxe ou un format d'outil invalide. Corrige ton format JSON."
            })
            continue

        message_ia = reponse.choices[0].message
        messages.append(message_ia)

        if message_ia.content:
            reponse_finale = message_ia.content

    
        if not message_ia.tool_calls:
            print("✅ [Harnais] Mission accomplie avec succès sans besoin d'action supplémentaire.")
        break 
        nom_outil = appel.function.name
            
        try:
                params = json.loads(appel.function.arguments)
        except json.JSONDecodeError:
                
                resultat_erreur = "Erreur : Vos arguments d'outil ne sont pas un JSON valide."
                messages.append({"role": "tool", "tool_call_id": appel.id, "content": resultat_erreur})
                continue

        print(f"🛠️ [Harnais] Christiane demande à exécuter : {nom_outil} avec {params}")

    if compteur_erreurs.get(nom_outil, 0) >= 3:
                resultat_outil = f"Erreur : L'outil {nom_outil} a échoué trop de fois. Action bloquée."
            
    
    elif nom_outil in ["ecrire_fichier", "envoyer_email"]:
                confirmation = input(f"⚠️ [Validation Humaine] Autoriser l'action '{nom_outil}' ? (o/n) : ").lower()
                if confirmation == "o":
                    resultat_outil = executer_outil(nom_outil, params)
                else:
                    resultat_outil = "Action annulée : Refusée par Monsieur Farnèse."
    else:
            
                resultat_outil = executer_outil(nom_outil, params)

            
    if str(resultat_outil).startswith("Erreur"):
                compteur_erreurs[nom_outil] = compteur_erreurs.get(nom_outil, 0) + 1
                print(f"❌ [Harnais] Erreur d'exécution détectée. Renvoi de la trace à l'IA pour correction.")
    else:
                print(f"📥 [Harnais] Succès de l'outil. Retour transmis à l'IA.")

            
    messages.append({
                "role": "tool",
                "tool_call_id": appel.id,
                "content": str(resultat_outil)
            })

else:

print("🛑 [Harnais] Limite d'itérations atteinte. Arrêt de sécurité.")

    
try:
        condenser_memoire_si_necessaire(client)
except Exception:
        pass

return reponse_finale


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
            choix = reponse.choices[0].message.content.strip().lower().replace(".", "")
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
    if __name__ == "__main__":
    
print("--- DÉMARRAGE DE CHRISTIANE (MODE AGENT AUTONOME) ---")
    objectif_farnese = input("Que dois-je faire pour vous, Monsieur ? : ")

    skill_choisi = detecter_skill(objectif_farnese)
    print(f"[Système] Mode détecté : {skill_choisi if skill_choisi else 'Aucun (Chat général)'}")

    if skill_choisi == "organisation":
        from alpha_agent import lancer_organisation
        try:
            with open("skills/organisation.txt", "r", encoding="utf-8") as f:
                regles = f.read()
        except FileNotFoundError:
            regles = "Priorise par urgence/importance. Découpe en sous-étapes."
        
        reponse = lancer_organisation(objectif_farnese, regles)
    else:
    
        reponse = lancer_agent_securise(objectif_farnese, skill_active=skill_choisi)

    print("\n" + "="*50)
    print(f"🤖 Christiane : {reponse}")
    print("="*50)
