import dash
from dash import html, dcc, Input, Output, State, callback
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import odeint

dash.register_page(__name__, path='/modelo_sir', name='Modelo SIR')

#### Layout ####
layout = html.Div([
    html.Div([
        html.H2("Modelo SIR - Epidemiología", className="title"),
        
        html.Div([
            html.H3("Parámetros del modelo:", style={'font-size': '16px', 'color': '#333'}),
            
            html.Div([
                html.Label("Población total (N):"),
                dcc.Input(id="input-N", type="number", value=1000, className="input-field")
            ], className="input-group"),

            html.Div([
                html.Label("Tasa de transmisión (β):"),
                dcc.Input(id="input-beta", type="number", value=0.3, step=0.01, className="input-field")
            ], className="input-group"),

            html.Div([
                html.Label("Tasa de recuperación (γ):"),
                dcc.Input(id="input-gamma", type="number", value=0.1, step=0.01, className="input-field")
            ], className="input-group"),

            html.Div([
                html.Label("Infectados iniciales:"),
                dcc.Input(id="input-I0", type="number", value=1, className="input-field")
            ], className="input-group"),

            html.Div([
                html.Label("Tiempo de simulación (días):"),
                dcc.Input(id="input-tiempo", type="number", value=100, className="input-field")
            ], className="input-group"),

            html.Button("Simular epidemia", id="btn-simular", className="btn-generar"),
            
            # Información educativa
            html.Div([
                html.H4("¿Qué significan los parámetros?", style={'font-size': '14px', 'margin-top': '20px'}),
                html.P("• β = 0.3: cada infectado contagia 0.3 personas/día", style={'font-size': '12px', 'margin': '3px 0'}),
                html.P("• γ = 0.1: 10% se recupera cada día (10 días promedio)", style={'font-size': '12px', 'margin': '3px 0'}),
                html.P("• R₀ = β/γ = número reproductivo básico", style={'font-size': '12px', 'margin': '3px 0'}),
                html.Div(id="info-r0", style={'font-weight': 'bold', 'color': 'red', 'margin-top': '10px'})
            ], style={'background': '#f0f8ff', 'padding': '10px', 'border-radius': '5px', 'margin-top': '15px'})

        ])
    ], className="content left"),

    html.Div([
        html.H2("Evolución de la Epidemia", className="title"),
        dcc.Graph(id="grafica-sir", style={'height': '400px', 'width': '100%'}),
        
        html.Div([
            html.H3("Resultados:", style={'font-size': '16px', 'margin-top': '15px'}),
            html.Div(id="resultados-sir", style={'font-size': '14px'})
        ])
    ], className="content right")

], className="page-container")


#### Función del modelo SIR ####
def modelo_sir(y, t, beta, gamma, N):
    """
    Sistema de ecuaciones diferenciales del modelo SIR
    
    y = [S, I, R] - estado actual de la población
    t = tiempo
    beta = tasa de transmisión
    gamma = tasa de recuperación  
    N = población total
    """
    S, I, R = y
    
    # Ecuaciones del modelo SIR
    dS_dt = -beta * S * I / N
    dI_dt = beta * S * I / N - gamma * I
    dR_dt = gamma * I
    
    return [dS_dt, dI_dt, dR_dt]


#### Callback ####
@callback(
    [Output("grafica-sir", "figure"),
     Output("resultados-sir", "children"),
     Output("info-r0", "children")],
    Input("btn-simular", "n_clicks"),
    [State("input-N", "value"),
     State("input-beta", "value"),
     State("input-gamma", "value"),
     State("input-I0", "value"),
     State("input-tiempo", "value")],
    prevent_initial_call=False
)
def simular_sir(n_clicks, N, beta, gamma, I0, tiempo_max):
    
    # Condiciones iniciales
    S0 = N - I0  # Susceptibles iniciales
    R0_inicial = 0  # Recuperados iniciales
    y0 = [S0, I0, R0_inicial]
    
    # Vector de tiempo
    t = np.linspace(0, tiempo_max, tiempo_max * 2)  # 2 puntos por día
    
    # Resolver el sistema de ecuaciones diferenciales
    try:
        solucion = odeint(modelo_sir, y0, t, args=(beta, gamma, N))
        S, I, R = solucion.T  # Separar las soluciones
    except:
        # Si hay error, usar valores constantes
        S = np.full_like(t, S0)
        I = np.full_like(t, I0) 
        R = np.full_like(t, R0_inicial)
    
    # Crear gráfica
    fig = go.Figure()
    
    # Línea de Susceptibles (azul)
    fig.add_trace(go.Scatter(
        x=t, y=S,
        mode='lines',
        name='Susceptibles (S)',
        line=dict(color='blue', width=3),
        hovertemplate='Día %{x:.0f}<br>Susceptibles: %{y:.0f}<extra></extra>'
    ))
    
    # Línea de Infectados (rojo)
    fig.add_trace(go.Scatter(
        x=t, y=I,
        mode='lines',
        name='Infectados (I)',
        line=dict(color='red', width=3),
        hovertemplate='Día %{x:.0f}<br>Infectados: %{y:.0f}<extra></extra>'
    ))
    
    # Línea de Recuperados (verde)
    fig.add_trace(go.Scatter(
        x=t, y=R,
        mode='lines',
        name='Recuperados (R)',
        line=dict(color='green', width=3),
        hovertemplate='Día %{x:.0f}<br>Recuperados: %{y:.0f}<extra></extra>'
    ))
    
    # Configurar el layout
    fig.update_layout(
        title=dict(
            text='<b>Evolución del Modelo SIR</b>',
            x=0.5,
            font=dict(size=18, color='darkblue')
        ),
        xaxis_title='Tiempo (días)',
        yaxis_title='Número de personas',
        paper_bgcolor='lightcyan',
        plot_bgcolor='white',
        font=dict(family='Arial', size=12),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        margin=dict(l=40, r=40, t=80, b=40)
    )
    
    fig.update_xaxes(
        showgrid=True, gridcolor='lightgray',
        zeroline=True, zerolinecolor='black'
    )
    fig.update_yaxes(
        showgrid=True, gridcolor='lightgray',
        zeroline=True, zerolinecolor='black'
    )
    
    # Calcular estadísticas importantes
    pico_infectados = np.max(I)
    dia_pico = t[np.argmax(I)]
    total_recuperados_final = R[-1]
    porcentaje_afectado = (total_recuperados_final / N) * 100
    
    # Número reproductivo básico
    R0 = beta / gamma if gamma > 0 else 0
    
    # Crear texto de resultados
    resultados = [
        html.P(f"• Pico de infectados: {pico_infectados:.0f} personas (día {dia_pico:.0f})"),
        html.P(f"• Total de personas que se enfermaron: {total_recuperados_final:.0f} ({porcentaje_afectado:.1f}%)"),
        html.P(f"• Susceptibles al final: {S[-1]:.0f} personas"),
        html.P(f"• Duración aproximada: {tiempo_max} días simulados")
    ]
    
    # Información sobre R0
    if R0 > 1:
        info_r0 = f"R₀ = {R0:.2f} > 1 → ¡HAY EPIDEMIA!"
        color_r0 = 'red'
    elif R0 == 1:
        info_r0 = f"R₀ = {R0:.2f} = 1 → Equilibrio crítico"
        color_r0 = 'orange'
    else:
        info_r0 = f"R₀ = {R0:.2f} < 1 → No hay epidemia"
        color_r0 = 'green'
    
    info_r0_element = html.P(info_r0, style={'color': color_r0})
    
    return fig, resultados, info_r0_element