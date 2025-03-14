import sqlite3
import pandas as pd
import os
from LLM import *

# Cargar el archivo CSV en un DataFrame de pandas
ruta_base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Construir la ruta completa al archivo 'cohorte_alegias.csv'
csv_file = os.path.join(ruta_base, 'Datos sintéticos reto 2', 'cohorte_alegias.csv')

df = pd.read_csv(csv_file)

# Crear una conexión SQLite en memoria
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Crear una tabla en SQLite a partir de las columnas del CSV
df.to_sql('pacientes', conn, index=False, if_exists='replace')

prompt = "Quiero ver la cantidad de los pacientes con alergia al polen diagnosticados hace mas de un año y menos de 5 y ademas alergicos a los cacahuetes"

# Ejecutar una consulta SQL en la tabla
consulta = convertir_a_sql(prompt,csv_file)

cursor.execute(consulta)



# Mostrar los resultados
print(f'\nPrompt de entrada al LLM:\n \n{prompt}')
print('\n-----------------------------------------------------\n')
print(f'Sentencia sql generada por el LLM sobre el csv dado:\n\n {consulta}')
print('\n-----------------------------------------------------\n')
print(f'CSV resultante: \n\n')

resultados = cursor.fetchall()
for fila in resultados:
    print(fila)

resumen = analizar_prompt(prompt,consulta)
print(f'\n\n Resumen de la salida del prompt:\n\n{resumen}')

# Cerrar la conexión
conn.close()
