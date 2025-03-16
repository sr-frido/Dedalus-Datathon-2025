import sqlite3
import pandas as pd
import os
from procesar_peticion import *
from prompt_enginering import *

# Cargar todos los archivos CSV en un directorio y convertirlos a tablas en SQLite

# Directorio donde están los CSVs
path_to_database = os.path.join(os.path.dirname(__file__), "DataBase")

# Obtener todos los archivos CSV en el directorio
archivos_csv = [archivo for archivo in os.listdir(path_to_database) if archivo.endswith('.csv')]

# Crear una conexión SQLite en memoria
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Cargar y crear una tabla para cada archivo CSV
for archivo in archivos_csv:
    ruta_completa = os.path.join(path_to_database, archivo)
    df = pd.read_csv(ruta_completa)

    # Crear la tabla en SQLite con el nombre del archivo (sin la extensión)
    df.to_sql(archivo.split('.')[0], conn, index=False, if_exists='replace')

# Definir el prompt que queremos pasar al LLM
prompt = preprocesar_prompt("Dame los pacientes mayores de edad")

# Función para convertir el prompt en una consulta SQL
consulta = convertir_a_sql(prompt)

print(consulta)

# Ejecutar la consulta SQL en la base de datos
cursor.execute(consulta)

# Mostrar los resultados
print(f'\nPrompt de entrada al LLM:\n \n{prompt}')
print('\n-----------------------------------------------------\n')
print(f'Sentencia SQL generada por el LLM sobre los CSVs dados:\n\n{consulta}')
print('\n-----------------------------------------------------\n')
print(f'CSV resultante: \n\n')

# Obtener y mostrar los resultados
resultados = cursor.fetchall()
for fila in resultados:
    print(fila)

# Analizar el prompt y la consulta generada
resumen = analizar_prompt(prompt, consulta)
print(f'\n\n Resumen de la salida del prompt:\n\n{resumen}')

# Cerrar la conexión
conn.close()
