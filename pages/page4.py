import dash
from dash import html, dcc, callback, Input, Output, State
import plotly.graph_objects as go
import requests
from datetime import datetime
import pandas as pd

dash.register_page(__name__, path='/covid', name='COVID-19 Dashboard')

layout = html.Div([
    html.Div([
        html.H2("Dashboard COVID-19 Global", className="title"),
        
        html.Div([
            html.Label("Selecciona un país:"),
            dcc.Dropdown(
                id="dropdown-pais",
                options=[
                    {'label': '🌎 Perú', 'value': 'Peru'},
                    {'label': '🇺🇸 Estados Unidos', 'value': 'US'},
                    {'label': '🇪🇸 España', 'value': 'Spain'},
                    {'label': '🇲🇽 México', 'value': 'Mexico'},
                    {'label': '🇦🇷 Argentina', 'value': 'Argentina'},
                    {'label': '🇧🇷 Brasil', 'value': 'Brazil'},
                    {'label': '🇨🇴 Colombia', 'value': 'Colombia'},
                    {'label': '🇨🇱 Chile', 'value': 'Chile'},
                    {'label': '🇮🇹 Italia', 'value': 'Italy'},
                    {'label': '🇫🇷 Francia', 'value': 'France'},
                ],
                value='Peru',
                className="input-field",
                style={'width': '100%'}
            )
        ], className="input-group"),

        html.Div([
            html.Label("Días de histórico:"),
            dcc.Dropdown(
                id="dropdown-dias-covid",
                options=[
                    {'label': '30 días', 'value': 30},
                    {'label': '60 días', 'value': 60},
                    {'label': '90 días', 'value': 90},
                    {'label': 'Todo el histórico', 'value': 'all'},
                ],
                value=90,
                className="input-field",
                style={'width': '100%'}
            )
        ], className="input-group"),

        html.Button("Actualizar Datos", id="btn-actualizar-covid", className="btn-generar"),
        
        html.Div(id="info-actualizado-covid", style={
            'marginTop': '20px',
            'padding': '10px',
            'backgroundColor': '#e8f5e9',
            'borderRadius': '5px',
            'fontSize': '12px',
            'textAlign': 'center'
        })
    ], className="content left"),

    html.Div([
        html.H2("Estadísticas en Tiempo Real", className="title"),
        
        # Cards con información
        html.Div([
            html.Div([
                html.H4("Total Casos", style={'color': '#1976d2', 'marginBottom': '5px', 'fontSize': '14px'}),
                html.H3(id="total-casos", style={'color': '#0d47a1', 'margin': '0', 'fontSize': '22px'})
            ], style={
                'backgroundColor': 'white',
                'padding': '15px',
                'borderRadius': '10px',
                'textAlign': 'center',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'flex': '1',
                'margin': '5px'
            }),
            
            html.Div([
                html.H4("Casos Nuevos Hoy", style={'color': '#f57c00', 'marginBottom': '5px', 'fontSize': '14px'}),
                html.H3(id="casos-nuevos", style={'color': '#e65100', 'margin': '0', 'fontSize': '22px'})
            ], style={
                'backgroundColor': 'white',
                'padding': '15px',
                'borderRadius': '10px',
                'textAlign': 'center',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'flex': '1',
                'margin': '5px'
            }),
            
            html.Div([
                html.H4("Total Muertes", style={'color': '#d32f2f', 'marginBottom': '5px', 'fontSize': '14px'}),
                html.H3(id="total-muertes", style={'color': '#b71c1c', 'margin': '0', 'fontSize': '22px'})
            ], style={
                'backgroundColor': 'white',
                'padding': '15px',
                'borderRadius': '10px',
                'textAlign': 'center',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'flex': '1',
                'margin': '5px'
            }),
            
            html.Div([
                html.H4("Recuperados", style={'color': '#388e3c', 'marginBottom': '5px', 'fontSize': '14px'}),
                html.H3(id="total-recuperados", style={'color': '#1b5e20', 'margin': '0', 'fontSize': '22px'})
            ], style={
                'backgroundColor': 'white',
                'padding': '15px',
                'borderRadius': '10px',
                'textAlign': 'center',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'flex': '1',
                'margin': '5px'
            }),
        ], style={'display': 'flex', 'marginBottom': '20px', 'flexWrap': 'wrap'}),
        
        dcc.Graph(id="grafica-covid", style={"height": "380px", "width": "100%"}),
    ], className="content right")
], className="page-container")


# ==========================================
# FUNCIONES PARA CONECTAR CON LA API
# ==========================================

def obtener_datos_pais(pais):
    """
    Obtiene datos actuales de COVID-19 para un país específico
    API: disease.sh (totalmente gratuita, sin API key necesaria)
    """
    try:
        url = f"https://disease.sh/v3/covid-19/countries/{pais}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Lanza error si status code no es 200
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error obteniendo datos del país: {e}")
        return None


def obtener_historico_pais(pais, dias):
    """
    Obtiene el histórico de casos de COVID-19 para un país
    Parámetros:
        - pais: nombre del país
        - dias: número de días o 'all' para todo el histórico
    """
    try:
        url = f"https://disease.sh/v3/covid-19/historical/{pais}"
        params = {'lastdays': dias}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error obteniendo histórico: {e}")
        return None


def formatear_numero(numero):
    """
    Formatea un número grande con comas para legibilidad
    Ejemplo: 1234567 -> 1,234,567
    """
    if numero is None:
        return "N/A"
    return f"{numero:,}"


# ==========================================
# CALLBACK PRINCIPAL
# ==========================================

@callback(
    [Output("grafica-covid", "figure"),
     Output("total-casos", "children"),
     Output("casos-nuevos", "children"),
     Output("total-muertes", "children"),
     Output("total-recuperados", "children"),
     Output("info-actualizado-covid", "children")],
    [Input("btn-actualizar-covid", "n_clicks"),
     State("dropdown-pais", "value"),
     State("dropdown-dias-covid", "value")],
    prevent_initial_call=False
)
def actualizar_dashboard_covid(n_clicks, pais, dias):
    """
    Callback que actualiza todo el dashboard cuando cambian los inputs
    """
    
    # PASO 1: Obtener datos actuales del país
    datos_actuales = obtener_datos_pais(pais)
    historico = obtener_historico_pais(pais, dias)
    
    # PASO 2: Validar que la API respondió correctamente
    if not datos_actuales or not historico:
        # Crear figura vacía con mensaje de error
        fig = go.Figure()
        fig.add_annotation(
            text="⚠️ Error al conectar con la API.<br>Verifica tu conexión a internet.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="red")
        )
        fig.update_layout(
            paper_bgcolor="lightcyan",
            plot_bgcolor="white"
        )
        return fig, "N/A", "N/A", "N/A", "N/A", "❌ Error al cargar datos"
    
    # PASO 3: Extraer datos actuales
    total_casos = datos_actuales.get('cases', 0)
    casos_hoy = datos_actuales.get('todayCases', 0)
    total_muertes = datos_actuales.get('deaths', 0)
    total_recuperados = datos_actuales.get('recovered', 0)
    
    # PASO 4: Formatear números para mostrar
    total_casos_texto = formatear_numero(total_casos)
    casos_hoy_texto = f"+{formatear_numero(casos_hoy)}"
    total_muertes_texto = formatear_numero(total_muertes)
    total_recuperados_texto = formatear_numero(total_recuperados)
    
    # PASO 5: Procesar datos históricos
    timeline = historico.get('timeline', {})
    casos_historicos = timeline.get('cases', {})
    muertes_historicas = timeline.get('deaths', {})
    
    # Convertir diccionarios a listas
    fechas = list(casos_historicos.keys())
    valores_casos = list(casos_historicos.values())
    valores_muertes = list(muertes_historicas.values())
    
    # Convertir fechas de string a datetime
    fechas_dt = [datetime.strptime(fecha, '%m/%d/%y') for fecha in fechas]
    
    # PASO 6: Crear la gráfica con Plotly
    fig = go.Figure()
    
    # Línea de casos totales
    fig.add_trace(go.Scatter(
        x=fechas_dt,
        y=valores_casos,
        mode='lines',
        name='Casos Totales',
        line=dict(color='#1976d2', width=2.5),
        fill='tozeroy',
        fillcolor='rgba(25, 118, 210, 0.1)',
        hovertemplate='<b>Fecha:</b> %{x|%d/%m/%Y}<br>' +
                      '<b>Casos:</b> %{y:,.0f}<br>' +
                      '<extra></extra>'
    ))
    
    # Línea de muertes (en eje secundario)
    fig.add_trace(go.Scatter(
        x=fechas_dt,
        y=valores_muertes,
        mode='lines',
        name='Muertes Totales',
        line=dict(color='#d32f2f', width=2, dash='dash'),
        yaxis='y2',
        hovertemplate='<b>Fecha:</b> %{x|%d/%m/%Y}<br>' +
                      '<b>Muertes:</b> %{y:,.0f}<br>' +
                      '<extra></extra>'
    ))
    
    # PASO 7: Configurar el layout de la gráfica
    fig.update_layout(
        title=dict(
            text=f"<b>Evolución COVID-19 en {pais}</b>",
            x=0.5,
            font=dict(size=16, color="darkblue")
        ),
        xaxis_title="Fecha",
        yaxis_title="Casos Totales",
        yaxis2=dict(
            title="Muertes Totales",
            overlaying='y',
            side='right',
            showgrid=False
        ),
        paper_bgcolor="lightcyan",
        plot_bgcolor="white",
        font=dict(family="Outfit", size=12),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=60, r=60, t=60, b=40)
    )
    
    # Configurar ejes
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightpink',
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor='black'
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightpink',
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor='black'
    )
    
    # PASO 8: Crear mensaje de actualización
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    mensaje = f"✅ Datos actualizados: {ahora}"
    
    # PASO 9: Retornar todos los outputs
    return (
        fig,
        total_casos_texto,
        casos_hoy_texto,
        total_muertes_texto,
        total_recuperados_texto,
        mensaje
    )