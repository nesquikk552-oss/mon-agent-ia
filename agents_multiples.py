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
planificateur = Agent(
    role="Gestionnaire du temps et Organisateur personnel",
    goal="Prioriser les tâches de Monsieur Farnèse et concevoir un planning réaliste et structuré.",
    backstory=(
        "Tu t'appelles Christiane. Tu es l'assistante personnelle espiègle et taquine de Farnèse. "
        "Tu le vouvoies systématiquement et l'appelles 'Monsieur'. Tu es une experte absolue de la méthode "
        "d'organisation (Urgence vs Importance) et tu détestes le désordre."
    ),
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
def lancer_organisation(demande_planning: str, instructions_skill: str) -> str:
    """Gère le mode organisation en appliquant les consignes strictes du skill."""
    
    tache_organisation = Task(
        description=(
            f"Analyse et organise la demande suivante de Monsieur Farnèse : '{demande_planning}'.\n\n"
            f"CONSIGNES SUPPLÉMENTAIRES DU SKILL :\n{instructions_skill}\n\n"
            "Prends en compte sa personnalité d'assistante (espiègle, vouvoiement) dans le résultat final."
        ),
        agent=planificateur,
        expected_output="Un planning clair en liste Markdown, trié par urgence/importance avec créneaux horaires."
    )

    equipe_planning = Crew(
        agents=[planificateur],
        tasks=[tache_organisation]
    )
    
    resultat = equipe_planning.kickoff()
    return str(resultat)

if __name__ == "__main__":
    choix = input("1 pour Révisions (Crew), 2 pour Organisation : ")
    if choix == "1":
        sujet = input("Sujet à explorer et réviser : ")
        print(lancer_equipe(sujet))
    else:
        demande = input("Votre demande de planning, Monsieur ? : ")
        # Exemple de simulation des instructions lues depuis le fichier de skill
        instructions_simulees = "Priorise par urgence/importance. Découpe en sous-étapes. Liste Markdown."
        print(lancer_organisation(demande, instructions_simulees))