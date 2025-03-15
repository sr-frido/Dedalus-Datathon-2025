import os
import openai
from dotenv import load_dotenv
from LLM import *

# Cargar las variables de entorno
load_dotenv()

# Configurar cliente OpenAI con LiteLLM como proxy
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://litellm.dccp.pbu.dedalus.com"
)

def preprocesar_prompt(prompt):

    context="Eres un asistente experto en análisis de datos médicos. Tu tarea es reformular consultas informales o ambiguas de los usuarios en instrucciones claras y bien estructuradas para un sistema de generación de SQL. Solo escribe la sentencia procesada, nada más. Si la consulta no esta relacionada con peticiones a una base de datos de salud entonces vas a escribir la palabra Error"
    # Realizar la solicitud al modelo
    response = client.chat.completions.create(
        model="bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0",  # Cambia al modelo permitido
        messages=[{"role": "system", "content": context},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()