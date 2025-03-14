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

# Path de la base de datos de los pacientes.
path_to_database = os.path.join(os.path.dirname(__file__), "DataBase")

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


# Información base sobre cada csv de nuestro database
def obtener_info_csvs(directorio):
    datos = {}  # Diccionario para almacenar la info de cada archivo

    # Obtener todos los archivos CSV en el directorio
    archivos_csv = [archivo for archivo in os.listdir(directorio) if archivo.endswith(".csv")]

    for archivo in archivos_csv:
        ruta_completa = os.path.join(directorio, archivo)

        try:
            df = pd.read_csv(ruta_completa)  # Leer el CSV

            # Guardar en el diccionario
            datos[archivo] = {
                "columnas": df.columns.tolist(),
                "muestra": df.sample(min(5, len(df))).to_dict(orient="records")  # Muestra aleatoria
            }
        except Exception as e:
            print(f"⚠️ Error al leer {archivo}: {e}")

    return datos

# Código para la conversión a sql hecha por el LLM de openai
def convertir_a_sql(consulta_natural):
    info_csv = obtener_info_csvs(path_to_database)

    prompt = f"""
    Convierte la siguiente solicitud en una consulta sqlite3 válida para una base de datos de pacientes:

    Solicitud: "{consulta_natural}"

    La base de datos contiene las siguientes tablas y sus respectivas columnas:
    """

    # Se añade la información de cada tabla con un formato más organizado
    for archivo, info in info_csv.items():
        prompt += f"\n- **Tabla**: {archivo}\n"
        prompt += f"  - **Columnas**: {', '.join(info['columnas'])}\n"
        prompt += f"  - **Muestra de filas aleatorias**:\n"
        
        # Añadir las filas aleatorias de forma legible
        for i, fila in enumerate(info['muestra'], 1):
            prompt += f"    {i}. {fila}\n"
    
    prompt += "\n\n    Devuelve SOLO la consulta SQL sin explicaciones."

     # Realizar la solicitud al modelo
    response = client.chat.completions.create(
        model="bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0",  # Cambia al modelo permitido
        messages=[{"role": "system", "content": "Eres un asistente experto en sqlite3. Por defecto las sentencias mostraran todos losd atos sobre los pacientes a no ser que se especifique lo contrario. Si la consulta que te llega es la palabra Error entonces vas a devulver un codigo sql que no haga completamente nada"},
                  {"role": "user", "content": prompt}]
    )

    return(response.choices[0].message.content.strip())
