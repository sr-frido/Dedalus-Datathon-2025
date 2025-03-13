import os
import openai
import pandas as pd
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Configurar cliente OpenAI con LiteLLM como proxy
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://litellm.dccp.pbu.dedalus.com"
)

# Código para la conversión a sql hecha por el LLM de openai
def convertir_a_sql(consulta_natural, archivo_csv):
    """
    Usa el LLM para convertir una consulta en lenguaje natural a SQL,
    adaptado a las columnas de un archivo CSV.
    """
    # Cargar el archivo CSV para obtener las columnas dinámicamente
    df = pd.read_csv(archivo_csv)
    columnas = df.columns.tolist()

    # Tomar las primeras 5 filas para mostrarle un ejemplo al modelo
    ejemplo_filas = df.head().to_string(index=False)

    # Crear una cadena con las columnas del archivo CSV
    columnas_sql = "\n".join([f"- {col} (TEXT)" for col in columnas])

    # Definir el prompt con las columnas dinámicas y un ejemplo de las filas
    prompt = f"""
    Convierte la siguiente solicitud en una consulta SQL válida para una base de datos de pacientes:

    Solicitud: "{consulta_natural}"

    La base de datos tiene la tabla 'pacientes' con las siguientes columnas:
    {columnas_sql}

    Aquí hay un ejemplo de las primeras filas de datos:
    {ejemplo_filas}

    Devuelve SOLO la consulta SQL sin explicaciones.
    """

    # Realizar la solicitud al modelo
    response = client.chat.completions.create(
        model="bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0",  # Cambia al modelo permitido
        messages=[{"role": "system", "content": "Eres un asistente experto en SQL."},
                  {"role": "user", "content": prompt}]
    )

    # Devolver la consulta SQL generada
    return response.choices[0].message.content.strip()

def analizar_prompt(input, peticion):
    prompt = f"""
    El siguiente prompt ha generado una sentencia sql:

    Prompt: "{input}"

    Sentencia sql: "{peticion}"

    Aquí hay un ejemplo de las columnas de los datos

    Devuelve una respueste breve sobre el prompt, un párrafo no muy largo
    """

     # Realizar la solicitud al modelo
    response = client.chat.completions.create(
        model="bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0",  # Cambia al modelo permitido
        messages=[{"role": "system", "content": "Eres un asistente que responde en una o dos lines a un usuario sobre una petición que ha realizado y una sentencia sql que ha generado otro LLM, el usuario no tiene ni idea de sql ni de bases de datos así que no des explicaciones sobre eso ."},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
