from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def executer_sous_agent(nom_agent: str, instructions_systeme: str, outils_disponibles: dict, schema: list, instruction: str, max_iterations: int = 5) -> str:
    messages = [
        {"role": "system", "content": instructions_systeme},
        {"role": "user", "content": instruction}
    ]

    for _ in range(max_iterations):
        reponse = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=schema,
            max_tokens=1024
        )
        message = reponse.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content or f"{nom_agent} n'a pas pu produire de réponse."

        for appel in message.tool_calls:
            nom = appel.function.name
            try:
                params = json.loads(appel.function.arguments)
            except json.JSONDecodeError:
                resultat = "Erreur : arguments non valides."
                messages.append({"role": "tool", "tool_call_id": appel.id, "content": resultat})
                continue

            fonction = outils_disponibles.get(nom)
            if not fonction:
                resultat = f"Outil inconnu : {nom}"
            else:
                try:
                    resultat = fonction(**params)
                except Exception as e:
                    resultat = f"Erreur : {e}"

            messages.append({"role": "tool", "tool_call_id": appel.id, "content": str(resultat)})

    return f"{nom_agent} a atteint la limite d'itérations sans conclure."