import dash
from dash import html, dcc

dash.register_page(__name__, path='/pagina1', name='Pagina 1')

layout = html.Div([
    html.H1("Bienvenido a la página 1"),
])