import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CSVGrapherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gráfica de CSV en Tkinter")

        # Botón para cargar archivo CSV
        self.btn_cargar = ttk.Button(root, text="Cargar CSV", command=self.cargar_csv)
        self.btn_cargar.pack(pady=5)

        # Combobox para seleccionar columnas (se llenará después de cargar el CSV)
        self.frame_seleccion = ttk.Frame(root)
        self.frame_seleccion.pack(pady=5)

        self.label_x = ttk.Label(self.frame_seleccion, text="Eje X:")
        self.label_x.grid(row=0, column=0)
        self.combo_x = ttk.Combobox(self.frame_seleccion, state="readonly")
        self.combo_x.grid(row=0, column=1)

        self.label_y = ttk.Label(self.frame_seleccion, text="Eje Y:")
        self.label_y.grid(row=1, column=0)
        self.combo_y = ttk.Combobox(self.frame_seleccion, state="readonly")
        self.combo_y.grid(row=1, column=1)

        # Botón para graficar
        self.btn_graficar = ttk.Button(root, text="Graficar", command=self.graficar)
        self.btn_graficar.pack(pady=5)

        # Área para la gráfica
        self.frame_grafica = ttk.Frame(root)
        self.frame_grafica.pack()

        self.df = None  # Variable para almacenar los datos

    def cargar_csv(self):
        """Abre un cuadro de diálogo para seleccionar un archivo CSV y carga los datos"""
        archivo = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
        if not archivo:
            return

        try:
            self.df = pd.read_csv(archivo)
            columnas = list(self.df.columns)

            # Llenar los combobox con las columnas disponibles
            self.combo_x["values"] = columnas
            self.combo_y["values"] = columnas

            if columnas:
                self.combo_x.current(0)
                self.combo_y.current(1)

            messagebox.showinfo("Éxito", "Archivo CSV cargado correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el CSV:\n{e}")

    def graficar(self):
        """Grafica las columnas seleccionadas"""
        if self.df is None:
            messagebox.showwarning("Atención", "Primero carga un archivo CSV")
            return

        col_x = self.combo_x.get()
        col_y = self.combo_y.get()

        if not col_x or not col_y:
            messagebox.showwarning("Atención", "Selecciona las columnas a graficar")
            return

        # Crear la figura
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.plot(self.df[col_x], self.df[col_y], marker='o', linestyle='-')
        ax.set_xlabel(col_x)
        ax.set_ylabel(col_y)
        ax.set_title(f"Gráfica de {col_x} vs {col_y}")

        # Limpiar frame anterior y mostrar nueva gráfica
        for widget in self.frame_grafica.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack()

# Ejecutar la aplicación
root = tk.Tk()
app = CSVGrapherApp(root)
root.mainloop()
