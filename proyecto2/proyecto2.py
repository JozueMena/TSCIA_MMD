# =============================================
# Proyecto 2 - Análisis Predictivo de Recompra
# Autor: Josué Gabriel Mena
# Descripción: Análisis de recompra usando dataset real de promociones
# =============================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix
import os
import warnings
warnings.filterwarnings('ignore')

# ---------------------------------------------
# 1. CONFIGURACIÓN INICIAL
# ---------------------------------------------
print("=" * 60)
print("PROYECTO 2 - ANÁLISIS PREDICTIVO DE RECOMPRA")
print("=" * 60)

# Configurar estilo de gráficos
plt.style.use('default')
sns.set_palette("husl")

# ---------------------------------------------
# 2. CARGA Y VERIFICACIÓN DE DATOS
# ---------------------------------------------
print("\n📥 CARGANDO DATOS DESDE EXCEL...")

# Buscar el archivo Excel
archivo_excel = "Mini_Proyecto_Clientes_Promociones.xlsx"

if not os.path.exists(archivo_excel):
    print(f"❌ ERROR: No se encuentra el archivo '{archivo_excel}'")
    print("📂 Buscando archivos Excel en el directorio actual...")
    
    archivos_excel = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xls'))]
    if archivos_excel:
        print("✅ Archivos Excel encontrados:")
        for archivo in archivos_excel:
            print(f"   - {archivo}")
        archivo_excel = archivos_excel[0]
        print(f"📁 Usando archivo: {archivo_excel}")
    else:
        print("❌ No se encontraron archivos Excel en el directorio")
        exit()

try:
    # Cargar el dataset real
    df = pd.read_excel(archivo_excel)
    print(f"✅ DATASET CARGADO EXITOSAMENTE")
    print(f"📊 Dimensiones: {df.shape[0]} filas, {df.shape[1]} columnas")
    
except Exception as e:
    print(f"❌ ERROR al cargar el archivo: {e}")
    exit()

# ---------------------------------------------
# 3. EXPLORACIÓN INICIAL DE DATOS
# ---------------------------------------------
print("\n🔍 EXPLORACIÓN INICIAL DE DATOS...")

print("\n📋 PRIMERAS 5 FILAS:")
print(df.head())

print("\n📝 INFORMACIÓN GENERAL:")
print(df.info())

print("\n📊 ESTADÍSTICAS DESCRIPTIVAS:")
print(df.describe())

print("\n🔢 DISTRIBUCIÓN DE VARIABLES CATEGÓRICAS:")
print("Género:")
print(df['Genero'].value_counts())
print("\nRecibió Promoción:")
print(df['Recibio_Promo'].value_counts())
print("\nRecompra:")
print(df['Recompra'].value_counts())

print("\n🔍 VALORES NULOS:")
print(df.isnull().sum())

# ---------------------------------------------
# 4. ANÁLISIS ESTADÍSTICO INICIAL
# ---------------------------------------------
print("\n📈 ANÁLISIS ESTADÍSTICO INICIAL...")

# Tasa de recompra general
tasa_recompra = (df['Recompra'] == 'Si').mean() * 100
print(f"📊 Tasa general de recompra: {tasa_recompra:.1f}%")

# Tasa de recompra por promoción
recompra_con_promo = (df[df['Recibio_Promo'] == 'Si']['Recompra'] == 'Si').mean() * 100
recompra_sin_promo = (df[df['Recibio_Promo'] == 'No']['Recompra'] == 'Si').mean() * 100

print(f"📊 Recompra CON promoción: {recompra_con_promo:.1f}%")
print(f"📊 Recompra SIN promoción: {recompra_sin_promo:.1f}%")
print(f"📈 Diferencia: {recompra_con_promo - recompra_sin_promo:.1f} puntos porcentuales")

# ---------------------------------------------
# 5. TRANSFORMACIÓN Y CODIFICACIÓN
# ---------------------------------------------
print("\n🔄 TRANSFORMANDO VARIABLES CATEGÓRICAS...")

# Hacer copia para no modificar el original
df_encoded = df.copy()

# Codificar variables categóricas a numéricas
df_encoded['Genero'] = df_encoded['Genero'].map({'F': 0, 'M': 1})
df_encoded['Recibio_Promo'] = df_encoded['Recibio_Promo'].map({'Si': 1, 'No': 0})
df_encoded['Recompra'] = df_encoded['Recompra'].map({'Si': 1, 'No': 0})

print("✅ Variables codificadas correctamente")
print(df_encoded[['Genero', 'Recibio_Promo', 'Recompra']].head())

# ---------------------------------------------
# 6. VISUALIZACIÓN DE RELACIONES CLAVE
# ---------------------------------------------
print("\n📊 CREANDO VISUALIZACIONES...")

# Crear figura con múltiples subplots
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('ANÁLISIS DE RECOMPRA - DATASET REAL', fontsize=16, fontweight='bold')

# Gráfico 1: Recompra vs Monto de Promoción
sns.boxplot(data=df, x='Recompra', y='Monto_Promo', ax=axes[0,0])
axes[0,0].set_title('Recompra vs Monto de Promoción')
axes[0,0].set_xlabel('¿Recompró?')
axes[0,0].set_ylabel('Monto de Promoción ($)')

# Gráfico 2: Recompra vs Ingreso Mensual
sns.boxplot(data=df, x='Recompra', y='Ingreso_Mensual', ax=axes[0,1])
axes[0,1].set_title('Recompra vs Ingreso Mensual')
axes[0,1].set_xlabel('¿Recompró?')
axes[0,1].set_ylabel('Ingreso Mensual ($)')

# Gráfico 3: Distribución por Género y Recompra
pd.crosstab(df['Genero'], df['Recompra']).plot(kind='bar', ax=axes[1,0])
axes[1,0].set_title('Recompra por Género')
axes[1,0].set_xlabel('Género')
axes[1,0].set_ylabel('Cantidad de Clientes')
axes[1,0].legend(title='Recompra')

# Gráfico 4: Total de Compras vs Recompra
sns.boxplot(data=df, x='Recompra', y='Total_Compras', ax=axes[1,1])
axes[1,1].set_title('Recompra vs Total de Compras')
axes[1,1].set_xlabel('¿Recompró?')
axes[1,1].set_ylabel('Total de Compras')

plt.tight_layout()
plt.savefig('analisis_recompra_real.png', dpi=300, bbox_inches='tight')
plt.show()

# Gráfico adicional: Efecto de la Promoción
plt.figure(figsize=(10, 6))
sns.countplot(data=df, x='Recibio_Promo', hue='Recompra')
plt.title('EFECTO DE LA PROMOCIÓN EN LA RECOMPRA - DATASET REAL')
plt.xlabel('¿Recibió Promoción?')
plt.ylabel('Cantidad de Clientes')
plt.legend(title='¿Recompró?')
plt.savefig('promocion_recompra_real.png', dpi=300, bbox_inches='tight')
plt.show()

# ---------------------------------------------
# 7. ANÁLISIS DE CORRELACIONES
# ---------------------------------------------
print("\n📈 ANALIZANDO CORRELACIONES...")

# Matriz de correlación
correlation_matrix = df_encoded.corr()

plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
            square=True, linewidths=0.5)
plt.title('MATRIZ DE CORRELACIÓN - VARIABLES DEL DATASET')
plt.tight_layout()
plt.savefig('matriz_correlacion.png', dpi=300, bbox_inches='tight')
plt.show()

print("📊 Matriz de correlación con variable objetivo 'Recompra':")
print(correlation_matrix['Recompra'].sort_values(ascending=False))

# ---------------------------------------------
# 8. MODELADO PREDICTIVO - CLASIFICACIÓN
# ---------------------------------------------
print("\n🤖 ENTRENANDO MODELO PREDICTIVO...")

# Preparar datos para el modelo
X = df_encoded.drop(['Cliente_ID', 'Recompra'], axis=1)
y = df_encoded['Recompra']

print("🔧 Variables utilizadas en el modelo:")
for i, col in enumerate(X.columns):
    print(f"   {i+1}. {col}")

# Dividir en conjunto de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n📊 División de datos:")
print(f"   Entrenamiento: {X_train.shape[0]} muestras")
print(f"   Prueba: {X_test.shape[0]} muestras")

# Entrenar modelo de Árbol de Decisión
modelo = DecisionTreeClassifier(random_state=42, max_depth=3)
modelo.fit(X_train, y_train)

# Predecir en conjunto de prueba
y_pred = modelo.predict(X_test)

# ---------------------------------------------
# 9. EVALUACIÓN DEL MODELO
# ---------------------------------------------
print("\n📋 EVALUANDO EL MODELO...")

print("🔢 MATRIZ DE CONFUSIÓN:")
cm = confusion_matrix(y_test, y_pred)
print(cm)

print("\n📊 REPORTE DE CLASIFICACIÓN:")
print(classification_report(y_test, y_pred))

# Calcular accuracy
accuracy = (y_pred == y_test).mean() * 100
print(f"\n🎯 PRECISIÓN DEL MODELO: {accuracy:.1f}%")

# ---------------------------------------------
# 10. ANÁLISIS DE IMPORTANCIA DE VARIABLES
# ---------------------------------------------
print("\n🔍 ANALIZANDO IMPORTANCIA DE VARIABLES...")

importancias = modelo.feature_importances_
features = X.columns

plt.figure(figsize=(10, 6))
sns.barplot(x=importancias, y=features, palette='viridis')
plt.title('IMPORTANCIA DE VARIABLES EN LA PREDICCIÓN DE RECOMPRA')
plt.xlabel('Importancia')
plt.ylabel('Variables')
plt.tight_layout()
plt.savefig('importancia_variables_real.png', dpi=300, bbox_inches='tight')
plt.show()

print("📊 Importancia de variables:")
for feature, importancia in zip(features, importancias):
    print(f"   {feature}: {importancia:.3f}")

# ---------------------------------------------
# 11. ANÁLISIS DE SEGMENTOS Y RECOMENDACIONES
# ---------------------------------------------
print("\n💡 ANÁLISIS DE SEGMENTOS Y RECOMENDACIONES...")

# Segmentar clientes
segmento_recompra = df[df['Recompra'] == 'Si']
segmento_no_recompra = df[df['Recompra'] == 'No']

print(f"\n📈 CLIENTES QUE RECOMPRARON ({len(segmento_recompra)} clientes):")
print(f"   • Edad promedio: {segmento_recompra['Edad'].mean():.1f} años")
print(f"   • Ingreso promedio: ${segmento_recompra['Ingreso_Mensual'].mean():.0f}")
print(f"   • Total compras promedio: {segmento_recompra['Total_Compras'].mean():.1f}")
print(f"   • % que recibió promoción: {(segmento_recompra['Recibio_Promo'] == 'Si').mean() * 100:.1f}%")

print(f"\n📉 CLIENTES QUE NO RECOMPRARON ({len(segmento_no_recompra)} clientes):")
print(f"   • Edad promedio: {segmento_no_recompra['Edad'].mean():.1f} años")
print(f"   • Ingreso promedio: ${segmento_no_recompra['Ingreso_Mensual'].mean():.0f}")
print(f"   • Total compras promedio: {segmento_no_recompra['Total_Compras'].mean():.1f}")
print(f"   • % que recibió promoción: {(segmento_no_recompra['Recibio_Promo'] == 'Si').mean() * 100:.1f}%")

# ---------------------------------------------
# 12. GUARDAR RESULTADOS
# ---------------------------------------------
print("\n💾 GUARDANDO RESULTADOS...")

# Guardar dataset procesado
df_encoded.to_csv('dataset_procesado.csv', index=False)

print("✅ ARCHIVOS GUARDADOS:")
print("   • analisis_recompra_real.png")
print("   • promocion_recompra_real.png")
print("   • matriz_correlacion.png")
print("   • importancia_variables_real.png")
print("   • dataset_procesado.csv")

# ---------------------------------------------
# 13. CONCLUSIONES Y RECOMENDACIONES FINALES
# ---------------------------------------------
print("\n" + "=" * 60)
print("📋 CONCLUSIONES Y RECOMENDACIONES FINALES")
print("=" * 60)

print(f"\n🎯 HALLAZGOS PRINCIPALES:")
print(f"   1. La promoción aumenta la recompra en {recompra_con_promo - recompra_sin_promo:.1f}%")
print(f"   2. Modelo predictivo con {accuracy:.1f}% de precisión")
print(f"   3. Variable más importante: {features[np.argmax(importancias)]}")

print(f"\n💡 RECOMENDACIONES PARA MARKETING:")
print(f"   1. ENFOCAR promociones en clientes con: {features[np.argmax(importancias)]} alto")
print(f"   2. OPTIMIZAR montos de promoción basado en análisis de correlación")
print(f"   3. SEGMENTAR campañas por edad y nivel de ingresos")

print(f"\n📊 RESUMEN EJECUTIVO:")
print(f"   • Dataset: {df.shape[0]} clientes analizados")
print(f"   • Tasa recompra general: {tasa_recompra:.1f}%")
print(f"   • Efecto promoción: +{recompra_con_promo - recompra_sin_promo:.1f}%")
print(f"   • Precisión modelo: {accuracy:.1f}%")

print("=" * 60)
print("✅ PROYECTO 2 COMPLETADO EXITOSAMENTE")
print("=" * 60)