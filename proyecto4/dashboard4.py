# proyecto4/dashboard4.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from datetime import datetime
import sys
from io import StringIO, BytesIO
import zipfile

# =============================================
# CONFIGURACIÓN STREAMLIT
# =============================================

st.set_page_config(
    page_title="Dashboard Proyecto 4 - Sistema Completo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================
# CONFIGURACIÓN DE DATOS
# =============================================

CARPETA_DATOS = 'datos'

# =============================================
# FUNCIONES DE CARGA DE DATOS (CORREGIDAS)
# =============================================

@st.cache_data
def cargar_datos_completos():
    """Carga todos los datos de tus archivos CSV con manejo de errores"""
    try:
        st.info("🔄 Cargando archivos CSV...")
        
        # Cargar todos los archivos que tienes
        clientes = pd.read_csv(f'{CARPETA_DATOS}/clientes.csv')
        productos = pd.read_csv(f'{CARPETA_DATOS}/productos.csv')
        facturas_encabezado = pd.read_csv(f'{CARPETA_DATOS}/facturas_encabezado.csv')
        facturas_detalle = pd.read_csv(f'{CARPETA_DATOS}/facturas_detalle.csv')
        rubros = pd.read_csv(f'{CARPETA_DATOS}/rubros.csv')
        sucursales = pd.read_csv(f'{CARPETA_DATOS}/sucursales.csv')
        condicion_iva = pd.read_csv(f'{CARPETA_DATOS}/condicion_iva.csv')
        localidades = pd.read_csv(f'{CARPETA_DATOS}/localidades.csv')
        proveedores = pd.read_csv(f'{CARPETA_DATOS}/proveedores.csv')
        provincias = pd.read_csv(f'{CARPETA_DATOS}/provincias.csv')
        ventas = pd.read_csv(f'{CARPETA_DATOS}/ventas.csv')
        
        st.info("✅ Archivos CSV cargados correctamente")
        st.info("🔄 Procesando datos...")
        
        # Preparar datos con merge seguros
        productos_renom = productos.rename(columns={'descripcion': 'nombre_producto'})
        rubros_renom = rubros.rename(columns={'descripcion': 'nombre_rubro'})
        condicion_iva_renom = condicion_iva.rename(columns={'descripcion': 'tipo_iva'})
        localidades_renom = localidades.rename(columns={'nombre': 'nombre_localidad'})
        provincias_renom = provincias.rename(columns={'nombre': 'nombre_provincia'})
        sucursales_renom = sucursales.rename(columns={'nombre': 'nombre_sucursal'})
        
        # Merge de detalles con productos y rubros
        detalles_completos = (facturas_detalle
            .merge(productos_renom, on='id_producto', how='left')
            .merge(rubros_renom, on='id_rubro', how='left')
        )
        
        # Merge de facturas con clientes, condición IVA y sucursales (SIN localidades/provincias por ahora)
        facturas_completas = (facturas_encabezado
            .merge(clientes, on='id_cliente', how='left')
            .merge(condicion_iva_renom, on='id_condicion_iva', how='left')
            .merge(sucursales_renom, on='id_sucursal', how='left')
        )
        
        # Merge de clientes con localidades y provincias (si existen las columnas)
        try:
            clientes_completos = (clientes
                .merge(localidades_renom, on='id_localidad', how='left')
                .merge(provincias_renom, left_on='id_provincia', right_on='id_provincia', how='left')
            )
        except:
            st.warning("⚠️ No se pudo hacer merge completo de clientes con localidades/provincias")
            clientes_completos = clientes.copy()
        
        # Merge de productos con proveedores y rubros
        try:
            productos_completos = (productos
                .merge(proveedores, on='id_proveedor', how='left')
                .merge(rubros_renom, on='id_rubro', how='left')
            )
        except:
            st.warning("⚠️ No se pudo hacer merge completo de productos")
            productos_completos = productos.copy()
        
        # Convertir fechas
        try:
            facturas_encabezado['fecha'] = pd.to_datetime(facturas_encabezado['fecha'])
        except:
            st.warning("⚠️ No se pudo convertir fecha de facturas")
        
        try:
            ventas['fecha_venta'] = pd.to_datetime(ventas['fecha_venta'])
        except:
            st.warning("⚠️ No se pudo convertir fecha de ventas")
        
        st.info("✅ Datos procesados correctamente")
        
        return {
            'clientes': clientes,
            'productos': productos,
            'facturas_encabezado': facturas_encabezado,
            'facturas_detalle': facturas_detalle,
            'rubros': rubros,
            'sucursales': sucursales,
            'condicion_iva': condicion_iva,
            'localidades': localidades,
            'proveedores': proveedores,
            'provincias': provincias,
            'ventas': ventas,
            'detalles_completos': detalles_completos,
            'facturas_completas': facturas_completas,
            'clientes_completos': clientes_completos,
            'productos_completos': productos_completos
        }
        
    except FileNotFoundError as e:
        st.error(f"❌ Error: Archivo no encontrado - {e}")
        # Mostrar qué archivos hay en la carpeta
        if os.path.exists(CARPETA_DATOS):
            archivos = os.listdir(CARPETA_DATOS)
            st.error(f"📁 Archivos en carpeta 'datos/': {archivos}")
        return None
    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        import traceback
        st.error(f"📋 Detalles del error: {traceback.format_exc()}")
        return None

# =============================================
# FUNCIONES DE GRÁFICOS INTERACTIVOS - ORIGINALES
# =============================================

def crear_grafico_ventas_mensuales(facturas_encabezado):
    """Gráfico de ventas mensuales interactivo"""
    try:
        facturas_encabezado['mes'] = facturas_encabezado['fecha'].dt.month
        ventas_mensuales = facturas_encabezado.groupby('mes')['total_venta'].sum()
        
        meses = ['Enero', 'Febrero', 'Marzo']
        
        ventas_mensuales.index = [meses[i-1] for i in ventas_mensuales.index if i <= len(meses)]
        
        fig = px.bar(
            x=ventas_mensuales.index,
            y=ventas_mensuales.values,
            title='📈 Ventas Mensuales (Barras)',
            labels={'x': 'Mes', 'y': 'Ventas Totales ($)'},
            color=ventas_mensuales.values,
            color_continuous_scale='blues'
        )
        fig.update_layout(showlegend=False)
        return fig
    except Exception as e:
        st.error(f"Error en gráfico ventas mensuales: {e}")
        return go.Figure()

def crear_grafico_ventas_sucursal(facturas_completas):
    """Gráfico de ventas por sucursal"""
    try:
        ventas_sucursal = facturas_completas.groupby('nombre_sucursal')['total_venta'].sum()
        
        fig = px.pie(
            values=ventas_sucursal.values,
            names=ventas_sucursal.index,
            title='🏪 Distribución de Ventas por Sucursal'
        )
        return fig
    except Exception as e:
        st.error(f"Error en gráfico ventas sucursal: {e}")
        return go.Figure()

def crear_grafico_top_productos_ventas(detalles_completos):
    """Top productos por ventas"""
    try:
        ventas_producto = detalles_completos.groupby('nombre_producto')['subtotal_linea'].sum().nlargest(8)
        
        fig = px.bar(
            x=ventas_producto.values,
            y=ventas_producto.index,
            orientation='h',
            title='🏆 Top 8 Productos por Ventas',
            labels={'x': 'Ventas Totales ($)', 'y': 'Producto'},
            color=ventas_producto.values,
            color_continuous_scale='greens'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        return fig
    except Exception as e:
        st.error(f"Error en gráfico top productos: {e}")
        return go.Figure()

def crear_grafico_ventas_tipo_iva(facturas_completas):
    """Ventas por tipo de IVA"""
    try:
        ventas_iva = facturas_completas.groupby('tipo_iva')['total_venta'].sum()
        
        fig = px.bar(
            x=ventas_iva.index,
            y=ventas_iva.values,
            title='💰 Ventas por Tipo de IVA',
            labels={'x': 'Tipo de IVA', 'y': 'Ventas ($)'},
            color=ventas_iva.values,
            color_continuous_scale='reds'
        )
        return fig
    except Exception as e:
        st.error(f"Error en gráfico ventas IVA: {e}")
        return go.Figure()

def crear_grafico_productos_mas_vendidos(detalles_completos):
    """Productos más vendidos por cantidad"""
    try:
        cantidad_producto = detalles_completos.groupby('nombre_producto')['cantidad'].sum().nlargest(8)
        
        fig = px.bar(
            x=cantidad_producto.values,
            y=cantidad_producto.index,
            orientation='h',
            title='📦 Productos Más Vendidos (Cantidad)',
            labels={'x': 'Unidades Vendidas', 'y': 'Producto'},
            color=cantidad_producto.values,
            color_continuous_scale='purples'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        return fig
    except Exception as e:
        st.error(f"Error en gráfico productos vendidos: {e}")
        return go.Figure()

def crear_grafico_ventas_rubro(detalles_completos):
    """Ventas por rubro"""
    try:
        ventas_rubro = detalles_completos.groupby('nombre_rubro')['subtotal_linea'].sum()
        
        fig = px.pie(
            values=ventas_rubro.values,
            names=ventas_rubro.index,
            title='📊 Ventas por Rubro'
        )
        return fig
    except Exception as e:
        st.error(f"Error en gráfico ventas rubro: {e}")
        return go.Figure()

def crear_grafico_stock_rubro(productos_completos):
    """Stock por rubro"""
    try:
        stock_rubro = productos_completos.groupby('nombre_rubro')['stock'].sum()
        
        fig = px.bar(
            x=stock_rubro.index,
            y=stock_rubro.values,
            title='📦 Stock por Rubro',
            labels={'x': 'Rubro', 'y': 'Stock Total'},
            color=stock_rubro.values,
            color_continuous_scale='oranges'
        )
        return fig
    except Exception as e:
        st.error(f"Error en gráfico stock rubro: {e}")
        return go.Figure()

# =============================================
# NUEVAS FUNCIONES DE GRÁFICOS DE TENDENCIA TEMPORAL
# =============================================

def crear_grafico_ventas_semanales(facturas_encabezado):
    """Gráfico de líneas para ventas semanales"""
    try:
        # Crear copia para no modificar el original
        df = facturas_encabezado.copy()
        df['semana'] = df['fecha'].dt.to_period('W').dt.start_time
        
        ventas_semanales = df.groupby('semana')['total_venta'].sum().reset_index()
        
        fig = px.line(
            ventas_semanales,
            x='semana',
            y='total_venta',
            title='📈 Ventas Semanales',
            labels={'semana': 'Semana', 'total_venta': 'Ventas Totales ($)'},
            markers=True
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=8))
        fig.update_layout(
            xaxis=dict(tickformat='%d/%m/%Y'),
            hovermode='x unified'
        )
        return fig
    except Exception as e:
        st.error(f"Error en gráfico ventas semanales: {e}")
        return go.Figure()

def crear_grafico_ventas_mensuales_lineas(facturas_encabezado):
    """Gráfico de líneas para ventas mensuales"""
    try:
        df = facturas_encabezado.copy()
        df['mes'] = df['fecha'].dt.to_period('M').dt.start_time
        
        ventas_mensuales = df.groupby('mes')['total_venta'].sum().reset_index()
        
        fig = px.line(
            ventas_mensuales,
            x='mes',
            y='total_venta',
            title='📊 Ventas Mensuales (Línea)',
            labels={'mes': 'Mes', 'total_venta': 'Ventas Totales ($)'},
            markers=True
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=8))
        fig.update_layout(
            xaxis=dict(tickformat='%b %Y'),
            hovermode='x unified'
        )
        return fig
    except Exception as e:
        st.error(f"Error en gráfico ventas mensuales línea: {e}")
        return go.Figure()

def crear_grafico_ventas_anuales(facturas_encabezado):
    """Gráfico de líneas para ventas anuales"""
    try:
        df = facturas_encabezado.copy()
        df['año'] = df['fecha'].dt.year
        
        ventas_anuales = df.groupby('año')['total_venta'].sum().reset_index()
        
        # MOSTRAR GRÁFICO AUNQUE SOLO HAYA UN AÑO
        fig = px.line(
            ventas_anuales,
            x='año',
            y='total_venta',
            title='📅 Ventas Anuales',
            labels={'año': 'Año', 'total_venta': 'Ventas Totales ($)'},
            markers=True
        )
        
        # Personalizar el gráfico para un solo año
        if len(ventas_anuales) == 1:
            año = ventas_anuales['año'].iloc[0]
            venta_total = ventas_anuales['total_venta'].iloc[0]
            
            # Agregar anotación con el total
            fig.add_annotation(
                text=f"Total {año}: ${venta_total:,.2f}",
                x=año, y=venta_total,
                xref="x", yref="y",
                showarrow=True,
                arrowhead=2,
                ax=0, ay=-40,
                bgcolor="white",
                bordercolor="black",
                borderwidth=1
            )
            
            fig.update_layout(
                title=f"📅 Ventas Anuales - {año}",
                xaxis=dict(tickmode='array', tickvals=[año])
            )
        
        fig.update_traces(line=dict(width=4), marker=dict(size=10))
        return fig
        
    except Exception as e:
        st.error(f"Error en gráfico ventas anuales: {e}")
        return go.Figure()

def crear_grafico_tendencia_ventas_completo(facturas_encabezado):
    """Gráfico completo con tendencia de ventas por día/semana/mes"""
    try:
        df = facturas_encabezado.copy()
        
        # Crear diferentes agrupaciones
        df_diario = df.groupby('fecha')['total_venta'].sum().reset_index()
        df_semanal = df.groupby(df['fecha'].dt.to_period('W').dt.start_time)['total_venta'].sum().reset_index()
        df_semanal = df_semanal.rename(columns={'fecha': 'semana'})
        df_mensual = df.groupby(df['fecha'].dt.to_period('M').dt.start_time)['total_venta'].sum().reset_index()
        df_mensual = df_mensual.rename(columns={'fecha': 'mes'})
        
        # Crear subplots
        fig = go.Figure()
        
        # Agregar líneas para cada período
        fig.add_trace(go.Scatter(
            x=df_diario['fecha'], y=df_diario['total_venta'],
            mode='lines+markers', name='Ventas Diarias',
            line=dict(width=1, color='lightblue'),
            marker=dict(size=4)
        ))
        
        fig.add_trace(go.Scatter(
            x=df_semanal['semana'], y=df_semanal['total_venta'],
            mode='lines+markers', name='Ventas Semanales',
            line=dict(width=3, color='blue'),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=df_mensual['mes'], y=df_mensual['total_venta'],
            mode='lines+markers', name='Ventas Mensuales',
            line=dict(width=4, color='darkblue'),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title='📈 Tendencia de Ventas - Diario/Semanal/Mensual',
            xaxis_title='Fecha',
            yaxis_title='Ventas Totales ($)',
            hovermode='x unified',
            height=500
        )
        
        return fig
    except Exception as e:
        st.error(f"Error en gráfico tendencia completa: {e}")
        return go.Figure()

# =============================================
# FUNCIONES DEL EDITOR DE DATOS
# =============================================

def mostrar_editor_datos():
    """Editor de datos interactivo"""
    st.header("🛠️ Editor de Datos")
    
    if 'datos_completos' not in st.session_state:
        st.error("❌ No hay datos cargados")
        return
        
    datos = st.session_state.datos_completos
    
    # Selector de tabla con TODOS tus archivos
    tablas_disponibles = {
        'Clientes': datos['clientes'],
        'Productos': datos['productos'], 
        'Facturas Encabezado': datos['facturas_encabezado'],
        'Facturas Detalle': datos['facturas_detalle'],
        'Rubros': datos['rubros'],
        'Sucursales': datos['sucursales'],
        'Condición IVA': datos['condicion_iva'],
        'Localidades': datos['localidades'],
        'Proveedores': datos['proveedores'],
        'Provincias': datos['provincias'],
        'Ventas': datos['ventas']
    }
    
    tabla_seleccionada = st.selectbox("Selecciona la tabla a editar:", list(tablas_disponibles.keys()))
    
    df = tablas_disponibles[tabla_seleccionada]
    
    # Análisis de datos
    st.subheader("📈 Análisis de Datos")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Filas totales", len(df))
    with col2:
        st.metric("Columnas totales", len(df.columns))
    with col3:
        st.metric("Valores faltantes", df.isnull().sum().sum())
    with col4:
        memoria_mb = round(df.memory_usage(deep=True).sum() / 1024**2, 2)
        st.metric("Memoria (MB)", memoria_mb)
    
    # Editor de datos
    st.subheader("✏️ Editor de Datos")
    
    col_edit1, col_edit2 = st.columns([3, 1])
    
    with col_edit2:
        st.subheader("Acciones")
        if st.button("➕ Agregar Fila", use_container_width=True):
            nueva_fila = {col: "" for col in df.columns}
            df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
            # Actualizar en session_state
            clave_tabla = tabla_seleccionada.lower().replace(' ', '_')
            st.session_state.datos_completos[clave_tabla] = df
            st.rerun()
            
        if st.button("🔄 Reiniciar Tabla", use_container_width=True):
            # Recargar datos originales
            datos_originales = cargar_datos_completos()
            if datos_originales:
                st.session_state.datos_completos = datos_originales
                st.success("✅ Datos reiniciados correctamente")
                st.rerun()
            else:
                st.error("❌ Error al recargar datos")
    
    with col_edit1:
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            key=f"editor_{tabla_seleccionada}"
        )
        
        # Actualizar datos si hay cambios
        if not edited_df.equals(df):
            clave_tabla = tabla_seleccionada.lower().replace(' ', '_')
            st.session_state.datos_completos[clave_tabla] = edited_df
            st.success("✅ Cambios guardados en la sesión actual")
    
    # Descargas
    st.subheader("📥 Descargar Datos")
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        csv_buffer = StringIO()
        edited_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="⬇️ Descargar CSV",
            data=csv_buffer.getvalue(),
            file_name=f"{tabla_seleccionada.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_dl2:
        json_data = edited_df.to_json(orient="records", indent=4, force_ascii=False)
        st.download_button(
            label="⬇️ Descargar JSON",
            data=json_data,
            file_name=f"{tabla_seleccionada.lower().replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True
        )

# =============================================
# FUNCIONES DE EXPORTACIÓN
# =============================================

def mostrar_exportacion_datos():
    """Exportación de datos completos"""
    st.header("📤 Exportación de Datos")
    
    if 'datos_completos' not in st.session_state:
        st.error("❌ No hay datos cargados")
        return
        
    datos = st.session_state.datos_completos
    
    # Exportación individual por tabla
    st.subheader("📊 Exportación por Tabla")
    
    tablas = [
        ('Clientes', 'clientes'),
        ('Productos', 'productos'),
        ('Facturas Encabezado', 'facturas_encabezado'),
        ('Facturas Detalle', 'facturas_detalle'),
        ('Rubros', 'rubros'),
        ('Sucursales', 'sucursales'),
        ('Condición IVA', 'condicion_iva'),
        ('Localidades', 'localidades'),
        ('Proveedores', 'proveedores'),
        ('Provincias', 'provincias'),
        ('Ventas', 'ventas')
    ]
    
    for nombre_tabla, clave_tabla in tablas:
        with st.expander(f"📋 {nombre_tabla}"):
            df = datos[clave_tabla]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    label="⬇️ CSV",
                    data=df.to_csv(index=False),
                    file_name=f"{clave_tabla}.csv",
                    mime="text/csv",
                    key=f"csv_{clave_tabla}"
                )
            
            with col2:
                json_data = df.to_json(orient="records", indent=4, force_ascii=False)
                st.download_button(
                    label="⬇️ JSON",
                    data=json_data,
                    file_name=f"{clave_tabla}.json",
                    mime="application/json",
                    key=f"json_{clave_tabla}"
                )
    
    # Exportación completa
    st.subheader("📦 Exportación Completa del Sistema")
    
    if st.button("🎁 Generar Paquete Completo", use_container_width=True):
        # Crear archivo ZIP con todos los datos
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for nombre_tabla, clave_tabla in tablas:
                df = datos[clave_tabla]
                zip_file.writestr(f"{clave_tabla}.csv", df.to_csv(index=False))
                zip_file.writestr(f"{clave_tabla}.json", df.to_json(orient="records", indent=4, force_ascii=False))
        
        st.download_button(
            label="⬇️ Descargar Paquete Completo (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="sistema_ventas_completo.zip",
            mime="application/zip",
            use_container_width=True
        )

# =============================================
# DASHBOARD PRINCIPAL (ACTUALIZADO CON TENDENCIAS)
# =============================================

def mostrar_dashboard_principal():
    """Dashboard principal con métricas y gráficos"""
    st.header("📊 Dashboard Principal - Sistema de Ventas Completo")
    
    if 'datos_completos' not in st.session_state:
        st.error("❌ No hay datos cargados")
        return
        
    datos = st.session_state.datos_completos
    
    # Métricas principales
    total_ventas = datos['facturas_encabezado']['total_venta'].sum()
    total_facturas = len(datos['facturas_encabezado'])
    total_clientes = len(datos['clientes'])
    total_productos = len(datos['productos'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Ventas Totales", f"${total_ventas:,.2f}")
    with col2:
        st.metric("🧾 Total Facturas", f"{total_facturas:,}")
    with col3:
        st.metric("👥 Total Clientes", f"{total_clientes:,}")
    with col4:
        st.metric("📦 Total Productos", f"{total_productos:,}")
    
    st.markdown("---")
    
    # NUEVA SECCIÓN: TENDENCIAS TEMPORALES
    st.subheader("📈 Análisis de Tendencia Temporal")
    
    # Gráfico completo de tendencias
    fig_tendencia_completa = crear_grafico_tendencia_ventas_completo(datos['facturas_encabezado'])
    st.plotly_chart(fig_tendencia_completa, use_container_width=True)
    
    # Gráficos individuales por período
    col1, col2 = st.columns(2)
    
    with col1:
        fig_semanales = crear_grafico_ventas_semanales(datos['facturas_encabezado'])
        st.plotly_chart(fig_semanales, use_container_width=True)
    
    with col2:
        fig_mensuales_linea = crear_grafico_ventas_mensuales_lineas(datos['facturas_encabezado'])
        st.plotly_chart(fig_mensuales_linea, use_container_width=True)
    
    # Gráfico anual
    fig_anuales = crear_grafico_ventas_anuales(datos['facturas_encabezado'])
    st.plotly_chart(fig_anuales, use_container_width=True)
    
    st.markdown("---")
    
    # SECCIÓN ORIGINAL: ANÁLISIS POR CATEGORÍAS
    st.subheader("📊 Análisis por Categorías")
    
    # Primera fila de gráficos originales
    col1, col2 = st.columns(2)
    
    with col1:
        fig_ventas_sucursal = crear_grafico_ventas_sucursal(datos['facturas_completas'])
        st.plotly_chart(fig_ventas_sucursal, use_container_width=True)
    
    with col2:
        fig_top_productos = crear_grafico_top_productos_ventas(datos['detalles_completos'])
        st.plotly_chart(fig_top_productos, use_container_width=True)
    
    # Segunda fila de gráficos
    col3, col4 = st.columns(2)
    
    with col3:
        fig_ventas_iva = crear_grafico_ventas_tipo_iva(datos['facturas_completas'])
        st.plotly_chart(fig_ventas_iva, use_container_width=True)
    
    with col4:
        fig_productos_vendidos = crear_grafico_productos_mas_vendidos(datos['detalles_completos'])
        st.plotly_chart(fig_productos_vendidos, use_container_width=True)
    
    # Tercera fila de gráficos
    col5, col6 = st.columns(2)
    
    with col5:
        fig_ventas_rubro = crear_grafico_ventas_rubro(datos['detalles_completos'])
        st.plotly_chart(fig_ventas_rubro, use_container_width=True)
    
    with col6:
        fig_stock_rubro = crear_grafico_stock_rubro(datos['productos_completos'])
        st.plotly_chart(fig_stock_rubro, use_container_width=True)
    
    # Cuarta fila - Gráfico de barras mensual original
    fig_mensuales_barras = crear_grafico_ventas_mensuales(datos['facturas_encabezado'])
    st.plotly_chart(fig_mensuales_barras, use_container_width=True)

# =============================================
# BARRA LATERAL
# =============================================

def mostrar_sidebar():
    """Barra lateral de navegación"""
    st.sidebar.title("🏪 Sistema de Ventas")
    st.sidebar.markdown("**Proyecto 4 - Dashboard Completo**")
    st.sidebar.markdown("---")
    
    opcion = st.sidebar.radio(
        "Navegación",
        ["📊 Dashboard", "🛠️ Editor de Datos", "📤 Exportación", "⚙️ Configuración"]
    )
    
    st.sidebar.markdown("---")
    
    # Información del sistema
    if 'datos_completos' in st.session_state:
        datos = st.session_state.datos_completos
        st.sidebar.info(
            f"**Datos cargados:**\n"
            f"• {len(datos['clientes'])} clientes\n"
            f"• {len(datos['productos'])} productos\n"
            f"• {len(datos['facturas_encabezado'])} facturas\n"
            f"• {len(datos['proveedores'])} proveedores"
        )
    
    return opcion

# =============================================
# APLICACIÓN PRINCIPAL
# =============================================

def main():
    """Función principal de la aplicación"""
    
    # Inicializar datos en session_state
    if 'datos_completos' not in st.session_state:
        datos = cargar_datos_completos()
        if datos is not None:
            st.session_state.datos_completos = datos
        else:
            st.error("❌ No se pudieron cargar los datos. Verifica la carpeta 'datos/'")
            # Mostrar qué archivos hay disponibles
            if os.path.exists(CARPETA_DATOS):
                archivos = os.listdir(CARPETA_DATOS)
                st.info(f"📁 Archivos encontrados en 'datos/': {archivos}")
            return
    
    # Barra lateral
    opcion = mostrar_sidebar()
    
    # Contenido principal según selección
    if opcion == "📊 Dashboard":
        mostrar_dashboard_principal()
    
    elif opcion == "🛠️ Editor de Datos":
        mostrar_editor_datos()
    
    elif opcion == "📤 Exportación":
        mostrar_exportacion_datos()
    
    elif opcion == "⚙️ Configuración":
        st.header("⚙️ Configuración del Sistema")
        
        datos = st.session_state.datos_completos
        
        st.subheader("📊 Estado de los Datos")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Tablas principales:**")
            st.write(f"• 👥 Clientes: {len(datos['clientes'])} registros")
            st.write(f"• 📦 Productos: {len(datos['productos'])} registros")
            st.write(f"• 🧾 Facturas: {len(datos['facturas_encabezado'])} registros")
            st.write(f"• 📋 Detalles: {len(datos['facturas_detalle'])} registros")
            st.write(f"• 🏪 Sucursales: {len(datos['sucursales'])} registros")
        
        with col2:
            st.write("**Tablas de configuración:**")
            st.write(f"• 📊 Rubros: {len(datos['rubros'])} registros")
            st.write(f"• 💰 Cond. IVA: {len(datos['condicion_iva'])} registros")
            st.write(f"• 🗺️ Localidades: {len(datos['localidades'])} registros")
            st.write(f"• 🏭 Proveedores: {len(datos['proveedores'])} registros")
            st.write(f"• 🗺️ Provincias: {len(datos['provincias'])} registros")
            st.write(f"• 💸 Ventas: {len(datos['ventas'])} registros")
        
        # Mostrar estructura de datos importantes
        with st.expander("🔍 Ver estructura de datos"):
            st.write("**Clientes:**", list(datos['clientes'].columns))
            st.write("**Facturas:**", list(datos['facturas_encabezado'].columns))
            st.write("**Sucursales:**", list(datos['sucursales'].columns))
            st.write("**Localidades:**", list(datos['localidades'].columns))
        
        st.subheader("🔄 Recargar Datos")
        if st.button("🔄 Recargar Todos los Datos"):
            nuevos_datos = cargar_datos_completos()
            if nuevos_datos is not None:
                st.session_state.datos_completos = nuevos_datos
                st.success("✅ Datos recargados correctamente")
                st.rerun()
            else:
                st.error("❌ Error al recargar los datos")

# =============================================
# EJECUCIÓN
# =============================================

if __name__ == "__main__":
    main()