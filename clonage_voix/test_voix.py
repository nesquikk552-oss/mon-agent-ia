import torch
import torchaudio
import soundfile as sf

def charger_audio_simple(chemin, *args, **kwargs):
    donnees, frequence = sf.read(chemin, dtype="float32", always_2d=True)
    return torch.from_numpy(donnees.T), frequence

torchaudio.load = charger_audio_simple

from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")

tts.tts_to_file(
    text="Bonjour Monsieur, je suis Christiane, votre assistante personnelle.",
    speaker_wav="voix_echantillon.wav",
    language="fr",
    file_path="test_resultat.wav"
)

print("Terminé ! Fichier généré : test_resultat.wav")