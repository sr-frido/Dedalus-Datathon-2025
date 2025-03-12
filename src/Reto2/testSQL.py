import sqlite3
import pandas as pd
import os
from LLM import convertir_a_sql

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

prompt = "Quiero ver todos los pacientes alergicos al polen diagnosticados hace mas de un año"

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


consulta = "Pacientes con alergia a los frutos secos diagnosticados hace más de una semana"
#hola = convertir_a_sql(consulta,csv_file)
#print(f'El reultado es: \n{hola}')

# Cerrar la conexión
conn.close()
