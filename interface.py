from datetime import datetime
import streamlit as st
import edge_tts
import asyncio
import re
import os
import json
import base64
import streamlit.components.v1 as components
import datetime as dt
from main import lancer_agent, client
from agents_multiples import lancer_equipe
from streamlit_mic_recorder import speech_to_text

def charger_carte_monde_base64(chemin="carte_monde.png"):
    try:
        with open(chemin, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

def charger_logo_base64(chemin="logo.png"):
    try:
        with open(chemin, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None
carte_monde_b64 = charger_carte_monde_base64()

logo_b64 = charger_logo_base64()
st.set_page_config(page_title="Christiane", page_icon="logo.png" if os.path.exists("logo.png") else "🌐", layout="wide")

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at 50% 20%, #131A2A 0%, #0B0F1A 55%, #060810 100%);
}
.fond-hud {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-image: radial-gradient(#22D3EE22 1px, transparent 1px);
    background-size: 22px 22px;
}
.carte-monde-fond {
    position: fixed;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 650px;
    max-width: 85vw;
    opacity: 0.07;
    z-index: 0;
    pointer-events: none;
    filter: grayscale(1) sepia(1) hue-rotate(150deg) saturate(3);
    -webkit-mask-image: radial-gradient(circle, black 40%, transparent 70%);
    mask-image: radial-gradient(circle, black 40%, transparent 70%);
}
.logo-fond {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 480px;
    opacity: 0.05;
    z-index: 0;
    pointer-events: none;
}
.carte-connexion {
    position: relative;
    z-index: 1;
    background: #0E1420cc;
    border: 1px solid #22D3EE55;
    border-radius: 4px;
    padding: 40px 34px;
    backdrop-filter: blur(4px);
    box-shadow: 0 0 30px #22D3EE22;
}
.carte-connexion::before, .carte-connexion::after {
    content: "";
    position: absolute;
    width: 18px; height: 18px;
    border: 2px solid #22D3EE;
    opacity: 0.8;
}
.carte-connexion::before { top: -2px; left: -2px; border-right: none; border-bottom: none; }
.carte-connexion::after { bottom: -2px; right: -2px; border-left: none; border-top: none; }
.logo-globe {
    font-size: 34px;
    text-shadow: 0 0 12px #22D3EE, 0 0 24px #22D3EE88;
}
[data-testid="stSidebar"] { background-color: #0E1420; }
.sidebar-titre {
    display:flex; align-items:center; gap:8px;
    font-size: 20px; font-weight:600; color:#E5E9F0;
    margin-bottom: 18px;
}
.sidebar-section {
    text-transform: uppercase; font-size: 11px; letter-spacing: 1.5px;
    color: #5E6B85; margin: 22px 0 8px 0;
}
.historique-item {
    font-size: 13px; color: #9AA6BC; padding: 6px 0;
    border-bottom: 1px solid #1C2333; overflow: hidden;
    text-overflow: ellipsis; white-space: nowrap;
}
.hero-accueil { text-align: center; margin: 10px 0 20px 0; }
.hero-accueil .sous-titre {
    text-transform: uppercase; letter-spacing: 3px; font-size: 12px;
    color: #22D3EE; margin-top: 14px; margin-bottom: 6px;
}
.hero-accueil h1 { font-size: 30px; color: #E5E9F0; margin: 0; }
.composer {
    background: #131A2A; border: 1px solid #22D3EE33;
    border-radius: 18px; padding: 10px 16px; margin: 10px 0 26px 0;
}
.carte-suggestion {
    background: #131A2A; border: 1px solid #22D3EE22; border-radius: 12px;
    padding: 16px; text-align:left; margin-bottom: 8px;
}
.carte-suggestion .titre { color:#22D3EE; font-weight:600; font-size:14px; margin-bottom:4px; }
.carte-suggestion .desc { color:#7C8AA5; font-size:12px; }
.bulle-utilisateur {
    background-color: #22D3EE; color: #0B0F1A; padding: 12px 16px;
    border-radius: 14px 14px 4px 14px; margin: 8px 0; max-width: 80%;
    margin-left: auto; font-weight: 500;
}
.bulle-christiane {
    background-color: #131A2A; color: #E5E9F0; border: 1px solid #22D3EE22;
    padding: 12px 16px; border-radius: 14px 14px 14px 4px; margin: 8px 0;
    max-width: 80%; margin-right: auto;
}
.zone-vocale { text-align: center; padding: 40px 20px; max-width: 600px; margin: 0 auto; }
.zone-vocale .logo-vocal { font-size: 70px; text-shadow: 0 0 20px #22D3EE, 0 0 40px #22D3EE88; margin-bottom: 10px; }
.logo-vocal.actif { animation: pulsation-hologramme 1.2s ease-in-out infinite; }
@keyframes pulsation-hologramme {
    0%, 100% { text-shadow: 0 0 20px #22D3EE, 0 0 40px #22D3EE88; transform: scale(1); }
    50% { text-shadow: 0 0 35px #22D3EE, 0 0 70px #22D3EEcc; transform: scale(1.05); }
}
.anneaux-hologramme { position: relative; width: 120px; height: 120px; margin: 0 auto 16px; }
.anneaux-hologramme .anneau { position: absolute; inset: 0; border: 1.5px solid #22D3EE; border-radius: 50%; opacity: 0; animation: expansion-anneau 2s ease-out infinite; }
.anneaux-hologramme .anneau:nth-child(2) { animation-delay: 0.6s; }
.anneaux-hologramme .anneau:nth-child(3) { animation-delay: 1.2s; }
@keyframes expansion-anneau {
    0% { transform: scale(0.6); opacity: 0.7; }
    100% { transform: scale(1.4); opacity: 0; }
}
.reponse-vocale { background: #131A2A; border: 1px solid #22D3EE33; border-radius: 14px; padding: 24px; margin-top: 20px; font-size: 18px; line-height: 1.6; text-align: left; }
.question-vocale-affichee { color: #7C8AA5; font-size: 14px; margin-bottom: 10px; text-align: left; }
</style>
""", unsafe_allow_html=True)
def globe_anime_html(taille=140):
    rayon = int(taille * 0.85)
    return f"""
    <div style="position:relative; display:flex; justify-content:center; align-items:center; width:{taille}px; height:{taille}px; margin:0 auto; perspective:700px; overflow:visible;">
        <div class="tumble_{taille}" style="width:{int(taille*0.75)}px; height:{int(taille*0.75)}px; transform-style:preserve-3d; will-change:transform;">
            <img src="data:image/png;base64,{logo_b64}" style="width:100%; height:100%; object-fit:contain; image-rendering:auto;">
        </div>
        <div class="orbite_{taille} orbite-a_{taille}"><div class="satellite_{taille} sat-a_{taille}"></div></div>
        <div class="orbite_{taille} orbite-b_{taille}"><div class="satellite_{taille} sat-b_{taille}"></div></div>
        <div class="orbite_{taille} orbite-c_{taille}"><div class="satellite_{taille} sat-c_{taille}"></div></div>
    </div>
    <style>
    .tumble_{taille} {{
        animation: tumble_{taille} 10s ease-in-out infinite;
    }}
    @keyframes tumble_{taille} {{
        0%   {{ transform: rotateY(0deg); }}
        50%  {{ transform: rotateY(180deg); }}
        100% {{ transform: rotateY(360deg); }}
    }}
    .orbite_{taille} {{
        position: absolute;
        top: 50%; left: 50%;
        width: 0; height: 0;
        transform-style: preserve-3d;
    }}
    .satellite_{taille} {{
        position: absolute;
        width: 7px; height: 7px;
        border-radius: 50%;
        background: #22D3EE;
        box-shadow: 0 0 8px #22D3EE, 0 0 14px #22D3EEcc;
    }}
    .orbite-a_{taille} {{ animation: orbite-a_{taille} 5s linear infinite; }}
    .sat-a_{taille} {{ top: -{rayon}px; left: -3px; }}
    @keyframes orbite-a_{taille} {{
        from {{ transform: rotate(0deg) rotateX(70deg); }}
        to   {{ transform: rotate(360deg) rotateX(70deg); }}
    }}
    .orbite-b_{taille} {{ animation: orbite-b_{taille} 8s linear infinite reverse; }}
    .sat-b_{taille} {{ top: -{rayon}px; left: -3px; background:#7FE7D8; box-shadow: 0 0 8px #7FE7D8, 0 0 14px #7FE7D8cc; }}
    @keyframes orbite-b_{taille} {{
        from {{ transform: rotate(0deg) rotateX(-55deg) rotateZ(35deg); }}
        to   {{ transform: rotate(360deg) rotateX(-55deg) rotateZ(35deg); }}
    }}
    .orbite-c_{taille} {{ animation: orbite-c_{taille} 12s linear infinite; }}
    .sat-c_{taille} {{ top: -{rayon}px; left: -2.5px; width:5px; height:5px; background:#BFFBF0; box-shadow: 0 0 6px #BFFBF0; }}
    @keyframes orbite-c_{taille} {{
        from {{ transform: rotate(0deg) rotateX(25deg) rotateZ(-40deg); }}
        to   {{ transform: rotate(360deg) rotateX(25deg) rotateZ(-40deg); }}
    }}
    </style>
    """

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
        '', texte
    )
    return texte

if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

if not st.session_state.authentifie:
    st.markdown("<div class='fond-hud'></div>", unsafe_allow_html=True)
    if carte_monde_b64:
        st.markdown(f"<img class='carte-monde-fond' src='data:image/png;base64,{carte_monde_b64}'>", unsafe_allow_html=True)
    if logo_b64:
        st.markdown(f"<img class='logo-fond' src='data:image/png;base64,{logo_b64}'>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='carte-connexion'>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        components.html(globe_anime_html(160), height=180)
        st.markdown("<h2 style='text-align:center; margin-top:-10px;'>Christiane</h2></div>", unsafe_allow_html=True)
        mot_de_passe_saisi = st.text_input("Mot de passe", type="password")
        bouton_connexion = st.button("Se connecter")
    st.markdown("</div>", unsafe_allow_html=True)

    if bouton_connexion:
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
def traiter_question(question, mode_equipe, autoriser_actions_locales):
    if mode_equipe:
        reponse_texte = lancer_equipe(question)
        journal = "Mode équipe : Chercheur → Rédacteur → Créateur de flashcards"
        skill_utilise = "équipe"
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
        resultat = lancer_agent(objectif_avec_skill, confirmer_action=lambda: autoriser_actions_locales)
        reponse_texte = resultat["reponse"]
        journal = resultat["journal"]
        skill_utilise = skill_choisi or "aucun"

    st.session_state.historique.append({
        "question": question, "reponse": reponse_texte,
        "journal": journal, "skill": skill_utilise
    })
    sauvegarder_historique(st.session_state.historique)
    generer_audio(nettoyer_texte_audio(reponse_texte))
    return reponse_texte
with st.sidebar:
    logo_sidebar = f"<img src='data:image/png;base64,{logo_b64}' width='28' style='vertical-align:middle;margin-right:8px;'>" if logo_b64 else "🌐"
    st.markdown(f"<div class='sidebar-titre'>{logo_sidebar} Christiane</div>", unsafe_allow_html=True)

    if st.button("🔄 Nouvelle conversation", use_container_width=True):
        st.session_state.historique = []
        sauvegarder_historique([])
        st.rerun()
    st.markdown("<div class='sidebar-section'>Mode</div>", unsafe_allow_html=True)
    mode_vocal = st.toggle("🎙️ Mode vocal uniquement", key="mode_vocal")
    st.markdown("<div class='sidebar-section'>Réglages</div>", unsafe_allow_html=True)
    mode = st.radio("Mode", ["Normal", "Équipe (recherche + rédaction + flashcards)"], label_visibility="collapsed")
    autoriser_actions = st.checkbox("Autoriser les actions sensibles")
    fichier_uploade = st.file_uploader("Déposer un PDF", type="pdf")
    if fichier_uploade:
        with open(f"upload_{fichier_uploade.name}", "wb") as f:
            f.write(fichier_uploade.getbuffer())
        st.success(f"{fichier_uploade.name} prêt.")

    st.markdown("<div class='sidebar-section'>Historique récent</div>", unsafe_allow_html=True)
    for echange in list(reversed(st.session_state.historique))[:6]:
        st.markdown(f"<div class='historique-item'>{echange['question']}</div>", unsafe_allow_html=True)

mode_equipe_actif = mode == "Équipe (recherche + rédaction + flashcards)"

if mode_vocal:
    logo_vocal = f"<img src='data:image/png;base64,{logo_b64}' width='70'>" if logo_b64 else "<span class='logo-vocal'>🌐</span>"
    st.markdown(f"""
    <div class='zone-vocale'>
        <div class='anneaux-hologramme'>
            <div class='anneau'></div>
            <div class='anneau'></div>
            <div class='anneau'></div>
            <div class='logo-vocal actif' style='position:absolute; inset:0; display:flex; align-items:center; justify-content:center;'>{logo_vocal}</div>
        </div>
        <div class='sous-titre' style='color:#22D3EE; letter-spacing:3px; font-size:12px; text-transform:uppercase;'>Mode vocal</div>
        <h1 style='color:#E5E9F0;'>Parlez à Christiane</h1>
    </div>
    """, unsafe_allow_html=True)

    col_g, col_c, col_d = st.columns([1, 1, 1])
    with col_c:
        question_vocale_seule = speech_to_text(
            language="fr", start_prompt="🎤 Appuyez pour parler",
            stop_prompt="⏹️ Arrêter", just_once=True, use_container_width=True,
            key="micro_vocal_seul"
        )

    if question_vocale_seule:
        with st.spinner("Christiane réfléchit..."):
            reponse = traiter_question(question_vocale_seule, mode_equipe_actif, autoriser_actions)
        st.markdown(f"""
        <div class='reponse-vocale'>
            <div class='question-vocale-affichee'>🎤 {question_vocale_seule}</div>
            {reponse}
        </div>
        """, unsafe_allow_html=True)
        st.audio("reponse_audio.mp3", autoplay=True)

else:
    logo_hero = f"<img src='data:image/png;base64,{logo_b64}' width='70'>" if logo_b64 else "<span class='logo-globe'>🌐</span>"
    st.markdown(f"""
    <div class='hero-accueil'>
        {logo_hero}
        <div class='sous-titre'>Bon retour</div>
        <h1>Que puis-je faire pour vous aujourd'hui ?</h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='composer'>", unsafe_allow_html=True)
    col_micro, col_texte, col_envoyer = st.columns([1, 6, 1])
    with col_micro:
        question_vocale = speech_to_text(language="fr", start_prompt="🎤", stop_prompt="⏹️", just_once=True, key="micro_christiane")
    with col_texte:
        question_texte = st.text_input("Que dois-je faire ?", label_visibility="collapsed", placeholder="Écrivez ou parlez à Christiane...")
    with col_envoyer:
        bouton_envoyer = st.button("➤", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col_logo, col_titre, col_date = st.columns([1, 4, 2])
    with col_logo:
        components.html(globe_anime_html(65), height=75)
    with col_titre:
        st.markdown("<h1 style='color:#22D3EE; letter-spacing:2px; margin:8px 0 0 0;'>CHRISTIANE</h1><p style='color:#7C8AA5; font-size:13px; margin:0;'>Assistante personnelle</p>", unsafe_allow_html=True)
    maintenant = datetime.now().strftime("%A %d %B %Y")
    with col_date:
        st.markdown(f"<div style='text-align:right; color:#7C8AA5; font-size:13px; margin-top:16px;'>{maintenant}</div>", unsafe_allow_html=True)

    if question_vocale:
        st.caption(f"🎤 Tu as dit : {question_vocale}")

    question = question_vocale or question_texte

    suggestions = {
        "revision": ("📘", "Réviser un cours", "Prépare une fiche ou un QCM sur un sujet"),
        "redaction": ("✍️", "Rédiger un texte", "Aide à écrire ou structurer un document"),
        "organisation": ("🗂️", "M'organiser", "Planifier mes révisions ou mes tâches"),
    }
    col_a, col_b, col_c = st.columns(3)
    cartes = [col_a, col_b, col_c]
    for col, (cle, (icone, titre, desc)) in zip(cartes, suggestions.items()):
        with col:
            st.markdown(f"<div class='carte-suggestion'><div class='titre'>{icone} {titre}</div><div class='desc'>{desc}</div></div>", unsafe_allow_html=True)
            if st.button("Utiliser", key=f"suggestion_{cle}", use_container_width=True):
                question = titre
                bouton_envoyer = True

    if bouton_envoyer and question:
        with st.spinner("Christiane réfléchit..."):
            traiter_question(question, mode_equipe_actif, autoriser_actions)
        st.audio("reponse_audio.mp3", autoplay=True)

    for echange in reversed(st.session_state.historique):
        st.markdown(f"<div class='bulle-utilisateur'>{echange['question']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='bulle-christiane'>{echange['reponse']}</div>", unsafe_allow_html=True)
        with st.expander("Voir le détail technique"):
            st.text(echange['journal'])