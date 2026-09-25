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
logo_grio_b64 = charger_logo_base64("grio_logo.png")
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
.badge-alpha {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #131A2A;
    border: 1px solid #22D3EE44;
    border-radius: 20px;
    padding: 6px 14px;
    margin-top: 12px;
    font-size: 13px;
    color: #9AA6BC;
}
.badge-alpha .lettre-alpha {
    font-size: 18px;
    font-weight: 700;
    color: #22D3EE;
    text-shadow: 0 0 10px #22D3EE, 0 0 20px #22D3EE88
    .badge-beta {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #131A2A;
    border: 1px solid #22D3EE44;
    border-radius: 20px;
    padding: 6px 14px;
    margin-top: 8px;
    font-size: 13px;
    color: #9AA6BC;
}
.badge-beta .lettre-beta {
    font-size: 18px;
    font-weight: 700;
    color: #22D3EE;
    text-shadow: 0 0 10px #22D3EE, 0 0 20px #22D3EE88;
}
.badge-grio {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #131A2A;
    border: 1px solid #22D3EE44;
    border-radius: 20px;
    padding: 6px 14px;
    margin-top: 8px;
    font-size: 13px;
    color: #9AA6BC;
}
.badge-grio img {
    height: 20px;
    width: auto;
}
.badge-delta {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #131A2A;
    border: 1px solid #22D3EE44;
    border-radius: 20px;
    padding: 6px 14px;
    margin-top: 8px;
    font-size: 13px;
    color: #9AA6BC;
}
.badge-delta .lettre-delta {
    font-size: 18px;
    font-weight: 700;
    color: #22D3EE;
    text-shadow: 0 0 10px #22D3EE, 0 0 20px #22D3EE88;
}
.badge-gamma {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #131A2A;
    border: 1px solid #22D3EE44;
    border-radius: 20px;
    padding: 6px 14px;
    margin-top: 8px;
    font-size: 13px;
    color: #9AA6BC;
}
.badge-gamma .lettre-gamma {
    font-size: 18px;
    font-weight: 700;
    color: #22D3EE;
    text-shadow: 0 0 10px #22D3EE, 0 0 20px #22D3EE88;
}
.badge-lambda {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #131A2A;
    border: 1px solid #22D3EE44;
    border-radius: 20px;
    padding: 6px 14px;
    margin-top: 8px;
    font-size: 13px;
    color: #9AA6BC;
}
.badge-lambda .lettre-lambda {
    font-size: 18px;
    font-weight: 700;
    color: #22D3EE;
    text-shadow: 0 0 10px #22D3EE, 0 0 20px #22D3EE88;
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
    if "mode_vocal_precedent" not in st.session_state:
        st.session_state.mode_vocal_precedent = False
vient_dactiver_vocal = mode_vocal and not st.session_state.mode_vocal_precedent
st.session_state.mode_vocal_precedent = mode_vocal
if not mode_vocal:
        st.markdown("<div class='sidebar-section'>Réglages</div>", unsafe_allow_html=True)
        mode = st.radio("Mode", ["Normal", "Équipe (recherche + rédaction + flashcards)"], label_visibility="collapsed")
        autoriser_actions = st.checkbox("Autoriser les actions sensibles")
        fichier_uploade = st.file_uploader("Déposer un PDF", type="pdf")
        with st.sidebar.expander("🤖 Délégations récentes"):
                try:
                    with open("delegations.log", "r", encoding="utf-8") as f:
                        lignes = f.read().strip().split("\n")
                    dernieres = "\n".join(lignes[-20:])
                    st.text(dernieres if dernieres else "Aucune délégation pour l'instant.")
                except FileNotFoundError:
                    st.text("Aucune délégation pour l'instant.")
        if fichier_uploade:
            with open(f"upload_{fichier_uploade.name}", "wb") as f:
                f.write(fichier_uploade.getbuffer())
            st.success(f"{fichier_uploade.name} prêt.")
else:
        mode = "Normal"
        autoriser_actions = False
if not mode_vocal:
        st.markdown("<div class='sidebar-section'>Historique récent</div>", unsafe_allow_html=True)
        for echange in list(reversed(st.session_state.historique))[:6]:
            st.markdown(f"<div class='historique-item'>{echange['question']}</div>", unsafe_allow_html=True)
mode_equipe_actif = mode == "Équipe (recherche + rédaction + flashcards)"
if "parlant_vocal" not in st.session_state:
    st.session_state.parlant_vocal = False
if mode_vocal:
    if vient_dactiver_vocal:
        heure_actuelle = dt.datetime.now().hour
        salutation = "Bonjour" if 5 <= heure_actuelle < 18 else "Bonsoir"
        generer_audio(f"{salutation} Monsieur, que puis-je faire pour vous ?", chemin="salutation_audio.mp3")
        st.audio("salutation_audio.mp3", autoplay=True)
    st.markdown("<div class='zone-vocale'>", unsafe_allow_html=True)

st.markdown("<div class='zone-vocale'>", unsafe_allow_html=True)
components.html(globe_anime_html(300, parlant=st.session_state.parlant_vocal), height=320)
st.markdown("</div>", unsafe_allow_html=True)
col_g, col_c, col_d = st.columns([1, 1, 1])
with col_c:
        question_vocale_seule = speech_to_text(
            language="fr", start_prompt="🎤 Appuyez pour parler",
            stop_prompt="⏹️ Arrêter", just_once=True, use_container_width=True,
            key="micro_vocal_seul"
        )

if question_vocale_seule:
        st.session_state.parlant_vocal = False
        with st.spinner("Christiane réfléchit..."):
            reponse = traiter_question(question_vocale_seule, mode_equipe_actif, autoriser_actions)
        st.session_state.parlant_vocal = True
        st.markdown(f"""
        <div class='reponse-vocale'>
            <div class='question-vocale-affichee'>🎤 {question_vocale_seule}</div>
            {reponse}
        </div>
        """, unsafe_allow_html=True)
        st.audio("reponse_audio.mp3", autoplay=True)
        st.rerun()

else:
    logo_hero = f"<img src='data:image/png;base64,{logo_b64}' width='70'>" if logo_b64 else "<span class='logo-globe'>🌐</span>"
    st.markdown(f"""
<div class='hero-accueil'>
    {logo_hero}
    <div class='sous-titre'>Bon retour</div>
    <h1>Que puis-je faire pour vous aujourd'hui ?</h1>
    <div class='badge-alpha'><span class='lettre-alpha'>Αα</span> Alpha, assistant de recherche, actif</div>
    <div class='badge-beta'><span class='lettre-beta'>Ββ</span> Beta, assistant fichiers, actif</div>
    <div class='badge-grio'><img src='data:image/png;base64,{logo_grio_b64}'> Grio, assistant mathématiques, actif</div>
    <div class='badge-delta'><span class='lettre-delta'>Δδ</span> Delta, assistant révisions, actif</div>
    <div class='badge-gamma'><span class='lettre-gamma'>Γγ</span> Gamma, assistant agenda et météo, actif</div>
    <div class='badge-lambda'><span class='lettre-lambda'>Λλ</span> Lambda, assistant documents, actif</div>
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

    