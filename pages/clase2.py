import dash
from dash import html, dcc, Input, Output, State, callback
import numpy as np
import plotly.graph_objects as go
 
dash.register_page(__name__, path='/campo_vectorial', name='Campo Vectorial')
 
#### Layout ####
layout = html.Div([
    html.Div([
        html.H2("Campo Vectorial 2D", className="title"),
 
        html.Div([
            html.Label("Ecuación dx/dt ="),
            dcc.Input(id="input-fx", type="text", value="np.sin(X)", className="input-field")
        ], className="input-group"),
 
        html.Div([
            html.Label("Ecuación dy/dt ="),
            dcc.Input(id="input-fy", type="text", value="np.sin(Y)", className="input-field")
        ], className="input-group"),
 
        html.Div([
            html.Label("Rango del eje X:"),
            dcc.Input(id="input-xmax", type="number", value=5, className="input-field")
        ], className="input-group"),
 
        html.Div([
            html.Label("Rango del eje Y:"),
            dcc.Input(id="input-ymax", type="number", value=5, className="input-field")
        ], className="input-group"),
 
        html.Div([
            html.Label("Resolución de la malla:"),
            dcc.Input(id="input-n", type="number", value=15, className="input-field")
        ], className="input-group"),
 
        html.Button("Generar campo", id="btn-generar", className="btn-generar"),
        # Agregar ejemplos para los estudiantes
        html.Div([
            html.H3("Ejemplos para probar:", style={'margin-top': '20px', 'font-size': '14px'}),
            html.P("• dx/dt = X, dy/dt = Y (radial)", style={'font-size': '12px', 'margin': '5px 0'}),
            html.P("• dx/dt = -Y, dy/dt = X (rotacional)", style={'font-size': '12px', 'margin': '5px 0'}),
            html.P("• dx/dt = Y, dy/dt = -X (rotacional inverso)", style={'font-size': '12px', 'margin': '5px 0'}),
            html.P("• dx/dt = np.sin(X), dy/dt = np.cos(Y)", style={'font-size': '12px', 'margin': '5px 0'}),
        ], style={'background': '#f0f8ff', 'padding': '10px', 'border-radius': '5px', 'margin-top': '15px'})
 
    ], className="content left"),
 
    html.Div([
        html.H2("Visualización del Campo Vectorial", className="title"),
        dcc.Graph(id="grafica-campo", style={'height': '450px', 'width': '100%'}),
        # Información adicional
        html.Div(id="info-campo", style={'margin-top': '10px', 'font-size': '12px', 'color': '#666'})
    ], className="content right")
 
], className="page-container")
 
 
#### Callback ####
@callback(
    [Output("grafica-campo", "figure"),
     Output("info-campo", "children")],
    Input("btn-generar", "n_clicks"),
    State("input-fx", "value"),
    State("input-fy", "value"),
    State("input-xmax", "value"),
    State("input-ymax", "value"),
    State("input-n", "value"),
    prevent_initial_call=False
)
def actualizar_campo(n_clicks, fx_str, fy_str, xmax, ymax, n):
    # Crear malla de puntos
    x = np.linspace(-xmax, xmax, n)
    y = np.linspace(-ymax, ymax, n)
    X, Y = np.meshgrid(x, y)  # X, Y son arrays 2D
    info_mensaje = ""
    # Evaluar funciones de forma segura
    try:
        # Crear un entorno seguro para eval con las variables correctas
        entorno_seguro = {
            'X': X,           # Array 2D para x
            'Y': Y,           # Array 2D para y
            'np': np,         # NumPy
            'sin': np.sin,    # Funciones matemáticas
            'cos': np.cos,
            'tan': np.tan,
            'exp': np.exp,
            'sqrt': np.sqrt,
            'pi': np.pi,
            'e': np.e
        }
        # Evaluar las expresiones
        fx = eval(fx_str, {"__builtins__": {}}, entorno_seguro)
        fy = eval(fy_str, {"__builtins__": {}}, entorno_seguro)
        # Calcular algunas estadísticas
        mag_max = np.max(np.sqrt(fx**2 + fy**2))
        mag_min = np.min(np.sqrt(fx**2 + fy**2))
        info_mensaje = f"Magnitud: min = {mag_min:.2f}, max = {mag_max:.2f}"
    except Exception as e:
        # Si hay error, usar campo cero
        fx = np.zeros_like(X)
        fy = np.zeros_like(Y)
        info_mensaje = f"Error en las expresiones: {str(e)}"
 
    # Crear gráfica
    fig = go.Figure()
 
    # Agregar vectores como flechas simplificadas
    for i in range(n):
        for j in range(n):
            x0, y0 = X[i, j], Y[i, j]          # Punto inicial
            x1, y1 = x0 + fx[i, j], y0 + fy[i, j]  # Punto final
            # Línea del vector
            fig.add_trace(go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines+markers",
                line=dict(color="blue", width=2),
                marker=dict(size=[3, 5], color=["blue", "red"]),  # Punto inicial y final
                showlegend=False,
                hovertemplate=f'Punto: ({x0:.1f}, {y0:.1f})<br>Vector: ({fx[i,j]:.2f}, {fy[i,j]:.2f})<extra></extra>'
            ))
 
    # Ajustes de estilo
    fig.update_layout(
        title=dict(
            text=f"<b>Campo Vectorial: dx/dt = {fx_str}, dy/dt = {fy_str}</b>",
            x=0.5, font=dict(size=16, color="green")
        ),
        xaxis_title="x",
        yaxis_title="y",
        paper_bgcolor="lightyellow",
        plot_bgcolor="white",
        font=dict(family="Outfit", size=12),
        margin=dict(l=40, r=40, t=60, b=40)
    )
 
    fig.update_xaxes(
        range=[-xmax*1.1, xmax*1.1],  # Un poco más amplio para ver los vectores completos
        zeroline=True, zerolinecolor="black", zerolinewidth=2,
        showgrid=True, gridcolor="lightgray"
    )
    fig.update_yaxes(
        range=[-ymax*1.1, ymax*1.1],
        zeroline=True, zerolinecolor="black", zerolinewidth=2,
        showgrid=True, gridcolor="lightgray",
        scaleanchor="x", scaleratio=1  # Mantener aspecto cuadrado
    )
 
    return fig, info_mensaje