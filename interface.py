import streamlit as st
import os
from main import lancer_agent, client

st.title("Christiane - Assistant IA")

if "historique" not in st.session_state:
    st.session_state.historique = []

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

autoriser_actions = st.checkbox("Autoriser les actions sensibles (écriture de fichiers, envoi d'emails)")
question = st.text_input("Que dois-je faire ?")

if st.button("Envoyer") and question:
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

for echange in reversed(st.session_state.historique):
    st.write(f"**Toi :** {echange['question']}")
    st.write(f"**Christiane** *(mode: {echange['skill']})* : {echange['reponse']}")
    with st.expander("Voir le détail technique"):
        st.text(echange['journal'])
    st.divider()