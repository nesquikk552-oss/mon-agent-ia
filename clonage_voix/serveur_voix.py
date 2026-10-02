import io
import json
import threading
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio

DOSSIER = Path(__file__).resolve().parent
ECHANTILLON = DOSSIER / "voix_echantillon.wav"
LANGUE = "fr"
TEMPERATURE = 0.5
GRAINE = 42
LONGUEUR_MAX_TEXTE = 800  # garde-fou : XTTS est lent sur CPU
HOTE, PORT = "127.0.0.1", 5005


# torchaudio.load remplacé par soundfile (évite les problèmes de backend audio)
def charger_audio_simple(chemin, *args, **kwargs):
    donnees, frequence = sf.read(chemin, dtype="float32", always_2d=True)
    return torch.from_numpy(donnees.T), frequence


torchaudio.load = charger_audio_simple

from TTS.api import TTS  # noqa: E402  (doit venir après le remplacement de torchaudio.load)

if not ECHANTILLON.exists():
    raise SystemExit(f"Échantillon vocal introuvable : {ECHANTILLON}")

print("Chargement du modèle de voix, patiente...")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
modele = tts.synthesizer.tts_model
FREQUENCE = tts.synthesizer.output_sample_rate

# Calculé une seule fois : évite de ré-analyser l'échantillon à chaque requête
print("Analyse de l'échantillon vocal...")
with torch.inference_mode():
    latents_gpt, embedding_locuteur = modele.get_conditioning_latents(
        audio_path=[str(ECHANTILLON)]
    )
print("Modèle prêt.")

# Une seule synthèse à la fois : le modèle n'est pas prévu pour tourner en parallèle
verrou_synthese = threading.Lock()


def synthetiser(texte):
    with verrou_synthese, torch.inference_mode():
        torch.manual_seed(GRAINE)
        sortie = modele.inference(
            texte,
            LANGUE,
            latents_gpt,
            embedding_locuteur,
            temperature=TEMPERATURE,
            enable_text_splitting=True,  # découpe en phrases pour les textes longs
        )
    audio = np.asarray(sortie["wav"], dtype="float32")

    tampon = io.BytesIO()
    sf.write(tampon, audio, FREQUENCE, format="WAV")
    return tampon.getvalue()


class GestionnaireVoix(BaseHTTPRequestHandler):
    def _repondre(self, code, corps=b"", type_contenu="text/plain; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", type_contenu)
        self.send_header("Content-Length", str(len(corps)))
        self.end_headers()
        if corps:
            self.wfile.write(corps)

    def do_GET(self):
        if self.path == "/sante":
            self._repondre(200, b"ok")
        else:
            self._repondre(404)

    def do_POST(self):
        if self.path != "/parler":
            self._repondre(404)
            return
        try:
            taille = int(self.headers.get("Content-Length", 0))
            corps = json.loads(self.rfile.read(taille).decode("utf-8"))
            texte = str(corps.get("texte", "")).strip()
        except (ValueError, json.JSONDecodeError):
            self._repondre(400, "JSON invalide".encode("utf-8"))
            return

        if not texte:
            self._repondre(400, "Champ 'texte' vide".encode("utf-8"))
            return
        texte = texte[:LONGUEUR_MAX_TEXTE]

        try:
            contenu = synthetiser(texte)
        except Exception as e:
            traceback.print_exc()
            self._repondre(500, f"Erreur de synthèse : {e}".encode("utf-8"))
            return

        self._repondre(200, contenu, "audio/wav")

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    serveur = ThreadingHTTPServer((HOTE, PORT), GestionnaireVoix)
    print(f"Serveur de voix prêt sur http://{HOTE}:{PORT} (Ctrl+C pour arrêter)")
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur.")
        serveur.server_close()
