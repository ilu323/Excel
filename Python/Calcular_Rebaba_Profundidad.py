import pandas as pd
import numpy as np

# Configuración de Archivos
input_file = 'Datos_Totales_Con_Rugosidad.xlsx'
output_rebaba = 'Graficos_Altura_Rebaba.xlsx'
output_profundidad = 'Graficos_Profundidad.xlsx'

print("--- INICIANDO CÁLCULO DE GEOMETRÍA (REBABA Y PROFUNDIDAD) ---")

# 1. Cargar Datos
try:
    df = pd.read_excel(input_file)
except:
    try:
        df = pd.read_csv(input_file, encoding='latin1')
    except:
        try:
            df = pd.read_csv(input_file, encoding='utf-8')
        except:
             print(f"ERROR: No se puede leer el archivo {input_file}")
             exit()

# Limpieza de columnas
df.columns = [c.strip() for c in df.columns]

# 2. Selección de Columnas Clave (Sección FUENTE LINE)
cols_necesarias = [
    'FUENTE LINE', 'ID', 'P1 Y', 'P2 Y',
    'Potencia.1', 'Frecuencia.1', 'Velocidad.1', 'Ancho de Pulso.1', 
    'Densidad de energía.1', 'solapamiento.1'
]

# Filtrar solo si existe FUENTE LINE
if 'FUENTE LINE' not in df.columns:
    print("ERROR: No encuentro la columna 'FUENTE LINE'.")
    exit()

df_work = df[cols_necesarias].copy()
df_work = df_work.dropna(subset=['FUENTE LINE', 'ID'])

# --- CORRECCIÓN CLAVE AQUÍ ---
# Extraemos el número del texto (ej: "Line 1" -> 1)
df_work['ID_Num'] = df_work['ID'].astype(str).str.extract(r'(\d+)').astype(float)
df_work = df_work.dropna(subset=['ID_Num'])
df_work['ID_Num'] = df_work['ID_Num'].astype(int)

# 3. Pivotar Tabla
# Usamos 'ID_Num' en vez de 'ID'
pivot_df = df_work.pivot_table(
    index='FUENTE LINE', 
    columns='ID_Num', 
    values=['P1 Y', 'P2 Y'],
    aggfunc='first'
)

# Aplanar columnas (ej: ('P1 Y', 1) -> 'P1Y_L1')
pivot_df.columns = [f'{col[0]}_L{col[1]}' for col in pivot_df.columns]
pivot_df = pivot_df.reset_index()

# Verificar columnas necesarias
required_cols = ['P1 Y_L1', 'P2 Y_L2', 'P2 Y_L3']
missing = [c for c in required_cols if c not in pivot_df.columns]

if missing:
    print(f"ADVERTENCIA CRÍTICA: Faltan las columnas: {missing}")
    print("Verifica que tus IDs en el Excel sean 'Line 1', 'Line 2', etc.")
    # Rellenar con NaN para que no falle el script, aunque los datos saldrán vacíos
    for c in missing:
        pivot_df[c] = np.nan
else:
    print("Datos de líneas encontrados correctamente.")

# 4. Cálculos Matemáticos
# Altura Rebaba = Altura Rebaba Absoluta (L2, P2) - Referencia (L1, P1)
pivot_df['Altura_Rebaba'] = pivot_df['P2 Y_L2'] - pivot_df['P1 Y_L1']

# Profundidad = Referencia (L1, P1) - Profundidad Absoluta (L3, P2)
# Usamos valor absoluto por si el sistema de coordenadas está invertido
pivot_df['Profundidad'] = (pivot_df['P1 Y_L1'] - pivot_df['P2 Y_L3']).abs()

# 5. Recuperar Parámetros y Agrupar
params_df = df_work[['FUENTE LINE', 'Potencia.1', 'Frecuencia.1', 'Velocidad.1', 
                     'Ancho de Pulso.1', 'Densidad de energía.1', 'solapamiento.1']].drop_duplicates('FUENTE LINE')

df_final = pd.merge(pivot_df, params_df, on='FUENTE LINE', how='inner')

# Extraer ID Familia (ej: "1_1..." -> 1)
def extract_family(val):
    try:
        return int(str(val).split('_')[0])
    except:
        return None

df_final['ID_Familia'] = df_final['FUENTE LINE'].apply(extract_family)
df_final = df_final.dropna(subset=['ID_Familia'])
df_final = df_final.sort_values('ID_Familia')

# Calcular Medias por Familia
df_resumen = df_final.groupby('ID_Familia').agg({
    'Altura_Rebaba': 'mean',
    'Profundidad': 'mean',
    'Potencia.1': 'first',
    'Frecuencia.1': 'first',
    'Velocidad.1': 'first',
    'Ancho de Pulso.1': 'first',
    'Densidad de energía.1': 'first',
    'solapamiento.1': 'first'
}).reset_index()

# 6. Exportar
# --- Excel 1: REBABA ---
df_rebaba = df_resumen[[
    'ID_Familia', 'Altura_Rebaba', 
    'Potencia.1', 'Frecuencia.1', 'Velocidad.1', 
    'Ancho de Pulso.1', 'Densidad de energía.1', 'solapamiento.1'
]].copy()

df_rebaba.columns = [
    'ID_Familia', 'Altura_Rebaba (mm)', # Asumo mm por los valores típicos, cambia a µm si es necesario
    'Potencia (W)', 'Frecuencia (kHz)', 'Velocidad (mm/s)', 
    'Ancho_Pulso (ns)', 'Densidad_Energia', 'Solapamiento'
]
df_rebaba.to_excel(output_rebaba, index=False)
print(f"-> Generado: {output_rebaba}")

# --- Excel 2: PROFUNDIDAD ---
df_prof = df_resumen[[
    'ID_Familia', 'Profundidad', 
    'Potencia.1', 'Frecuencia.1', 'Velocidad.1', 
    'Ancho de Pulso.1', 'Densidad de energía.1', 'solapamiento.1'
]].copy()

df_prof.columns = [
    'ID_Familia', 'Profundidad (mm)', 
    'Potencia (W)', 'Frecuencia (kHz)', 'Velocidad (mm/s)', 
    'Ancho_Pulso (ns)', 'Densidad_Energia', 'Solapamiento'
]
df_prof.to_excel(output_profundidad, index=False)
print(f"-> Generado: {output_profundidad}")

print("\n¡Proceso completado con éxito!")