from ddgs import DDGS
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def collecter_informations(question, nombre_resultats=5):
    resultats = []
    with DDGS() as recherche:
        for r in recherche.text(question, max_results=nombre_resultats):
            resultats.append(f"- {r['title']} : {r['body']} (source : {r['href']})")

    if not resultats:
        return "Aucune information trouvée sur le web pour cette question."

    contenu_brut = "\n".join(resultats)

    prompt_synthese = (
        f"Voici des résultats de recherche web sur la question : {question}\n\n"
        f"{contenu_brut}\n\n"
        f"Résume ces informations de façon claire et fiable, en gardant les sources importantes."
    )

    reponse = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt_synthese}],
        max_tokens=600
    )
    return reponse.choices[0].message.content