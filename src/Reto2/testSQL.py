import sqlite3
import pandas as pd
import os

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

# Ejecutar una consulta SQL en la tabla
consulta = "SELECT * FROM pacientes WHERE PacienteId = 22"
cursor.execute(consulta)

# Mostrar los resultados
resultados = cursor.fetchall()
for fila in resultados:
    print(fila)

# Cerrar la conexión
conn.close()
