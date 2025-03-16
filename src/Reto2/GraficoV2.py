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

df_pacientes = cargar_datos()
df_alergias = cargar_otras_cohortes('cohorte_alegias.csv')
df_condiciones = cargar_otras_cohortes('cohorte_condiciones.csv')
df_encuentros = cargar_otras_cohortes('cohorte_encuentros.csv')
df_medicaciones = cargar_otras_cohortes('cohorte_medicationes.csv')
df_procedimientos = cargar_otras_cohortes('cohorte_procedimientos.csv')

# Listado de las columnas de cada cohorte
cohortes_columnas = {
    "Cohorte Pacientes": df_pacientes.columns.tolist(),
    "Cohorte Alergias": df_alergias.columns.tolist(),
    "Cohorte Condiciones": df_condiciones.columns.tolist(),
    "Cohorte Encuentros": df_encuentros.columns.tolist(),
    "Cohorte Medicaciones": df_medicaciones.columns.tolist(),
    "Cohorte Procedimientos": df_procedimientos.columns.tolist()
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
        )
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
    app.run_server(debug=True)
