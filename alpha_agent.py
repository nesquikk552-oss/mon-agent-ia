from ddgs import DDGS
from groq import Groq
import os
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