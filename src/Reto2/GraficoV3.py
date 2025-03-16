#pip instal dash
# pip install tkinterweb
import dash
import os
from dash import dcc, html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

# Cargar datos de prueba (puede estar en inglés o español)
def cargar_datos():
    ruta_base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    csv_file = os.path.join(ruta_base, 'Datos sintéticos reto 2', 'cohorte_pacientes.csv')
    df = pd.read_csv(csv_file)
    df.rename(columns={
        "Gender": "Género", "Age": "Edad", "Province": "Provincia",
        "Genero": "Género", "Provincia": "Provincia"
    }, inplace=True, errors='ignore')
    return df

# Cargar otras cohortes
def cargar_otras_cohortes(nombre_cohorte):
    ruta_base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    csv_file = os.path.join(ruta_base, 'Datos sintéticos reto 2', nombre_cohorte)
    df = pd.read_csv(csv_file)
    return df

# Cargar SNOMED para alergias, condiciones y procedimientos
def cargar_snomed(nombre_cohorte):
    ruta_base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    csv_file = os.path.join(ruta_base, 'Datos sintéticos reto 2', nombre_cohorte)
    df = pd.read_csv(csv_file)
    # Mapeo de Código SNOMED a Descripción
    snomed_dict = dict(zip(df['Código_SNOMED'], df['Descripcion']))
    return snomed_dict

# Cargar los CSV
df_pacientes = cargar_datos()
df_alergias = cargar_otras_cohortes('cohorte_alegias.csv')
df_condiciones = cargar_otras_cohortes('cohorte_condiciones.csv')
df_encuentros = cargar_otras_cohortes('cohorte_encuentros.csv')
df_medicaciones = cargar_otras_cohortes('cohorte_medicationes.csv')
df_procedimientos = cargar_otras_cohortes('cohorte_procedimientos.csv')

# Cargar SNOMED
snomed_alergias = cargar_snomed('SNOMED_alergias.csv')
snomed_condiciones = cargar_snomed('SNOMED_condiciones.csv')
snomed_procedimientos = cargar_snomed('SNOMED_procedimientos.csv')

# Listado de las columnas de cada cohorte, excluyendo 'PacienteID' y 'Descripción' cuando corresponda
def filtrar_columnas(df, excluir_descripcion=False):
    columnas = [col for col in df.columns if col != 'PacienteID']
    if excluir_descripcion:
        columnas = [col for col in columnas if col != 'Descripcion']
    return columnas

cohortes_columnas = {
    "Cohorte Pacientes": filtrar_columnas(df_pacientes),
    "Cohorte Alergias": filtrar_columnas(df_alergias, excluir_descripcion=True),
    "Cohorte Condiciones": filtrar_columnas(df_condiciones, excluir_descripcion=True),
    "Cohorte Encuentros": filtrar_columnas(df_encuentros),
    "Cohorte Medicaciones": filtrar_columnas(df_medicaciones),
    "Cohorte Procedimientos": filtrar_columnas(df_procedimientos, excluir_descripcion=True)
}

# Gráficos iniciales
def crear_grafico(df, columna, tipo="pie"):
    if tipo == "pie":
        return px.pie(df, names=columna, title=f"Distribución por {columna}")
    elif tipo == "histogram":
        return px.histogram(df, x=columna, title=f"Distribución por {columna}", nbins=5)

# Layout de la aplicación
app = dash.Dash(__name__)

app.layout = html.Div([
    # Selector de cohorte y columna para filtro
    html.Div([
        dcc.Dropdown(
            id='cohorte-dropdown',
            options=[{'label': cohorte, 'value': cohorte} for cohorte in cohortes_columnas.keys()],
            value='Cohorte Pacientes',  # Valor por defecto
            style={'width': '48%'}
        ),
        dcc.Dropdown(
            id='columna-dropdown',
            style={'width': '48%'}
        ),
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),

    # Selector para Código SNOMED y leyenda
    html.Div([
        dcc.Dropdown(
            id='codigo-snomed-dropdown',
            style={'width': '48%'}
        ),
        html.Div(id='leyenda-snomed', style={'marginTop': '20px'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),

    # Contenedores de gráficos
    html.Div([
        dcc.Graph(id='grafico')
    ], style={'marginTop': '20px'})
])


# Actualizar las opciones del dropdown de columnas según la cohorte seleccionada
@app.callback(
    Output('columna-dropdown', 'options'),
    Output('columna-dropdown', 'value'),
    Input('cohorte-dropdown', 'value')
)
def actualizar_columnas(cohorte_seleccionado):
    columnas = cohortes_columnas[cohorte_seleccionado]
    return [{'label': col, 'value': col} for col in columnas], columnas[0]

# Actualizar las opciones para Código SNOMED según la cohorte seleccionada
@app.callback(
    Output('codigo-snomed-dropdown', 'options'),
    Output('codigo-snomed-dropdown', 'value'),
    Input('cohorte-dropdown', 'value')
)
def actualizar_snomed(cohorte_seleccionado):
    if cohorte_seleccionado == "Cohorte Alergias":
        snomed_dict = snomed_alergias
    elif cohorte_seleccionado == "Cohorte Condiciones":
        snomed_dict = snomed_condiciones
    elif cohorte_seleccionado == "Cohorte Procedimientos":
        snomed_dict = snomed_procedimientos
    else:
        return [], None  # Si no es una cohorte con SNOMED

    options = [{'label': f'{codigo}: {descripcion}', 'value': codigo} for codigo, descripcion in snomed_dict.items()]
    return options, options[0]['value'] if options else None

# Callback para mostrar leyenda con SNOMED seleccionado
@app.callback(
    Output('leyenda-snomed', 'children'),
    Input('codigo-snomed-dropdown', 'value'),
    Input('cohorte-dropdown', 'value')
)
def mostrar_leyenda(codigo_snomed, cohorte_seleccionado):
    if not codigo_snomed:
        return 'Selecciona un código SNOMED para ver la descripción'

    # Seleccionar el diccionario SNOMED correspondiente según la cohorte
    if cohorte_seleccionado == "Cohorte Alergias":
        snomed_dict = snomed_alergias
    elif cohorte_seleccionado == "Cohorte Condiciones":
        snomed_dict = snomed_condiciones
    elif cohorte_seleccionado == "Cohorte Procedimientos":
        snomed_dict = snomed_procedimientos
    else:
        return ''  # Si no es una cohorte con SNOMED

    # Obtener la descripción del código SNOMED
    descripcion = snomed_dict.get(codigo_snomed, 'Descripción no disponible')

    # Mostrar la leyenda con el código SNOMED y la descripción
    return f"Código SNOMED: {codigo_snomed}, Descripción: {descripcion}"


# Crear gráfico dinámico
@app.callback(
    Output('grafico', 'figure'),
    Input('cohorte-dropdown', 'value'),
    Input('columna-dropdown', 'value')
)
def actualizar_grafico(cohorte_seleccionado, columna_seleccionada):
    # Cargar el DataFrame correspondiente
    if cohorte_seleccionado == "Cohorte Pacientes":
        df = df_pacientes
    elif cohorte_seleccionado == "Cohorte Alergias":
        df = df_alergias
    elif cohorte_seleccionado == "Cohorte Condiciones":
        df = df_condiciones
    elif cohorte_seleccionado == "Cohorte Encuentros":
        df = df_encuentros
    elif cohorte_seleccionado == "Cohorte Medicaciones":
        df = df_medicaciones
    elif cohorte_seleccionado == "Cohorte Procedimientos":
        df = df_procedimientos

    # Crear gráfico
    if columna_seleccionada in ['Edad', 'Fecha_diagnostico', 'Fecha_inicio', 'Fecha_fin']:  # Si es numérico o temporal
        return crear_grafico(df, columna_seleccionada, tipo="histogram")
    else:
        return crear_grafico(df, columna_seleccionada, tipo="pie")



if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False, port=8050) # 'use_reloader=False' previene reinicios automáticos
