import streamlit as st
import edge_tts
import asyncio
import re
import os
import json
from main import lancer_agent, client
from streamlit_mic_recorder import speech_to_text
from agents_multiples import lancer_equipe

st.set_page_config(page_title="Christiane", page_icon="🪔", layout="centered")

st.markdown("""
<style>
.bulle-utilisateur {
    background-color: #E07A5F;
    color: white;
    padding: 12px 16px;
    border-radius: 18px 18px 4px 18px;
    margin: 8px 0;
    max-width: 80%;
    margin-left: auto;
}
.bulle-christiane {
    background-color: #F4E1D2;
    color: #3D2B1F;
    padding: 12px 16px;
    border-radius: 18px 18px 18px 4px;
    margin: 8px 0;
    max-width: 80%;
    margin-right: auto;
}
.entete-christiane {
    text-align: center;
    padding: 10px 0 20px 0;
}
</style>
""", unsafe_allow_html=True)

def generer_audio(texte, chemin="reponse_audio.mp3"):
    async def _generer():
        communicate = edge_tts.Communicate(texte, "fr-FR-VivienneMultilingualNeural", rate="-5%")
        await communicate.save(chemin)
    asyncio.run(_generer())

def nettoyer_texte_audio(texte):
    texte = re.sub(r'#+\s*', '', texte)
    texte = re.sub(r'\*\*(.*?)\*\*', r'\1', texte)
    texte = re.sub(r'\*(.*?)\*', r'\1', texte)
    texte = re.sub(r'`(.*?)`', r'\1', texte)
    texte = re.sub(r'^[\-\*]\s+', '', texte, flags=re.MULTILINE)
    texte = re.sub(
        r'[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\U00002700-\U000027BF\U0001F900-\U0001F9FF\U00002190-\U000021FF\U00002B00-\U00002BFF]+',
        '',
        texte
    )
    return texte

if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

if not st.session_state.authentifie:
    st.markdown("<div class='entete-christiane'><h1>🪔 Christiane</h1></div>", unsafe_allow_html=True)
    mot_de_passe_saisi = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if mot_de_passe_saisi == os.getenv("INTERFACE_MOT_DE_PASSE"):
            st.session_state.authentifie = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect")
    st.stop()

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

with st.sidebar:
    st.markdown("### ⚙️ Réglages")
    mode = st.radio("Mode", ["Normal", "Équipe (recherche + rédaction + flashcards)"])
    autoriser_actions = st.checkbox("Autoriser les actions sensibles (écriture de fichiers, envoi d'emails)")
    fichier_uploade = st.file_uploader("Déposer un PDF à analyser", type="pdf")
    if fichier_uploade:
        with open(f"upload_{fichier_uploade.name}", "wb") as f:
            f.write(fichier_uploade.getbuffer())
        st.success(f"Fichier {fichier_uploade.name} prêt.")

st.markdown("<div class='entete-christiane'><h1>🪔 Christiane</h1><p>Ton assistante personnelle</p></div>", unsafe_allow_html=True)

st.write("🎤 Clique et parle, Christiane transcrit en direct :")
question_vocale = speech_to_text(
    language="fr",
    start_prompt="🎤 Parler",
    stop_prompt="⏹️ Arrêter",
    just_once=True,
    key="micro_christiane"
)
if question_vocale:
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
    st.markdown(f"<div class='bulle-utilisateur'>{echange['question']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='bulle-christiane'>{echange['reponse']}</div>", unsafe_allow_html=True)
    with st.expander("Voir le détail technique"):
        st.text(echange['journal'])