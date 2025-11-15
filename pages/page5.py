import dash
from dash import html, dcc, callback, Input, Output, State
import plotly.graph_objects as go
import requests
from datetime import datetime

dash.register_page(__name__, path='/clima', name='Dashboard Clima')

layout = html.Div([
    html.Div([
        html.H2("Dashboard de Clima en Tiempo Real", className="title"),
        
        html.Div([
            html.Label("Selecciona una ciudad:"),
            dcc.Dropdown(
                id="dropdown-ciudad",
                options=[
                    {'label': '🏛️ Lima, Perú', 'value': 'lima'},
                    {'label': '🗽 Nueva York, USA', 'value': 'nueva_york'},
                    {'label': '🌆 Madrid, España', 'value': 'madrid'},
                    {'label': '🌴 Ciudad de México', 'value': 'mexico'},
                    {'label': '🏖️ Buenos Aires, Argentina', 'value': 'buenos_aires'},
                    {'label': '🌃 São Paulo, Brasil', 'value': 'sao_paulo'},
                    {'label': '🗼 París, Francia', 'value': 'paris'},
                    {'label': '🏰 Londres, Inglaterra', 'value': 'londres'},
                    {'label': '🎌 Tokio, Japón', 'value': 'tokio'},
                    {'label': '🕌 Dubái, EAU', 'value': 'dubai'},
                ],
                value='lima',
                className="input-field",
                style={'width': '100%'}
            )
        ], className="input-group"),

        html.Div([
            html.Label("Tipo de visualización:"),
            dcc.RadioItems(
                id="radio-tipo-grafica",
                options=[
                    {'label': ' Temperatura', 'value': 'temperatura'},
                    {'label': ' Precipitación', 'value': 'precipitacion'},
                    {'label': ' Viento', 'value': 'viento'},
                ],
                value='temperatura',
                className="input-field",
                style={'display': 'flex', 'flexDirection': 'column', 'gap': '10px'}
            )
        ], className="input-group"),

        html.Button("Actualizar Clima", id="btn-actualizar-clima", className="btn-generar"),
        
        html.Div(id="info-actualizado-clima", style={
            'marginTop': '20px',
            'padding': '10px',
            'backgroundColor': '#e3f2fd',
            'borderRadius': '5px',
            'fontSize': '12px',
            'textAlign': 'center'
        })
    ], className="content left"),

    html.Div([
        html.H2("Pronóstico de 7 Días", className="title"),
        
        # Cards con información actual
        html.Div([
            html.Div([
                html.H4("Temperatura", style={'color': '#ff6f00', 'marginBottom': '5px', 'fontSize': '14px'}),
                html.H3(id="temp-actual", style={'color': '#e65100', 'margin': '0', 'fontSize': '26px'})
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
                html.H4("Humedad", style={'color': '#0288d1', 'marginBottom': '5px', 'fontSize': '14px'}),
                html.H3(id="humedad-actual", style={'color': '#01579b', 'margin': '0', 'fontSize': '26px'})
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
                html.H4("Viento", style={'color': '#00897b', 'marginBottom': '5px', 'fontSize': '14px'}),
                html.H3(id="viento-actual", style={'color': '#004d40', 'margin': '0', 'fontSize': '26px'})
            ], style={
                'backgroundColor': 'white',
                'padding': '15px',
                'borderRadius': '10px',
                'textAlign': 'center',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'flex': '1',
                'margin': '5px'
            }),
        ], style={'display': 'flex', 'marginBottom': '20px'}),
        
        dcc.Graph(id="grafica-clima", style={"height": "380px", "width": "100%"}),
    ], className="content right")
], className="page-container")


# ==========================================
# COORDENADAS DE LAS CIUDADES
# ==========================================

CIUDADES = {
    'lima': {'lat': -12.0464, 'lon': -77.0428, 'nombre': 'Lima'},
    'nueva_york': {'lat': 40.7128, 'lon': -74.0060, 'nombre': 'Nueva York'},
    'madrid': {'lat': 40.4168, 'lon': -3.7038, 'nombre': 'Madrid'},
    'mexico': {'lat': 19.4326, 'lon': -99.1332, 'nombre': 'Ciudad de México'},
    'buenos_aires': {'lat': -34.6037, 'lon': -58.3816, 'nombre': 'Buenos Aires'},
    'sao_paulo': {'lat': -23.5505, 'lon': -46.6333, 'nombre': 'São Paulo'},
    'paris': {'lat': 48.8566, 'lon': 2.3522, 'nombre': 'París'},
    'londres': {'lat': 51.5074, 'lon': -0.1278, 'nombre': 'Londres'},
    'tokio': {'lat': 35.6762, 'lon': 139.6503, 'nombre': 'Tokio'},
    'dubai': {'lat': 25.2048, 'lon': 55.2708, 'nombre': 'Dubái'},
}


# ==========================================
# FUNCIONES PARA CONECTAR CON LA API
# ==========================================

def obtener_datos_clima(ciudad_key):
    """
    Obtiene datos del clima usando Open-Meteo API
    API totalmente gratuita, sin necesidad de registro o API key
    
    Documentación: https://open-meteo.com/
    """
    try:
        ciudad = CIUDADES[ciudad_key]
        
        # URL de la API de Open-Meteo
        url = "https://api.open-meteo.com/v1/forecast"
        
        # Parámetros de la petición
        params = {
            'latitude': ciudad['lat'],
            'longitude': ciudad['lon'],
            'hourly': 'temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m',
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max',
            'timezone': 'auto',
            'forecast_days': 7
        }
        
        # Hacer la petición GET
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Lanza error si hay problema
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener datos del clima: {e}")
        return None


# ==========================================
# CALLBACK PRINCIPAL
# ==========================================

@callback(
    [Output("grafica-clima", "figure"),
     Output("temp-actual", "children"),
     Output("humedad-actual", "children"),
     Output("viento-actual", "children"),
     Output("info-actualizado-clima", "children")],
    [Input("btn-actualizar-clima", "n_clicks"),
     State("dropdown-ciudad", "value"),
     State("radio-tipo-grafica", "value")],
    prevent_initial_call=False
)
def actualizar_dashboard_clima(n_clicks, ciudad_key, tipo_grafica):
    """
    Actualiza el dashboard con datos del clima en tiempo real
    """
    
    # PASO 1: Obtener datos de la API
    datos = obtener_datos_clima(ciudad_key)
    
    # PASO 2: Validar que la API respondió
    if not datos:
        fig = go.Figure()
        fig.add_annotation(
            text="⚠️ Error al conectar con la API del clima.<br>Intenta nuevamente.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="red")
        )
        fig.update_layout(paper_bgcolor="lightcyan", plot_bgcolor="white")
        return fig, "N/A", "N/A", "N/A", "❌ Error al cargar datos"
    
    # PASO 3: Extraer datos actuales (primera hora del pronóstico)
    temp_actual = datos['hourly']['temperature_2m'][0]
    humedad_actual = datos['hourly']['relative_humidity_2m'][0]
    viento_actual = datos['hourly']['wind_speed_10m'][0]
    
    # Formatear valores actuales
    temp_texto = f"{temp_actual:.1f}°C"
    humedad_texto = f"{humedad_actual:.0f}%"
    viento_texto = f"{viento_actual:.1f} km/h"
    
    # PASO 4: Extraer datos diarios para la gráfica
    fechas = datos['daily']['time']
    fechas_dt = [datetime.strptime(fecha, '%Y-%m-%d') for fecha in fechas]
    
    # PASO 5: Crear gráfica según el tipo seleccionado
    fig = go.Figure()
    
    nombre_ciudad = CIUDADES[ciudad_key]['nombre']
    
    if tipo_grafica == 'temperatura':
        temp_max = datos['daily']['temperature_2m_max']
        temp_min = datos['daily']['temperature_2m_min']
        
        fig.add_trace(go.Scatter(
            x=fechas_dt,
            y=temp_max,
            mode='lines+markers',
            name='Temp. Máxima',
            line=dict(color='#ff6f00', width=2.5),
            marker=dict(size=8),
            hovertemplate='<b>Fecha:</b> %{x|%d/%m}<br>' +
                          '<b>Temp. Máx:</b> %{y:.1f}°C<br>' +
                          '<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=fechas_dt,
            y=temp_min,
            mode='lines+markers',
            name='Temp. Mínima',
            line=dict(color='#0288d1', width=2.5),
            marker=dict(size=8),
            hovertemplate='<b>Fecha:</b> %{x|%d/%m}<br>' +
                          '<b>Temp. Mín:</b> %{y:.1f}°C<br>' +
                          '<extra></extra>'
        ))
        
        titulo = f"<b>Temperatura en {nombre_ciudad} - Próximos 7 días</b>"
        yaxis_title = "Temperatura (°C)"
        
    elif tipo_grafica == 'precipitacion':
        precipitacion = datos['daily']['precipitation_sum']
        
        fig.add_trace(go.Bar(
            x=fechas_dt,
            y=precipitacion,
            name='Precipitación',
            marker_color='#0288d1',
            hovertemplate='<b>Fecha:</b> %{x|%d/%m}<br>' +
                          '<b>Lluvia:</b> %{y:.1f} mm<br>' +
                          '<extra></extra>'
        ))
        
        titulo = f"<b>Precipitación en {nombre_ciudad} - Próximos 7 días</b>"
        yaxis_title = "Precipitación (mm)"
        
    else:  # viento
        viento_max = datos['daily']['wind_speed_10m_max']
        
        fig.add_trace(go.Scatter(
            x=fechas_dt,
            y=viento_max,
            mode='lines+markers',
            name='Velocidad del Viento',
            line=dict(color='#00897b', width=2.5),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(0, 137, 123, 0.1)',
            hovertemplate='<b>Fecha:</b> %{x|%d/%m}<br>' +
                          '<b>Viento:</b> %{y:.1f} km/h<br>' +
                          '<extra></extra>'
        ))
        
        titulo = f"<b>Viento en {nombre_ciudad} - Próximos 7 días</b>"
        yaxis_title = "Velocidad (km/h)"
    
    # PASO 6: Configurar layout
    fig.update_layout(
        title=dict(
            text=titulo,
            x=0.5,
            font=dict(size=16, color="darkblue")
        ),
        xaxis_title="Fecha",
        yaxis_title=yaxis_title,
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
        margin=dict(l=60, r=40, t=60, b=40)
    )
    
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
    
    # PASO 7: Mensaje de actualización
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    mensaje = f"✅ Clima actualizado: {ahora} - {nombre_ciudad}"
    
    return fig, temp_texto, humedad_texto, viento_texto, mensaje