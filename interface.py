import streamlit as st
import os
from main import lancer_agent

st.title("Christiane - Assistant IA")

if "historique" not in st.session_state:
    st.session_state.historique = []

skills_disponibles = []
if os.path.exists("skills"):
    skills_disponibles = [f.replace(".txt", "") for f in os.listdir("skills") if f.endswith(".txt")]

skill_choisi = st.selectbox("Mode (skill)", ["aucun"] + skills_disponibles)
autoriser_actions = st.checkbox("Autoriser les actions sensibles (écriture de fichiers, envoi d'emails)")

question = st.text_input("Que dois-je faire ?")

if st.button("Envoyer") and question:
    instructions_skill = ""
    if skill_choisi != "aucun":
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
        "journal": resultat["journal"]
    })

for echange in reversed(st.session_state.historique):
    st.write(f"**Toi :** {echange['question']}")
    st.write(f"**Christiane :** {echange['reponse']}")
    with st.expander("Voir le détail technique"):
        st.text(echange['journal'])
    st.divider()