# =============================================
# Proyecto 1 - Python / CSV / JSON / EXCEL / Pandas
# Descripción:
#   Sistema completo de gestión de ventas con CRUD,
#   análisis de datos y exportación a JSON, Excel y CSV individuales.
# =============================================

import pandas as pd
import os
import json
from datetime import datetime

# ---------------------------------------------
# CONFIGURACIÓN DE RUTAS
# ---------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(SCRIPT_DIR, "datos")
JSON_OUTPUT = os.path.join(SCRIPT_DIR, "json_salida")
EXCEL_OUTPUT = os.path.join(SCRIPT_DIR, "excel_salida")
CSV_OUTPUT = os.path.join(SCRIPT_DIR, "salida")  # Para los CSV individuales

# Crear carpetas si no existen
os.makedirs(BASE, exist_ok=True)
os.makedirs(JSON_OUTPUT, exist_ok=True)
os.makedirs(EXCEL_OUTPUT, exist_ok=True)
os.makedirs(CSV_OUTPUT, exist_ok=True)

# Archivos de entrada
r_clientes = os.path.join(BASE, "clientes.csv")
r_empleados = os.path.join(BASE, "empleados.csv")
r_fact_enc = os.path.join(BASE, "facturas_enc.csv")
r_fact_det = os.path.join(BASE, "facturas_det.csv")

# ---------------------------------------------
# FUNCIONES CRUD PARA CSV
# ---------------------------------------------

def cargar_csv(ruta_archivo):
    """Carga un archivo CSV y retorna el DataFrame"""
    try:
        if os.path.exists(ruta_archivo):
            return pd.read_csv(ruta_archivo)
        else:
            print(f"❌ Archivo no encontrado: {ruta_archivo}")
            return None
    except Exception as e:
        print(f"❌ Error cargando {ruta_archivo}: {e}")
        return None

def guardar_csv(df, ruta_archivo):
    """Guarda un DataFrame en un archivo CSV"""
    try:
        df.to_csv(ruta_archivo, index=False)
        print(f"✅ Datos guardados en: {ruta_archivo}")
        return True
    except Exception as e:
        print(f"❌ Error guardando {ruta_archivo}: {e}")
        return False

def mostrar_tabla(df, nombre_tabla, max_filas=10):
    """Muestra una tabla con formato"""
    if df is None or df.empty:
        print(f"📭 {nombre_tabla} está vacía")
        return
    
    print(f"\n📋 {nombre_tabla} (mostrando {min(max_filas, len(df))} de {len(df)} registros):")
    print("-" * 80)
    print(df.head(max_filas).to_string(index=False))
    print("-" * 80)

def insertar_registro(df, nuevo_registro, ruta_archivo):
    """Inserta un nuevo registro en el DataFrame y lo guarda"""
    try:
        nuevo_df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
        if guardar_csv(nuevo_df, ruta_archivo):
            print("✅ Registro insertado correctamente")
            return nuevo_df
    except Exception as e:
        print(f"❌ Error insertando registro: {e}")
    return df

def modificar_registro(df, columna_busqueda, valor_busqueda, cambios, ruta_archivo):
    """Modifica un registro existente"""
    try:
        # Encontrar el índice del registro
        mask = df[columna_busqueda] == valor_busqueda
        if not mask.any():
            print("❌ No se encontró el registro")
            return df
        
        # Aplicar cambios
        for columna, nuevo_valor in cambios.items():
            if columna in df.columns:
                df.loc[mask, columna] = nuevo_valor
            else:
                print(f"⚠️ Columna '{columna}' no existe")
        
        if guardar_csv(df, ruta_archivo):
            print("✅ Registro modificado correctamente")
        
        return df
    except Exception as e:
        print(f"❌ Error modificando registro: {e}")
        return df

def eliminar_registro(df, columna_busqueda, valor_busqueda, ruta_archivo):
    """Elimina un registro"""
    try:
        mask = df[columna_busqueda] == valor_busqueda
        if not mask.any():
            print("❌ No se encontró el registro")
            return df
        
        registros_eliminados = df[mask]
        df = df[~mask]
        
        if guardar_csv(df, ruta_archivo):
            print(f"✅ Registro eliminado: {registros_eliminados.iloc[0].to_dict()}")
        
        return df
    except Exception as e:
        print(f"❌ Error eliminando registro: {e}")
        return df

# ---------------------------------------------
# MENÚ INTERACTIVO CRUD
# ---------------------------------------------

def menu_crud():
    """Menú interactivo para operaciones CRUD"""
    while True:
        print("\n" + "="*60)
        print("🎯 MENÚ CRUD - GESTIÓN DE DATOS")
        print("="*60)
        print("1. 👥  Gestionar Clientes")
        print("2. 👨‍💼 Gestionar Empleados") 
        print("3. 🧾 Gestionar Facturas (Encabezado)")
        print("4. 📦 Gestionar Facturas (Detalle)")
        print("5. 📊 Mostrar Todos los Datos")
        print("6. 🔄 Recargar Datos desde CSV")
        print("0. ↩️  Volver al Menú Principal")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            gestionar_clientes()
        elif opcion == "2":
            gestionar_empleados()
        elif opcion == "3":
            gestionar_facturas_enc()
        elif opcion == "4":
            gestionar_facturas_det()
        elif opcion == "5":
            mostrar_todos_los_datos()
        elif opcion == "6":
            return True  # Indicar que se deben recargar los datos
        elif opcion == "0":
            return False
        else:
            print("❌ Opción inválida")

def gestionar_clientes():
    """Menú específico para gestión de clientes"""
    global clientes
    while True:
        print(f"\n👥 GESTIÓN DE CLIENTES ({len(clientes)} registros)")
        print("1. 📋 Mostrar clientes")
        print("2. ➕ Insertar cliente")
        print("3. ✏️  Modificar cliente")
        print("4. 🗑️  Eliminar cliente")
        print("0. ↩️  Volver")
        
        opcion = input("Seleccione: ").strip()
        
        if opcion == "1":
            mostrar_tabla(clientes, "CLIENTES")
        elif opcion == "2":
            nuevo_cliente = {
                'id_cliente': clientes['id_cliente'].max() + 1,
                'nombre': input("Nombre: "),
                'apellido': input("Apellido: "),
                'email': input("Email: "),
                'telefono': input("Teléfono: "),
                'direccion': input("Dirección: "),
                'id_localidad': int(input("ID Localidad: "))
            }
            clientes = insertar_registro(clientes, nuevo_cliente, r_clientes)
        elif opcion == "3":
            id_cliente = int(input("ID del cliente a modificar: "))
            cambios = {}
            print("Deje en blanco los campos que no desea modificar:")
            for col in ['nombre', 'apellido', 'email', 'telefono', 'direccion', 'id_localidad']:
                if col != 'id_cliente':
                    nuevo_valor = input(f"{col}: ")
                    if nuevo_valor:
                        cambios[col] = nuevo_valor
            if cambios:
                clientes = modificar_registro(clientes, 'id_cliente', id_cliente, cambios, r_clientes)
        elif opcion == "4":
            id_cliente = int(input("ID del cliente a eliminar: "))
            clientes = eliminar_registro(clientes, 'id_cliente', id_cliente, r_clientes)
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida")

def gestionar_empleados():
    """Menú específico para gestión de empleados"""
    global empleados
    while True:
        print(f"\n👨‍💼 GESTIÓN DE EMPLEADOS ({len(empleados)} registros)")
        print("1. 📋 Mostrar empleados")
        print("2. ➕ Insertar empleado")
        print("3. ✏️  Modificar empleado")
        print("4. 🗑️  Eliminar empleado")
        print("0. ↩️  Volver")
        
        opcion = input("Seleccione: ").strip()
        
        if opcion == "1":
            mostrar_tabla(empleados, "EMPLEADOS")
        elif opcion == "2":
            nuevo_empleado = {
                'nombre': input("Nombre: "),
                'edad': int(input("Edad: ")),
                'labor': input("Labor: ")
            }
            empleados = insertar_registro(empleados, nuevo_empleado, r_empleados)
        elif opcion == "3":
            nombre = input("Nombre del empleado a modificar: ")
            cambios = {}
            print("Deje en blanco los campos que no desea modificar:")
            for col in ['nombre', 'edad', 'labor']:
                nuevo_valor = input(f"{col}: ")
                if nuevo_valor:
                    if col == 'edad':
                        cambios[col] = int(nuevo_valor)
                    else:
                        cambios[col] = nuevo_valor
            if cambios:
                empleados = modificar_registro(empleados, 'nombre', nombre, cambios, r_empleados)
        elif opcion == "4":
            nombre = input("Nombre del empleado a eliminar: ")
            empleados = eliminar_registro(empleados, 'nombre', nombre, r_empleados)
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida")

def gestionar_facturas_enc():
    """Menú específico para gestión de facturas encabezado"""
    global fact_enc
    while True:
        print(f"\n🧾 GESTIÓN DE FACTURAS ENCABEZADO ({len(fact_enc)} registros)")
        print("1. 📋 Mostrar facturas")
        print("2. ➕ Insertar factura")
        print("3. ✏️  Modificar factura")
        print("4. 🗑️  Eliminar factura")
        print("0. ↩️  Volver")
        
        opcion = input("Seleccione: ").strip()
        
        if opcion == "1":
            mostrar_tabla(fact_enc, "FACTURAS ENCABEZADO")
        elif opcion == "2":
            nueva_factura = {
                'id_factura': fact_enc['id_factura'].max() + 1,
                'fecha': input("Fecha (YYYY-MM-DD): "),
                'id_cliente': int(input("ID Cliente: ")),
                'id_sucursal': int(input("ID Sucursal: ")),
                'total': float(input("Total: "))
            }
            fact_enc = insertar_registro(fact_enc, nueva_factura, r_fact_enc)
        elif opcion == "3":
            id_factura = int(input("ID de la factura a modificar: "))
            cambios = {}
            print("Deje en blanco los campos que no desea modificar:")
            for col in ['fecha', 'id_cliente', 'id_sucursal', 'total']:
                nuevo_valor = input(f"{col}: ")
                if nuevo_valor:
                    if col in ['id_cliente', 'id_sucursal']:
                        cambios[col] = int(nuevo_valor)
                    elif col == 'total':
                        cambios[col] = float(nuevo_valor)
                    else:
                        cambios[col] = nuevo_valor
            if cambios:
                fact_enc = modificar_registro(fact_enc, 'id_factura', id_factura, cambios, r_fact_enc)
        elif opcion == "4":
            id_factura = int(input("ID de la factura a eliminar: "))
            fact_enc = eliminar_registro(fact_enc, 'id_factura', id_factura, r_fact_enc)
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida")

def gestionar_facturas_det():
    """Menú específico para gestión de facturas detalle"""
    global fact_det
    while True:
        print(f"\n📦 GESTIÓN DE FACTURAS DETALLE ({len(fact_det)} registros)")
        print("1. 📋 Mostrar detalles")
        print("2. ➕ Insertar detalle")
        print("3. ✏️  Modificar detalle")
        print("4. 🗑️  Eliminar detalle")
        print("0. ↩️  Volver")
        
        opcion = input("Seleccione: ").strip()
        
        if opcion == "1":
            mostrar_tabla(fact_det, "FACTURAS DETALLE")
        elif opcion == "2":
            nuevo_detalle = {
                'id_factura_det': fact_det['id_factura_det'].max() + 1,
                'id_factura': int(input("ID Factura: ")),
                'id_producto': int(input("ID Producto: ")),
                'cantidad': int(input("Cantidad: ")),
                'precio_unitario': float(input("Precio Unitario: ")),
                'subtotal': float(input("Subtotal: "))
            }
            fact_det = insertar_registro(fact_det, nuevo_detalle, r_fact_det)
        elif opcion == "3":
            id_detalle = int(input("ID del detalle a modificar: "))
            cambios = {}
            print("Deje en blanco los campos que no desea modificar:")
            for col in ['id_factura', 'id_producto', 'cantidad', 'precio_unitario', 'subtotal']:
                nuevo_valor = input(f"{col}: ")
                if nuevo_valor:
                    if col in ['id_factura', 'id_producto', 'cantidad']:
                        cambios[col] = int(nuevo_valor)
                    else:
                        cambios[col] = float(nuevo_valor)
            if cambios:
                fact_det = modificar_registro(fact_det, 'id_factura_det', id_detalle, cambios, r_fact_det)
        elif opcion == "4":
            id_detalle = int(input("ID del detalle a eliminar: "))
            fact_det = eliminar_registro(fact_det, 'id_factura_det', id_detalle, r_fact_det)
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida")

def mostrar_todos_los_datos():
    """Muestra todas las tablas"""
    print("\n" + "="*80)
    print("📊 VISUALIZACIÓN COMPLETA DE DATOS")
    print("="*80)
    
    mostrar_tabla(clientes, "CLIENTES", 5)
    mostrar_tabla(empleados, "EMPLEADOS", 5)
    mostrar_tabla(fact_enc, "FACTURAS ENCABEZADO", 5)
    mostrar_tabla(fact_det, "FACTURAS DETALLE", 5)
    
    input("\nPresione Enter para continuar...")

# ---------------------------------------------
# FUNCIONES DE EXPORTACIÓN MEJORADAS
# ---------------------------------------------

def generar_reportes_csv():
    """Genera todos los archivos CSV individuales como en el código original"""
    print("\n📊 Generando reportes CSV individuales...")
    
    try:
        # 1) RANKING DE CLIENTES POR TOTAL COMPRADO
        ventas_por_cliente = (
            fact_enc.groupby('id_cliente', as_index=False)['total']
            .sum()
            .rename(columns={'total': 'total_comprado'})
            .merge(clientes[['id_cliente', 'nombre_completo', 'email', 'id_localidad']], 
                   how='left', on='id_cliente')
            .sort_values('total_comprado', ascending=False)
        )
        ventas_por_cliente.to_csv(os.path.join(CSV_OUTPUT, 'ventas_por_cliente.csv'), index=False)

        # 2) TICKET PROMEDIO POR CLIENTE
        facturas_por_cliente = (
            fact_enc.groupby('id_cliente', as_index=False)['id_factura']
            .count()
            .rename(columns={'id_factura': 'cantidad_facturas'})
        )
        ticket_promedio = (
            ventas_por_cliente.merge(facturas_por_cliente, how='left', on='id_cliente')
        )
        ticket_promedio['ticket_promedio'] = (
            ticket_promedio['total_comprado'] / ticket_promedio['cantidad_facturas']
        ).round(2)
        ticket_promedio.to_csv(os.path.join(CSV_OUTPUT, 'ticket_promedio_por_cliente.csv'), index=False)

        # 3) FACTURAS MÁS ALTAS (TOP 20)
        facturas_completas = fact_enc.merge(
            clientes[['id_cliente', 'nombre_completo', 'email', 'id_localidad']], 
            how='left', 
            on='id_cliente'
        )
        top_facturas = (
            facturas_completas
            .sort_values('total', ascending=False)
            .head(20)
            [['id_factura', 'fecha', 'nombre_completo', 'total', 'id_sucursal']]
        )
        top_facturas.to_csv(os.path.join(CSV_OUTPUT, 'top_facturas.csv'), index=False)

        # 4) VENTAS POR MES
        fact_enc['year_month'] = fact_enc['fecha'].dt.to_period('M').astype(str)
        ventas_por_mes = (
            fact_enc.groupby('year_month', as_index=False)['total']
            .agg(['sum', 'count'])
        )
        ventas_por_mes.columns = ['mes', 'ventas_totales', 'cantidad_facturas']
        ventas_por_mes['promedio_ventas'] = (ventas_por_mes['ventas_totales'] / ventas_por_mes['cantidad_facturas']).round(2)
        ventas_por_mes.to_csv(os.path.join(CSV_OUTPUT, 'ventas_por_mes.csv'), index=False)

        # 5) PRODUCTOS MÁS VENDIDOS
        # Por cantidad
        productos_cantidad = (
            fact_det.groupby('id_producto', as_index=False)['cantidad']
            .sum()
            .rename(columns={'cantidad': 'cantidad_vendida'})
            .sort_values('cantidad_vendida', ascending=False)
        )
        productos_cantidad.to_csv(os.path.join(CSV_OUTPUT, 'productos_mas_vendidos_cantidad.csv'), index=False)

        # Por facturación
        fact_det['facturacion'] = fact_det['cantidad'] * fact_det['precio_unitario']
        productos_facturacion = (
            fact_det.groupby('id_producto', as_index=False)['facturacion']
            .sum()
            .sort_values('facturacion', ascending=False)
        )
        productos_facturacion.to_csv(os.path.join(CSV_OUTPUT, 'productos_mas_vendidos_facturacion.csv'), index=False)

        # 6) VENTAS POR SUCURSAL
        ventas_por_sucursal = (
            fact_enc.groupby('id_sucursal', as_index=False)['total']
            .agg(['sum', 'count', 'mean'])
        )
        ventas_por_sucursal.columns = ['id_sucursal', 'ventas_totales', 'cantidad_facturas', 'promedio_ventas']
        ventas_por_sucursal['promedio_ventas'] = ventas_por_sucursal['promedio_ventas'].round(2)
        ventas_por_sucursal.to_csv(os.path.join(CSV_OUTPUT, 'ventas_por_sucursal.csv'), index=False)

        # 7) CLIENTES POR LOCALIDAD
        clientes_por_localidad = (
            clientes.groupby('id_localidad', as_index=False)['id_cliente']
            .count()
            .rename(columns={'id_cliente': 'cantidad_clientes'})
            .sort_values('cantidad_clientes', ascending=False)
        )
        clientes_por_localidad.to_csv(os.path.join(CSV_OUTPUT, 'clientes_por_localidad.csv'), index=False)

        # 8) EMPLEADOS POR CARGO
        empleados_por_cargo = (
            empleados.groupby('labor', as_index=False)['nombre']
            .count()
            .rename(columns={'nombre': 'cantidad_empleados'})
            .sort_values('cantidad_empleados', ascending=False)
        )
        empleados_por_cargo.to_csv(os.path.join(CSV_OUTPUT, 'empleados_por_cargo.csv'), index=False)

        print("✅ Reportes CSV generados:")
        print("   • ventas_por_cliente.csv")
        print("   • ticket_promedio_por_cliente.csv")
        print("   • top_facturas.csv")
        print("   • ventas_por_mes.csv")
        print("   • productos_mas_vendidos_cantidad.csv")
        print("   • productos_mas_vendidos_facturacion.csv")
        print("   • ventas_por_sucursal.csv")
        print("   • clientes_por_localidad.csv")
        print("   • empleados_por_cargo.csv")
        
    except Exception as e:
        print(f"❌ Error generando reportes CSV: {e}")

def exportar_a_json():
    """Exporta todos los análisis a formato JSON (incluye los CSV individuales)"""
    print("\n📤 Exportando a JSON...")
    
    try:
        # Primero generar los CSV individuales
        generar_reportes_csv()
        
        # Resumen estadístico (igual que antes)
        resumen_estadistico = {
            'total_clientes': len(clientes),
            'total_empleados': len(empleados),
            'total_facturas': len(fact_enc),
            'total_detalles': len(fact_det),
            'ventas_totales': fact_enc['total'].sum(),
            'venta_promedio': fact_enc['total'].mean(),
            'venta_maxima': fact_enc['total'].max(),
            'venta_minima': fact_enc['total'].min(),
            'periodo_inicio': fact_enc['fecha'].min().strftime('%Y-%m-%d'),
            'periodo_fin': fact_enc['fecha'].max().strftime('%Y-%m-%d'),
            'sucursales_activas': fact_enc['id_sucursal'].nunique(),
            'productos_vendidos': fact_det['id_producto'].nunique(),
            'fecha_exportacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Cargar los CSV recién generados para el JSON completo
        def convertir_a_serializable(df):
            return df.to_dict('records')

        # Compilar todos los datos para el JSON completo
        datos_exportacion = {
            'resumen_estadistico': resumen_estadistico,
            'top_10_clientes': convertir_a_serializable(pd.read_csv(os.path.join(CSV_OUTPUT, 'ventas_por_cliente.csv')).head(10)),
            'top_10_productos_cantidad': convertir_a_serializable(pd.read_csv(os.path.join(CSV_OUTPUT, 'productos_mas_vendidos_cantidad.csv')).head(10)),
            'top_10_productos_facturacion': convertir_a_serializable(pd.read_csv(os.path.join(CSV_OUTPUT, 'productos_mas_vendidos_facturacion.csv')).head(10)),
            'ventas_mensuales': convertir_a_serializable(pd.read_csv(os.path.join(CSV_OUTPUT, 'ventas_por_mes.csv'))),
            'ventas_por_sucursal': convertir_a_serializable(pd.read_csv(os.path.join(CSV_OUTPUT, 'ventas_por_sucursal.csv'))),
            'clientes_por_localidad': convertir_a_serializable(pd.read_csv(os.path.join(CSV_OUTPUT, 'clientes_por_localidad.csv'))),
            'empleados_por_cargo': convertir_a_serializable(pd.read_csv(os.path.join(CSV_OUTPUT, 'empleados_por_cargo.csv')))
        }

        # Guardar archivo JSON principal
        archivo_json_completo = os.path.join(JSON_OUTPUT, 'resumen_analisis_completo.json')
        with open(archivo_json_completo, 'w', encoding='utf-8') as f:
            json.dump(datos_exportacion, f, ensure_ascii=False, indent=2)
        
        # Guardar resumen individual
        archivo_resumen = os.path.join(JSON_OUTPUT, 'resumen_estadistico.json')
        with open(archivo_resumen, 'w', encoding='utf-8') as f:
            json.dump(resumen_estadistico, f, ensure_ascii=False, indent=2)

        print("✅ Exportación JSON completada:")
        print(f"   📁 {archivo_json_completo}")
        print(f"   📁 {archivo_resumen}")
        
    except Exception as e:
        print(f"❌ Error en exportación JSON: {e}")

def exportar_a_excel():
    """Exporta todos los datos y análisis a Excel (incluye los CSV individuales)"""
    print("\n📤 Exportando a Excel...")
    
    try:
        # Primero generar los CSV individuales
        generar_reportes_csv()
        
        archivo_excel = os.path.join(EXCEL_OUTPUT, 'analisis_completo.xlsx')
        
        with pd.ExcelWriter(archivo_excel, engine='openpyxl') as writer:
            # 1. Datos originales
            clientes.to_excel(writer, sheet_name='Clientes', index=False)
            empleados.to_excel(writer, sheet_name='Empleados', index=False)
            fact_enc.to_excel(writer, sheet_name='Facturas_Enc', index=False)
            fact_det.to_excel(writer, sheet_name='Facturas_Det', index=False)
            
            # 2. Todos los reportes CSV como hojas separadas
            reportes = [
                'ventas_por_cliente', 'ticket_promedio_por_cliente', 'top_facturas',
                'ventas_por_mes', 'productos_mas_vendidos_cantidad', 'productos_mas_vendidos_facturacion',
                'ventas_por_sucursal', 'clientes_por_localidad', 'empleados_por_cargo'
            ]
            
            for reporte in reportes:
                df_reporte = pd.read_csv(os.path.join(CSV_OUTPUT, f'{reporte}.csv'))
                # Nombre de hoja más corto para Excel
                nombre_hoja = reporte[:31]  # Excel limita a 31 caracteres
                df_reporte.to_excel(writer, sheet_name=nombre_hoja, index=False)
            
            # 3. Resumen ejecutivo
            resumen_data = {
                'Métrica': [
                    'Total Clientes', 'Total Empleados', 'Total Facturas', 'Total Detalles',
                    'Ventas Totales', 'Venta Promedio', 'Venta Máxima', 'Venta Mínima',
                    'Período Inicio', 'Período Fin', 'Sucursales Activas', 'Productos Vendidos'
                ],
                'Valor': [
                    len(clientes), len(empleados), len(fact_enc), len(fact_det),
                    f"${fact_enc['total'].sum():,.2f}", f"${fact_enc['total'].mean():.2f}",
                    f"${fact_enc['total'].max():.2f}", f"${fact_enc['total'].min():.2f}",
                    fact_enc['fecha'].min().strftime('%Y-%m-%d'),
                    fact_enc['fecha'].max().strftime('%Y-%m-%d'),
                    fact_enc['id_sucursal'].nunique(),
                    fact_det['id_producto'].nunique()
                ]
            }
            resumen_df = pd.DataFrame(resumen_data)
            resumen_df.to_excel(writer, sheet_name='Resumen', index=False)

        print("✅ Exportación Excel completada:")
        print(f"   📁 {archivo_excel}")
        print(f"   📊 {12 + len(reportes)} hojas de análisis generadas")
        
    except Exception as e:
        print(f"❌ Error en exportación Excel: {e}")

# ---------------------------------------------
# CARGA INICIAL DE DATOS
# ---------------------------------------------

def cargar_datos():
    """Carga todos los datos desde los archivos CSV"""
    global clientes, empleados, fact_enc, fact_det
    
    print("📥 Cargando datos desde CSV...")
    
    clientes = cargar_csv(r_clientes)
    empleados = cargar_csv(r_empleados)
    fact_enc = cargar_csv(r_fact_enc)
    fact_det = cargar_csv(r_fact_det)
    
    if clientes is not None:
        clientes['nombre_completo'] = clientes['nombre'] + ' ' + clientes['apellido']
    
    if fact_enc is not None:
        fact_enc['fecha'] = pd.to_datetime(fact_enc['fecha'])
    
    # Verificar carga exitosa
    datos_cargados = all(df is not None for df in [clientes, empleados, fact_enc, fact_det])
    
    if datos_cargados:
        print("✅ Datos cargados correctamente")
        print(f"   👥 Clientes: {len(clientes)}")
        print(f"   👨‍💼 Empleados: {len(empleados)}") 
        print(f"   🧾 Facturas: {len(fact_enc)}")
        print(f"   📦 Detalles: {len(fact_det)}")
    else:
        print("❌ Error: No se pudieron cargar todos los datos")
    
    return datos_cargados

def menu_principal():
    """Menú principal del sistema"""
    while True:
        print("\n" + "="*60)
        print("🏪 SISTEMA DE GESTIÓN DE VENTAS - VERSIÓN COMPLETA")
        print("="*60)
        print("1. 🎯 Gestión de Datos (CRUD)")
        print("2. 📊 Generar Reportes CSV Individuales")
        print("3. 📤 Exportar a JSON")
        print("4. 📤 Exportar a Excel") 
        print("5. 📄 Generar Reporte PDF")  # ← Esta opción debe estar
        print("6. 🔄 Recargar Datos")
        print("0. 🚪 Salir")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            if menu_crud():
                cargar_datos()
        elif opcion == "2":
            generar_reportes_csv()
        elif opcion == "3":
            exportar_a_json()
        elif opcion == "4":
            exportar_a_excel()
        elif opcion == "5":
            generar_reporte_pdf()  # ← Y esta llamada
        elif opcion == "6":
            cargar_datos()
        elif opcion == "0":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")

# =============================================
# MENÚ PRINCIPAL MEJORADO CON PDF
# =============================================

def menu_principal():
    """Menú principal del sistema"""
    
    def generar_reporte_pdf_simple():
        """Función PDF dentro del menú - VERSIÓN GUÍA DE ESTUDIO"""
        print("\n📄 Generando guía de estudio en PDF...")
        
        try:
            # Intentar importar FPDF
            try:
                from fpdf import FPDF
            except ImportError:
                print("❌ FPDF no está instalado. Instala con: pip install fpdf")
                return
            
            # Verificar que hay datos cargados
            if clientes is None or fact_enc is None:
                print("❌ No hay datos cargados para generar el PDF")
                return
            
            # Crear PDF con soporte UTF-8
            pdf = FPDF()
            
            # Agregar fuentes que soporten UTF-8
            pdf.add_page()
            
            # ===== PORTADA =====
            pdf.set_font('Arial', 'B', 24)
            pdf.cell(0, 40, 'GUIA DE ESTUDIO - SISTEMA DE GESTION', 0, 1, 'C')
            pdf.ln(20)
            
            pdf.set_font('Arial', 'I', 16)
            pdf.cell(0, 10, 'Analisis de Datos de Ventas', 0, 1, 'C')
            pdf.ln(30)
            
            pdf.set_font('Arial', '', 14)
            pdf.multi_cell(0, 8, 
                "Este documento contiene:\n"
                "- Explicacion del sistema\n" 
                "- Analisis de datos reales\n"
                "- Metricas y estadisticas\n"
                "- Ejemplos practicos\n"
                "- Conceptos clave para el parcial"
            )
            pdf.ln(20)
            
            pdf.set_font('Arial', 'I', 12)
            pdf.cell(0, 10, f'Generado el: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
            
            # ===== PÁGINA 2: EXPLICACIÓN DEL SISTEMA =====
            pdf.add_page()
            pdf.set_font('Arial', 'B', 18)
            pdf.cell(0, 10, '1. DESCRIPCION DEL SISTEMA', 0, 1, 'L')
            pdf.ln(8)
            
            pdf.set_font('Arial', '', 12)
            contenido_sistema = (
                "Este sistema de gestion comercial permite:\n\n"
                "- GESTION CRUD: Crear, Leer, Actualizar y Eliminar registros\n"
                "- ANALISIS: Procesar datos de ventas, clientes y productos\n" 
                "- REPORTES: Generar CSV, JSON, Excel y PDF automaticamente\n"
                "- VISUALIZACION: Mostrar datos de forma organizada\n\n"
                
                "TABLAS PRINCIPALES:\n"
                "- Clientes: Informacion de clientes y localidades\n"
                "- Empleados: Datos del personal y sus cargos\n"
                "- Facturas_enc: Encabezados de facturas\n"
                "- Facturas_det: Detalles de productos vendidos\n\n"
                
                "TECNOLOGIAS UTILIZADAS:\n"
                "- Python 3.x + Pandas para analisis de datos\n"
                "- CSV para almacenamiento de datos\n"
                "- FPDF para generacion de reportes PDF\n"
                "- JSON para intercambio de datos estructurados"
            )
            pdf.multi_cell(0, 8, contenido_sistema)
            
            # ===== PÁGINA 3: ANÁLISIS ESTADÍSTICO =====
            pdf.add_page()
            pdf.set_font('Arial', 'B', 18)
            pdf.cell(0, 10, '2. ANALISIS ESTADISTICO - DATOS REALES', 0, 1, 'L')
            pdf.ln(8)
            
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'METRICAS PRINCIPALES DEL SISTEMA:', 0, 1, 'L')
            pdf.ln(5)
            
            pdf.set_font('Arial', '', 12)
            metricas = [
                f'- Total de Clientes Registrados: {len(clientes):,}',
                f'- Cantidad de Empleados: {len(empleados):,}',
                f'- Facturas Procesadas: {len(fact_enc):,}',
                f'- Detalles de Ventas: {len(fact_det):,}',
                f'- Ventas Totales: ${fact_enc["total"].sum():,.2f}',
                f'- Ticket Promedio: ${fact_enc["total"].mean():.2f}',
                f'- Venta Mas Alta: ${fact_enc["total"].max():.2f}',
                f'- Venta Mas Baja: ${fact_enc["total"].min():.2f}',
                f'- Sucursales Activas: {fact_enc["id_sucursal"].nunique()}',
                f'- Productos Diferentes: {fact_det["id_producto"].nunique()}',
                f'- Periodo Analizado: {fact_enc["fecha"].min().strftime("%d/%m/%Y")} - {fact_enc["fecha"].max().strftime("%d/%m/%Y")}'
            ]
            
            for metrica in metricas:
                pdf.cell(0, 8, metrica, 0, 1, 'L')
            
            # ===== PÁGINA 4: TOP CLIENTES Y CONCEPTOS =====
            pdf.add_page()
            pdf.set_font('Arial', 'B', 18)
            pdf.cell(0, 10, '3. ANALISIS DE CLIENTES - EJEMPLO PRACTICO', 0, 1, 'L')
            pdf.ln(8)
            
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'TOP 10 CLIENTES POR VOLUMEN DE COMPRAS:', 0, 1, 'L')
            pdf.ln(5)
            
            # Calcular top clientes
            ventas_cliente = (
                fact_enc.groupby('id_cliente')['total']
                .sum()
                .reset_index()
                .merge(clientes[['id_cliente', 'nombre_completo']], on='id_cliente')
                .sort_values('total', ascending=False)
                .head(10)
            )
            
            pdf.set_font('Arial', '', 11)
            for i, (_, row) in enumerate(ventas_cliente.iterrows(), 1):
                pdf.cell(0, 7, f'{i:2d}. {row["nombre_completo"][:35]:35} ${row["total"]:10,.2f}', 0, 1, 'L')
            
            pdf.ln(8)
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'CONCEPTOS CLAVE PARA EL PARCIAL:', 0, 1, 'L')
            pdf.ln(5)
            
            pdf.set_font('Arial', '', 11)
            conceptos = [
                '- AGRUPAMIENTO (GROUP BY): Agrupar datos por categorias',
                '- FILTRADO: Seleccionar registros especificos',
                '- JOIN: Combinar datos de multiples tablas', 
                '- AGREGACION: Suma, promedio, conteo, maximo, minimo',
                '- ORDENAMIENTO: Ordenar resultados ascendente/descendente',
                '- EXPORTACION: Generar diferentes formatos de salida',
                '- CRUD: Operaciones basicas de base de datos',
                '- ANALISIS ESTADISTICO: Metricas descriptivas'
            ]
            
            for concepto in conceptos:
                pdf.multi_cell(0, 6, concepto)
            
            # ===== PÁGINA 5: EJEMPLOS DE CÓDIGO =====
            pdf.add_page()
            pdf.set_font('Arial', 'B', 18)
            pdf.cell(0, 10, '4. EJEMPLOS DE CODIGO - PANDAS', 0, 1, 'L')
            pdf.ln(8)
            
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'CODIGO PARA CALCULO DE VENTAS POR CLIENTE:', 0, 1, 'L')
            pdf.ln(5)
            
            pdf.set_font('Courier', '', 10)
            codigo_ejemplo = (
                "# 1. Agrupar ventas por cliente\n"
                "ventas_por_cliente = fact_enc.groupby('id_cliente')['total'].sum()\n\n"
                
                "# 2. Combinar con datos de clientes\n" 
                "resultado = ventas_por_cliente.merge(\n"
                "    clientes[['id_cliente', 'nombre']], \n"
                "    on='id_cliente'\n"
                ")\n\n"
                
                "# 3. Ordenar por ventas descendente\n"
                "resultado = resultado.sort_values('total', ascending=False)\n\n"
                
                "# 4. Mostrar top 10\n"
                "print(resultado.head(10))"
            )
            pdf.multi_cell(0, 6, codigo_ejemplo)
            
            pdf.ln(8)
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'CODIGO PARA VENTAS MENSUALES:', 0, 1, 'L')
            pdf.ln(5)
            
            pdf.set_font('Courier', '', 10)
            codigo_mensual = (
                "# 1. Extraer mes de la fecha\n"
                "fact_enc['mes'] = fact_enc['fecha'].dt.to_period('M')\n\n"
                
                "# 2. Agrupar por mes y calcular metricas\n"
                "ventas_mensuales = fact_enc.groupby('mes')['total'].agg([\n"
                "    ('ventas_totales', 'sum'),\n"
                "    ('cantidad_facturas', 'count')\n"
                "])\n\n"
                
                "# 3. Calcular promedio\n"
                "ventas_mensuales['ticket_promedio'] = \\\n"
                "    ventas_mensuales['ventas_totales'] / ventas_mensuales['cantidad_facturas']"
            )
            pdf.multi_cell(0, 6, codigo_mensual)
            
            # ===== PÁGINA 6: RESUMEN Y RECOMENDACIONES =====
            pdf.add_page()
            pdf.set_font('Arial', 'B', 18)
            pdf.cell(0, 10, '5. RESUMEN Y RECOMENDACIONES', 0, 1, 'L')
            pdf.ln(8)
            
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'PUNTOS CLAVE PARA EL PARCIAL:', 0, 1, 'L')
            pdf.ln(5)
            
            pdf.set_font('Arial', '', 11)
            puntos_clave = [
                '> Entender operaciones CRUD (Create, Read, Update, Delete)',
                '> Dominar agrupamientos y agregaciones con GROUP BY',
                '> Saber combinar tablas con merge/join',
                '> Conocer funciones de fechas en pandas',
                '> Poder exportar a diferentes formatos',
                '> Interpretar metricas estadisticas basicas',
                '> Escribir consultas eficientes',
                '> Validar y limpiar datos antes del analisis'
            ]
            
            for punto in puntos_clave:
                pdf.cell(0, 7, punto, 0, 1, 'L')
            
            pdf.ln(8)
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'PRACTICA RECOMENDADA:', 0, 1, 'L')
            pdf.ln(5)
            
            pdf.set_font('Arial', '', 11)
            practica = (
                "1. Ejecutar cada funcion del sistema y entender que hace\n"
                "2. Modificar los datos y observar cambios en los reportes\n"
                "3. Probar diferentes tipos de analisis\n"
                "4. Revisar el codigo fuente para entender la implementacion\n"
                "5. Crear tus propios analisis basados en este modelo"
            )
            pdf.multi_cell(0, 7, practica)
            
            # Guardar archivo
            PDF_OUTPUT = os.path.join(SCRIPT_DIR, "pdf_salida")
            os.makedirs(PDF_OUTPUT, exist_ok=True)
            archivo_pdf = os.path.join(PDF_OUTPUT, f"guia_estudio_parcial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            pdf.output(archivo_pdf)
            
            print("✅ Guía de estudio PDF generada exitosamente!")
            print(f"   📁 Ubicación: {archivo_pdf}")
            print(f"   📄 Páginas: {pdf.page_no()} páginas de contenido educativo")
            
        except Exception as e:
            print(f"❌ Error generando PDF: {e}")
    
    # Menú principal
    while True:
        print("\n" + "="*60)
        print("🏪 SISTEMA DE GESTIÓN DE VENTAS - VERSIÓN COMPLETA")
        print("="*60)
        print("1. 🎯 Gestión de Datos (CRUD)")
        print("2. 📊 Generar Reportes CSV Individuales")
        print("3. 📤 Exportar a JSON")
        print("4. 📤 Exportar a Excel") 
        print("5. 📄 Generar Reporte PDF")
        print("6. 🔄 Recargar Datos")
        print("0. 🚪 Salir")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            if menu_crud():
                cargar_datos()
        elif opcion == "2":
            generar_reportes_csv()
        elif opcion == "3":
            exportar_a_json()
        elif opcion == "4":
            exportar_a_excel()
        elif opcion == "5":
            generar_reporte_pdf_simple()  # Llamar a la función local
        elif opcion == "6":
            cargar_datos()
        elif opcion == "0":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")
# ---------------------------------------------
# EJECUCIÓN PRINCIPAL
# ---------------------------------------------

if __name__ == "__main__":
    print("🚀 INICIANDO SISTEMA DE GESTIÓN DE VENTAS")
    print("   • CRUD para CSV")
    print("   • Análisis de datos") 
    print("   • Exportación JSON y Excel")
    print("   • Carpeta 'json_salida/' para JSON")
    print("   • Carpeta 'excel_salida/' para Excel")
    
    if cargar_datos():
        menu_principal()
    else:
        print("❌ No se pudieron cargar los datos iniciales")
        
