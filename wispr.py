"""Micro de Christiane : Wispr Flow > Groq Whisper > micro d'origine.

Ordre de priorité, automatique selon les clés présentes dans le .env :
  1. WISPR_API_KEY  -> Wispr Flow (repli sur Groq Whisper en cas d'erreur)
  2. GROQ_API_KEY   -> Groq Whisper (whisper-large-v3-turbo)
  3. aucune clé     -> speech_to_text d'origine
"""
import base64
import hashlib
import os
import subprocess
import tempfile

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

URL_WISPR = "https://platform-api.wisprflow.ai/api/v1/dash/api"
MODELES_WHISPER = ("whisper-large-v3-turbo", "whisper-large-v3")


def transcrire_wispr(octets_wav: bytes, langue: str = "fr") -> str:
    """Transcription via l'API Wispr Flow."""
    cle = os.getenv("WISPR_API_KEY")
    if not cle:
        raise RuntimeError("WISPR_API_KEY est absente du fichier .env")

    # Wispr exige du WAV 16 kHz mono (ffmpeg est déjà utilisé dans le projet)
    with tempfile.TemporaryDirectory() as dossier:
        entree = os.path.join(dossier, "entree.wav")
        sortie = os.path.join(dossier, "sortie_16k.wav")
        with open(entree, "wb") as f:
            f.write(octets_wav)
        subprocess.run(
            ["ffmpeg", "-y", "-i", entree, "-ar", "16000", "-ac", "1", sortie],
            check=True, capture_output=True,
        )
        with open(sortie, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()

    reponse = requests.post(
        URL_WISPR,
        headers={"Authorization": f"Bearer {cle}"},
        json={
            "audio": audio_b64,
            "language": [langue],
            "context": {"app": {"type": "ai"}},
            # ancien format, ignoré par Wispr si "context" est présent
            "properties": {"language": langue, "app_type": "ai"},
        },
        timeout=60,
    )
    if reponse.status_code != 200:
        raise RuntimeError(f"HTTP {reponse.status_code} : {reponse.text[:200]}")
    return reponse.json().get("text", "").strip()


def transcrire_groq(octets_wav: bytes, langue: str = "fr") -> str:
    """Transcription via Whisper hébergé par Groq (utilise GROQ_API_KEY)."""
    from groq import Groq

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    derniere_erreur = None
    for modele in MODELES_WHISPER:
        try:
            reponse = client.audio.transcriptions.create(
                file=("audio.wav", octets_wav),
                model=modele,
                language=langue,
                response_format="json",
            )
            return (reponse.text or "").strip()
        except Exception as e:
            derniere_erreur = e
    raise RuntimeError(f"Groq Whisper indisponible : {derniere_erreur}")


def _transcrire(octets: bytes):
    """Retourne (texte, nom du service utilisé)."""
    if os.getenv("WISPR_API_KEY"):
        try:
            return transcrire_wispr(octets), "Wispr Flow"
        except Exception as e:
            if not os.getenv("GROQ_API_KEY"):
                raise
            print(f"[wispr] échec, repli sur Groq Whisper : {e}")
    return transcrire_groq(octets), "Groq Whisper"


def micro_wispr(key: str, plein_largeur: bool = False):
    """Affiche le micro et retourne le texte dicté (une fois par enregistrement)."""
    if not os.getenv("WISPR_API_KEY") and not os.getenv("GROQ_API_KEY"):
        from streamlit_mic_recorder import speech_to_text
        return speech_to_text(
            language="fr", start_prompt="🎤 Appuyez pour parler" if plein_largeur else "🎤",
            stop_prompt="⏹️ Arrêter" if plein_largeur else "⏹️",
            just_once=True, use_container_width=plein_largeur, key=key,
        )

    audio = st.audio_input("Parler à Christiane", key=key, label_visibility="collapsed")
    if audio is None:
        return None

    octets = audio.getvalue()
    empreinte = hashlib.md5(octets).hexdigest()
    cle_etat = f"{key}_dernier"
    if st.session_state.get(cle_etat) == empreinte:
        return None  # enregistrement déjà traité
    st.session_state[cle_etat] = empreinte

    try:
        with st.spinner("Transcription en cours..."):
            texte, _ = _transcrire(octets)
    except Exception as e:
        st.error(f"Transcription impossible : {e}")
        return None
    return texte or None
