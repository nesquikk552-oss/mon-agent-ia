from collaboration import suivre_agent, creer_outil_collaboration, schema_collaboration
from ddgs import DDGS
from groq import Groq
import os
from sous_agent_commun import executer_sous_agent
from outils import lire_page_web, ouvrir_navigateur
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def charger_lecons_alpha() -> str:
    try:
        with open("alpha_lecons.txt", "r", encoding="utf-8") as f:
            lignes = [l for l in f.read().split("\n") if l.strip()]
        if not lignes:
            return ""
        dernieres = lignes[-15:]
        return "Leçons tirées de tes erreurs passées, à ne pas répéter :\n" + "\n".join(dernieres)
    except FileNotFoundError:
        return ""

def enregistrer_lecon_alpha(erreur: str, correction: str):
    try:
        with open("alpha_lecons.txt", "a", encoding="utf-8") as f:
            f.write(f"- Erreur : {erreur} → Correction : {correction}\n")
    except Exception:
        pass

def collecter_informations(question, nombre_resultats=5):
    resultats = []
    with DDGS() as recherche:
        for r in recherche.text(question, max_results=nombre_resultats):
            resultats.append(f"- {r['title']} : {r['body']} (source : {r['href']})")

    if not resultats:
        return "Aucune information trouvée sur le web pour cette question."

    contenu_brut = "\n".join(resultats)

    lecons = charger_lecons_alpha()
    prompt_synthese = (
        f"Voici des résultats de recherche web sur la question : {question}\n\n"
        f"{contenu_brut}\n\n"
        f"Résume ces informations de façon claire et fiable, en gardant les sources importantes."
    )
    if lecons:
        prompt_synthese += f"\n\n{lecons}"

    reponse = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt_synthese}],
        max_tokens=600
    )
    reponse_brute = reponse.choices[0].message.content

    try:
        verification = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{
                "role": "user",
                "content": (
                    f"Voici des résultats de recherche web bruts sur la question '{question}' :\n\n"
                    f"{contenu_brut}\n\n"
                    f"Et voici le résumé qui en a été fait :\n\n"
                    f"{reponse_brute}\n\n"
                    f"Vérifie que ce résumé reflète fidèlement les résultats ci-dessus, sans invention ni déformation. "
                    f"Si c'est correct, réponds uniquement 'CORRECT'. "
                    f"Sinon, réponds au format exact suivant :\n"
                    f"ERREUR: <description brève de l'erreur>\n"
                    f"CORRECTION: <le résumé corrigé complet>"
                )
            }],
            max_tokens=600
        )
        contenu_verif = verification.choices[0].message.content.strip()

        if contenu_verif.startswith("ERREUR"):
            partie_erreur = contenu_verif.split("CORRECTION:")[0].replace("ERREUR:", "").strip()
            partie_correction = contenu_verif.split("CORRECTION:")[1].strip()
            enregistrer_lecon_alpha(partie_erreur, partie_correction)
            return partie_correction
    except Exception:
        pass

    return reponse_brute
def transmettre_a_lambda(instruction: str) -> str:
    from lambda_agent import gerer_documents
    return gerer_documents(instruction)
OUTILS_ALPHA = {
    "rechercher_sur_le_web": collecter_informations,
    "lire_page_web": lire_page_web,
    "ouvrir_navigateur": ouvrir_navigateur,
    "transmettre_a_lambda": transmettre_a_lambda,
}

SCHEMA_ALPHA = [
    {"type": "function", "function": {"name": "rechercher_sur_le_web", "description": "Recherche sur le web et renvoie une synthèse vérifiée et sourcée", "parameters": {"type": "object", "properties": {"question": {"type": "string"}}, "required": ["question"]}}},
    {"type": "function", "function": {"name": "lire_page_web", "description": "Lit le texte d'une page web précise à partir de son URL", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "ouvrir_navigateur", "description": "Ouvre une page ou une recherche dans le navigateur de Monsieur, sur son écran", "parameters": {"type": "object", "properties": {"cible": {"type": "string", "description": "Une URL complète, ou des mots-clés pour lancer une recherche Google"}}, "required": ["cible"]}}},
    {"type": "function", "function": {"name": "transmettre_a_lambda", "description": "Confie à Lambda, l'agent des documents, la création d'un document Word contenant les informations rassemblées. L'instruction doit inclure le nom du fichier, le titre et TOUT le contenu à y ranger", "parameters": {"type": "object", "properties": {"instruction": {"type": "string"}}, "required": ["instruction"]}}},
]
OUTILS_ALPHA["demander_a_un_agent"] = creer_outil_collaboration("Alpha")
SCHEMA_ALPHA.append(schema_collaboration("Alpha"))

@suivre_agent("Alpha")

def rechercher_avec_agent(question: str) -> str:
    instructions_systeme = (
        "Tu es Alpha, un agent de recherche. Utilise rechercher_sur_le_web pour les questions générales "
        "(plusieurs fois, sous des angles différents, si Monsieur veut un dossier complet), lire_page_web "
        "pour lire une URL précise, et ouvrir_navigateur quand Monsieur demande de voir ou d'ouvrir une "
        "page ou une recherche. Si Monsieur demande d'enregistrer les informations dans un document Word, "
        "rassemble d'abord les informations (au moins trois recherches ou pages), puis appelle "
        "transmettre_a_lambda avec une instruction complète : le nom du fichier (ex: recherche_<sujet>.docx), "
        "le titre, l'ordre de l'ouvrir ensuite avec l'Explorateur, et TOUT le contenu rassemblé, en texte brut "
        "organisé en sections, sans symboles markdown. Tu n'écris jamais le document toi-même. "
        "Commence ta réponse finale par un résumé oral de 4 à 5 phrases (400 caractères maximum, sans liste "
        "ni symboles), puis indique le nom du document créé par Lambda. Réponds de façon claire et sourcée."
    )
    return executer_sous_agent("Alpha", instructions_systeme, OUTILS_ALPHA, SCHEMA_ALPHA, question,
                               max_iterations=10, max_tokens=4096)