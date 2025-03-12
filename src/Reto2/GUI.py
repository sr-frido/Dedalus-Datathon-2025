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
root.geometry("800x600")

# Crear estructura de la interfaz
frame_izquierda = tk.Frame(root, width=200, height=600)
frame_izquierda.pack(side=tk.LEFT, fill=tk.Y)

frame_superior_derecha = tk.Frame(root, width=400, height=300)
frame_superior_derecha.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

frame_inferior_derecha = tk.Frame(root, width=400, height=300)
frame_inferior_derecha.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

frame_inferior_izquierda = tk.Frame(root, width=200, height=300)
frame_inferior_izquierda.pack(side=tk.BOTTOM, fill=tk.Y)

# Lista de templates
listbox_templates = Listbox(frame_izquierda, height=20)
listbox_templates.pack(fill=tk.BOTH, expand=True)

# Botón para cargar datos
tk.Button(frame_izquierda, text="Cargar Datos CSV", command=cargar_datos).pack(pady=10)

# Botón para analizar datos
tk.Button(frame_izquierda, text="Analizar Datos", command=analizar_datos).pack(pady=10)

# Cuadros de entrada y salida
input_text = scrolledtext.ScrolledText(frame_superior_derecha, width=60, height=5)
input_text.pack(pady=10, fill=tk.BOTH, expand=True)

output_text = scrolledtext.ScrolledText(frame_superior_derecha, width=60, height=10, state=tk.DISABLED)
output_text.pack(pady=10, fill=tk.BOTH, expand=True)

# Lista de cohortes previos
listbox_cohortes = Listbox(frame_inferior_izquierda, height=10)
listbox_cohortes.pack(fill=tk.BOTH, expand=True)

# Espacio para gráficos
canvas_graficos = tk.Canvas(frame_inferior_derecha, bg="white")
canvas_graficos.pack(fill=tk.BOTH, expand=True)

root.mainloop()