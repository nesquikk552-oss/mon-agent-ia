"""Teste la clé Wispr Flow sans lancer Streamlit.

Usage : python test_wispr.py mon_audio.wav
(n'importe quel WAV convient, par exemple votre échantillon de clonage vocal)
"""
import sys

from wispr import transcrire_wispr

if len(sys.argv) < 2:
    sys.exit("Usage : python test_wispr.py fichier.wav")

with open(sys.argv[1], "rb") as f:
    print("Transcription :", transcrire_wispr(f.read()))
