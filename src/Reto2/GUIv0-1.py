import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, Listbox
import pandas as pd
import matplotlib.pyplot as plt

# Inicializar df
df = None

def cargar_datos():
    global df
    filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if filepath:
        df = pd.read_csv(filepath)
        messagebox.showinfo("Carga exitosa", "Datos cargados correctamente")

def analizar_datos():
    global df
    if df is not None:
        plt.figure(figsize=(6, 4))
        df["edad"].hist(bins=20, color='skyblue')
        plt.xlabel("Edad")
        plt.ylabel("Cantidad de Pacientes")
        plt.title("Distribución de Edades")
        plt.show()
    else:
        messagebox.showerror("Error", "Primero carga un archivo CSV")

# Crear ventana principal
root = tk.Tk()
root.title("Agente de Salud para Identificación de Cohortes")
root.geometry("900x600")

# Crear estructura de la interfaz con Frames
frame_superior = tk.Frame(root, height=50)
frame_superior.pack(fill=tk.X)

frame_izquierda = tk.Frame(root, width=200, height=550)
frame_izquierda.pack(side=tk.LEFT, fill=tk.Y)

frame_derecha = tk.Frame(root, width=700, height=550)
frame_derecha.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

frame_superior_derecha = tk.Frame(frame_derecha, height=200)
frame_superior_derecha.pack(fill=tk.X)

frame_medio_derecha = tk.Frame(frame_derecha, height=200)
frame_medio_derecha.pack(fill=tk.X)

frame_inferior_derecha = tk.Frame(frame_derecha, height=200)
frame_inferior_derecha.pack(fill=tk.BOTH, expand=True)

# Botón para cargar datos en la parte superior
tk.Button(frame_superior, text="Cargar Datos", command=cargar_datos).pack(pady=5, padx=10, side=tk.LEFT)

# Lista de templates en el panel izquierdo
listbox_templates = Listbox(frame_izquierda, height=15)
listbox_templates.pack(fill=tk.BOTH, expand=True, pady=5)

# Lista de cohortes guardados en el panel izquierdo
listbox_cohortes = Listbox(frame_izquierda, height=10)
listbox_cohortes.pack(fill=tk.BOTH, expand=True, pady=5)

# Cuadro de entrada de prompt para el modelo
input_text = scrolledtext.ScrolledText(frame_superior_derecha, width=80, height=5)
input_text.pack(pady=5, fill=tk.BOTH, expand=True)

# Botón para analizar datos en el centro
tk.Button(frame_medio_derecha, text="Analizar Cohorte", command=analizar_datos).pack(pady=5, fill=tk.X)

# Cuadro de feedback/salida del modelo
output_text = scrolledtext.ScrolledText(frame_medio_derecha, width=80, height=5, state=tk.DISABLED)
output_text.pack(pady=5, fill=tk.BOTH, expand=True)

# Área de gráficos
canvas_graficos = tk.Canvas(frame_inferior_derecha, bg="white")
canvas_graficos.pack(fill=tk.BOTH, expand=True)

root.mainloop()
