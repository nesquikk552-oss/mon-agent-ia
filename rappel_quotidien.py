from main import lancer_agent
from outils import envoyer_email
from dotenv import load_dotenv
import os

load_dotenv()

def envoyer_rappel():
    try:
        with open("taches.txt", "r", encoding="utf-8") as f:
            taches = f.read()
    except FileNotFoundError:
        taches = "Aucune tâche notée."

    resultat = lancer_agent(
        f"Résume ces tâches de façon motivante pour bien démarrer la journée : {taches}",
        confirmer_action=lambda: True
    )

    envoyer_email(
        destinataire=os.getenv("EMAIL_ADRESSE"),
        sujet="Ton résumé du jour - Christiane",
        message=resultat["reponse"]
    )

if __name__ == "__main__":
    envoyer_rappel()