import streamlit as st
import edge_tts
import asyncio
import re
import os
from main import lancer_agent, client
from agents_multiples import lancer_equipe
st.title("Christiane - Assistant IA")
import os

def generer_audio(texte, chemin="reponse_audio.mp3"):
    async def _generer():
        communicate = edge_tts.Communicate(texte, "fr-FR-DeniseNeural")
        await communicate.save(chemin)
    asyncio.run(_generer())

def nettoyer_texte_audio(texte):
    texte = re.sub(r'#+\s*', '', texte)
    texte = re.sub(r'\*\*(.*?)\*\*', r'\1', texte)
    texte = re.sub(r'\*(.*?)\*', r'\1', texte)
    texte = re.sub(r'`(.*?)`', r'\1', texte)
    texte = re.sub(r'^[\-\*]\s+', '', texte, flags=re.MULTILINE)
    return texte

if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

if not st.session_state.authentifie:
    mot_de_passe_saisi = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if mot_de_passe_saisi == os.getenv("INTERFACE_MOT_DE_PASSE"):
            st.session_state.authentifie = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect")
    st.stop()
import json

def charger_historique():
    try:
        with open("historique.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def sauvegarder_historique(historique):
    with open("historique.json", "w", encoding="utf-8") as f:
        json.dump(historique, f, ensure_ascii=False, indent=2)

if "historique" not in st.session_state:
    st.session_state.historique = charger_historique()

skills_disponibles = []
if os.path.exists("skills"):
    skills_disponibles = [f.replace(".txt", "") for f in os.listdir("skills") if f.endswith(".txt")]

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
        f"\n\nDemande : {objectif_utilisateur}\n\n"
        f"Réponds uniquement avec le nom du mode le plus pertinent, ou 'aucun'."
    )
    try:
        reponse = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt_detection}],
            max_tokens=20
        )
        choix = reponse.choices[0].message.content.strip().lower()
        return choix if choix in skills_disponibles else ""
    except Exception:
        return ""
mode = st.radio("Mode", ["Normal", "Équipe (recherche + rédaction + flashcards)"])
autoriser_actions = st.checkbox("Autoriser les actions sensibles (écriture de fichiers, envoi d'emails)")
fichier_uploade = st.file_uploader("Ou dépose un PDF à analyser", type="pdf")
if fichier_uploade:
    with open(f"upload_{fichier_uploade.name}", "wb") as f:
        f.write(fichier_uploade.getbuffer())
    st.success(f"Fichier {fichier_uploade.name} prêt. Demande à Christiane de le lire avec lire_pdf.")

st.write("🎤 Ou enregistre ta question à la voix :")
audio_enregistre = st.audio_input("Clique pour parler")

question_vocale = ""
if audio_enregistre is not None:
    with st.spinner("Transcription en cours..."):
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio_enregistre.read()),
            model="whisper-large-v3",
            language="fr"
        )
        question_vocale = transcription.text
    st.success(f"Tu as dit : {question_vocale}")

question_texte = st.text_input("Que dois-je faire ?")
question = question_vocale or question_texte

if st.button("Envoyer") and question:
    if mode == "Équipe (recherche + rédaction + flashcards)":
        with st.spinner("L'équipe travaille (ça peut prendre 1 à 2 minutes)..."):
            reponse_texte = lancer_equipe(question)
        st.session_state.historique.append({
            "question": question,
            "reponse": reponse_texte,
            "journal": "Mode équipe : Chercheur → Rédacteur → Créateur de flashcards",
            "skill": "équipe"
        })
        generer_audio(nettoyer_texte_audio(reponse_texte))
        st.audio("reponse_audio.mp3", autoplay=True)
    else:
        skill_choisi = detecter_skill(question)
        instructions_skill = ""
        if skill_choisi:
            try:
                with open(f"skills/{skill_choisi}.txt", "r", encoding="utf-8") as f:
                    instructions_skill = f.read()
            except FileNotFoundError:
                pass

        objectif_avec_skill = f"{instructions_skill}\n\n{question}" if instructions_skill else question
        resultat = lancer_agent(objectif_avec_skill, confirmer_action=lambda: autoriser_actions)
        st.session_state.historique.append({
            "question": question,
            "reponse": resultat["reponse"],
            "journal": resultat["journal"],
            "skill": skill_choisi or "aucun"
        })
        generer_audio(nettoyer_texte_audio(resultat["reponse"]))
        st.audio("reponse_audio.mp3", autoplay=True)

sauvegarder_historique(st.session_state.historique)
for echange in reversed(st.session_state.historique):
    st.write(f"**Toi :** {echange['question']}")
    st.write(f"**Christiane** *(mode: {echange['skill']})* : {echange['reponse']}")
    with st.expander("Voir le détail technique"):
        st.text(echange['journal'])
    st.divider()