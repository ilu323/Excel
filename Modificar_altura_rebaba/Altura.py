import pandas as pd
import numpy as np

# Configuración
ARCHIVO_ENTRADA = 'Datos_Totales_Corregidos.xlsx'
ARCHIVO_SALIDA = 'Altura_Rebaba_Individual_Por_Ranura.xlsx'

print(f"--- Procesando {ARCHIVO_ENTRADA} ---")

# 1. Cargar Datos
try:
    df = pd.read_excel(ARCHIVO_ENTRADA)
except:
    try:
        df = pd.read_csv(ARCHIVO_ENTRADA, encoding='latin1')
    except Exception as e:
        print(f"Error leyendo archivo: {e}")
        exit()

# Limpiar nombres de columnas
df.columns = [c.strip() for c in df.columns]

# 2. Filtrar columnas necesarias (Bloque FUENTE LINE)
cols_necesarias = [
    'FUENTE LINE', 'ID', 'P1 Y', 'P2 Y',
    'Potencia.1', 'Frecuencia.1', 'Velocidad.1', 'Ancho de Pulso.1', 
    'Densidad de energía.1', 'solapamiento.1'
]

# Verificar que existen las columnas
if 'FUENTE LINE' not in df.columns:
    print("Error: No se encuentra la columna 'FUENTE LINE'.")
    exit()

df_work = df[cols_necesarias].copy()
df_work = df_work.dropna(subset=['FUENTE LINE', 'ID'])

# 3. Extraer ID Numérico de la Línea (Line 1 -> 1, Line 2 -> 2...)
# Esto es crucial porque el formato "Line 1" no sirve para matemáticas
df_work['ID_Num'] = df_work['ID'].astype(str).str.extract(r'(\d+)').astype(float)
df_work = df_work.dropna(subset=['ID_Num'])
df_work['ID_Num'] = df_work['ID_Num'].astype(int)

# 4. Pivotar la tabla
# Queremos una fila por cada archivo (FUENTE LINE), con columnas para Line 1, Line 2, etc.
pivot_df = df_work.pivot_table(
    index='FUENTE LINE',
    columns='ID_Num',
    values=['P1 Y', 'P2 Y'],
    aggfunc='first'
)

# Aplanar nombres de columnas (ej: 'P1 Y' de 'Line 1' -> 'P1 Y_L1')
pivot_df.columns = [f'{col[0]}_L{col[1]}' for col in pivot_df.columns]
pivot_df = pivot_df.reset_index()

# 5. Calcular Geometría
# Altura Rebaba = Altura (Line 2) - Altura Referencia (Line 1)
# Usamos P2 Y para la cima de la rebaba y P1 Y para la referencia
if 'P2 Y_L2' in pivot_df.columns and 'P1 Y_L1' in pivot_df.columns:
    pivot_df['Altura_Rebaba'] = pivot_df['P2 Y_L2'] - pivot_df['P1 Y_L1']
else:
    pivot_df['Altura_Rebaba'] = np.nan

# Profundidad = Referencia (Line 1) - Fondo (Line 3)
if 'P1 Y_L1' in pivot_df.columns and 'P2 Y_L3' in pivot_df.columns:
    pivot_df['Profundidad'] = (pivot_df['P1 Y_L1'] - pivot_df['P2 Y_L3']).abs()
else:
    pivot_df['Profundidad'] = np.nan

# 6. Recuperar Parámetros del Láser
# Tomamos los parámetros originales (son iguales para todas las líneas del mismo archivo)
params_cols = ['FUENTE LINE', 'Potencia.1', 'Frecuencia.1', 'Velocidad.1', 
               'Ancho de Pulso.1', 'Densidad de energía.1', 'solapamiento.1']
df_params = df_work[params_cols].drop_duplicates(subset=['FUENTE LINE'])

# Unir todo
df_final = pd.merge(pivot_df, df_params, on='FUENTE LINE', how='inner')

# Extraer ID Familia para ordenar
def extract_family(val):
    try:
        return int(str(val).split('_')[0])
    except:
        return 9999

df_final['ID_Familia'] = df_final['FUENTE LINE'].apply(extract_family)

# Ordenar y Seleccionar columnas finales
df_final = df_final.sort_values(by=['ID_Familia', 'FUENTE LINE'])

cols_finales = [
    'ID_Familia', 'FUENTE LINE', 'Altura_Rebaba', 'Profundidad',
    'Potencia.1', 'Frecuencia.1', 'Velocidad.1', 
    'Ancho de Pulso.1', 'Densidad de energía.1', 'solapamiento.1'
]
# Filtrar solo las que existan (por si acaso faltó profundidad)
cols_finales = [c for c in cols_finales if c in df_final.columns]

df_export = df_final[cols_finales].rename(columns={
    'Potencia.1': 'Potencia (W)',
    'Frecuencia.1': 'Frecuencia (kHz)',
    'Velocidad.1': 'Velocidad (mm/s)',
    'Ancho de Pulso.1': 'Ancho_Pulso (ns)',
    'Densidad de energía.1': 'Densidad_Energia',
    'solapamiento.1': 'Solapamiento'
})

# Guardar
df_export.to_excel(ARCHIVO_SALIDA, index=False)
print(f"¡Éxito! Archivo generado: {ARCHIVO_SALIDA}")
print(f"Filas generadas: {len(df_export)}")