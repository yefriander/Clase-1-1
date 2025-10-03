import dash
from dash import html, dcc

dash.register_page(__name__, path='/pagina2', name='Pagina 2')

layout = html.Div([
    html.H1("Bienvenido a la página 2"),
])