import os
import openai
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Configurar cliente OpenAI con LiteLLM como proxy
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://litellm.dccp.pbu.dedalus.com"
)

def convertir_a_sql(consulta_natural):
    """
    Usa el LLM para convertir una consulta en lenguaje natural a SQL.
    """
    prompt = f"""
    Convierte la siguiente solicitud en una consulta SQL válida para una base de datos de pacientes:
    
    Solicitud: "{consulta_natural}"
    
    La base de datos tiene la tabla 'pacientes' con las columnas:
    - id (INTEGER)
    - nombre (TEXT)
    - edad (INTEGER)
    - enfermedad (TEXT)
    - fecha_diagnostico (DATE)

    Devuelve SOLO la consulta SQL sin explicaciones.
    """

    response = client.chat.completions.create(
        model="bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0",  # Cambia al modelo permitido
        messages=[{"role": "system", "content": "Eres un asistente experto en SQL."},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


# Ejemplo de prueba con una consulta en lenguaje natural
consulta = "Pacientes con diabetes tipo 2 mayores de 50 años"
sql_generado = convertir_a_sql(consulta)

# Imprimir la consulta SQL generada por el LLM
print("Consulta SQL generada:\n")
print(sql_generado)
