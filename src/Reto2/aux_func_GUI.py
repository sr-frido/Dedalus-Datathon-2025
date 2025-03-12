import os

def leer_lineas_no_vacias(ruta_fichero):
    """
    Lee un fichero de texto y devuelve una lista con las líneas no vacías.
    
    :param ruta_fichero: Ruta del archivo a leer.
    :return: Lista de líneas no vacías.
    """
    try:
        with open(ruta_fichero, "r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: El archivo '{ruta_fichero}' no se encontró.")
        return []
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return []


def listar_carpetas(ruta_directorio):
    """
    Retorna una lista con los nombres de todas las carpetas en un directorio.

    :param ruta_directorio: Ruta del directorio a examinar.
    :return: Lista con los nombres de las carpetas dentro del directorio.
    """
    try:
        return [nombre for nombre in os.listdir(ruta_directorio) 
                if os.path.isdir(os.path.join(ruta_directorio, nombre))]
    except FileNotFoundError:
        print(f"Error: El directorio '{ruta_directorio}' no existe.")
        return []
    except Exception as e:
        print(f"Error al leer el directorio: {e}")
        return []
