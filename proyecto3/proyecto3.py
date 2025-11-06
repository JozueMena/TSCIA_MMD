# Proyecto 3 - Análisis de Datos con Visualizaciones
# VERSIÓN COMPLETA - Con todos los archivos CSV

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# ==============================
# CONFIGURACIÓN
# ==============================
CARPETA_DATOS = 'datos'
carpeta_imagenes = "graficos"

if not os.path.exists(carpeta_imagenes):
    os.makedirs(carpeta_imagenes)

plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# ==============================
# CARGA DE TODOS LOS ARCHIVOS CSV
# ==============================
print("📁 Cargando TODOS los archivos CSV...")

try:
    # Cargar los 11 archivos CSV
    clientes = pd.read_csv(f'{CARPETA_DATOS}/clientes.csv')
    productos = pd.read_csv(f'{CARPETA_DATOS}/productos.csv')
    facturas_encabezado = pd.read_csv(f'{CARPETA_DATOS}/facturas_encabezado.csv')
    facturas_detalle = pd.read_csv(f'{CARPETA_DATOS}/facturas_detalle.csv')
    rubros = pd.read_csv(f'{CARPETA_DATOS}/rubros.csv')
    sucursales = pd.read_csv(f'{CARPETA_DATOS}/sucursales.csv')
    condicion_iva = pd.read_csv(f'{CARPETA_DATOS}/condicion_iva.csv')
    localidades = pd.read_csv(f'{CARPETA_DATOS}/localidades.csv')
    provincias = pd.read_csv(f'{CARPETA_DATOS}/provincias.csv')
    proveedores = pd.read_csv(f'{CARPETA_DATOS}/proveedores.csv')
    ventas = pd.read_csv(f'{CARPETA_DATOS}/ventas.csv')
    
    print("✅ Todos los 11 archivos CSV cargados correctamente")
    print("📋 Archivos cargados: clientes, productos, facturas_encabezado, facturas_detalle, rubros, sucursales, condicion_iva, localidades, provincias, proveedores, ventas")
    
except FileNotFoundError as e:
    print(f"❌ Error: No se encontró {e.filename}")
    print("💡 Asegúrate de que todos los archivos estén en la carpeta 'datos'")
    exit()

# ==============================
# PREPARACIÓN DE DATOS COMPLETA
# ==============================
print("\n🔄 Preparando datos con todas las tablas...")

# Renombrar columnas para evitar conflictos
productos_renom = productos.rename(columns={'descripcion': 'nombre_producto'})
rubros_renom = rubros.rename(columns={'descripcion': 'nombre_rubro'})
condicion_iva_renom = condicion_iva.rename(columns={'descripcion': 'tipo_iva'})
provincias_renom = provincias.rename(columns={'nombre': 'nombre_provincia'})
localidades_renom = localidades.rename(columns={'nombre': 'nombre_localidad'})

# Unir localidades con provincias
localidades_completas = localidades_renom.merge(provincias_renom, on='id_provincia', how='left')

# Unir clientes con información geográfica completa
clientes_completos = clientes.merge(localidades_completas, on='id_localidad', how='left')

# Unir productos con proveedores
productos_completos = productos_renom.merge(proveedores, on='id_proveedor', how='left', suffixes=('_producto', '_proveedor'))

# Merge seguro de detalles con productos y rubros
detalles_completos = (facturas_detalle
    .merge(productos_completos, on='id_producto', how='left')
    .merge(rubros_renom, on='id_rubro', how='left')
)

# Merge seguro de facturas con clientes y condición IVA
facturas_completas = (facturas_encabezado
    .merge(clientes_completos, on='id_cliente', how='left')
    .merge(condicion_iva_renom, on='id_condicion_iva', how='left')
    .merge(sucursales, on='id_sucursal', how='left')
)

# Unir con ventas
facturas_completas = facturas_completas.merge(ventas, on='id_factura', how='left')

# Convertir fecha
facturas_encabezado['fecha'] = pd.to_datetime(facturas_encabezado['fecha'])
facturas_completas['fecha'] = pd.to_datetime(facturas_completas['fecha'])

print("✅ Todos los datos preparados correctamente")

# ==============================
# ANÁLISIS BÁSICO COMPLETO
# ==============================
print("\n" + "="*50)
print("ANÁLISIS BÁSICO COMPLETO")
print("="*50)

total_ventas = facturas_encabezado['total_venta'].sum()
total_facturas = len(facturas_encabezado)
total_clientes = len(clientes)

print(f"💰 Ventas totales: ${total_ventas:,.2f}")
print(f"📄 Total facturas: {total_facturas}")
print(f"👥 Total clientes: {total_clientes}")
print(f"📦 Total productos: {len(productos)}")
print(f"🏪 Total sucursales: {len(sucursales)}")
print(f"🏙️ Total localidades: {len(localidades)}")
print(f"🏛️ Total provincias: {len(provincias)}")
print(f"🏭 Total proveedores: {len(proveedores)}")

# ==============================
# FUNCIÓN CORREGIDA PARA GRÁFICOS INDIVIDUALES
# ==============================

def crear_y_guardar_grafico_individual(nombre_archivo, funcion_grafico):
    """Crea y guarda un gráfico individual SIN usar plt.show()"""
    fig, ax = plt.subplots(figsize=(10, 6))
    funcion_grafico(ax)  # Pasar el axes para que dibuje
    plt.tight_layout()
    
    # PRIMERO GUARDAR
    archivo = os.path.join(carpeta_imagenes, f"individual_{nombre_archivo}.png")
    fig.savefig(archivo, dpi=300, bbox_inches='tight')
    print(f"   💾 individual_{nombre_archivo}.png")
    
    # LUEGO MOSTRAR (opcional)
    plt.show()
    
    # CERRAR
    plt.close(fig)

# ==============================
# DEFINICIÓN DE GRÁFICOS INDIVIDUALES (ACTUALIZADOS)
# ==============================

def grafico_01_ventas_mensuales(ax):
    ventas_mensuales = facturas_encabezado.groupby(facturas_encabezado['fecha'].dt.month)['total_venta'].sum()
    meses = ['Ene', 'Feb', 'Mar']
    ventas_mensuales.index = [meses[i-1] for i in ventas_mensuales.index if i <= len(meses)]
    ax.bar(ventas_mensuales.index, ventas_mensuales.values, color='skyblue', alpha=0.7)
    ax.set_title('Ventas por Mes', fontsize=14, fontweight='bold')
    ax.set_xlabel('Mes')
    ax.set_ylabel('Ventas ($)')
    ax.grid(True, alpha=0.3)

def grafico_02_ventas_sucursal(ax):
    ventas_sucursal = facturas_completas.groupby('id_sucursal')['total_venta'].sum()
    ax.pie(ventas_sucursal.values, labels=[f'Sucursal {i}' for i in ventas_sucursal.index], 
           autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99'])
    ax.set_title('Ventas por Sucursal', fontsize=14, fontweight='bold')

def grafico_03_top_productos_ventas(ax):
    ventas_producto = detalles_completos.groupby('nombre_producto')['subtotal_linea'].sum().nlargest(5)
    y_pos = range(len(ventas_producto))
    ax.barh(y_pos, ventas_producto.values, color='lightgreen')
    ax.set_title('Top 5 Productos por Ventas', fontsize=14, fontweight='bold')
    ax.set_xlabel('Ventas Totales ($)')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(ventas_producto.index)
    ax.grid(True, alpha=0.3, axis='x')

def grafico_04_ventas_tipo_iva(ax):
    ventas_iva = facturas_completas.groupby('tipo_iva')['total_venta'].sum()
    ax.bar(ventas_iva.index, ventas_iva.values, color='lightcoral')
    ax.set_title('Ventas por Tipo de IVA', fontsize=14, fontweight='bold')
    ax.set_xlabel('Tipo de IVA')
    ax.set_ylabel('Ventas ($)')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')

def grafico_05_distribucion_montos(ax):
    ax.hist(facturas_encabezado['total_venta'], bins=8, alpha=0.7, color='orange', edgecolor='black')
    ax.set_title('Distribución de Montos de Venta', fontsize=14, fontweight='bold')
    ax.set_xlabel('Monto de Venta ($)')
    ax.set_ylabel('Frecuencia')
    ax.grid(True, alpha=0.3)

def grafico_06_stock_rubro(ax):
    stock_rubro = productos_renom.merge(rubros_renom, on='id_rubro').groupby('nombre_rubro')['stock'].sum()
    ax.bar(stock_rubro.index, stock_rubro.values, color='gold')
    ax.set_title('Stock por Rubro', fontsize=14, fontweight='bold')
    ax.set_xlabel('Rubro')
    ax.set_ylabel('Stock Total')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')

def grafico_07_productos_mas_vendidos(ax):
    cantidad_producto = detalles_completos.groupby('nombre_producto')['cantidad'].sum().nlargest(8)
    y_pos = range(len(cantidad_producto))
    ax.barh(y_pos, cantidad_producto.values, color='lightblue')
    ax.set_title('Productos Más Vendidos (Cantidad)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Unidades Vendidas')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(cantidad_producto.index)
    ax.grid(True, alpha=0.3, axis='x')

def grafico_08_ventas_rubro(ax):
    ventas_rubro = detalles_completos.groupby('nombre_rubro')['subtotal_linea'].sum()
    ax.pie(ventas_rubro.values, labels=ventas_rubro.index, autopct='%1.1f%%', startangle=90)
    ax.set_title('Ventas por Rubro', fontsize=14, fontweight='bold')

def grafico_09_precio_promedio(ax):
    precio_promedio = detalles_completos.groupby('nombre_producto')['precio_unitario'].mean().nlargest(8)
    y_pos = range(len(precio_promedio))
    ax.barh(y_pos, precio_promedio.values, color='lightgreen')
    ax.set_title('Precio Promedio por Producto (Top 8)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Precio Promedio ($)')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(precio_promedio.index)
    ax.grid(True, alpha=0.3, axis='x')

def grafico_10_precio_vs_stock(ax):
    ax.scatter(productos_renom['precio'], productos_renom['stock'], alpha=0.6, color='purple', s=60)
    ax.set_xlabel('Precio ($)')
    ax.set_ylabel('Stock')
    ax.set_title('Relación Precio vs Stock', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

def grafico_11_productos_por_rubro(ax):
    productos_por_rubro = productos_renom.merge(rubros_renom, on='id_rubro')['nombre_rubro'].value_counts()
    ax.bar(productos_por_rubro.index, productos_por_rubro.values, color='coral')
    ax.set_title('Cantidad de Productos por Rubro', fontsize=14, fontweight='bold')
    ax.set_xlabel('Rubro')
    ax.set_ylabel('Cantidad de Productos')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')

def grafico_12_ticket_promedio(ax):
    ax.hist(facturas_encabezado['total_venta'], bins=10, alpha=0.7, color='teal', edgecolor='black')
    ax.set_title('Distribución del Ticket Promedio', fontsize=14, fontweight='bold')
    ax.set_xlabel('Ticket Promedio ($)')
    ax.set_ylabel('Frecuencia')
    ax.grid(True, alpha=0.3)

# NUEVOS GRÁFICOS CON LOS DATOS COMPLETOS
def grafico_13_clientes_por_provincia(ax):
    clientes_por_provincia = clientes_completos['nombre_provincia'].value_counts()
    ax.bar(clientes_por_provincia.index, clientes_por_provincia.values, color='steelblue', alpha=0.7)
    ax.set_title('Clientes por Provincia', fontsize=14, fontweight='bold')
    ax.set_xlabel('Provincia')
    ax.set_ylabel('Número de Clientes')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')

def grafico_14_productos_por_proveedor(ax):
    productos_por_proveedor = productos_completos['nombre'].value_counts()
    ax.bar(productos_por_proveedor.index, productos_por_proveedor.values, color='darkorange', alpha=0.7)
    ax.set_title('Productos por Proveedor', fontsize=14, fontweight='bold')
    ax.set_xlabel('Proveedor')
    ax.set_ylabel('Cantidad de Productos')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')

def grafico_15_ventas_por_provincia(ax):
    ventas_por_provincia = facturas_completas.groupby('nombre_provincia')['total_venta'].sum()
    ax.bar(ventas_por_provincia.index, ventas_por_provincia.values, color='crimson', alpha=0.7)
    ax.set_title('Ventas por Provincia', fontsize=14, fontweight='bold')
    ax.set_xlabel('Provincia')
    ax.set_ylabel('Ventas Totales ($)')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')

# ==============================
# GENERAR GRÁFICOS INDIVIDUALES (15 ahora)
# ==============================
print("\n📊 Generando 15 gráficos individuales...")

graficos_individuales = [
    ("01_ventas_mensuales", grafico_01_ventas_mensuales),
    ("02_ventas_sucursal", grafico_02_ventas_sucursal),
    ("03_top_productos_ventas", grafico_03_top_productos_ventas),
    ("04_ventas_tipo_iva", grafico_04_ventas_tipo_iva),
    ("05_distribucion_montos", grafico_05_distribucion_montos),
    ("06_stock_rubro", grafico_06_stock_rubro),
    ("07_productos_mas_vendidos", grafico_07_productos_mas_vendidos),
    ("08_ventas_rubro", grafico_08_ventas_rubro),
    ("09_precio_promedio", grafico_09_precio_promedio),
    ("10_precio_vs_stock", grafico_10_precio_vs_stock),
    ("11_productos_por_rubro", grafico_11_productos_por_rubro),
    ("12_ticket_promedio", grafico_12_ticket_promedio),
    ("13_clientes_por_provincia", grafico_13_clientes_por_provincia),
    ("14_productos_por_proveedor", grafico_14_productos_por_proveedor),
    ("15_ventas_por_provincia", grafico_15_ventas_por_provincia)
]

for nombre, funcion in graficos_individuales:
    crear_y_guardar_grafico_individual(nombre, funcion)

# ==============================
# DASHBOARDS ACTUALIZADOS
# ==============================

print("\n📊 Generando Dashboard Principal...")
fig1, axes1 = plt.subplots(3, 3, figsize=(18, 15))
fig1.suptitle('Dashboard Principal - Análisis Completo', fontsize=20, fontweight='bold')

# Aplicar las funciones a los subplots
grafico_01_ventas_mensuales(axes1[0, 0])
grafico_02_ventas_sucursal(axes1[0, 1])
grafico_03_top_productos_ventas(axes1[0, 2])
grafico_04_ventas_tipo_iva(axes1[1, 0])
grafico_05_distribucion_montos(axes1[1, 1])
grafico_13_clientes_por_provincia(axes1[1, 2])
grafico_15_ventas_por_provincia(axes1[2, 0])
grafico_14_productos_por_proveedor(axes1[2, 1])
grafico_12_ticket_promedio(axes1[2, 2])

plt.tight_layout()

# PRIMERO GUARDAR
archivo_principal = os.path.join(carpeta_imagenes, "dashboard_principal.png")
fig1.savefig(archivo_principal, dpi=300, bbox_inches='tight')
print(f"💾 Dashboard principal guardado: {archivo_principal}")

# LUEGO MOSTRAR
plt.show()
plt.close(fig1)

print("\n📦 Generando Dashboard de Productos...")
fig2, axes2 = plt.subplots(3, 2, figsize=(15, 15))
fig2.suptitle('Dashboard de Análisis de Productos', fontsize=20, fontweight='bold')

# Aplicar funciones a los subplots
grafico_06_stock_rubro(axes2[0, 0])
grafico_07_productos_mas_vendidos(axes2[0, 1])
grafico_08_ventas_rubro(axes2[1, 0])
grafico_09_precio_promedio(axes2[1, 1])
grafico_10_precio_vs_stock(axes2[2, 0])
grafico_11_productos_por_rubro(axes2[2, 1])

plt.tight_layout()

# PRIMERO GUARDAR
archivo_productos = os.path.join(carpeta_imagenes, "dashboard_productos.png")
fig2.savefig(archivo_productos, dpi=300, bbox_inches='tight')
print(f"💾 Dashboard de productos guardado: {archivo_productos}")

# LUEGO MOSTRAR
plt.show()
plt.close(fig2)

# ==============================
# RESUMEN FINAL COMPLETO
# ==============================
print("\n" + "="*50)
print("🎉 ANÁLISIS COMPLETADO CON TODOS LOS DATOS")
print("="*50)

print(f"\n📁 ARCHIVOS GENERADOS EN: {carpeta_imagenes}/")
print(f"📊 2 dashboards y 15 gráficos individuales")
print(f"💰 Ventas totales: ${total_ventas:,.2f}")
print(f"📈 Total de visualizaciones: 17 archivos PNG")

print(f"\n📋 DATOS PROCESADOS:")
print(f"• 11 archivos CSV cargados")
print(f"• {len(facturas_encabezado)} facturas analizadas")
print(f"• {len(productos)} productos en inventario")
print(f"• {len(clientes)} clientes en sistema")
print(f"• {len(provincias)} provincias cubiertas")