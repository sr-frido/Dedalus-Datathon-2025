import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, Listbox
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from aux_func_GUI import leer_lineas_no_vacias, listar_carpetas

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

def analizar_datos():
    """
    Muestra un histograma de la columna 'edad' del DataFrame 'cohorte_pacientes'
    si se encuentra disponible.
    """
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
            messagebox.showwarning("Columna no encontrada", 
                                   "El DataFrame 'cohorte_pacientes' no contiene la columna 'edad'.")
    else:
        messagebox.showerror("Error", "No existe 'cohorte_pacientes' en los datos cargados.")

def guardar_cohorte():
    nombre_nuevo = "Cohorte Pacientes Filtrada"
    if "cohorte_pacientes" in cohortes:
        cohortes_guardados[nombre_nuevo] = cohortes["cohorte_pacientes"].copy()
        listbox_cohortes.insert(tk.END, nombre_nuevo)
        messagebox.showinfo("Guardado", f"Se guardó la cohorte como '{nombre_nuevo}'.")
    else:
        messagebox.showerror("Error", "No se encontró 'cohorte_pacientes' para guardar.")

def llamar_a_llm_bedrock(prompt):
    """
    Placeholder para conexión real a AWS Bedrock o LiteLLM.
    """
    respuesta_simulada = (
        "Respuesta simulada del LLM.\n\n"
        f"Prompt recibido:\n{prompt}"
    )
    return respuesta_simulada

def enviar_a_llm():
    prompt = input_text.get("1.0", tk.END).strip()
    if not prompt:
        messagebox.showwarning("Advertencia", "El prompt está vacío.")
        return
    
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


# ---------------------------
# Configuración de la ventana principal y estilos
# ---------------------------
root = tk.Tk()
root.title("Agente de Salud para Identificación de Cohortes")
root.geometry("1000x600")
root.configure(bg="#f0f0f0")

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

label_templates = ttk.Label(frame_templates, text="Plantillas:")
label_templates.pack(anchor="w", padx=5, pady=(0,5))

# Agregar el botón de "Añadir Plantilla" en el frame de plantillas (por ejemplo, debajo del listbox de plantillas)
btn_add_template = ttk.Button(frame_templates, text="+", command=add_template)
btn_add_template.pack(pady=5)

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
pw_right.add(frame_superior_derecha, height=200)

label_input = ttk.Label(frame_superior_derecha, text="Prompt para LLM:")
label_input.pack(anchor="w", padx=5, pady=(0,5))

input_text = scrolledtext.ScrolledText(frame_superior_derecha, width=80, height=5, font=("Helvetica", 10))
input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Sección media: Botones y salida del LLM
frame_medio_derecha = ttk.Frame(pw_right, padding=10)
pw_right.add(frame_medio_derecha, height=200)

btn_analizar = ttk.Button(frame_medio_derecha, text="Analizar Cohorte (Ej. hist edad)", command=analizar_datos)
btn_analizar.pack(fill=tk.X, padx=5, pady=5)

btn_enviar = ttk.Button(frame_medio_derecha, text="Enviar a LLM", command=enviar_a_llm)
btn_enviar.pack(fill=tk.X, padx=5, pady=5)

label_output = ttk.Label(frame_medio_derecha, text="Respuesta del Sistema:")
label_output.pack(anchor="w", padx=5, pady=(10,5))

output_text = scrolledtext.ScrolledText(frame_medio_derecha, width=80, height=5, state=tk.DISABLED, font=("Helvetica", 10))
output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Sección inferior: Área de gráficos o resultados visuales
frame_inferior_derecha = ttk.Frame(pw_right, padding=10)
pw_right.add(frame_inferior_derecha, height=200)

canvas_graficos = tk.Canvas(frame_inferior_derecha, bg="white")
canvas_graficos.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

root.mainloop()
