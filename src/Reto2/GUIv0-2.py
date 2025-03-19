# ---------------------------
# Imports
# ---------------------------
import os
import re
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, Listbox
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

from aux_func_GUI import leer_lineas_no_vacias, listar_carpetas

import shutil

# ---------------------------
# Crear una carpeta temporal dentro del proyecto si no existe
# ---------------------------
#Se debe crear antes para evitar problemas
temp_folder = os.path.join(os.path.dirname(__file__), "temp")
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

temp_file = os.path.join(temp_folder, "resultado.txt")
temp_csv = os.path.join(temp_folder, "resultado.csv")

#CAMBIAR NOMBRES EN EL FUTURO
from procesar_peticion import *
from prompt_enginering import *
from gestion_csvs import *



# ---------------------------
# Configuración global y datos
# ---------------------------
template_file       = "./src/Reto2/user-templates.txt"
saved_cohorts_dir   = "./src/Reto2/saved-cohorts"
templates           = leer_lineas_no_vacias(template_file)
cohortes            = listar_carpetas(saved_cohorts_dir)
cohortes_guardados  = {}

current_cohort = None
cohort_ids = []

# Variables globales para info-output
input = "Aún no hay información"
sentencia = "Aún no hay información"
dataSet = "Aún no hay información"


# ---------------------------
# Funciones de manejo de datos y LLM
# ---------------------------
def cargar_datos():
    directory = filedialog.askdirectory()
    if directory:
        archivos_csv = [f for f in os.listdir(directory) if f.endswith(".csv")]
        if not archivos_csv:
            messagebox.showwarning("Advertencia", "No se encontraron archivos CSV en la carpeta seleccionada.")
            return

        cohortes.clear()
        for filename in archivos_csv:
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath)
            nombre_cohorte = os.path.splitext(filename)[0]
            cohortes[nombre_cohorte] = df

        messagebox.showinfo("Carga exitosa", f"Se cargaron {len(cohortes)} CSVs en total.")


def analizar_datos():
    """Muestra un histograma de la columna 'edad' si está disponible."""
    if "cohorte_pacientes" in cohortes:
        df_pacientes = cohortes["cohorte_pacientes"]
        if "edad" in df_pacientes.columns:
            plt.figure(figsize=(6, 4))
            df_pacientes["edad"].hist(bins=20, color='skyblue')
            plt.xlabel("Edad")
            plt.ylabel("Cantidad de Pacientes")
            plt.title("Distribución de Edades (cohorte_pacientes)")
            plt.show()
        else:
            messagebox.showwarning("Columna no encontrada", "El DataFrame 'cohorte_pacientes' no contiene la columna 'edad'.")
    else:
        messagebox.showerror("Error", "No existe 'cohorte_pacientes' en los datos cargados.")
def reset():
    """
    Resetea el cohorte y los prompts
    """
    with open(temp_file, "w") as archivo:
        archivo.write("")

    if os.path.exists(temp_csv):  # Verifica si el archivo existe
        os.remove(temp_csv)  # Borra el archivo
    print("Archivo eliminado.")

    if os.path.exists(temp_file):  # Verifica si el archivo existe
        os.remove(temp_file)  # Borra el archivo
    print("Archivo eliminado.")

    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, "")
    output_text.config(state=tk.DISABLED)

    input_text.delete("1.0", tk.END)
    


def guardar_cohorte():
    # Archivo de origen fijo
    origen = temp_csv  # Reemplaza con la ruta real
    
    # Verificar si el archivo de origen existe
    if not os.path.exists(origen):
        messagebox.showwarning("Aviso", "Aún no has creado ningún cohorte.")
        return
    
    # Seleccionar la ubicación y nombre de destino (solo archivos CSV)
    destino = filedialog.asksaveasfilename(title="Guardar archivo como", defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not destino:
        return  # Si no se elige destino, salir de la función
    
    try:
        # Copiar el archivo
        shutil.copy(origen, destino)
        messagebox.showinfo("Éxito", "Archivo guardado correctamente")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo copiar el archivo: {e}")


def llamar_a_llm_bedrock(prompt):
    """Placeholder para conexión real a AWS Bedrock o LiteLLM."""
    respuesta_simulada = (
        "Respuesta simulada del LLM.\n\n"
        f"Prompt recibido:\n{prompt}"
    )
    # return respuesta_simulada
    """
    Placeholder para conexión real a AWS Bedrock o LiteLLM.
    """
    consulta = preprocesar_prompt(prompt)
    respuesta_LLM = analizar_prompt(prompt, consulta)

    global input 
    global sentencia
    global dataSet

    input = consulta
    sentencia = convertir_a_sql(prompt)
    dataSet = ejecutar_peticion(sentencia)

    with open(temp_file, "w") as archivo:
        archivo.write(sentencia)

    return respuesta_LLM


def enviar_a_llm():
    prompt = input_text.get("1.0", tk.END).strip()
    if not prompt:
        messagebox.showwarning("Advertencia", "El prompt está vacío.")
        return

    
    
    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, "Procesando...")
    output_text.config(state=tk.DISABLED)
    output_text.update_idletasks()

    respuesta = llamar_a_llm_bedrock(prompt)
    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, respuesta)
    output_text.config(state=tk.DISABLED)


    input_text.delete("1.0", tk.END)

def on_template_select(event):
    seleccion = listbox_templates.curselection()
    if seleccion:
        template = listbox_templates.get(seleccion)
        input_text.delete("1.0", tk.END)
        input_text.insert(tk.END, template)


def on_cohort_select(event):
    global current_cohort, cohort_ids

    widget = event.widget
    index  = widget.nearest(event.y)
    if index not in widget.curselection():
        return

    current_cohort = widget.get(index)
    cohorte_path = os.path.join(saved_cohorts_dir, current_cohort)

    # Plantillas específicas del cohorte
    plantillas_file = os.path.join(cohorte_path, "cohort_templates.txt")
    cohort_templates = leer_lineas_no_vacias(plantillas_file)
    for plantilla in cohort_templates:
        listbox_templates.insert(tk.END, plantilla)

    # Extraer IDs desde log del cohorte
    log_file = os.path.join(cohorte_path, "cohort_log.txt")
    lineas   = leer_lineas_no_vacias(log_file)
    contenido = " ".join(lineas)

    match = re.search(r"\{([^}]+)\}", contenido)
    if match:
        ids_str        = match.group(1)
        ids_lista      = [valor.strip() for valor in ids_str.split(",") if valor.strip()]
        ids_convertidos = []
        for valor in ids_lista:
            try:
                ids_convertidos.append(int(valor))
            except ValueError:
                ids_convertidos.append(valor)
        cohort_ids = ids_convertidos
    else:
        cohort_ids = []

    print("Cohorte seleccionado:", current_cohort)
    print("Plantillas añadidas:", cohort_templates)
    print("IDs extraídos:", cohort_ids)


def exit_cohort():
    global current_cohort, cohort_ids
    cohort_ids = []
    current_cohort = None
    listbox_templates.delete(0, tk.END)
    for t in templates:
        listbox_templates.insert(tk.END, t)
    print("Se ha salido del cohorte y se han cargado los templates por defecto.")


def add_template():
    from tkinter import simpledialog

    global current_cohort
    nueva_plantilla = simpledialog.askstring("Nueva Plantilla", "Introduce el texto de la nueva plantilla:")
    if not nueva_plantilla:
        return

    if current_cohort is not None:
        respuesta = messagebox.askyesno("Agregar a Cohorte", "¿Deseas agregar esta plantilla al cohorte actual?")
        if respuesta:
            cohorte_path = os.path.join(saved_cohorts_dir, current_cohort)
            plantilla_file = os.path.join(cohorte_path, "cohort_templates.txt")
            try:
                with open(plantilla_file, "a", encoding="utf-8") as f:
                    f.write(nueva_plantilla + "\n")
                listbox_templates.insert(tk.END, nueva_plantilla)
                messagebox.showinfo("Éxito", "Plantilla agregada al cohorte actual.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo agregar la plantilla al cohorte: {e}")
            return

    try:
        with open(template_file, "a", encoding="utf-8") as f:
            f.write(nueva_plantilla + "\n")
        templates.append(nueva_plantilla)
        listbox_templates.insert(tk.END, nueva_plantilla)
        messagebox.showinfo("Éxito", "Plantilla agregada a los templates de usuario.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo agregar la plantilla a los templates del usuario: {e}")
    
def abrir_info_output():
    """
    Abre una nueva ventana con tres cuadros de texto para mostrar información adicional.
    """
    ventana_info = tk.Toplevel(root)
    ventana_info.title("Información del Output")
    ventana_info.geometry("500x650")

    ttk.Label(ventana_info, text="Input procesado:", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=5)
    resumen_text = tk.Text(ventana_info, height=1, width=60, font=("Helvetica", 10), wrap="word")
    resumen_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    resumen_text.insert(tk.END, input)
    resumen_text.config(state=tk.DISABLED)

    ttk.Label(ventana_info, text="Consulta generada:", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=5)
    analisis_text = tk.Text(ventana_info, height=3, width=60, font=("Helvetica", 10), wrap="word")
    analisis_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    analisis_text.insert(tk.END, sentencia)
    analisis_text.config(state=tk.DISABLED)

    ttk.Label(ventana_info, text="Datos filtrados:", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=5)
    observaciones_text = tk.Text(ventana_info, height=4, width=60, font=("Helvetica", 10))
    observaciones_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    observaciones_text.insert(tk.END, dataSet)
    observaciones_text.config(state=tk.DISABLED)




# ---------------------------
# Configuración de la ventana principal y estilos 
# ---------------------------
root = tk.Tk()
root.title("Agente de Salud para Identificación de Cohortes")
root.geometry("1000x600")
root.configure(bg="#2e2e2e")

# Obtener el tamaño de la pantalla y ajustar la ventana
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}+0+0")  # Esto maximiza la ventana sin ocultar los botones

# Permitir salir con ESC
root.bind("<Escape>", lambda event: root.geometry("1000x600"))  # Regresar al tamaño inicial si se presiona ESC

# Usamos ttk para un aspecto más moderno
style = ttk.Style()
style.theme_use("clam")

# Paleta de colores oscuros
bg_dark = "#2e2e2e"
bg_frame = "#1e1e1e"
fg_text = "#ffffff"
accent = "#3c3c3c"

# Estilo para frames y widgets
style.configure("TFrame", background=bg_frame)
style.configure("TLabel", background=bg_frame, foreground=fg_text, font=("Segoe UI", 10))
style.configure("TButton", background=accent, foreground=fg_text, font=("Segoe UI", 10), padding=6)
style.map("TButton",
          background=[("active", "#505050")],
          foreground=[("active", "#ffffff")])


# ---------------------------
# Frame superior: Botones principales
# ---------------------------
frame_superior = ttk.Frame(root, padding=10)
frame_superior.pack(fill=tk.X)

btn_cargar  = ttk.Button(frame_superior, text="Cargar Datos", command=cargar_datos)
btn_guardar = ttk.Button(frame_superior, text="Guardar como Cohorte", command=guardar_cohorte)

btn_cargar.pack(side=tk.LEFT, padx=5)
"""
btn_cargar = ttk.Button(frame_superior, text="Cargar Datos", command=cargar_datos)
btn_cargar.pack(side=tk.LEFT, padx=5)
DESACTIVADO TEMPORAL
"""

btn_guardar = ttk.Button(frame_superior, text="Guardar como cohorte", command=guardar_cohorte)
btn_guardar.pack(side=tk.LEFT, padx=5)

# ---------------------------
# PanedWindow principal
# ---------------------------
pw_horizontal = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg=bg_dark, sashwidth=5, sashrelief=tk.FLAT, sashpad=0)
pw_horizontal.pack(fill=tk.BOTH, expand=True)

# PANEL IZQUIERDO
pw_left = tk.PanedWindow(pw_horizontal, orient=tk.VERTICAL, bg=bg_dark, sashwidth=5, sashrelief=tk.FLAT, sashpad=0)
pw_horizontal.add(pw_left, width=300)

# Plantillas
frame_templates = ttk.Frame(pw_left, padding=10)
pw_left.add(frame_templates, height=200)

frame_header = ttk.Frame(frame_templates)
frame_header.pack(fill=tk.X)

label_templates = ttk.Label(frame_header, text="Plantillas:")
btn_add_template = ttk.Button(frame_header, text="+", command=add_template, width=3)

label_templates.pack(side=tk.LEFT, padx=(0, 5))
btn_add_template.pack(side=tk.LEFT)

listbox_templates = Listbox(frame_templates, height=10, font=("Segoe UI", 10),
                            bg=bg_dark, fg=fg_text, selectbackground=accent, selectforeground=fg_text, relief=tk.FLAT)
listbox_templates.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

for t in templates:
    listbox_templates.insert(tk.END, t)
listbox_templates.bind("<<ListboxSelect>>", on_template_select)

# Cohortes guardados
frame_cohortes = ttk.Frame(pw_left, padding=10)
pw_left.add(frame_cohortes, height=200)

label_cohortes = ttk.Label(frame_cohortes, text="Cohortes guardados:")
label_cohortes.pack(anchor="w", padx=5, pady=(0, 5))

listbox_cohortes = Listbox(frame_cohortes, height=10, font=("Segoe UI", 10),
                           bg=bg_dark, fg=fg_text, selectbackground=accent, selectforeground=fg_text, relief=tk.FLAT)
listbox_cohortes.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

for t in cohortes:
    listbox_cohortes.insert(tk.END, t)
listbox_cohortes.bind("<<ListboxSelect>>", on_cohort_select)

btn_exit_cohort = ttk.Button(frame_cohortes, text="Salir Cohorte", command=exit_cohort)
btn_exit_cohort.pack(pady=5)

# PANEL DERECHO
pw_right = tk.PanedWindow(pw_horizontal, orient=tk.VERTICAL, bg=bg_dark, sashwidth=5, sashrelief=tk.FLAT, sashpad=0)
pw_horizontal.add(pw_right, stretch="always")

# Entrada LLM
frame_superior_derecha = ttk.Frame(pw_right, padding=10)
pw_right.add(frame_superior_derecha, height=100)

label_input = ttk.Label(frame_superior_derecha, text="Consulta para cohorte:")
label_input.pack(anchor="w", padx=5, pady=(0,5))

input_text = scrolledtext.ScrolledText(frame_superior_derecha, width=80, height=5,
                                       font=("Segoe UI", 10), bg=bg_dark, fg=fg_text, insertbackground=fg_text)
input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Salida y análisis
frame_medio_derecha = ttk.Frame(pw_right, padding=10)
pw_right.add(frame_medio_derecha, height=260)

btn_enviar = ttk.Button(frame_medio_derecha, text="Procesar cohorte", command=enviar_a_llm)
btn_enviar.pack(fill=tk.X, padx=5, pady=5)

btn_reset = ttk.Button(frame_medio_derecha, text="Reset", command=reset)
btn_reset.pack(fill=tk.X, padx=5, pady=5)

label_output = ttk.Label(frame_medio_derecha, text="Respuesta del Sistema:")
label_output.pack(anchor="w", padx=5, pady=(10, 5))

output_text = scrolledtext.ScrolledText(frame_medio_derecha, width=80, height=5,
                                        state=tk.DISABLED, font=("Segoe UI", 10),
                                        bg=bg_dark, fg=fg_text, insertbackground=fg_text)
output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Gráficos y dashboard
frame_inferior_derecha = ttk.Frame(pw_right, padding=10)
pw_right.add(frame_inferior_derecha, height=200)

#--------------------------------------------------------------------
from plotly.offline import plot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

# Función para cargar los datos
def cargar_datos(nombre_cohorte):
    ruta_base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    csv_file = os.path.join(ruta_base, 'src','Reto2','temp', nombre_cohorte)
    df = pd.read_csv(csv_file)
    return df

# Función mejorada para crear gráfico de barras (histograma)
def crear_histograma(df, columna):
    fig, ax = plt.subplots(figsize=(8, 5))  # Aumentar el tamaño del gráfico
    # Estilo de Seaborn
    sns.set_style("whitegrid")
    # Definir bins en función del número de valores únicos (máximo 20)
    bins = min(20, df[columna].nunique())
    # Crear el histograma con mejoras visuales
    ax.hist(df[columna].dropna(), bins=bins, color='royalblue', edgecolor='black', alpha=0.7)
    # Mejorar etiquetas y título
    ax.set_title(f'Distribución de {columna}', fontsize=14, fontweight='bold')
    ax.set_xlabel(columna, fontsize=12)
    ax.set_ylabel('Frecuencia', fontsize=12)
    return fig


# Función mejorada para crear gráfico de líneas
def crear_grafico_lineas(df, columna):
    fig, ax = plt.subplots(figsize=(8, 5))  # Aumentar tamaño
    # Eliminar valores nulos
    df_filtrado = df.dropna(subset=[columna]).sort_values(by=columna)
    # Estilo de Seaborn
    sns.set_style("whitegrid")
    # Graficar con línea más gruesa y puntos destacados
    ax.plot(df_filtrado[columna], marker='o', linestyle='-', color='darkorange', linewidth=2, markersize=6)
    # Mejorar etiquetas y título
    ax.set_title(f'Tendencia de {columna}', fontsize=14, fontweight='bold')
    ax.set_xlabel("Índice", fontsize=12)
    ax.set_ylabel(columna, fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)  # Grid más suave    
    return fig

# Función para crear gráfico circular
def crear_grafico_circular(df, columna):
    fig, ax = plt.subplots(figsize=(8, 5))  # Aumentar tamaño
    # Contar frecuencias de cada categoría
    conteo = df[columna].value_counts()
    # Crear gráfico de pastel
    ax.pie(conteo, labels=conteo.index, autopct='%1.1f%%', colors=sns.color_palette("pastel"), startangle=90)
    ax.set_title(f'Distribución de {columna}', fontsize=14, fontweight='bold')
    return fig


# Función para mostrar gráficos en una nueva ventana
def mostrar_grafico_en_ventana(df):
    global nueva_ventana
    if "nueva_ventana" in globals() and nueva_ventana.winfo_exists():
        nueva_ventana.lift()  # Traer la ventana al frente si ya existe
        return

    nueva_ventana = tk.Toplevel()
    nueva_ventana.title("Gráficos")
    nueva_ventana.geometry("900x600") 
    nueva_ventana.config(bg="gray18")


    # Evitar que cerrar esta ventana afecte la principal
    nueva_ventana.protocol("WM_DELETE_WINDOW", nueva_ventana.destroy)

    # Crear Notebook en la nueva ventana
    notebook = ttk.Notebook(nueva_ventana)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Frame para selección de columna
    frame_selector = ttk.Frame(nueva_ventana)
    frame_selector.pack(fill=tk.X, padx=10, pady=10)

    # Obtener columnas numéricas excluyendo "Pacientes ID"
    columnas_numericas = df.columns.tolist()
    if "PacienteID" in columnas_numericas:
        columnas_numericas.remove("PacienteID")

    if not columnas_numericas:
        messagebox.showerror("Error", "No hay columnas numéricas disponibles para filtrar.")
        nueva_ventana.destroy()
        return

    label_combo = ttk.Label(frame_selector, text="Selecciona una columna:")
    label_combo.pack(side=tk.LEFT, padx=5)

    combo_columnas = ttk.Combobox(frame_selector, values=columnas_numericas, state="readonly")
    combo_columnas.pack(side=tk.LEFT, padx=5)
    combo_columnas.current(0)  # Seleccionar la primera opción

    # Contenedor de gráficos
    frame_graficos = ttk.Frame(nueva_ventana)
    frame_graficos.pack(fill=tk.BOTH, expand=True)

    notebook_hist = ttk.Frame(notebook)
    notebook.add(notebook_hist, text="Histograma")

    notebook_lineas = ttk.Frame(notebook)
    notebook.add(notebook_lineas, text="Gráfico de Líneas")

    notebook_pie = ttk.Frame(notebook)
    notebook.add(notebook_pie, text="Gráfico Circular")

    # Función para actualizar los gráficos al cambiar la columna
    def actualizar_graficos(event):
        columna = combo_columnas.get()

        for widget in notebook_hist.winfo_children():
            widget.destroy()
        for widget in notebook_lineas.winfo_children():
            widget.destroy()
        for widget in notebook_pie.winfo_children():
            widget.destroy()

        

        # Graficar Circular si es categórico o tiene pocos valores únicos
        fig_pie = crear_grafico_circular(df, columna)
        canvas_pie = FigureCanvasTkAgg(fig_pie, master=notebook_pie)
        canvas_pie.draw()
        canvas_pie.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        fig_hist = crear_histograma(df, columna)
        canvas_hist = FigureCanvasTkAgg(fig_hist, master=notebook_hist)
        canvas_hist.draw()
        canvas_hist.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        fig_lineas = crear_grafico_lineas(df, columna)
        canvas_lineas = FigureCanvasTkAgg(fig_lineas, master=notebook_lineas)
        canvas_lineas.draw()
        canvas_lineas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    combo_columnas.bind("<<ComboboxSelected>>", actualizar_graficos)

    # Generar los gráficos por primera vez
    actualizar_graficos(None)

# Función para cerrar correctamente la ventana secundaria
def cerrar_ventana(ventana):
    ventana.destroy()

# Función que se ejecuta al presionar el botón
def on_button_click():
    try:
        df = cargar_datos('resultado.csv')
        mostrar_grafico_en_ventana(df)
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")


# Botón para generar los gráficos
boton_generar = ttk.Button(frame_inferior_derecha, text="Generar Gráficos", command=lambda: on_button_click())
boton_generar.pack(pady=20) #(side=tk.BOTTOM, padx=5, pady=5)

# Manejar el cierre de la ventana principal
root.protocol("WM_DELETE_WINDOW", root.quit)

root.mainloop()


# ---------------------------
# Eliminar la carpeta temporal y su contenido al finalizar el programa
# ---------------------------
if os.path.exists(temp_folder):
    shutil.rmtree(temp_folder)
    print(f'\nLa carpeta temporal {temp_folder} y su contenido han sido eliminados.')