import pandas as pd
import random

def crear_nuevo_cohorte_pacientes():
    # Datos originales proporcionados
    original_data = [
        [1, "Masculino", 21, "Almería", 36.8416, -2.4637],
        [2, "Masculino", 84, "Huelva", 37.2614, -6.9447],
        [3, "Femenino", 59, "Córdoba", 37.8847, -4.7792],
        [4, "Femenino", 78, "Granada", 37.1773, -3.5986],
        [5, "Femenino", 31, "Málaga", 36.7194, -4.42],
        [6, "Femenino", 47, "Córdoba", 37.8847, -4.7792],
        [7, "Masculino", 35, "Almería", 36.8416, -2.4637],
        [8, "Masculino", 19, "Granada", 37.1773, -3.5986],
        [9, "Femenino", 30, "Huelva", 37.2614, -6.9447],
        [10, "Femenino", 29, "Huelva", 37.2614, -6.9447],
        [11, "Masculino", 40, "Málaga", 36.7194, -4.42],
        [12, "Femenino", 19, "Granada", 37.1773, -3.5986],
        [13, "Femenino", 56, "Almería", 36.8416, -2.4637],
        [14, "Femenino", 63, "Córdoba", 37.8847, -4.7792],
        [15, "Masculino", 29, "Málaga", 36.7194, -4.42],
        [16, "Masculino", 45, "Granada", 37.1773, -3.5986],
        [17, "Masculino", 43, "Sevilla", 37.3886, -5.9823],
        [18, "Masculino", 44, "Málaga", 36.7194, -4.42],
        [19, "Femenino", 73, "Córdoba", 37.8847, -4.7792],
        [20, "Masculino", 62, "Almería", 36.8416, -2.4637],
        [21, "Masculino", 36, "Córdoba", 37.8847, -4.7792],
        [22, "Femenino", 27, "Málaga", 36.7194, -4.42],
        [23, "Masculino", 41, "Granada", 37.1773, -3.5986],
        [24, "Masculino", 35, "Almería", 36.8416, -2.4637],
        [25, "Masculino", 63, "Córdoba", 37.8847, -4.7792],
        [26, "Masculino", 80, "Huelva", 37.2614, -6.9447],
        [27, "Masculino", 71, "Almería", 36.8416, -2.4637],
        [28, "Femenino", 38, "Málaga", 36.7194, -4.42],
        [29, "Femenino", 21, "Málaga", 36.7194, -4.42],
        [30, "Femenino", 41, "Málaga", 36.7194, -4.42],
        [31, "Masculino", 50, "Sevilla", 37.3886, -5.9823],
        [32, "Femenino", 67, "Huelva", 37.2614, -6.9447],
        [33, "Masculino", 28, "Córdoba", 37.8847, -4.7792]
    ]

    # Generar más provincias incluyendo las nuevas
    provincias = {
        "Jaén": (37.7799, -3.7794),
        "Cádiz": (36.5271, -6.2923),
        "Almería": (36.8416, -2.4637),
        "Huelva": (37.2614, -6.9447),
        "Córdoba": (37.8847, -4.7792),
        "Granada": (37.1773, -3.5986),
        "Málaga": (36.7194, -4.42),
        "Sevilla": (37.3886, -5.9823)
    }

    # Generar nuevos pacientes hasta completar N filas
    for i in range(len(original_data), 1000):
        paciente_id = i + 1
        genero = random.choice(["Masculino", "Femenino"])
        edad = random.randint(18, 90)
        provincia = random.choice(list(provincias.keys()))
        latitud, longitud = provincias[provincia]
        
        original_data.append([paciente_id, genero, edad, provincia, latitud, longitud])

    # Crear el dataframe final
    df_final = pd.DataFrame(original_data, columns=["PacienteID", "Genero", "Edad", "Provincia", "Latitud", "Longitud"])

    # Guardar el archivo CSV actualizado
    file_path_updated = "/home/juan/Repositories/Dedalus-Datathon-2025/src/Reto2/DataBase/cohorte_pacientes.csv"
    df_final.to_csv(file_path_updated, index=False)

    file_path_updated
