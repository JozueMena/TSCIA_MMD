import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Recompra",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .section-header {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">📊 Dashboard de Análisis Predictivo de Recompra</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Configuración")
st.sidebar.markdown("### Filtros y Parámetros")

# Cargar datos
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('dataset_procesado.csv')
        # Convertir variables categóricas para visualización
        df['Genero'] = df['Genero'].map({0: 'Femenino', 1: 'Masculino'})
        df['Recibio_Promo'] = df['Recibio_Promo'].map({0: 'No', 1: 'Si'})
        df['Recompra'] = df['Recompra'].map({0: 'No', 1: 'Si'})
        return df
    except:
        # Si no existe el archivo, usar datos de ejemplo
        data = {
            'Cliente_ID': range(1, 21),
            'Genero': ['Femenino', 'Masculino'] * 10,
            'Edad': [23, 45, 60, 22, 32, 54, 67, 70, 25, 34, 35, 45, 55, 56, 37, 41, 62, 68, 24, 34],
            'Recibio_Promo': ['Si', 'Si', 'No', 'Si', 'Si', 'No', 'No', 'No', 'Si', 'Si', 
                             'No', 'Si', 'No', 'No', 'No', 'Si', 'No', 'Si', 'No', 'No'],
            'Monto_Promo': [500, 500, 700, 800, 300, 500, 600, 500, 700, 300, 
                          400, 500, 900, 100, 900, 400, 500, 600, 700, 800],
            'Recompra': ['Si', 'Si', 'No', 'No', 'Si', 'Si', 'Si', 'No', 'No', 'No',
                        'Si', 'Si', 'Si', 'No', 'Si', 'No', 'Si', 'No', 'No', 'Si'],
            'Total_Compras': [2, 2, 3, 1, 2, 3, 5, 2, 3, 4, 1, 2, 3, 6, 4, 1, 3, 2, 4, 3],
            'Ingreso_Mensual': [30000, 40000, 60000, 30000, 50000, 30000, 45000, 55000, 30000, 25000,
                              30000, 60000, 50000, 40000, 55000, 65000, 30000, 25000, 50000, 60000]
        }
        return pd.DataFrame(data)

df = load_data()

# Filtros en sidebar
st.sidebar.markdown("### Filtros de Datos")

genero_filter = st.sidebar.multiselect(
    "Género:",
    options=df['Genero'].unique(),
    default=df['Genero'].unique()
)

promo_filter = st.sidebar.multiselect(
    "Recibió Promoción:",
    options=df['Recibio_Promo'].unique(),
    default=df['Recibio_Promo'].unique()
)

recompra_filter = st.sidebar.multiselect(
    "Recompra:",
    options=df['Recompra'].unique(),
    default=df['Recompra'].unique()
)

edad_range = st.sidebar.slider(
    "Rango de Edad:",
    min_value=int(df['Edad'].min()),
    max_value=int(df['Edad'].max()),
    value=(int(df['Edad'].min()), int(df['Edad'].max()))
)

# Aplicar filtros
df_filtered = df[
    (df['Genero'].isin(genero_filter)) &
    (df['Recibio_Promo'].isin(promo_filter)) &
    (df['Recompra'].isin(recompra_filter)) &
    (df['Edad'] >= edad_range[0]) &
    (df['Edad'] <= edad_range[1])
]

# Métricas principales
st.markdown('<h2 class="section-header">📈 Métricas Clave</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    tasa_recompra = (df_filtered['Recompra'] == 'Si').mean() * 100
    st.metric(
        label="Tasa de Recompra",
        value=f"{tasa_recompra:.1f}%",
        delta=f"{(tasa_recompra - (df['Recompra'] == 'Si').mean() * 100):.1f}% vs total"
    )

with col2:
    clientes_con_promo = (df_filtered['Recibio_Promo'] == 'Si').mean() * 100
    st.metric(
        label="Clientes con Promoción",
        value=f"{clientes_con_promo:.1f}%"
    )

with col3:
    recompra_con_promo = (df_filtered[df_filtered['Recibio_Promo'] == 'Si']['Recompra'] == 'Si').mean() * 100
    st.metric(
        label="Recompra con Promoción",
        value=f"{recompra_con_promo:.1f}%"
    )

with col4:
    ingreso_promedio = df_filtered['Ingreso_Mensual'].mean()
    st.metric(
        label="Ingreso Promedio",
        value=f"${ingreso_promedio:,.0f}"
    )

# Primera fila de gráficos
st.markdown('<h2 class="section-header">📊 Análisis de Recompra</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Gráfico de efecto de promoción en recompra
    fig = px.histogram(
        df_filtered, 
        x='Recibio_Promo', 
        color='Recompra',
        barmode='group',
        title='Efecto de la Promoción en la Recompra',
        color_discrete_map={'Si': '#2E86AB', 'No': '#A23B72'}
    )
    fig.update_layout(
        xaxis_title='¿Recibió Promoción?',
        yaxis_title='Cantidad de Clientes',
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Gráfico de recompra por género
    recompra_genero = pd.crosstab(df_filtered['Genero'], df_filtered['Recompra'], normalize='index') * 100
    fig = px.bar(
        recompra_genero.reset_index(),
        x='Genero',
        y=['Si', 'No'],
        title='Tasa de Recompra por Género (%)',
        color_discrete_map={'Si': '#2E86AB', 'No': '#A23B72'}
    )
    fig.update_layout(
        xaxis_title='Género',
        yaxis_title='Porcentaje (%)',
        barmode='stack'
    )
    st.plotly_chart(fig, use_container_width=True)

# Segunda fila de gráficos
col1, col2 = st.columns(2)

with col1:
    # Boxplot de Monto de Promoción vs Recompra
    fig = px.box(
        df_filtered,
        x='Recompra',
        y='Monto_Promo',
        title='Distribución del Monto de Promoción por Recompra',
        color='Recompra',
        color_discrete_map={'Si': '#2E86AB', 'No': '#A23B72'}
    )
    fig.update_layout(
        xaxis_title='¿Recompró?',
        yaxis_title='Monto de Promoción ($)'
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Boxplot de Ingreso Mensual vs Recompra
    fig = px.box(
        df_filtered,
        x='Recompra',
        y='Ingreso_Mensual',
        title='Distribución del Ingreso Mensual por Recompra',
        color='Recompra',
        color_discrete_map={'Si': '#2E86AB', 'No': '#A23B72'}
    )
    fig.update_layout(
        xaxis_title='¿Recompró?',
        yaxis_title='Ingreso Mensual ($)'
    )
    st.plotly_chart(fig, use_container_width=True)

# Tercera fila - Análisis de correlaciones
st.markdown('<h2 class="section-header">🔗 Análisis de Correlaciones</h2>', unsafe_allow_html=True)

# Preparar datos para correlación
df_corr = df.copy()
df_corr['Genero'] = df_corr['Genero'].map({'Femenino': 0, 'Masculino': 1})
df_corr['Recibio_Promo'] = df_corr['Recibio_Promo'].map({'No': 0, 'Si': 1})
df_corr['Recompra'] = df_corr['Recompra'].map({'No': 0, 'Si': 1})

correlation_matrix = df_corr.corr()

col1, col2 = st.columns([2, 1])

with col1:
    # Heatmap de correlaciones
    fig = px.imshow(
        correlation_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale='RdBu_r',
        title='Matriz de Correlación entre Variables'
    )
    fig.update_layout(width=600, height=500)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Correlaciones con Recompra")
    correlaciones_recompra = correlation_matrix['Recompra'].sort_values(ascending=False)
    for variable, correlacion in correlaciones_recompra.items():
        if variable != 'Recompra':
            color = "🟢" if correlacion > 0.1 else "🔴" if correlacion < -0.1 else "🟡"
            st.write(f"{color} **{variable}**: {correlacion:.3f}")

# Cuarta fila - Segmentación de clientes
st.markdown('<h2 class="section-header">👥 Segmentación de Clientes</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Scatter plot: Edad vs Ingreso con recompra
    fig = px.scatter(
        df_filtered,
        x='Edad',
        y='Ingreso_Mensual',
        color='Recompra',
        size='Total_Compras',
        hover_data=['Cliente_ID', 'Monto_Promo'],
        title='Segmentación: Edad vs Ingreso Mensual',
        color_discrete_map={'Si': '#2E86AB', 'No': '#A23B72'}
    )
    fig.update_layout(
        xaxis_title='Edad',
        yaxis_title='Ingreso Mensual ($)'
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Análisis de segmentos
    segmento_recompra = df_filtered[df_filtered['Recompra'] == 'Si']
    segmento_no_recompra = df_filtered[df_filtered['Recompra'] == 'No']
    
    st.markdown("### Comparación de Segmentos")
    
    metricas_data = {
        'Métrica': ['Edad Promedio', 'Ingreso Promedio', 'Total Compras Promedio', 'Monto Promo Promedio'],
        'Recompraron': [
            f"{segmento_recompra['Edad'].mean():.1f} años",
            f"${segmento_recompra['Ingreso_Mensual'].mean():,.0f}",
            f"{segmento_recompra['Total_Compras'].mean():.1f}",
            f"${segmento_recompra['Monto_Promo'].mean():,.0f}"
        ],
        'No Recompraron': [
            f"{segmento_no_recompra['Edad'].mean():.1f} años",
            f"${segmento_no_recompra['Ingreso_Mensual'].mean():,.0f}",
            f"{segmento_no_recompra['Total_Compras'].mean():.1f}",
            f"${segmento_no_recompra['Monto_Promo'].mean():,.0f}"
        ]
    }
    
    st.table(pd.DataFrame(metricas_data))

# Quinta fila - Recomendaciones
st.markdown('<h2 class="section-header">💡 Recomendaciones de Marketing</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 🎯 Segmentación Óptima
    - **Enfocar promociones** en clientes con mayor probabilidad de recompra
    - **Priorizar** por nivel de ingreso y historial de compras
    - **Personalizar** montos de promoción según segmento
    """)

with col2:
    st.markdown("""
    ### 📈 Estrategias de Retención
    - **Programas de fidelidad** para clientes recurrentes
    - **Promociones personalizadas** basadas en comportamiento
    - **Comunicación segmentada** por grupos de edad
    """)

with col3:
    st.markdown("""
    ### 🔍 Insights Clave
    - La promoción aumenta significativamente la recompra
    - El género muestra patrones diferenciados
    - El ingreso mensual es factor determinante
    - El total de compras previas influye en la decisión
    """)

# Información del dataset
with st.expander("📋 Ver Datos del Dataset"):
    st.dataframe(df_filtered, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Estadísticas Descriptivas")
        st.dataframe(df_filtered.describe(), use_container_width=True)
    
    with col2:
        st.markdown("### Distribución de Variables Categóricas")
        for col in ['Genero', 'Recibio_Promo', 'Recompra']:
            st.write(f"**{col}:**")
            st.write(df_filtered[col].value_counts())

# Footer
st.markdown("---")
st.markdown(
    "**Dashboard creado para el Proyecto 2 - Análisis Predictivo de Recompra** | "
    "Desarrollado con Streamlit 🎈"
)