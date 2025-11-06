import streamlit as st
import pandas as pd
from io import StringIO
import random
from datetime import datetime, timedelta

st.set_page_config(page_title="Editor de CSV", page_icon="📊", layout="wide")

# ==============================
# FUNCIONES DE GENERACIÓN
# ==============================
def generar_nombres(n):
    nombres = ["Juan", "María", "Carlos", "Ana", "Pedro", "Laura", "Diego", "Sofía", 
               "Miguel", "Lucía", "Fernando", "Valentina", "Roberto", "Camila", "Jorge",
               "Isabella", "Luis", "Martina", "Antonio", "Victoria"]
    apellidos = ["García", "Rodríguez", "Martínez", "López", "González", "Pérez", 
                 "Sánchez", "Ramírez", "Torres", "Flores", "Rivera", "Gómez", "Díaz",
                 "Cruz", "Morales", "Reyes", "Jiménez", "Hernández", "Ruiz", "Vargas"]
    return [f"{random.choice(nombres)} {random.choice(apellidos)}" for _ in range(n)]

def generar_emails(n):
    dominios = ["gmail.com", "hotmail.com", "yahoo.com", "outlook.com", "empresa.com"]
    nombres = ["user", "contact", "info", "admin", "support", "juan", "maria", "carlos"]
    return [f"{random.choice(nombres)}{random.randint(1, 999)}@{random.choice(dominios)}" for _ in range(n)]

def generar_telefonos(n):
    return [f"+54 9 11 {random.randint(1000, 9999)}-{random.randint(1000, 9999)}" for _ in range(n)]

def generar_fechas(n, inicio="2020-01-01", fin="2024-12-31"):
    start = datetime.strptime(inicio, "%Y-%m-%d")
    end = datetime.strptime(fin, "%Y-%m-%d")
    delta = end - start
    return [(start + timedelta(days=random.randint(0, delta.days))).strftime("%Y-%m-%d") for _ in range(n)]

def generar_numeros(n, minimo=1, maximo=100, decimales=False):
    if decimales:
        return [round(random.uniform(minimo, maximo), 2) for _ in range(n)]
    return [random.randint(minimo, maximo) for _ in range(n)]

def generar_ciudades(n):
    ciudades = ["Buenos Aires", "Córdoba", "Rosario", "Mendoza", "La Plata", "San Miguel de Tucumán",
                "Mar del Plata", "Salta", "Santa Fe", "San Juan", "Resistencia", "Neuquén",
                "Posadas", "Bahía Blanca", "Paraná", "San Salvador de Jujuy"]
    return [random.choice(ciudades) for _ in range(n)]

def generar_productos(n):
    productos = ["Laptop", "Mouse", "Teclado", "Monitor", "Auriculares", "Webcam", "Micrófono",
                 "Tablet", "Smartphone", "Impresora", "Scanner", "Router", "Disco Duro", "USB",
                 "Cable HDMI", "Adaptador", "Cargador", "Batería", "Mousepad", "Soporte"]
    return [random.choice(productos) for _ in range(n)]

def generar_booleanos(n):
    return [random.choice([True, False]) for _ in range(n)]

def generar_lorem(n):
    palabras = ["lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
                "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
                "magna", "aliqua"]
    return [" ".join(random.choices(palabras, k=random.randint(3, 8))).capitalize() + "." for _ in range(n)]

# ==============================
# FUNCIONES DE ANÁLISIS DE DATOS
# ==============================
def analizar_datos(df):
    """Analiza el dataframe y devuelve estadísticas"""
    analysis = {}
    
    # Información básica
    analysis['filas'] = len(df)
    analysis['columnas'] = len(df.columns)
    analysis['valores_faltantes'] = df.isnull().sum().sum()
    analysis['memoria_mb'] = round(df.memory_usage(deep=True).sum() / 1024**2, 2)
    
    # Análisis por columna
    analysis['columnas_info'] = {}
    for col in df.columns:
        col_info = {
            'tipo': str(df[col].dtype),
            'valores_unicos': df[col].nunique(),
            'valores_faltantes': df[col].isnull().sum(),
            'porcentaje_faltantes': round((df[col].isnull().sum() / len(df)) * 100, 2)
        }
        
        # Estadísticas para columnas numéricas
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info.update({
                'min': round(df[col].min(), 2),
                'max': round(df[col].max(), 2),
                'media': round(df[col].mean(), 2),
                'mediana': round(df[col].median(), 2),
                'desviacion_std': round(df[col].std(), 2)
            })
        
        analysis['columnas_info'][col] = col_info
    
    return analysis

# ==============================
# INTERFAZ PRINCIPAL
# ==============================
st.title("📊 Editor de Archivos CSV")
st.markdown("Sube uno o múltiples archivos CSV, edítalos y descárgalos en CSV o JSON.")

# Inicializar session_state para múltiples archivos
if 'all_dataframes' not in st.session_state:
    st.session_state.all_dataframes = {}
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'editing_mode' not in st.session_state:
    st.session_state.editing_mode = False
if 'delete_mode' not in st.session_state:
    st.session_state.delete_mode = False

# Uploader para múltiples archivos
uploaded_files = st.file_uploader(
    "Selecciona uno o múltiples archivos CSV", 
    type=['csv'], 
    accept_multiple_files=True
)

# Procesar archivos subidos
if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name not in st.session_state.all_dataframes:
            try:
                df = pd.read_csv(uploaded_file)
                st.session_state.all_dataframes[uploaded_file.name] = {
                    'dataframe': df,
                    'edited': False
                }
                st.success(f"✅ Archivo cargado: {uploaded_file.name} ({len(df)} filas, {len(df.columns)} columnas)")
            except Exception as e:
                st.error(f"❌ Error al procesar {uploaded_file.name}: {str(e)}")
    
    # Selector de archivo actual
    if st.session_state.all_dataframes:
        file_names = list(st.session_state.all_dataframes.keys())
        if st.session_state.current_file is None:
            st.session_state.current_file = file_names[0]
        
        selected_file = st.selectbox(
            "Selecciona el archivo a editar:",
            options=file_names,
            index=file_names.index(st.session_state.current_file) if st.session_state.current_file in file_names else 0
        )
        st.session_state.current_file = selected_file
        
        # Obtener el dataframe actual
        current_data = st.session_state.all_dataframes[selected_file]
        df = current_data['dataframe']
        
        # ANÁLISIS DE DATOS
        st.subheader("📈 Análisis de Datos")
        analisis = analizar_datos(df)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Filas totales", analisis['filas'])
        with col2:
            st.metric("Columnas totales", analisis['columnas'])
        with col3:
            st.metric("Valores faltantes", analisis['valores_faltantes'])
        with col4:
            st.metric("Memoria (MB)", analisis['memoria_mb'])
        
        # Mostrar análisis por columnas
        with st.expander("📋 Detalles por columna"):
            for col, info in analisis['columnas_info'].items():
                st.write(f"**{col}** ({info['tipo']})")
                cols_info = st.columns(5)
                with cols_info[0]:
                    st.metric("Únicos", info['valores_unicos'])
                with cols_info[1]:
                    st.metric("Faltantes", info['valores_faltantes'])
                with cols_info[2]:
                    st.metric("% Faltantes", f"{info['porcentaje_faltantes']}%")
                
                if 'min' in info:
                    with cols_info[3]:
                        st.metric("Mín", info['min'])
                    with cols_info[4]:
                        st.metric("Máx", info['max'])

        st.info(f"**Archivo actual:** {selected_file} | Filas: {len(df)} | Columnas: {len(df.columns)}")

        # BOTONES DE ACCIÓN CLAROS
        st.subheader("Acciones:")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✏️ Editar Datos", use_container_width=True, type="primary"):
                st.session_state.editing_mode = True
                st.session_state.delete_mode = False
                st.rerun()
                
        with col2:
            if st.button("➕ Agregar Fila", use_container_width=True):
                new_row = {col: "" for col in df.columns}
                new_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.all_dataframes[selected_file]['dataframe'] = new_df
                st.session_state.all_dataframes[selected_file]['edited'] = True
                st.session_state.editing_mode = True
                st.session_state.delete_mode = False
                st.rerun()
                
        with col3:
            if st.button("🗑️ Eliminar Filas Seleccionadas", use_container_width=True):
                st.session_state.delete_mode = not st.session_state.delete_mode
                st.session_state.editing_mode = False
                st.rerun()
                
        with col4:
            if st.button("🔄 Reiniciar Archivo", use_container_width=True):
                # Recargar el archivo original
                for uploaded_file in uploaded_files:
                    if uploaded_file.name == selected_file:
                        try:
                            df_original = pd.read_csv(uploaded_file)
                            st.session_state.all_dataframes[selected_file]['dataframe'] = df_original
                            st.session_state.all_dataframes[selected_file]['edited'] = False
                            st.session_state.editing_mode = False
                            st.session_state.delete_mode = False
                            st.success(f"✅ Archivo {selected_file} reiniciado al estado original")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error al reiniciar: {str(e)}")
                        break

        # MODO ELIMINACIÓN
        if st.session_state.delete_mode:
            st.warning("🔴 **Modo Eliminación Activado**: Selecciona las filas que quieres eliminar en la tabla y luego haz clic en 'Confirmar Eliminación'")
            
            # Agregar columna de selección
            current_df = df.copy()
            current_df['Seleccionar'] = False
            edited_with_selection = st.data_editor(
                current_df,
                use_container_width=True,
                num_rows="fixed",
                key=f"delete_editor_{selected_file}"
            )
            
            # Contar filas seleccionadas
            selected_count = edited_with_selection['Seleccionar'].sum()
            st.write(f"**Filas seleccionadas para eliminar: {selected_count}**")
            
            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if selected_count > 0:
                    if st.button("✅ Confirmar Eliminación", type="primary", use_container_width=True):
                        # Eliminar filas seleccionadas
                        new_df = df.loc[~edited_with_selection['Seleccionar']].reset_index(drop=True)
                        st.session_state.all_dataframes[selected_file]['dataframe'] = new_df
                        st.session_state.all_dataframes[selected_file]['edited'] = True
                        st.session_state.delete_mode = False
                        st.success(f"✅ {selected_count} fila(s) eliminada(s) exitosamente!")
                        st.rerun()
            
            with col_cancel:
                if st.button("❌ Cancelar Eliminación", use_container_width=True):
                    st.session_state.delete_mode = False
                    st.rerun()

        # EDITOR DE DATOS NORMAL
        elif st.session_state.editing_mode:
            st.subheader("Editando datos:")
            edited_df = st.data_editor(
                df, 
                use_container_width=True, 
                num_rows="dynamic", 
                key=f"data_editor_{selected_file}"
            )
            # Actualizar el dataframe si hay cambios
            if not edited_df.equals(df):
                st.session_state.all_dataframes[selected_file]['dataframe'] = edited_df
                st.session_state.all_dataframes[selected_file]['edited'] = True

        # VISUALIZACIÓN NORMAL (sin edición)
        else:
            st.subheader("Vista previa de datos:")
            st.dataframe(df, use_container_width=True)

        # DATOS ACTUALES PARA DESCARGA
        current_df = st.session_state.all_dataframes[selected_file]['dataframe']
        is_edited = st.session_state.all_dataframes[selected_file]['edited']

        st.subheader("Descargar archivo:")
        col_csv, col_json = st.columns(2)

        with col_csv:
            csv_buffer = StringIO()
            current_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="⬇️ Descargar CSV",
                data=csv_buffer.getvalue(),
                file_name=f"editado_{selected_file}",
                mime="text/csv",
                type="primary",
                key=f"download_csv_{selected_file}"
            )

        with col_json:
            json_data = current_df.to_json(orient="records", indent=4, force_ascii=False)
            st.download_button(
                label="⬇️ Descargar JSON",
                data=json_data,
                file_name=f"editado_{selected_file.replace('.csv', '.json')}",
                mime="application/json",
                type="secondary",
                key=f"download_json_{selected_file}"
            )

        # MÉTRICAS FINALES
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Filas totales", len(current_df))
        with col2:
            st.metric("Columnas totales", len(current_df.columns))
        with col3:
            status = "Editado" if is_edited else "Original"
            st.metric("Estado", status)

        # Botón para eliminar archivo actual
        st.markdown("---")
        if st.button("🗑️ Eliminar este archivo de la lista", type="secondary"):
            del st.session_state.all_dataframes[selected_file]
            if st.session_state.all_dataframes:
                st.session_state.current_file = list(st.session_state.all_dataframes.keys())[0]
            else:
                st.session_state.current_file = None
            st.rerun()

else:
    st.info("👆 Sube uno o múltiples archivos CSV para comenzar")

# Sección de ayuda
with st.expander("ℹ️ Ayuda"):
    st.markdown("""
    **Cómo usar el editor:**
    
    1. **Subir múltiples archivos**: Puedes cargar varios archivos CSV a la vez
    2. **Seleccionar archivo**: Usa el selector para cambiar entre archivos cargados
    3. **✏️ Editar Datos**: Activa el modo edición para modificar celdas directamente
    4. **➕ Agregar Fila**: Añade una nueva fila vacía al final de la tabla
    5. **🗑️ Eliminar Filas Seleccionadas**: Activa el modo eliminación para seleccionar y eliminar filas específicas
    6. **🔄 Reiniciar Archivo**: Vuelve al estado original del archivo seleccionado
    
    **Formatos de descarga:**
    - **CSV**: Formato estándar de valores separados por comas
    - **JSON**: Formato para intercambio de datos
    
    **Funcionalidades:**
    - Edita celdas directamente en modo edición
    - Selecciona múltiples filas para eliminar
    - Descarga en múltiples formatos
    - Gestiona múltiples archivos simultáneamente
    - Análisis automático de datos
    """)