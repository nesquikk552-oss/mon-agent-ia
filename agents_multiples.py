import os
from crewai import Agent, Task, Crew
from crewai.tools import tool
from dotenv import load_dotenv
load_dotenv()

from outils import rechercher_web
from outils import rechercher_web
import crewai.llms.cache as _crewai_cache
_crewai_cache.mark_cache_breakpoint = lambda msg: msg


MODELE = "groq/openai/gpt-oss-120b"

@tool("Recherche web")
def outil_recherche(sujet: str) -> str:
    """Recherche des informations à jour sur le web à propos d'un sujet donné."""
    resultat = rechercher_web(sujet)
    return resultat[:1500]
chercheur = Agent(
    role="Chercheur",
    goal="Trouver des informations précises et à jour sur un sujet donné",
    backstory="Tu es expert en recherche documentaire, rigoureux et factuel.",
    tools=[outil_recherche],
    llm=MODELE,
    verbose=True
)

redacteur = Agent(
    role="Rédacteur pédagogique",
    goal="Vulgariser et structurer l'information pour un étudiant en révision",
    backstory="Tu es expert en pédagogie, tu expliques simplement et clairement.",
    llm=MODELE,
    verbose=True
)

reviseur = Agent(
    role="Créateur de flashcards",
    goal="Transformer une explication en flashcards question/réponse",
    backstory="Tu es expert en mémorisation active et en création de fiches de révision.",
    llm=MODELE,
    verbose=True
)

def lancer_equipe(sujet: str) -> str:
    tache_recherche = Task(
    description=f"Recherche des informations précises et à jour sur : {sujet}. "
                f"IMPORTANT : ne recopie jamais de longs extraits de texte. Résume chaque source en 2-3 phrases maximum.",
    agent=chercheur,
    expected_output="Un résumé court et synthétique (maximum 300 mots au total) des points clés trouvés, sans citations longues"
)

    tache_redaction = Task(
        description=f"À partir des recherches précédentes, rédige une explication claire et structurée sur : {sujet}",
        agent=redacteur,
        expected_output="Un texte pédagogique structuré en plusieurs parties",
        context=[tache_recherche]
    )

    tache_flashcards = Task(
        description="À partir de l'explication précédente, crée 3 à 5 flashcards (question / réponse) pour réviser ce sujet.",
        agent=reviseur,
        expected_output="Une liste de flashcards au format Question: ... / Réponse: ...",
        context=[tache_redaction]
    )

    equipe = Crew(
        agents=[chercheur, redacteur, reviseur],
        tasks=[tache_recherche, tache_redaction, tache_flashcards]
    )
    resultat = equipe.kickoff()
    return str(resultat)

if __name__ == "__main__":
    sujet = input("Sujet à explorer et réviser : ")
    resultat = lancer_equipe(sujet)
    print("\n--- RÉSULTAT DE L'ÉQUIPE ---\n")
    print(resultat)