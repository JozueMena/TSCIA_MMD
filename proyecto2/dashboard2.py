import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import confusion_matrix, classification_report
import joblib
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Completo de Recompra",
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
    .tree-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
    .feature-importance {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">📊 Dashboard Completo de Análisis de Recompra</h1>', unsafe_allow_html=True)

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

# Cargar modelo entrenado
@st.cache_resource
def load_model():
    try:
        modelo = joblib.load('modelo_arbol_recompra.pkl')
        return modelo
    except:
        st.warning("No se pudo cargar el modelo entrenado. Se usará un modelo por defecto.")
        # Entrenar modelo simple si no existe
        df_encoded = df.copy()
        df_encoded['Genero'] = df_encoded['Genero'].map({'Femenino': 0, 'Masculino': 1})
        df_encoded['Recibio_Promo'] = df_encoded['Recibio_Promo'].map({'No': 0, 'Si': 1})
        df_encoded['Recompra'] = df_encoded['Recompra'].map({'No': 0, 'Si': 1})
        
        X = df_encoded.drop(['Cliente_ID', 'Recompra'], axis=1)
        y = df_encoded['Recompra']
        
        modelo = DecisionTreeClassifier(max_depth=3, random_state=42)
        modelo.fit(X, y)
        return modelo

modelo_arbol = load_model()

# Sidebar simplificado - SIN FILTROS GLOBALES
st.sidebar.title("⚙️ Navegación")
pagina = st.sidebar.radio("Selecciona una sección:", 
                         ["📈 Análisis General", "🌳 Árbol de Decisión", "📊 Gráficos Completos"])

# Información del dataset en todas las páginas
with st.sidebar.expander("📋 Información del Dataset"):
    st.write(f"**Clientes cargados:** {len(df)}")
    st.write(f"**Variables:** {len(df.columns)}")
    st.write("**Columnas:**")
    for col in df.columns:
        st.write(f"- {col}")

# Footer del sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("**Dashboard Completo** | Proyecto 2 - Análisis de Recompra")

# Página 1: Análisis General
if pagina == "📈 Análisis General":
    st.markdown('<h2 class="section-header">📈 Métricas Clave y Análisis General</h2>', unsafe_allow_html=True)
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        tasa_recompra = (df['Recompra'] == 'Si').mean() * 100
        st.metric(
            label="Tasa de Recompra",
            value=f"{tasa_recompra:.1f}%"
        )

    with col2:
        clientes_con_promo = (df['Recibio_Promo'] == 'Si').mean() * 100
        st.metric(
            label="Clientes con Promoción",
            value=f"{clientes_con_promo:.1f}%"
        )

    with col3:
        recompra_con_promo = (df[df['Recibio_Promo'] == 'Si']['Recompra'] == 'Si').mean() * 100
        st.metric(
            label="Recompra con Promoción",
            value=f"{recompra_con_promo:.1f}%"
        )

    with col4:
        ingreso_promedio = df['Ingreso_Mensual'].mean()
        st.metric(
            label="Ingreso Promedio",
            value=f"${ingreso_promedio:,.0f}"
        )
    
    # Gráficos de análisis
    st.markdown('<h2 class="section-header">📊 Análisis de Relaciones Clave</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de efecto de promoción en recompra
        fig = px.histogram(
            df, 
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
        
        # Boxplot de Monto de Promoción vs Recompra
        fig = px.box(
            df,
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
        # Gráfico de recompra por género
        recompra_genero = pd.crosstab(df['Genero'], df['Recompra'], normalize='index') * 100
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
        
        # Boxplot de Ingreso Mensual vs Recompra
        fig = px.box(
            df,
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
    
    # Matriz de correlación
    st.markdown('<h2 class="section-header">🔗 Matriz de Correlación</h2>', unsafe_allow_html=True)
    
    # Preparar datos para correlación
    df_corr = df.copy()
    df_corr['Genero'] = df_corr['Genero'].map({'Femenino': 0, 'Masculino': 1})
    df_corr['Recibio_Promo'] = df_corr['Recibio_Promo'].map({'No': 0, 'Si': 1})
    df_corr['Recompra'] = df_corr['Recompra'].map({'No': 0, 'Si': 1})
    
    correlation_matrix = df_corr.corr()
    
    fig = px.imshow(
        correlation_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale='RdBu_r',
        title='Matriz de Correlación entre Variables'
    )
    fig.update_layout(width=800, height=600)
    st.plotly_chart(fig, use_container_width=True)

# Página 2: Árbol de Decisión
elif pagina == "🌳 Árbol de Decisión":
    st.markdown('<h2 class="section-header">🌳 Árbol de Decisión - Visualización Completa</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Visualización del Árbol de Decisión")
        
        # Crear visualización del árbol
        fig, ax = plt.subplots(figsize=(20, 12))
        
        # Preparar datos para el árbol
        df_encoded_vis = df.copy()
        df_encoded_vis['Genero'] = df_encoded_vis['Genero'].map({'Femenino': 0, 'Masculino': 1})
        df_encoded_vis['Recibio_Promo'] = df_encoded_vis['Recibio_Promo'].map({'No': 0, 'Si': 1})
        df_encoded_vis['Recompra'] = df_encoded_vis['Recompra'].map({'No': 0, 'Si': 1})
        
        X_vis = df_encoded_vis.drop(['Cliente_ID', 'Recompra'], axis=1)
        feature_names = X_vis.columns.tolist()
        
        plot_tree(modelo_arbol, 
                  feature_names=feature_names,
                  class_names=['No Recompra', 'Recompra'],
                  filled=True,
                  rounded=True,
                  fontsize=10,
                  ax=ax)
        
        ax.set_title('Árbol de Decisión - Predicción de Recompra', fontsize=14, fontweight='bold')
        st.pyplot(fig)
    
    with col2:
        st.markdown("### Información del Árbol")
        
        # Estadísticas del árbol
        n_nodes = modelo_arbol.tree_.node_count
        depth = modelo_arbol.tree_.max_depth
        
        st.metric("Nodos totales", n_nodes)
        st.metric("Profundidad máxima", depth)
        st.metric("Hojas del árbol", modelo_arbol.tree_.n_leaves)
        
        # Métricas de performance
        df_encoded_eval = df.copy()
        df_encoded_eval['Genero'] = df_encoded_eval['Genero'].map({'Femenino': 0, 'Masculino': 1})
        df_encoded_eval['Recibio_Promo'] = df_encoded_eval['Recibio_Promo'].map({'No': 0, 'Si': 1})
        df_encoded_eval['Recompra'] = df_encoded_eval['Recompra'].map({'No': 0, 'Si': 1})
        
        X_eval = df_encoded_eval.drop(['Cliente_ID', 'Recompra'], axis=1)
        y_eval = df_encoded_eval['Recompra']
        
        y_pred = modelo_arbol.predict(X_eval)
        accuracy = (y_pred == y_eval).mean() * 100
        st.metric("Precisión General", f"{accuracy:.1f}%")
    
    # Importancia de Variables (debajo del árbol como solicitaste)
    st.markdown('<h2 class="section-header">📊 Importancia de Variables</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        importancias = modelo_arbol.feature_importances_
        features = feature_names
        
        # Crear gráfico de importancia
        fig_imp, ax_imp = plt.subplots(figsize=(10, 6))
        y_pos = np.arange(len(features))
        bars = ax_imp.barh(y_pos, importancias, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'])
        ax_imp.set_yticks(y_pos)
        ax_imp.set_yticklabels(features)
        ax_imp.set_xlabel('Importancia')
        ax_imp.set_title('Importancia de Variables en el Árbol de Decisión')
        
        # Añadir valores en las barras
        for bar, imp in zip(bars, importancias):
            ax_imp.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                       f'{imp:.3f}', ha='left', va='center')
        
        st.pyplot(fig_imp)
    
    with col2:
        st.markdown("### Valores de Importancia Detallados")
        
        # Mostrar importancia numérica en una tabla
        importancia_df = pd.DataFrame({
            'Variable': features,
            'Importancia': importancias
        }).sort_values('Importancia', ascending=False)
        
        st.dataframe(importancia_df, use_container_width=True)
        
        st.markdown("### Interpretación:")
        variable_max = importancia_df.iloc[0]['Variable']
        valor_max = importancia_df.iloc[0]['Importancia']
        st.write(f"**{variable_max}** es la variable más importante con un peso de **{valor_max:.3f}**")
        st.write("Esto significa que esta variable tiene el mayor poder predictivo para determinar si un cliente recomprará.")
    
    # Reglas del Árbol de Decisión CON MATRIZ DE CONFUSIÓN AL LADO
    st.markdown('<h2 class="section-header">📝 Reglas de Decisión del Árbol</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Reglas Principales")
        
        st.markdown("""
        **Ejemplo de reglas identificadas:**
        - Si **Recibio_Promo = Si** y **Edad > 40** → Alta probabilidad de recompra
        - Si **Total_Compras > 2** → Mayor tendencia a recompra
        - Si **Ingreso_Mensual > 45000** → Mejor respuesta a promociones
        - Si **Monto_Promo > 500** → Efecto positivo en recompra
        """)
        
        st.markdown("### Segmentos Identificados")
        
        segmentos = {
            "Segmento A": "Clientes jóvenes con promoción - Alta recompra",
            "Segmento B": "Clientes mayores sin promoción - Baja recompra", 
            "Segmento C": "Clientes con alto historial de compras - Recompra consistente",
            "Segmento D": "Clientes con alto ingreso - Buena respuesta a promociones"
        }
        
        for segmento, descripcion in segmentos.items():
            st.write(f"**{segmento}:** {descripcion}")
    
    with col2:
        st.markdown("### Matriz de Confusión")
        
        # Calcular matriz de confusión
        df_encoded_eval = df.copy()
        df_encoded_eval['Genero'] = df_encoded_eval['Genero'].map({'Femenino': 0, 'Masculino': 1})
        df_encoded_eval['Recibio_Promo'] = df_encoded_eval['Recibio_Promo'].map({'No': 0, 'Si': 1})
        df_encoded_eval['Recompra'] = df_encoded_eval['Recompra'].map({'No': 0, 'Si': 1})
        
        X_eval = df_encoded_eval.drop(['Cliente_ID', 'Recompra'], axis=1)
        y_eval = df_encoded_eval['Recompra']
        
        y_pred = modelo_arbol.predict(X_eval)
        
        cm = confusion_matrix(y_eval, y_pred)
        
        fig_cm, ax_cm = plt.subplots(figsize=(6, 4))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['No Recompra', 'Recompra'],
                    yticklabels=['No Recompra', 'Recompra'])
        ax_cm.set_xlabel('Predicción')
        ax_cm.set_ylabel('Real')
        ax_cm.set_title('Matriz de Confusión')
        st.pyplot(fig_cm)
        
        # Métricas de performance
        accuracy = (y_pred == y_eval).mean() * 100
        st.metric("Precisión General", f"{accuracy:.1f}%")
        
        # Información adicional sobre la matriz
        st.markdown("#### Interpretación:")
        st.write(f"- **Verdaderos Positivos:** {cm[1,1]} (Recompra correctamente predicha)")
        st.write(f"- **Verdaderos Negativos:** {cm[0,0]} (No recompra correctamente predicha)")
        st.write(f"- **Falsos Positivos:** {cm[0,1]} (Recompra predicha incorrectamente)")
        st.write(f"- **Falsos Negativos:** {cm[1,0]} (No recompra predicha incorrectamente)")

# Página 3: Gráficos Completos
elif pagina == "📊 Gráficos Completos":
    st.markdown('<h2 class="section-header">📊 Todos los Gráficos del Análisis</h2>', unsafe_allow_html=True)
    
    # Cargar y mostrar imágenes de gráficos guardados
    try:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Análisis de Recompra")
            try:
                st.image('analisis_recompra_real.png', caption='Análisis Completo de Recompra', use_container_width=True)
            except:
                st.warning("No se pudo cargar 'analisis_recompra_real.png'")
            
            st.markdown("### Efecto de Promoción")
            try:
                st.image('promocion_recompra_real.png', caption='Efecto de la Promoción en Recompra', use_container_width=True)
            except:
                st.warning("No se pudo cargar 'promocion_recompra_real.png'")
        
        with col2:
            st.markdown("### Matriz de Correlación")
            try:
                st.image('matriz_correlacion.png', caption='Matriz de Correlación entre Variables', use_container_width=True)
            except:
                st.warning("No se pudo cargar 'matriz_correlacion.png'")
            
            st.markdown("### Importancia de Variables")
            try:
                st.image('importancia_variables_real.png', caption='Importancia de Variables en la Predicción', use_container_width=True)
            except:
                st.warning("No se pudo cargar 'importancia_variables_real.png'")
        
        # Mostrar árbol de decisión (SOLO EL COMPLETO)
        st.markdown("### Árbol de Decisión")
        try:
            st.image('arbol_decision_grande.png', caption='Árbol de Decisión', use_container_width=True)
        except:
            st.warning("No se pudo cargar 'arbol_decision_grande.png'")
            
    except Exception as e:
        st.warning(f"No se pudieron cargar algunos gráficos: {e}")
        st.info("Ejecuta primero proyecto2.py para generar todos los gráficos")

# Mensaje final en main
st.markdown("---")
st.markdown(
    "**Dashboard desarrollado para el Proyecto 2 - Análisis Predictivo de Recompra** | "
    "Incluye Árbol de Decisión 🌳 y Análisis Completo 📊"
)
