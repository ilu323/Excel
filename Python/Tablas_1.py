import pandas as pd
import os

# ==========================================
#   CONFIGURACIÓN DE USUARIO (CAMBIA ESTO)
# ==========================================
# 1. El parámetro que quieres extraer y promediar (ej: 'Ra', 'Rz', 'Rq', 'Rp', 'Rv')
PARAMETRO_OBJETIVO = 'Svk'  

# 2. La unidad de medida (solo para que quede bonito en el Excel final)
UNIDAD = '(µm)'

# 3. Nombres de las columnas en tu Excel original (Datos_Totales_Con_Rugosidad)
# NOTA: Para rugosidad, suelen terminar en ".3". Si usas otros datos, revisa estos nombres.
COL_FUENTE = 'FUENTE SUP. TIPO 1'
COL_POTENCIA = 'Potencia.3'
COL_FRECUENCIA = 'Frecuencia.3'
COL_VELOCIDAD = 'Velocidad.3'
COL_ANCHO_PULSO = 'Ancho de Pulso.3'
# Asegúrate de que estas columnas existen en tu Excel, o coméntalas si no las tienes
COL_DENSIDAD = 'Densidad de energía.3' 
COL_SOLAPAMIENTO = 'solapamiento.3' 

# Archivo de entrada
FILE_PATH = 'Datos_Totales_Con_Rugosidad.xlsx'

# ==========================================
#   FIN DE LA CONFIGURACIÓN
# ==========================================

print(f"--- PROCESANDO DATOS PARA: {PARAMETRO_OBJETIVO} ---")

# 1. Cargar el archivo original
if not os.path.exists(FILE_PATH):
    print(f"ERROR: No encuentro el archivo '{FILE_PATH}'")
    exit()

print("Cargando Excel (esto puede tardar unos segundos)...")
try:
    df = pd.read_excel(FILE_PATH)
except:
    # Fallback por si acaso es un CSV disfrazado
    df = pd.read_csv(FILE_PATH, encoding='latin1')

# Limpieza de espacios en nombres de columnas
df.columns = [c.strip() for c in df.columns]

# 2. Verificar que las columnas existen
cols_needed = [
    COL_FUENTE, PARAMETRO_OBJETIVO, 
    COL_POTENCIA, COL_FRECUENCIA, COL_VELOCIDAD, 
    COL_ANCHO_PULSO, COL_DENSIDAD, COL_SOLAPAMIENTO
]

# Comprobación de seguridad
missing_cols = [c for c in cols_needed if c not in df.columns]
if missing_cols:
    print("¡ERROR! No encuentro las siguientes columnas en tu Excel:")
    print(missing_cols)
    print("Revisa la sección de CONFIGURACIÓN al principio del script.")
    exit()

# Seleccionar datos
df_work = df[cols_needed].copy()

# 3. Limpieza de datos
# Eliminar filas donde no haya datos del parámetro objetivo
df_work = df_work.dropna(subset=[PARAMETRO_OBJETIVO])
# Rellenar los nombres de archivo hacia abajo (ffill)
df_work[COL_FUENTE] = df_work[COL_FUENTE].ffill()

# 4. Lógica de Agrupación por Familia
def extract_family(filename):
    try:
        return int(str(filename).split('_')[0])
    except:
        return None

df_work['ID_Familia'] = df_work[COL_FUENTE].apply(extract_family)

# Eliminamos filas donde no se pudo identificar la familia
df_work = df_work.dropna(subset=['ID_Familia'])

# 5. Agrupar y Calcular Promedios
print("Agrupando por familias y calculando medias...")
df_resumen = df_work.groupby('ID_Familia').agg({
    PARAMETRO_OBJETIVO: 'mean',     # Promediamos el parámetro (Ra, Rz...)
    COL_POTENCIA: 'first',          # Datos constantes, tomamos el primero
    COL_FRECUENCIA: 'first',
    COL_VELOCIDAD: 'first',
    COL_ANCHO_PULSO: 'first',
    COL_DENSIDAD: 'first',
    COL_SOLAPAMIENTO: 'first'
}).reset_index()

# 6. Renombrar columnas para el Excel final (Estandarización)
df_resumen.columns = [
    'ID_Familia', 
    f'{PARAMETRO_OBJETIVO}',       # Mantenemos el nombre simple para que el otro script lo encuentre fácil
    'Potencia (W)', 
    'Frecuencia (kHz)', 
    'Velocidad (mm/s)', 
    'Ancho_Pulso (ns)',
    'Densidad_Energia', 
    'Solapamiento'
]

# 7. Ordenar
df_resumen = df_resumen.sort_values('ID_Familia')

# 8. Exportar
output_file = f'Graficos_{PARAMETRO_OBJETIVO}.xlsx'
df_resumen.to_excel(output_file, index=False)

print(f"¡ÉXITO! Se ha creado el archivo: {output_file}")
print(f"Filas generadas: {len(df_resumen)} (Deberían ser 81)")
print(f"Ahora puedes usar este archivo con el script de 'Analisis_Unificado'.")