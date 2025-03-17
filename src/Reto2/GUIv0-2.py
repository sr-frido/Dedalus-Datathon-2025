import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, Listbox
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
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
template_file = "./src/Reto2/user-templates.txt"
templates = leer_lineas_no_vacias(template_file)
saved_cohorts_dir = "./src/Reto2/saved-cohorts"
cohortes = listar_carpetas(saved_cohorts_dir)
cohortes_guardados = {}

# Variables globales para el cohorte actual y los IDs extraídos
current_cohort = None
cohort_ids = []

# Variables globales para info-output
input = "Aún no hay información"
sentencia = "Aún no hay información"
dataSet = "Aún no hay información"


# ---------------------------
# Funciones para manejo de datos y LLM
# ---------------------------
def cargar_datos():
    directory = filedialog.askdirectory()
    if directory:
        archivos_csv = [f for f in os.listdir(directory) if f.endswith(".csv")]
        if not archivos_csv:
            messagebox.showwarning("Advertencia", "No se encontraron archivos CSV en la carpeta seleccionada.")
            return
        
        cohortes.clear()  # Limpia el diccionario para la nueva carga
        for filename in archivos_csv:
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath)
            nombre_cohorte = os.path.splitext(filename)[0]
            cohortes[nombre_cohorte] = df
        
        messagebox.showinfo("Carga exitosa", f"Se cargaron {len(cohortes)} CSVs en total.")

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

def on_template_select(event):
    seleccion = listbox_templates.curselection()
    if seleccion:
        template = listbox_templates.get(seleccion)
        input_text.delete("1.0", tk.END)
        input_text.insert(tk.END, template)

def on_cohort_select(event):
    import os
    import re
    from aux_func_GUI import leer_lineas_no_vacias
    global current_cohort, cohort_ids

    widget = event.widget
    index = widget.nearest(event.y)
    if index not in widget.curselection():
        return

    current_cohort = widget.get(index)
    cohorte_path = os.path.join(saved_cohorts_dir, current_cohort)

    # Leer las plantillas específicas del cohorte y añadirlas al listbox de plantillas
    plantillas_file = os.path.join(cohorte_path, "cohort_templates.txt")
    cohort_templates = leer_lineas_no_vacias(plantillas_file)
    for plantilla in cohort_templates:
        listbox_templates.insert(tk.END, plantilla)

    # Leer el log del cohorte para extraer los IDs
    log_file = os.path.join(cohorte_path, "cohort_log.txt")
    lineas = leer_lineas_no_vacias(log_file)
    contenido = " ".join(lineas)
    match = re.search(r"\{([^}]+)\}", contenido)
    if match:
        ids_str = match.group(1)
        ids_lista = [valor.strip() for valor in ids_str.split(",") if valor.strip()]
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
    from tkinter import simpledialog, messagebox
    import os
    global current_cohort

    # Solicitar al usuario el texto de la nueva plantilla
    nueva_plantilla = simpledialog.askstring("Nueva Plantilla", "Introduce el texto de la nueva plantilla:")
    if not nueva_plantilla:
        return

    # Si se está en un cohorte (current_cohort no es None), preguntar si se desea agregar al cohorte actual
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

    # Si no se está en un cohorte o se decide no agregarlo al cohorte, agregar al fichero de templates del usuario
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
root.configure(bg="#f0f0f0")

# Obtener el tamaño de la pantalla y ajustar la ventana
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}+0+0")  # Esto maximiza la ventana sin ocultar los botones

# Permitir salir con ESC
root.bind("<Escape>", lambda event: root.geometry("1000x600"))  # Regresar al tamaño inicial si se presiona ESC

# Usamos ttk para un aspecto más moderno
style = ttk.Style()
style.theme_use("clam")
style.configure("TFrame", background="#f0f0f0")
style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 10))
style.configure("TButton", font=("Helvetica", 10), padding=5)

# ---------------------------
# Frame superior: botones principales
# ---------------------------
frame_superior = ttk.Frame(root, padding=10)
frame_superior.pack(fill=tk.X)

btn_cargar = ttk.Button(frame_superior, text="Cargar Datos", command=cargar_datos)
btn_cargar.pack(side=tk.LEFT, padx=5)

btn_guardar = ttk.Button(frame_superior, text="Guardar como Cohorte", command=guardar_cohorte)
btn_guardar.pack(side=tk.LEFT, padx=5)

# ---------------------------
# PanedWindow principal para dividir en panel izquierdo y derecho
# ---------------------------
pw_horizontal = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg="#f0f0f0", sashwidth=5)
pw_horizontal.pack(fill=tk.BOTH, expand=True)

# ---------------------------
# PANEL IZQUIERDO: PanedWindow vertical para plantillas y cohortes guardados
# ---------------------------
pw_left = tk.PanedWindow(pw_horizontal, orient=tk.VERTICAL, bg="#f0f0f0", sashwidth=5)
pw_horizontal.add(pw_left, width=300)

# Sección de plantillas
frame_templates = ttk.Frame(pw_left, padding=10)
pw_left.add(frame_templates, height=200)

# Crear un frame para colocar la etiqueta y el botón en la misma línea
frame_header = ttk.Frame(frame_templates)
frame_header.pack(fill=tk.X)

label_templates = ttk.Label(frame_header, text="Plantillas:")
label_templates.pack(side=tk.LEFT, padx=(0, 5))

btn_add_template = ttk.Button(frame_header, text="+", command=add_template, width=3)
btn_add_template.pack(side=tk.LEFT)

listbox_templates = Listbox(frame_templates, height=10, font=("Helvetica", 10))
listbox_templates.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


for t in templates:
    listbox_templates.insert(tk.END, t)
listbox_templates.bind("<<ListboxSelect>>", on_template_select)


# Sección de cohortes guardados
frame_cohortes = ttk.Frame(pw_left, padding=10)
pw_left.add(frame_cohortes, height=200)


label_cohortes = ttk.Label(frame_cohortes, text="Cohortes guardados:")
label_cohortes.pack(anchor="w", padx=5, pady=(0,5))

listbox_cohortes = Listbox(frame_cohortes, height=10, font=("Helvetica", 10))
listbox_cohortes.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

for t in cohortes:
    listbox_cohortes.insert(tk.END, t)
listbox_cohortes.bind("<<ListboxSelect>>", on_cohort_select)

btn_exit_cohort = ttk.Button(frame_cohortes, text="Salir Cohorte", command=exit_cohort)
btn_exit_cohort.pack(pady=5)

# ---------------------------
# PANEL DERECHO: PanedWindow vertical para entrada, salida y gráficos
# ---------------------------
pw_right = tk.PanedWindow(pw_horizontal, orient=tk.VERTICAL, bg="#f0f0f0", sashwidth=5)
pw_horizontal.add(pw_right, stretch="always")

# Sección superior: Entrada de prompt para LLM
frame_superior_derecha = ttk.Frame(pw_right, padding=10)
pw_right.add(frame_superior_derecha, height=100)

label_input = ttk.Label(frame_superior_derecha, text="Prompt para LLM:")
label_input.pack(anchor="w", padx=5, pady=(0,5))

input_text = scrolledtext.ScrolledText(frame_superior_derecha, width=80, height=5, font=("Helvetica", 10))
input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Sección media: Botones y salida del LLM
frame_medio_derecha = ttk.Frame(pw_right, padding=10)
pw_right.add(frame_medio_derecha, height=260)

btn_enviar = ttk.Button(frame_medio_derecha, text="Procesar cohorte", command=enviar_a_llm)
btn_enviar.pack(fill=tk.X, padx=5, pady=5)

btn_reset = ttk.Button(frame_medio_derecha, text="Reset", command=reset)
btn_reset.pack(fill=tk.X, padx=5, pady=5)

label_output = ttk.Label(frame_medio_derecha, text="Respuesta del Sistema:")
label_output.pack(anchor="w", padx=5, pady=(10,5))

output_text = scrolledtext.ScrolledText(frame_medio_derecha, width=80, height=5, state=tk.DISABLED, font=("Helvetica", 10), wrap="word")
output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Sección inferior: Área de gráficos o resultados visuales
frame_inferior_derecha = ttk.Frame(pw_right, padding=10)
pw_right.add(frame_inferior_derecha, height=200)

canvas_graficos = tk.Canvas(frame_inferior_derecha, bg="white")
canvas_graficos.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Crear botón justo debajo de output_text
btn_mostrar_info = ttk.Button(frame_medio_derecha, text="Mostrar Información", command=abrir_info_output)
btn_mostrar_info.pack(pady=5)  # Añade un pequeño espacio debajo

root.mainloop()


# ---------------------------
# Eliminar la carpeta temporal y su contenido al finalizar el programa
# ---------------------------
if os.path.exists(temp_folder):
    shutil.rmtree(temp_folder)
    print(f'\nLa carpeta temporal {temp_folder} y su contenido han sido eliminados.')