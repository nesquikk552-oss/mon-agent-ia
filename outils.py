import smtplib
from email.mime.text import MIMEText
import requests
import os
from datetime import datetime
from tavily import TavilyClient
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
def lire_fichier(chemin: str) -> str:
    from datetime import datetime
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Erreur : {e}"

def ecrire_fichier(chemin: str, contenu: str) -> str:
    try:
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(contenu)
        return f"Fichier {chemin} écrit avec succès."
    except Exception as e:
        return f"Erreur : {e}"

def lister_fichiers(dossier: str = ".") -> str:
    try:
        return "\n".join(os.listdir(dossier))
    except Exception as e:
        return f"Erreur : {e}"
def calculer(expression: str) -> str:
    try:
        resultat = eval(expression, {"__builtins__": {}})
        return str(resultat)
    except Exception as e:
        return f"Erreur de calcul : {e}"
def ajouter_a_memoire(information: str) -> str:
    try:
        with open("memoire.txt", "a", encoding="utf-8") as f:
            f.write(information + "\n")
        return "Information mémorisée avec succès."
    except Exception as e:
        return f"Erreur : {e}"
    from tavily import TavilyClient
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def rechercher_web(requete: str) -> str:
    try:
        resultats = tavily_client.search(requete, max_results=3)
        return str(resultats)
    except Exception as e:
        return f"Erreur : {e}"
def obtenir_date_heure() -> str:
    return datetime.now().strftime("%A %d %B %Y, %H:%M")
def creer_flashcard(question: str, reponse: str) -> str:
    try:
        with open("flashcards.txt", "a", encoding="utf-8") as f:
            f.write(f"Q: {question}\nR: {reponse}\n---\n")
        return "Flashcard ajoutée."
    except Exception as e:
        return f"Erreur : {e}"
def convertir_unite(valeur: float, de_unite: str, vers_unite: str) -> str:
    conversions = {
        ("km", "m"): 1000, ("m", "km"): 0.001,
        ("m", "cm"): 100, ("cm", "m"): 0.01,
        ("kg", "g"): 1000, ("g", "kg"): 0.001,
    }
    if de_unite == "celsius" and vers_unite == "fahrenheit":
        return str(valeur * 9/5 + 32)
    if de_unite == "fahrenheit" and vers_unite == "celsius":
        return str((valeur - 32) * 5/9)
    facteur = conversions.get((de_unite, vers_unite))
    if facteur:
        return str(valeur * facteur)
    return "Conversion non supportée"
def compter_mots(texte: str) -> str:
    nb_mots = len(texte.split())
    nb_caracteres = len(texte)
    return f"{nb_mots} mots, {nb_caracteres} caractères"
def obtenir_meteo(ville: str) -> str:
    try:
        cle = os.getenv("OPENWEATHER_API_KEY")
        url = f"https://api.openweathermap.org/data/2.5/weather?q={ville}&appid={cle}&units=metric&lang=fr"
        reponse = requests.get(url)
        data = reponse.json()
        if reponse.status_code != 200:
            return f"Erreur : {data.get('message', 'ville introuvable')}"
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return f"À {ville} : {temp}°C, {description}"
    except Exception as e:
        return f"Erreur : {e}"
def envoyer_email(destinataire: str, sujet: str, message: str) -> str:
    try:
        expediteur = os.getenv("EMAIL_ADRESSE")
        mot_de_passe = os.getenv("EMAIL_MOT_DE_PASSE")

        mail = MIMEText(message)
        mail["Subject"] = sujet
        mail["From"] = expediteur
        mail["To"] = destinataire

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as serveur:
            serveur.login(expediteur, mot_de_passe)
            serveur.sendmail(expediteur, destinataire, mail.as_string())

        return f"Email envoyé à {destinataire}."
    except Exception as e:
        return f"Erreur : {e}"
OUTILS_DISPONIBLES ={
    "lire_fichier": lire_fichier,
    "ecrire_fichier": ecrire_fichier,
    "lister_fichiers": lister_fichiers,
    "calculer": calculer,
    "ajouter_a_memoire": ajouter_a_memoire,
    "rechercher_web": rechercher_web,
    "obtenir_date_heure": obtenir_date_heure,
    "creer_flashcard": creer_flashcard,
    "convertir_unite": convertir_unite,
    "compter_mots": compter_mots,
    "obtenir_meteo": obtenir_meteo,
    "envoyer_email": envoyer_email,
}
