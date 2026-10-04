import asyncio
import base64
import html
import json
import os
import re
import subprocess
from uuid import uuid4
from datetime import datetime

import edge_tts
import requests
import streamlit as st
import streamlit.components.v1 as components
from wispr import micro_wispr

from agents_multiples import lancer_equipe
from main import client, lancer_agent

# ----------------------------------------------------------------------
# Constantes
# ----------------------------------------------------------------------
MODE_EQUIPE = "Équipe (recherche + rédaction + flashcards)"
URL_VOIX_LOCALE = "http://127.0.0.1:5005/parler"
LONGUEUR_MAX_VOIX = 500

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]

# (lettre grecque, texte) ; "grio" utilise l'image grio_logo.png si elle existe
AGENTS = [
    ("Αα", "Alpha, assistant de recherche, actif"),
    ("Ββ", "Beta, assistant fichiers, actif"),
    ("grio", "Grio, assistant mathématiques, actif"),
    ("Δδ", "Delta, assistant révisions, actif"),
    ("Γγ", "Gamma, assistant agenda et météo, actif"),
    ("Λλ", "Lambda, assistant documents, actif"),
]


# ----------------------------------------------------------------------
# Utilitaires
# ----------------------------------------------------------------------
def charger_image_base64(chemin):
    """Retourne l'image en base64, ou None si le fichier n'existe pas."""
    try:
        with open(chemin, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None


def date_francaise():
    n = datetime.now()
    return f"{JOURS[n.weekday()].capitalize()} {n.day} {MOIS[n.month - 1]} {n.year}"


carte_monde_b64 = charger_image_base64("carte_monde.png")
logo_b64 = charger_image_base64("logo.png")
logo_grio_b64 = charger_image_base64("grio_logo.png")

st.set_page_config(
    page_title="Christiane",
    page_icon="logo.png" if os.path.exists("logo.png") else "🌐",
    layout="wide",
)

# ----------------------------------------------------------------------
# Style
# ----------------------------------------------------------------------
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
.logo-globe {
    font-size: 34px;
    text-shadow: 0 0 12px #22D3EE, 0 0 24px #22D3EE88;
}
.badge-agent {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #131A2A;
    border: 1px solid #22D3EE44;
    border-radius: 20px;
    padding: 6px 14px;
    margin: 8px 4px 0 4px;
    font-size: 13px;
    color: #9AA6BC;
}
.badge-agent .lettre-agent {
    font-size: 18px;
    font-weight: 700;
    color: #22D3EE;
    text-shadow: 0 0 10px #22D3EE, 0 0 20px #22D3EE88;
}
.badge-agent img {
    height: 20px;
    width: auto;
    border-radius: 6px;
    object-fit: cover;
}
[data-testid="stSidebar"] { background-color: #0E1420; }
.sidebar-titre {
    display: flex; align-items: center; gap: 8px;
    font-size: 20px; font-weight: 600; color: #E5E9F0;
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
.carte-suggestion {
    background: #131A2A; border: 1px solid #22D3EE22; border-radius: 12px;
    padding: 16px; text-align: left; margin-bottom: 8px;
}
.carte-suggestion .titre { color: #22D3EE; font-weight: 600; font-size: 14px; margin-bottom: 4px; }
.carte-suggestion .desc { color: #7C8AA5; font-size: 12px; }
.bulle-utilisateur {
    background-color: #22D3EE; color: #0B0F1A; padding: 12px 16px;
    border-radius: 14px 14px 4px 14px; margin: 8px 0; max-width: 80%;
    margin-left: auto; font-weight: 500;
}
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------------
# Animations HTML (canvas)
# ----------------------------------------------------------------------
def globe_anime_html(taille=160, parlant=False):
    return f"""
    <style>html, body {{ background: transparent !important; margin:0; padding:0; }}</style>
    <div style="display:flex; justify-content:center; align-items:center; width:{taille}px; height:{taille}px; margin:0 auto;">
        <canvas id="globe_{taille}" width="{taille}" height="{taille}"></canvas>
    </div>
    <script>
    (function() {{
        var canvas = document.getElementById("globe_{taille}");
        var ctx = canvas.getContext("2d");
        var taille = {taille};
        var centre = taille / 2;
        var rayon = taille * 0.32;

        function pointsSphere() {{
            var pts = [];
            for (var lat = -80; lat <= 80; lat += 20) {{
                for (var lon = 0; lon < 360; lon += 12) {{
                    var latR = lat * Math.PI / 180;
                    var lonR = lon * Math.PI / 180;
                    pts.push({{
                        x: rayon * Math.cos(latR) * Math.cos(lonR),
                        y: rayon * Math.sin(latR),
                        z: rayon * Math.cos(latR) * Math.sin(lonR)
                    }});
                }}
            }}
            return pts;
        }}
        var sphere = pointsSphere();

        var satellites = [
            {{ rayon: taille*0.46, vitesse: 0.018, phase: 0, inclinaison: 0.9, couleur: "#22D3EE" }},
            {{ rayon: taille*0.42, vitesse: -0.013, phase: 2, inclinaison: -0.6, couleur: "#7FE7D8" }},
            {{ rayon: taille*0.50, vitesse: 0.009, phase: 4, inclinaison: 0.3, couleur: "#BFFBF0" }}
        ];

        var angle = 0;
        function dessiner() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            angle += 0.008;

            ctx.strokeStyle = "rgba(93, 224, 198, 0.5)";
            ctx.lineWidth = 1;
            ctx.beginPath();
            for (var i = 0; i < sphere.length; i++) {{
                var p = sphere[i];
                var cosA = Math.cos(angle), sinA = Math.sin(angle);
                var x = p.x * cosA - p.z * sinA;
                var z = p.x * sinA + p.z * cosA;
                var y = p.y;
                if (z > -rayon * 0.15) {{
                    var echelle = 1 + z / (taille * 2);
                    var px = centre + x * echelle;
                    var py = centre - y * echelle;
                    ctx.moveTo(px + 0.8, py);
                    ctx.arc(px, py, 0.9, 0, 6.3);
                }}
            }}
            ctx.stroke();

            var intensite = {str(parlant).lower()};
            var pulsation = intensite ? (22 + Math.sin(angle * 8) * 18) : 0;
            ctx.beginPath();
            ctx.arc(centre, centre, rayon + 2, 0, 6.3);
            ctx.strokeStyle = "rgba(191, 251, 240, 0.6)";
            ctx.lineWidth = 1.4;
            ctx.stroke();
            if (intensite) {{
                ctx.shadowColor = "#22D3EE";
                ctx.shadowBlur = pulsation;
                ctx.stroke();
                ctx.shadowBlur = 0;
            }}

            for (var s = 0; s < satellites.length; s++) {{
                var sat = satellites[s];
                var t = angle * (sat.vitesse / 0.008) + sat.phase;
                var sx = Math.cos(t) * sat.rayon;
                var sz = Math.sin(t) * sat.rayon * sat.inclinaison;
                var sy = Math.sin(t) * sat.rayon * (1 - Math.abs(sat.inclinaison)) * 0.5;
                var echelleS = 1 + sz / (taille * 2);
                var spx = centre + sx * echelleS;
                var spy = centre - sy;
                ctx.beginPath();
                ctx.arc(spx, spy, 3 * echelleS, 0, 6.3);
                ctx.fillStyle = sat.couleur;
                ctx.shadowColor = sat.couleur;
                ctx.shadowBlur = 8;
                ctx.fill();
                ctx.shadowBlur = 0;
            }}

            requestAnimationFrame(dessiner);
        }}
        dessiner();
    }})();
    </script>
    """


def globe_soleil_html(taille=260, parlant=False):
    """Variante 'soleil avec anneaux' (non utilisée pour l'instant)."""
    return f"""
    <style>html, body {{ background: transparent !important; margin:0; padding:0; }}</style>
    <div style="display:flex; justify-content:center; align-items:center; width:{taille}px; height:{taille}px; margin:0 auto;">
        <canvas id="soleil_{taille}" width="{taille}" height="{taille}"></canvas>
    </div>
    <script>
    (function() {{
        var canvas = document.getElementById("soleil_{taille}");
        var ctx = canvas.getContext("2d");
        var taille = {taille} * 0.40;
        var centre = canvas.width / 2;
        var rayonSoleil = taille * 0.16;

        function pointsSphere() {{
            var pts = [];
            for (var lat = -80; lat <= 80; lat += 18) {{
                for (var lon = 0; lon < 360; lon += 14) {{
                    var latR = lat * Math.PI / 180;
                    var lonR = lon * Math.PI / 180;
                    pts.push({{
                        x: rayonSoleil * Math.cos(latR) * Math.cos(lonR),
                        y: rayonSoleil * Math.sin(latR),
                        z: rayonSoleil * Math.cos(latR) * Math.sin(lonR)
                    }});
                }}
            }}
            return pts;
        }}
        var sphere = pointsSphere();

        var anneaux = [
            {{ rayon: taille*0.42, inclinaison: 0.15, vitesse: 0.022, couleur: "#22D3EE", couleurSat: "#FF6B9D", epaisseur: 9 }},
            {{ rayon: taille*0.52, inclinaison: 0.55, vitesse: -0.016, couleur: "#7FE7D8", couleurSat: "#FFD166", epaisseur: 8.5 }},
            {{ rayon: taille*0.62, inclinaison: -0.35, vitesse: 0.011, couleur: "#5DE0C6", couleurSat: "#C77DFF", epaisseur: 8 }},
            {{ rayon: taille*0.72, inclinaison: 0.75, vitesse: -0.008, couleur: "#BFFBF0", couleurSat: "#FF8C42", epaisseur: 7.5 }},
            {{ rayon: taille*0.82, inclinaison: -0.9, vitesse: 0.006, couleur: "#22D3EE", couleurSat: "#4CC9F0", epaisseur: 7 }}
        ];

        function projeter(x, y, z) {{
            var echelle = 1 + z / (taille * 2.2);
            return {{ x: centre + x * echelle, y: centre - y * echelle, echelle: echelle, z: z }};
        }}

        var angleSphere = 0;
        var anglesAnneaux = anneaux.map(function() {{ return 0; }});

        function dessinerAnneau(a, angleRot) {{
            var pts = [];
            var pointSatellite = null;
            for (var t = 0; t <= 360; t += 4) {{
                var r = t * Math.PI / 180;
                var bx = a.rayon * Math.cos(r);
                var bz = a.rayon * Math.sin(r);
                var by = 0;
                var cosI = Math.cos(a.inclinaison), sinI = Math.sin(a.inclinaison);
                var y1 = by * cosI - bz * sinI;
                var z1 = by * sinI + bz * cosI;
                var x1 = bx;
                var cosR = Math.cos(angleRot), sinR = Math.sin(angleRot);
                var x2 = x1 * cosR - z1 * sinR;
                var z2 = x1 * sinR + z1 * cosR;
                var proj = projeter(x2, y1, z2);
                pts.push(proj);
                if (t === 0) pointSatellite = proj;
            }}
            ctx.beginPath();
            ctx.strokeStyle = a.couleur;
            ctx.lineWidth = a.epaisseur;
            ctx.globalAlpha = 0.75;
            for (var i = 0; i < pts.length; i++) {{
                if (i === 0) ctx.moveTo(pts[i].x, pts[i].y);
                else ctx.lineTo(pts[i].x, pts[i].y);
            }}
            ctx.stroke();
            ctx.globalAlpha = 1;

            if (pointSatellite) {{
                ctx.beginPath();
                ctx.arc(pointSatellite.x, pointSatellite.y, 3.2 * pointSatellite.echelle, 0, 6.3);
                ctx.fillStyle = a.couleurSat;
                ctx.shadowColor = a.couleurSat;
                ctx.shadowBlur = 10;
                ctx.fill();
                ctx.shadowBlur = 0;
            }}
        }}

        function dessiner() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            angleSphere += 0.01;

            for (var i = 0; i < anneaux.length; i++) {{
                anglesAnneaux[i] += anneaux[i].vitesse;
                dessinerAnneau(anneaux[i], anglesAnneaux[i]);
            }}

            ctx.beginPath();
            ctx.strokeStyle = "rgba(93, 224, 198, 0.6)";
            ctx.lineWidth = 1;
            for (var j = 0; j < sphere.length; j++) {{
                var p = sphere[j];
                var cosA = Math.cos(angleSphere), sinA = Math.sin(angleSphere);
                var x = p.x * cosA - p.z * sinA;
                var z = p.x * sinA + p.z * cosA;
                if (z > -rayonSoleil * 0.1) {{
                    var proj = projeter(x, p.y, z);
                    ctx.moveTo(proj.x + 0.8, proj.y);
                    ctx.arc(proj.x, proj.y, 0.9, 0, 6.3);
                }}
            }}
            ctx.stroke();

            var intensite = {str(parlant).lower()};
            var pulsation = intensite ? (25 + Math.sin(angleSphere * 6) * 20) : (12 + Math.sin(angleSphere * 2.5) * 8);
            ctx.beginPath();
            ctx.arc(centre, centre, rayonSoleil + 1, 0, 6.3);
            ctx.strokeStyle = "rgba(191, 251, 240, 0.7)";
            ctx.lineWidth = 1.6;
            ctx.stroke();
            ctx.shadowColor = "#22D3EE";
            ctx.shadowBlur = pulsation;
            ctx.stroke();
            ctx.shadowBlur = 0;
            requestAnimationFrame(dessiner);
        }}
        dessiner();
    }})();
    </script>
    """


# ----------------------------------------------------------------------
# Audio
# ----------------------------------------------------------------------
def generer_audio_edge(texte, chemin="reponse_audio.mp3"):
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
        r'[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF'
        r'\U00002700-\U000027BF\U0001F900-\U0001F9FF\U00002190-\U000021FF'
        r'\U00002B00-\U00002BFF]+',
        '', texte
    )
    return texte


def couper_pour_voix(texte, maximum=LONGUEUR_MAX_VOIX):
    """Coupe proprement : à la dernière fin de phrase, sinon au dernier espace."""
    if len(texte) <= maximum:
        return texte
    extrait = texte[:maximum]
    fin_phrase = max(extrait.rfind(". "), extrait.rfind("! "), extrait.rfind("? "), extrait.rfind(".\n"))
    if fin_phrase > 100:
        return extrait[:fin_phrase + 1]
    dernier_espace = extrait.rfind(" ")
    return extrait[:dernier_espace] if dernier_espace > 0 else extrait


def generer_audio_clone(texte, chemin="reponse_audio.mp3"):
    """Voix clonée via le serveur local XTTS. Retourne False si indisponible."""
    try:
        reponse = requests.post(
            URL_VOIX_LOCALE,
            json={"texte": couper_pour_voix(texte)},
            timeout=(2, 180),  # connexion rapide (échec immédiat hors PC), synthèse lente OK
        )
        if reponse.status_code != 200:
            return False
        with open("reponse_temp.wav", "wb") as f:
            f.write(reponse.content)
        subprocess.run(
            ["ffmpeg", "-y", "-i", "reponse_temp.wav", chemin],
            check=True, capture_output=True,
        )
        return True
    except requests.exceptions.ConnectionError:
        return False  # serveur local non lancé : cas normal (Render, PC éteint...)
    except Exception as e:
        print(f"[voix clonée] {type(e).__name__}: {e}")
        return False


def generer_audio(texte, chemin="reponse_audio.mp3"):
    """Voix clonée en priorité, repli sur edge-tts. Retourne True si un audio est prêt."""
    if generer_audio_clone(texte, chemin):
        return True
    try:
        generer_audio_edge(texte, chemin)
        return True
    except Exception as e:
        print(f"[edge-tts] {type(e).__name__}: {e}")
        return False


# ----------------------------------------------------------------------
# Connexion
# ----------------------------------------------------------------------
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
        with st.form("connexion"):  # Entrée valide le formulaire
            components.html(globe_anime_html(160), height=180)
            st.markdown("<h2 style='text-align:center; margin-top:-10px;'>Christiane</h2>", unsafe_allow_html=True)
            mot_de_passe_attendu = os.getenv("INTERFACE_MOT_DE_PASSE")
            mot_de_passe_saisi = (
                st.text_input("Mot de passe", type="password") if mot_de_passe_attendu else ""
            )
            bouton_connexion = st.form_submit_button("Se connecter")

        if bouton_connexion:
            if not mot_de_passe_attendu or mot_de_passe_saisi == mot_de_passe_attendu:
                st.session_state.authentifie = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect")

# ----------------------------------------------------------------------
# Historique et skills
# ----------------------------------------------------------------------
FICHIER_CONVERSATIONS = "conversations.json"


def charger_conversations():
    try:
        with open(FICHIER_CONVERSATIONS, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    try:  # migration de l'ancien historique.json
        with open("historique.json", "r", encoding="utf-8") as f:
            anciens = json.load(f)
        if anciens:
            return [{"id": uuid4().hex, "titre": anciens[0]["question"][:40], "echanges": anciens}]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass
    return []


def sauvegarder_conversations():
    with open(FICHIER_CONVERSATIONS, "w", encoding="utf-8") as f:
        json.dump(st.session_state.conversations, f, ensure_ascii=False, indent=2)


def conversation_active():
    for conv in st.session_state.conversations:
        if conv["id"] == st.session_state.conv_id:
            return conv
    return None


def echanges_actifs():
    conv = conversation_active()
    return conv["echanges"] if conv else []

def historique_pour_agent(max_echanges=6, max_car=1500):
    """Derniers échanges de la conversation active, au format messages du modèle."""
    tours = []
    for e in echanges_actifs()[-max_echanges:]:
        if e.get("reponse"):
            tours.append({"role": "user", "content": e["question"]})
            tours.append({"role": "assistant", "content": e["reponse"][:max_car]})
    return tours
def nouvelle_conversation():
    st.session_state.conv_id = None


def ouvrir_conversation(conv_id):
    st.session_state.conv_id = conv_id


def supprimer_conversation(conv_id):
    st.session_state.conversations = [c for c in st.session_state.conversations if c["id"] != conv_id]
    if st.session_state.conv_id == conv_id:
        st.session_state.conv_id = None
    sauvegarder_conversations()


if "conversations" not in st.session_state:
    st.session_state.conversations = charger_conversations()
    st.session_state.conv_id = None


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
        "Voici les modes disponibles :\n" + "\n".join(descriptions) +
        f"\n\nDemande : {objectif_utilisateur}\n\n"
        "Réponds uniquement avec le nom du mode le plus pertinent, ou 'aucun'."
    )
    try:
        reponse = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt_detection}],
            max_tokens=20,
        )
        choix = reponse.choices[0].message.content.strip().lower()
        return choix if choix in skills_disponibles else ""
    except Exception:
        return ""


def traiter_question(question, mode_equipe, autoriser_actions_locales):
    """Retourne (texte de la réponse, audio_pret)."""
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
        resultat = lancer_agent(
            objectif_avec_skill,
            confirmer_action=lambda: autoriser_actions_locales,
            historique=historique_pour_agent(),
        )
        reponse_texte = resultat["reponse"]
        journal = resultat["journal"]
        skill_utilise = skill_choisi or "aucun"

        echange = {
        "question": question, "reponse": reponse_texte,
        "journal": journal, "skill": skill_utilise,
    }
    conv = conversation_active()
    if conv is None:
        conv = {"id": uuid4().hex, "titre": question[:40], "echanges": []}
        st.session_state.conversations.insert(0, conv)
        st.session_state.conv_id = conv["id"]
    conv["echanges"].append(echange)
    sauvegarder_conversations()
    audio_pret = generer_audio(nettoyer_texte_audio(reponse_texte))
    return reponse_texte, audio_pret


# ----------------------------------------------------------------------
# Barre latérale
# ----------------------------------------------------------------------
if "mode_vocal_precedent" not in st.session_state:
    st.session_state.mode_vocal_precedent = False

mode = "Normal"
autoriser_actions = False

with st.sidebar:
    logo_sidebar = (
        f"<img src='data:image/png;base64,{logo_b64}' width='28' style='vertical-align:middle;margin-right:8px;'>"
        if logo_b64 else "🌐"
    )
    st.markdown(f"<div class='sidebar-titre'>{logo_sidebar} Christiane</div>", unsafe_allow_html=True)

    st.button("➕ New Chat", use_container_width=True, on_click=nouvelle_conversation)
    st.markdown("<div class='sidebar-section'>Mode</div>", unsafe_allow_html=True)
    mode_vocal = st.toggle("🎙️ Mode vocal uniquement", key="mode_vocal")

    if not mode_vocal:
        st.markdown("<div class='sidebar-section'>Réglages</div>", unsafe_allow_html=True)
        mode = st.radio("Mode", ["Normal", MODE_EQUIPE], label_visibility="collapsed")
        autoriser_actions = st.checkbox("Autoriser les actions sensibles")
        fichier_uploade = st.file_uploader("Déposer un PDF", type="pdf")

        with st.expander("🤖 Délégations récentes"):
            try:
                with open("delegations.log", "r", encoding="utf-8") as f:
                    lignes = f.read().strip().split("\n")
                dernieres = "\n".join(lignes[-20:])
                st.text(dernieres if dernieres.strip() else "Aucune délégation pour l'instant.")
            except FileNotFoundError:
                st.text("Aucune délégation pour l'instant.")

        if fichier_uploade:
            nom_fichier = os.path.basename(fichier_uploade.name)
            with open(f"upload_{nom_fichier}", "wb") as f:
                f.write(fichier_uploade.getbuffer())
            st.success(f"{nom_fichier} prêt.")

        

vient_dactiver_vocal = mode_vocal and not st.session_state.mode_vocal_precedent
st.session_state.mode_vocal_precedent = mode_vocal
mode_equipe_actif = mode == MODE_EQUIPE

# ----------------------------------------------------------------------
# Page principale
# ----------------------------------------------------------------------
if mode_vocal:
    # ----- Mode vocal uniquement -----
    if vient_dactiver_vocal:
        salutation = "Bonjour" if 5 <= datetime.now().hour < 18 else "Bonsoir"
        if generer_audio(f"{salutation} Monsieur, que puis-je faire pour vous ?", chemin="salutation_audio.mp3"):
            st.audio("salutation_audio.mp3", autoplay=True)

    zone_globe = st.empty()
    with zone_globe.container():
        components.html(globe_anime_html(300, parlant=False), height=320)

    col_g, col_c, col_d = st.columns([1, 1, 1])
    with col_c:
        question_vocale_seule = micro_wispr("micro_vocal_seul", plein_largeur=True)

    if question_vocale_seule:
        with st.spinner("Christiane réfléchit..."):
            reponse, audio_pret = traiter_question(question_vocale_seule, mode_equipe_actif, autoriser_actions)
        with zone_globe.container():  # le globe pulse pendant qu'elle parle
            components.html(globe_anime_html(300, parlant=True), height=320)
        with st.container(border=True):
            st.caption(f"🎤 {question_vocale_seule}")
            st.markdown(reponse)
        if audio_pret:
            st.audio("reponse_audio.mp3", autoplay=True)

else:
    # ----- Mode normal -----
    logo_hero = (
        f"<img src='data:image/png;base64,{logo_b64}' width='70'>"
        if logo_b64 else "<span class='logo-globe'>🌐</span>"
    )

    badges = []
    for symbole, texte in AGENTS:
        if symbole == "grio":
            if logo_grio_b64:
                icone = f"<img src='data:image/png;base64,{logo_grio_b64}' width='24'>"
            else:
                icone = "<span class='lettre-agent'>Γρ</span>"
        else:
            icone = f"<span class='lettre-agent'>{symbole}</span>"
        badges.append(f"<div class='badge-agent'>{icone} {texte}</div>")

    st.markdown(
        "<div class='hero-accueil'>"
        f"{logo_hero}"
        "<div class='sous-titre'>Bon retour</div>"
        "<h1>Que puis-je faire pour vous aujourd'hui ?</h1>"
        f"{''.join(badges)}"
        "</div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        col_micro, col_texte, col_envoyer = st.columns([3, 5, 1] if (os.getenv("WISPR_API_KEY") or os.getenv("GROQ_API_KEY")) else [1, 6, 1])
        with col_micro:
            question_vocale = micro_wispr("micro_christiane")
        with col_texte:
            question_texte = st.text_input(
                "Que dois-je faire ?", label_visibility="collapsed",
                placeholder="Écrivez ou parlez à Christiane...",
            )
        with col_envoyer:
            bouton_envoyer = st.button("➤", use_container_width=True)

    col_logo, col_titre, col_date = st.columns([1, 4, 2])
    with col_logo:
        components.html(globe_anime_html(65), height=75)
    with col_titre:
        st.markdown(
            "<h1 style='color:#22D3EE; letter-spacing:2px; margin:8px 0 0 0;'>CHRISTIANE</h1>"
            "<p style='color:#7C8AA5; font-size:13px; margin:0;'>Assistante personnelle</p>",
            unsafe_allow_html=True,
        )
    with col_date:
        st.markdown(
            f"<div style='text-align:right; color:#7C8AA5; font-size:13px; margin-top:16px;'>{date_francaise()}</div>",
            unsafe_allow_html=True,
        )

    question = question_vocale or question_texte
    envoyer = bool(question_vocale) or bouton_envoyer  # une question dictée part directement

    suggestions = {
        "revision": ("📘", "Réviser un cours", "Prépare une fiche ou un QCM sur un sujet"),
        "redaction": ("✍️", "Rédiger un texte", "Aide à écrire ou structurer un document"),
        "organisation": ("🗂️", "M'organiser", "Planifier mes révisions ou mes tâches"),
    }
    for col, (cle, (icone, titre, desc)) in zip(st.columns(3), suggestions.items()):
        with col:
            st.markdown(
                f"<div class='carte-suggestion'><div class='titre'>{icone} {titre}</div>"
                f"<div class='desc'>{desc}</div></div>",
                unsafe_allow_html=True,
            )
            if st.button("Utiliser", key=f"suggestion_{cle}", use_container_width=True):
                question = titre
                envoyer = True

    if envoyer and question and question.strip():
        with st.spinner("Christiane réfléchit..."):
            _, audio_pret = traiter_question(question.strip(), mode_equipe_actif, autoriser_actions)
        if audio_pret:
            st.audio("reponse_audio.mp3", autoplay=True)

    # Conversation (les 8 derniers échanges, du plus ancien au plus récent)
    for echange in echanges_actifs():
        st.markdown(
            f"<div class='bulle-utilisateur'>{html.escape(echange['question'])}</div>",
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            st.markdown(echange["reponse"])
            # Liste des conversations (barre latérale) - à garder tout à la fin du fichier
if not mode_vocal:
    with st.sidebar:
        st.markdown("<div class='sidebar-section'>Conversations</div>", unsafe_allow_html=True)
        for conv in st.session_state.conversations:
            col_titre, col_suppr = st.columns([5, 1])
            with col_titre:
                st.button(
                    conv["titre"], key=f"conv_{conv['id']}", use_container_width=True,
                    type="primary" if conv["id"] == st.session_state.conv_id else "secondary",
                    on_click=ouvrir_conversation, args=(conv["id"],),
                )
            with col_suppr:
                st.button("🗑️", key=f"suppr_{conv['id']}",
                          on_click=supprimer_conversation, args=(conv["id"],))
                