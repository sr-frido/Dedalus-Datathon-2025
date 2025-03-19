import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

# Datos de ejemplo
data = {
    "Category": ["Country", "Country", "Site", "Gender", "Gender"],
    "Label": ["A", "B", "X", "Male", "Female"],
    "Value": [90, 10, 100, 95, 5]
}
df_pie = pd.DataFrame(data)

# Datos de edad
age_data = {
    "Age Group": ["40-49", "50-59", "60-69", "70-79", "80-95"],
    "Count": [7, 33, 15, 14, 2]
}
df_age = pd.DataFrame(age_data)

# Datos de reclutamiento
recruitment_data = {"Recruitable": 70, "Non Recruitable": 4, "Total": 74}

# Gráficos
fig_country = px.pie(df_pie[df_pie['Category'] == "Country"], names='Label', values='Value', title="Distribution by Country")
fig_site = px.pie(df_pie[df_pie['Category'] == "Site"], names='Label', values='Value', title="Distribution by Site")
fig_gender = px.pie(df_pie[df_pie['Category'] == "Gender"], names='Label', values='Value', title="Distribution by Gender")
fig_age = px.bar(df_age, x='Age Group', y='Count', title="Distribution by Age")

# Aplicación Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        dcc.Graph(figure=fig_country, style={'width': '30%', 'display': 'inline-block'}),
        dcc.Graph(figure=fig_site, style={'width': '30%', 'display': 'inline-block'}),
        dcc.Graph(figure=fig_gender, style={'width': '30%', 'display': 'inline-block'})
    ]),
    dcc.Graph(figure=fig_age, style={'width': '50%', 'margin': 'auto'}),
    html.Div([
        html.Div(f"Recruitable: {recruitment_data['Recruitable']}", style={'display': 'inline-block', 'margin': '20px', 'fontSize': '20px'}),
        html.Div(f"Non Recruitable: {recruitment_data['Non Recruitable']}", style={'display': 'inline-block', 'margin': '20px', 'fontSize': '20px'}),
        html.Div(f"Total: {recruitment_data['Total']}", style={'display': 'inline-block', 'margin': '20px', 'fontSize': '20px'})
    ], style={'textAlign': 'center'})
])

if __name__ == '__main__':
    app.run_server(debug=True)
