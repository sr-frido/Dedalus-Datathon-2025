import sqlite3
import pandas as pd
import os
from procesar_peticion import *
from prompt_enginering import *

temp_folder = os.path.join(os.path.dirname(__file__), "temp")

# Directorio donde están los CSVs
path_to_database = os.path.join(os.path.dirname(__file__), "DataBase")

# Obtener todos los archivos CSV en el directorio
archivos_csv = [archivo for archivo in os.listdir(path_to_database) if archivo.endswith('.csv')]

def ejecutar_peticion(peticion):
    # Crear una conexión SQLite en memoria
    conn = sqlite3.connect(':memory:')

    cursor = conn.cursor()
    # Cargar y crear una tabla para cada archivo CSV
    for archivo in archivos_csv:
        ruta_completa = os.path.join(path_to_database, archivo)
        df = pd.read_csv(ruta_completa)

        # Crear la tabla en SQLite con el nombre del archivo (sin la extensión)
        df.to_sql(archivo.split('.')[0], conn, index=False, if_exists='replace')

    # Ejecutar la consulta SQL en la base de datos
    cursor.execute(peticion)

    # Obtener los resultados de la consulta y convertirlos en un DataFrame
    resultados = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]
    df_resultado = pd.DataFrame(resultados, columns=columnas)

    # Crear una ruta para el archivo CSV dentro de la carpeta temporal
    temp_file_name = os.path.join(temp_folder, "resultado.csv")

    # Guardar los resultados en el archivo temporal
    df_resultado.to_csv(temp_file_name, index=False)
    print(f'\nArchivo CSV generado temporalmente en: {temp_file_name}')

    # Cerrar la conexión
    conn.close()

    return df_resultado