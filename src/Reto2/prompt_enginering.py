import os
import openai
from dotenv import load_dotenv
from procesar_peticion import *

# Cargar las variables de entorno
load_dotenv()

# Configurar cliente OpenAI con LiteLLM como proxy
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://litellm.dccp.pbu.dedalus.com"
)

temp_folder = os.path.join(os.path.dirname(__file__), "temp")
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

temp_file = os.path.join(temp_folder, "resultado.txt")
temp_csv = os.path.join(temp_folder, "resultado.csv")

def preprocesar_prompt(prompt):

    prompt += "\n\nSentencia sql ya existente: "

    if os.path.exists(temp_file):
        with open(temp_file, "r") as archivo:
            sentencia_sql = archivo.read()
            prompt += "\n" + sentencia_sql

    context="Eres un asistente experto en análisis de datos médicos y bases de datos. " \
            "Tu tarea es reformular consultas informales o ambiguas de los usuarios en instrucciones claras y bien estructuradas. " \
            "La finalidad es que otro LLM entienda mejor esas instrucciones para que las pueda traducir a sentencias para SQLite3. " \
            "No escribas nada más ni des explicaciones, solo devuelve esa sentencia reformulada. " \
            "Si la consulta no esta relacionada con peticiones a una base de datos de salud entonces vas a escribir la palabra Error. " \
            "Tienes que interpretar también si se desea añadir o excluir sobre la sentencia sql que ya hay generada y que te mostraran, si esque la hay."

    # Realizar la solicitud al modelo
    response = client.chat.completions.create(
        model="bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0",  # Cambia al modelo permitido
        messages=[{"role": "system", "content": context},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()