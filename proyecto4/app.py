# proyecto4/app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from datetime import datetime
import sys

# =============================================
# CONFIGURACIÓN DE IMPORTACIÓN
# =============================================

# Asegurar que podemos importar proyecto1.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import proyecto1
    IMPORT_SUCCESS = True
except ImportError as e:
    st.error(f"❌ Error importando proyecto1.py: {e}")
    IMPORT_SUCCESS = False

# =============================================
# CONFIGURACIÓN STREAMLIT
# =============================================

st.set_page_config(
    page_title="Dashboard Ventas - Proyecto 4",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================
# FUNCIONES AUXILIARES
# =============================================

@st.cache_data
def cargar_datos_streamlit():
    """Carga los datos usando las funciones del proyecto1"""
    if not IMPORT_SUCCESS:
        return None
    
    # Cargar datos usando proyecto1
    proyecto1.cargar_datos()
    
    # Verificar que los datos se cargaron correctamente
    if (proyecto1.clientes is not None and 
        proyecto1.empleados is not None and 
        proyecto1.fact_enc is not None and 
        proyecto1.fact_det is not None):
        
        return {
            'clientes': proyecto1.clientes,
            'empleados': proyecto1.empleados,
            'fact_enc': proyecto1.fact_enc,
            'fact_det': proyecto1.fact_det
        }
    else:
        st.error("❌ No se pudieron cargar los datos desde los archivos CSV")
        return None

def mostrar_metricas_principales(datos):
    """Muestra las métricas principales en el dashboard"""
    if datos is None:
        return
    
    clientes, empleados, fact_enc, fact_det = datos.values()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Total Clientes",
            value=f"{len(clientes):,}",
            delta=f"+{len(clientes)}" 
        )
    
    with col2:
        st.metric(
            label="🧾 Total Facturas",
            value=f"{len(fact_enc):,}",
            delta=f"+{len(fact_enc)}"
        )
    
    with col3:
        ventas_totales = fact_enc['total'].sum()
        st.metric(
            label="💰 Ventas Totales",
            value=f"${ventas_totales:,.2f}",
            delta=f"${ventas_totales:,.0f}"
        )
    
    with col4:
        st.metric(
            label="👨‍💼 Total Empleados",
            value=f"{len(empleados):,}",
            delta="+0"
        )

def crear_grafico_ventas_mensuales(fact_enc):
    """Crea gráfico de ventas mensuales"""
    fact_enc_copy = fact_enc.copy()
    fact_enc_copy['mes'] = fact_enc_copy['fecha'].dt.to_period('M').astype(str)
    ventas_mensuales = fact_enc_copy.groupby('mes')['total'].sum().reset_index()
    
    fig = px.line(
        ventas_mensuales, 
        x='mes', 
        y='total',
        title='📈 Ventas Mensuales',
        labels={'mes': 'Mes', 'total': 'Ventas Totales ($)'}
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    return fig

def crear_grafico_top_clientes(datos):
    """Crea gráfico de top clientes"""
    clientes, fact_enc = datos['clientes'], datos['fact_enc']
    
    ventas_cliente = (
        fact_enc.groupby('id_cliente')['total']
        .sum()
        .reset_index()
        .merge(clientes[['id_cliente', 'nombre_completo']], on='id_cliente')
        .sort_values('total', ascending=False)
        .head(10)
    )
    
    fig = px.bar(
        ventas_cliente,
        x='total',
        y='nombre_completo',
        orientation='h',
        title='🏆 Top 10 Clientes por Ventas',
        labels={'total': 'Ventas Totales ($)', 'nombre_completo': 'Cliente'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig

def crear_grafico_ventas_sucursal(fact_enc):
    """Crea gráfico de ventas por sucursal"""
    ventas_sucursal = fact_enc.groupby('id_sucursal')['total'].sum().reset_index()
    
    fig = px.pie(
        ventas_sucursal,
        values='total',
        names='id_sucursal',
        title='🏪 Distribución de Ventas por Sucursal'
    )
    return fig

def crear_grafico_productos_populares(fact_det):
    """Crea gráfico de productos más vendidos"""
    productos_vendidos = (
        fact_det.groupby('id_producto')
        .agg({'cantidad': 'sum', 'subtotal': 'sum'})
        .reset_index()
        .sort_values('cantidad', ascending=False)
        .head(10)
    )
    
    fig = px.bar(
        productos_vendidos,
        x='id_producto',
        y='cantidad',
        title='📦 Top 10 Productos por Cantidad Vendida',
        labels={'id_producto': 'Producto ID', 'cantidad': 'Cantidad Vendida'}
    )
    return fig

def crear_grafico_empleados_cargo(empleados):
    """Crea gráfico de empleados por cargo"""
    empleados_cargo = empleados.groupby('labor').size().reset_index(name='cantidad')
    
    fig = px.bar(
        empleados_cargo,
        x='labor',
        y='cantidad',
        title='👨‍💼 Empleados por Cargo',
        labels={'labor': 'Cargo', 'cantidad': 'Cantidad de Empleados'}
    )
    return fig

# =============================================
# SECCIÓN CRUD STREAMLIT
# =============================================

def mostrar_seccion_crud(datos):
    """Interfaz CRUD en Streamlit"""
    st.header("🎯 Gestión de Datos (CRUD)")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Clientes", "👨‍💼 Empleados", "🧾 Facturas Enc", "📦 Facturas Det"])
    
    with tab1:
        gestionar_clientes_streamlit(datos)
    
    with tab2:
        gestionar_empleados_streamlit(datos)
    
    with tab3:
        gestionar_facturas_enc_streamlit(datos)
    
    with tab4:
        gestionar_facturas_det_streamlit(datos)

def gestionar_clientes_streamlit(datos):
    """Gestión de clientes en Streamlit"""
    st.subheader("Gestión de Clientes")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🔄 Actualizar Vista Clientes", key="refresh_clientes"):
            st.rerun()
        st.dataframe(datos['clientes'], use_container_width=True, height=400)
    
    with col2:
        st.subheader("➕ Nuevo Cliente")
        with st.form("nuevo_cliente"):
            nombre = st.text_input("Nombre")
            apellido = st.text_input("Apellido")
            email = st.text_input("Email")
            telefono = st.text_input("Teléfono")
            direccion = st.text_input("Dirección")
            id_localidad = st.number_input("ID Localidad", min_value=1, value=1)
            
            if st.form_submit_button("💾 Guardar Cliente"):
                if nombre and apellido:
                    nuevo_cliente = {
                        'id_cliente': datos['clientes']['id_cliente'].max() + 1,
                        'nombre': nombre,
                        'apellido': apellido,
                        'email': email,
                        'telefono': telefono,
                        'direccion': direccion,
                        'id_localidad': id_localidad
                    }
                    proyecto1.clientes = proyecto1.insertar_registro(
                        datos['clientes'], nuevo_cliente, proyecto1.r_clientes
                    )
                    st.success("✅ Cliente agregado correctamente")
                    st.rerun()
                else:
                    st.error("❌ Nombre y apellido son obligatorios")
        
        st.subheader("🔍 Buscar Cliente")
        busqueda = st.text_input("Buscar por nombre:")
        if busqueda:
            clientes_filtrados = datos['clientes'][
                datos['clientes']['nombre_completo'].str.contains(busqueda, case=False, na=False)
            ]
            st.dataframe(clientes_filtrados, use_container_width=True)

def gestionar_empleados_streamlit(datos):
    """Gestión de empleados en Streamlit"""
    st.subheader("Gestión de Empleados")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🔄 Actualizar Vista Empleados", key="refresh_empleados"):
            st.rerun()
        st.dataframe(datos['empleados'], use_container_width=True, height=400)
    
    with col2:
        st.subheader("➕ Nuevo Empleado")
        with st.form("nuevo_empleado"):
            nombre = st.text_input("Nombre")
            edad = st.number_input("Edad", min_value=18, max_value=65, value=30)
            labor = st.text_input("Labor/Cargo")
            
            if st.form_submit_button("💾 Guardar Empleado"):
                if nombre and labor:
                    nuevo_empleado = {
                        'nombre': nombre,
                        'edad': edad,
                        'labor': labor
                    }
                    proyecto1.empleados = proyecto1.insertar_registro(
                        datos['empleados'], nuevo_empleado, proyecto1.r_empleados
                    )
                    st.success("✅ Empleado agregado correctamente")
                    st.rerun()
                else:
                    st.error("❌ Nombre y labor son obligatorios")

def gestionar_facturas_enc_streamlit(datos):
    """Gestión de facturas encabezado en Streamlit"""
    st.subheader("Gestión de Facturas (Encabezado)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🔄 Actualizar Vista Facturas", key="refresh_facturas"):
            st.rerun()
        st.dataframe(datos['fact_enc'], use_container_width=True, height=400)
    
    with col2:
        st.subheader("➕ Nueva Factura")
        with st.form("nueva_factura"):
            fecha = st.date_input("Fecha")
            id_cliente = st.number_input("ID Cliente", min_value=1, value=1)
            id_sucursal = st.number_input("ID Sucursal", min_value=1, value=1)
            total = st.number_input("Total", min_value=0.0, value=100.0)
            
            if st.form_submit_button("💾 Guardar Factura"):
                nueva_factura = {
                    'id_factura': datos['fact_enc']['id_factura'].max() + 1,
                    'fecha': fecha.strftime('%Y-%m-%d'),
                    'id_cliente': id_cliente,
                    'id_sucursal': id_sucursal,
                    'total': total
                }
                proyecto1.fact_enc = proyecto1.insertar_registro(
                    datos['fact_enc'], nueva_factura, proyecto1.r_fact_enc
                )
                st.success("✅ Factura agregada correctamente")
                st.rerun()

def gestionar_facturas_det_streamlit(datos):
    """Gestión de facturas detalle en Streamlit"""
    st.subheader("Gestión de Facturas (Detalle)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🔄 Actualizar Vista Detalles", key="refresh_detalles"):
            st.rerun()
        st.dataframe(datos['fact_det'], use_container_width=True, height=400)
    
    with col2:
        st.subheader("➕ Nuevo Detalle")
        with st.form("nuevo_detalle"):
            id_factura = st.number_input("ID Factura", min_value=1, value=1)
            id_producto = st.number_input("ID Producto", min_value=1, value=1)
            cantidad = st.number_input("Cantidad", min_value=1, value=1)
            precio_unitario = st.number_input("Precio Unitario", min_value=0.0, value=10.0)
            subtotal = st.number_input("Subtotal", min_value=0.0, value=10.0)
            
            if st.form_submit_button("💾 Guardar Detalle"):
                nuevo_detalle = {
                    'id_factura_det': datos['fact_det']['id_factura_det'].max() + 1,
                    'id_factura': id_factura,
                    'id_producto': id_producto,
                    'cantidad': cantidad,
                    'precio_unitario': precio_unitario,
                    'subtotal': subtotal
                }
                proyecto1.fact_det = proyecto1.insertar_registro(
                    datos['fact_det'], nuevo_detalle, proyecto1.r_fact_det
                )
                st.success("✅ Detalle de factura agregado correctamente")
                st.rerun()

# =============================================
# SECCIÓN EXPORTACIÓN
# =============================================

def mostrar_seccion_exportacion():
    """Interfaz para exportar datos"""
    st.header("📤 Exportación de Datos")
    
    st.info("💡 **Nota:** Las exportaciones usarán las funciones de proyecto1.py")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📊 Reportes CSV")
        if st.button("🔄 Generar Todos los CSV", key="btn_csv"):
            with st.spinner("Generando reportes CSV..."):
                try:
                    proyecto1.generar_reportes_csv()
                    st.success("✅ Reportes CSV generados correctamente")
                except Exception as e:
                    st.error(f"❌ Error generando CSV: {e}")
    
    with col2:
        st.subheader("📁 Exportar JSON")
        if st.button("🔄 Generar JSON Completo", key="btn_json"):
            with st.spinner("Generando JSON..."):
                try:
                    proyecto1.exportar_a_json()
                    st.success("✅ Exportación JSON completada")
                except Exception as e:
                    st.error(f"❌ Error generando JSON: {e}")
    
    with col3:
        st.subheader("📈 Exportar Excel")
        if st.button("🔄 Generar Excel Completo", key="btn_excel"):
            with st.spinner("Generando Excel..."):
                try:
                    proyecto1.exportar_a_excel()
                    st.success("✅ Exportación Excel completada")
                except Exception as e:
                    st.error(f"❌ Error generando Excel: {e}")
    
    # Mostrar archivos generados
    st.markdown("---")
    st.subheader("📂 Archivos Generados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**📊 CSV Individuales:**")
        if os.path.exists(proyecto1.CSV_OUTPUT):
            archivos = os.listdir(proyecto1.CSV_OUTPUT)
            for archivo in archivos:
                st.write(f"• `{archivo}`")
        else:
            st.write("No hay archivos CSV generados")
    
    with col2:
        st.write("**📁 JSON:**")
        if os.path.exists(proyecto1.JSON_OUTPUT):
            archivos = os.listdir(proyecto1.JSON_OUTPUT)
            for archivo in archivos:
                st.write(f"• `{archivo}`")
        else:
            st.write("No hay archivos JSON generados")
    
    with col3:
        st.write("**📈 Excel:**")
        if os.path.exists(proyecto1.EXCEL_OUTPUT):
            archivos = os.listdir(proyecto1.EXCEL_OUTPUT)
            for archivo in archivos:
                st.write(f"• `{archivo}`")
        else:
            st.write("No hay archivos Excel generados")

# =============================================
# DASHBOARD PRINCIPAL
# =============================================

def mostrar_dashboard(datos):
    """Muestra el dashboard principal con gráficos"""
    st.header("📊 Dashboard de Ventas - Proyecto 4")
    
    if datos is None:
        st.error("No hay datos disponibles para mostrar el dashboard")
        return
    
    # Métricas principales
    mostrar_metricas_principales(datos)
    
    st.markdown("---")
    
    # Primera fila de gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        fig_ventas_mensuales = crear_grafico_ventas_mensuales(datos['fact_enc'])
        st.plotly_chart(fig_ventas_mensuales, use_container_width=True)
    
    with col2:
        fig_top_clientes = crear_grafico_top_clientes(datos)
        st.plotly_chart(fig_top_clientes, use_container_width=True)
    
    # Segunda fila de gráficos
    col3, col4 = st.columns(2)
    
    with col3:
        fig_ventas_sucursal = crear_grafico_ventas_sucursal(datos['fact_enc'])
        st.plotly_chart(fig_ventas_sucursal, use_container_width=True)
    
    with col4:
        fig_productos_populares = crear_grafico_productos_populares(datos['fact_det'])
        st.plotly_chart(fig_productos_populares, use_container_width=True)
    
    # Tercera fila: Gráfico adicional
    col5, col6 = st.columns(2)
    
    with col5:
        fig_empleados_cargo = crear_grafico_empleados_cargo(datos['empleados'])
        st.plotly_chart(fig_empleados_cargo, use_container_width=True)
    
    with col6:
        st.subheader("📋 Resumen Ejecutivo")
        
        # Calcular algunas métricas adicionales
        ventas_totales = datos['fact_enc']['total'].sum()
        ticket_promedio = datos['fact_enc']['total'].mean()
        factura_maxima = datos['fact_enc']['total'].max()
        
        st.metric("💰 Ventas Totales", f"${ventas_totales:,.2f}")
        st.metric("🎫 Ticket Promedio", f"${ticket_promedio:.2f}")
        st.metric("📈 Factura Más Alta", f"${factura_maxima:.2f}")
        st.metric("🏪 Sucursales Activas", datos['fact_enc']['id_sucursal'].nunique())
        st.metric("📦 Productos Vendidos", datos['fact_det']['id_producto'].nunique())

# =============================================
# BARRA LATERAL
# =============================================

def mostrar_sidebar():
    """Muestra la barra lateral de navegación"""
    st.sidebar.title("🏪 Sistema de Ventas")
    st.sidebar.markdown("**Proyecto 4 - Streamlit Dashboard**")
    st.sidebar.markdown("---")
    
    opcion = st.sidebar.radio(
        "Navegación",
        ["📊 Dashboard", "🎯 Gestión CRUD", "📤 Exportación", "⚙️ Configuración"]
    )
    
    st.sidebar.markdown("---")
    
    # Información del sistema
    st.sidebar.info(
        "**Funcionalidades:**\n"
        "• Dashboard interactivo\n"
        "• Gestión CRUD completa\n"
        "• Exportación múltiple\n"
        "• Gráficos en tiempo real"
    )
    
    return opcion

# =============================================
# APLICACIÓN PRINCIPAL
# =============================================

def main():
    """Función principal de la aplicación Streamlit"""
    
    if not IMPORT_SUCCESS:
        st.error("""
        ❌ No se pudo importar proyecto1.py. Asegúrate de que:
        1. proyecto1.py esté en la misma carpeta que app.py
        2. Los archivos CSV estén en la carpeta 'datos/'
        3. Las dependencias estén instaladas
        """)
        return
    
    # Cargar datos
    datos = cargar_datos_streamlit()
    
    if datos is None:
        st.error("No se pudieron cargar los datos. Verifica los archivos CSV en la carpeta 'datos/'")
        return
    
    # Barra lateral
    opcion = mostrar_sidebar()
    
    # Contenido principal según selección
    if opcion == "📊 Dashboard":
        mostrar_dashboard(datos)
    
    elif opcion == "🎯 Gestión CRUD":
        mostrar_seccion_crud(datos)
    
    elif opcion == "📤 Exportación":
        mostrar_seccion_exportacion()
    
    elif opcion == "⚙️ Configuración":
        st.header("⚙️ Configuración del Sistema")
        
        st.subheader("📁 Estado de los Datos")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**👥 Clientes cargados:** {len(datos['clientes'])}")
            st.write(f"**👨‍💼 Empleados cargados:** {len(datos['empleados'])}")
        
        with col2:
            st.write(f"**🧾 Facturas cargadas:** {len(datos['fact_enc'])}")
            st.write(f"**📦 Detalles cargados:** {len(datos['fact_det'])}")
        
        st.subheader("🔄 Recargar Datos")
        if st.button("🔄 Recargar Todos los Datos"):
            proyecto1.cargar_datos()
            st.rerun()
            st.success("✅ Datos recargados correctamente")
        
        st.subheader("📊 Información del Sistema")
        st.write(f"**Ruta actual:** {os.getcwd()}")
        st.write(f"**Archivos en datos/:** {os.listdir('datos') if os.path.exists('datos') else 'No existe'}")

# =============================================
# EJECUCIÓN
# =============================================

if __name__ == "__main__":
    main()