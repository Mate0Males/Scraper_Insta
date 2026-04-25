import json
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def cargar_datos(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def construir_prompt(data):
    user = data["user_info"]

    prompt = f"""
Eres un analista de comportamiento digital en redes sociales.

Analiza el siguiente perfil de Instagram:

USUARIO:
- Username: {user['username']}
- Nombre: {user['full_name']}
- Bio: {user['biography']}
- Seguidores: {user['follower_count']}
- Siguiendo: {user['following_count']}
- Posts totales: {user['post_count']}

PUBLICACIONES Y COMENTARIOS:

"""

    for i, post in enumerate(data["posts"], 1):
        prompt += f"\nPOST {i}:\n"
        prompt += f"URL: {post['url']}\n"

        prompt += "Comentarios:\n"
        if post["comments"]:
            for c in post["comments"]:
                prompt += f"- @{c['username']}: {c['text']}\n"
        else:
            prompt += "- Sin comentarios\n"

    prompt += """

---

Genera un análisis con este formato:

1. Tipo de personalidad digital (no clínica, solo comportamiento online)
2. Estilo de comunicación
3. Temas principales del contenido
4. Tipo de interacción con su audiencia
5. Nivel de engagement (alto, medio, bajo) con explicación
6. Conclusión general del perfil

Sé analítico, objetivo y basado SOLO en los datos.
No inventes información externa.
"""

    return prompt


def analizar_archivo(json_file):
    data = cargar_datos(json_file)
    prompt = construir_prompt(data)

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )

    return response.text


if __name__ == "__main__":
    archivo = input("Archivo JSON del scraper (ej: leomessi_data.json): ").strip()

    resultado = analizar_archivo(archivo)

    print("\n==================== ANÁLISIS IA ====================\n")
    print(resultado)