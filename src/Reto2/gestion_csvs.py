import sqlite3
import pandas as pd
import os
from procesar_peticion import *
from prompt_enginering import *
import shutil

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

# Obtener los resultados de la consulta y convertirlos en un DataFrame
resultados = cursor.fetchall()
columnas = [desc[0] for desc in cursor.description]
df_resultado = pd.DataFrame(resultados, columns=columnas)

# Mostrar el DataFrame
print(df_resultado)

# Crear una carpeta temporal dentro del proyecto si no existe
temp_folder = os.path.join(os.path.dirname(__file__), "temp")
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

# Crear una ruta para el archivo CSV dentro de la carpeta temporal
temp_file_name = os.path.join(temp_folder, "resultado.csv")

# Guardar los resultados en el archivo temporal
df_resultado.to_csv(temp_file_name, index=False)
print(f'\nArchivo CSV generado temporalmente en: {temp_file_name}')

# Analizar el prompt y la consulta generada
resumen = analizar_prompt(prompt, consulta)
print(f'\n\n Resumen de la salida del prompt:\n\n{resumen}')

# Cerrar la conexión
conn.close()

# Eliminar la carpeta temporal y su contenido al finalizar el programa
if os.path.exists(temp_folder):
    shutil.rmtree(temp_folder)
    print(f'\nLa carpeta temporal {temp_folder} y su contenido han sido eliminados.')
