from main import lancer_agent
from outils import envoyer_email
from dotenv import load_dotenv
from outils import obtenir_meteo
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

    meteo_du_jour = obtenir_meteo("Cotonou")
    message_final = f"{resultat['reponse']}\n\nMétéo du jour à Cotonou : {meteo_du_jour}"

    envoyer_email(
        destinataire=os.getenv("EMAIL_ADRESSE"),
        sujet="Ton résumé du jour - Christiane",
        message=message_final
    )

if __name__ == "__main__":
    envoyer_rappel()