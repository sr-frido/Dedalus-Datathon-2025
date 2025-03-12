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

# Ejemplo de prueba con una consulta en lenguaje natural
consulta = "Pacientes con alergia a los frutos secos diagnosticados hace más de una semana"

# Cargar el archivo CSV en un DataFrame de pandas
ruta_base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Construir la ruta completa al archivo 'cohorte_alegias.csv'
csv_file = os.path.join(ruta_base, 'Datos sintéticos reto 2', 'cohorte_alegias.csv')

# Generar la consulta SQL a partir del LLM
sql_generado = convertir_a_sql(consulta, csv_file)

# Imprimir la consulta SQL generada por el LLM
print("Consulta SQL generada:\n")
print(sql_generado)
