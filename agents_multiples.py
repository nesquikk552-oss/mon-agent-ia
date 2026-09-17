from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from outils import rechercher_web

load_dotenv()

MODELE = "groq/openai/gpt-oss-120b"

chercheur = Agent(
    role="Chercheur",
    goal="Trouver des informations précises et à jour sur un sujet donné",
    backstory="Tu es expert en recherche documentaire, rigoureux et factuel.",
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
    infos = rechercher_web(sujet)

    tache_redaction = Task(
        description=f"À partir de ces informations : {infos}\n\nRédige une explication claire et structurée sur : {sujet}",
        agent=redacteur,
        expected_output="Un texte pédagogique structuré en plusieurs parties"
    )

    tache_flashcards = Task(
        description="À partir de l'explication précédente, crée 3 à 5 flashcards (question / réponse) pour réviser ce sujet.",
        agent=reviseur,
        expected_output="Une liste de flashcards au format Question: ... / Réponse: ..."
    )

    equipe = Crew(agents=[redacteur, reviseur], tasks=[tache_redaction, tache_flashcards])
    resultat = equipe.kickoff()
    return str(resultat)

if __name__ == "__main__":
    sujet = input("Sujet à explorer et réviser : ")
    resultat = lancer_equipe(sujet)
    print("\n--- RÉSULTAT DE L'ÉQUIPE ---\n")
    print(resultat)