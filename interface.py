import streamlit as st
from main import lancer_agent

st.title("Mon Agent IA")

if "historique" not in st.session_state:
    st.session_state.historique = []

autoriser_actions = st.checkbox("Autoriser les actions sensibles (écriture de fichiers, envoi d'emails)")

question = st.text_input("Que dois-je faire ?")

if st.button("Envoyer") and question:
    resultat = lancer_agent(question, confirmer_action=lambda: autoriser_actions)
    st.session_state.historique.append({
        "question": question,
        "reponse": resultat["reponse"],
        "journal": resultat["journal"]
    })

for echange in reversed(st.session_state.historique):
    st.write(f"**Toi :** {echange['question']}")
    st.write(f"**Agent :** {echange['reponse']}")
    with st.expander("Voir le détail technique"):
        st.text(echange['journal'])
    st.divider()