import pandas as pd
import os
import glob

# ==========================================
#   CONFIGURACIÓN
# ==========================================
OUTPUT_FILE = 'DOE_Completo_Minitab.xlsx'
PATTERN = 'Graficos_*.xlsx'

# Columnas que consideraremos "de entrada" (Fijas)
# Estas se copiarán una sola vez al principio del archivo
COLS_ENTRADA = [
    'ID_Familia', 
    'Potencia (W)', 
    'Frecuencia (kHz)', 
    'Velocidad (mm/s)', 
    'Ancho_Pulso (ns)'
    # Puedes añadir 'Densidad_Energia' o 'Solapamiento' si quieres
]

# ==========================================
#   SCRIPT
# ==========================================

print("--- GENERADOR DE DOE MAESTRO ---")

# 1. Buscar archivos
archivos = glob.glob(PATTERN)
print(f"Se han encontrado {len(archivos)} archivos de parámetros.")

if not archivos:
    print("Error: No he encontrado ningún archivo que empiece por 'Graficos_'.")
    exit()

# Ordenar archivos alfabéticamente para que las columnas salgan ordenadas
archivos.sort()

# 2. Inicializar el DataFrame Maestro
# Leemos el primero para coger las columnas de configuración (Potencia, Frecuencia...)
print("Inicializando archivo maestro...")
try:
    df_base = pd.read_excel(archivos[0])
except:
    # Fallback por si alguno está en formato CSV camuflado
    df_base = pd.read_csv(archivos[0], encoding='latin1')

# Normalizar nombres de columnas (quitar espacios extra)
df_base.columns = [c.strip() for c in df_base.columns]

# Verificamos que tenga las columnas clave
columnas_existentes = [c for c in COLS_ENTRADA if c in df_base.columns]
if not columnas_existentes:
    print(f"Error crítico: El archivo {archivos[0]} no tiene las columnas de Potencia/Frecuencia.")
    print("Columnas encontradas:", df_base.columns.tolist())
    exit()

# Creamos el DataFrame Maestro solo con las entradas
df_master = df_base[columnas_existentes].copy()

# 3. Iterar sobre todos los archivos para añadir los Resultados
for archivo in archivos:
    nombre_parametro = os.path.basename(archivo).replace('Graficos_', '').replace('.xlsx', '')
    print(f"Procesando: {nombre_parametro}...")
    
    try:
        df_temp = pd.read_excel(archivo)
    except:
        try:
            df_temp = pd.read_csv(archivo, encoding='latin1')
        except:
            print(f"  -> Error leyendo {archivo}, saltando.")
            continue
            
    df_temp.columns = [c.strip() for c in df_temp.columns]
    
    # Identificar la columna del dato
    # La lógica es: Buscar una columna que se llame como el parámetro o contenga su nombre
    # y que NO sea una de las columnas de entrada.
    col_dato = None
    
    # Caso especial: Angle
    if nombre_parametro == 'Angle':
        cols_angle = [c for c in df_temp.columns if 'Angulo' in c or 'Angle' in c]
        if cols_angle: col_dato = cols_angle[0]
    else:
        # Caso general (Ra, Sa, etc.)
        # Buscamos columnas que contengan "Ra" pero ignoramos "Densidad" o "Frecuencia"
        posibles = [c for c in df_temp.columns if nombre_parametro.lower() == c.lower() or 
                    (nombre_parametro.lower() in c.lower() and '(' in c)]
        
        # Filtramos para no coger columnas de entrada por error
        posibles = [c for c in posibles if c not in columnas_existentes and 'Densidad' not in c and 'Solapamiento' not in c]
        
        if posibles:
            col_dato = posibles[0] # Cogemos la primera coincidencia
            
    if col_dato:
        # Renombramos la columna al nombre simple del parámetro para el Excel final
        # (ej. "Ra_Promedio (µm)" -> "Ra")
        # O si prefieres mantener unidades, comenta la siguiente línea
        nuevo_nombre = nombre_parametro 
        
        subset = df_temp[['ID_Familia', col_dato]].rename(columns={col_dato: nuevo_nombre})
        
        # Hacemos MERGE usando el ID_Familia para asegurar que los datos no se desordenan
        df_master = pd.merge(df_master, subset, on='ID_Familia', how='left')
    else:
        print(f"  -> ADVERTENCIA: No encontré la columna de datos en {archivo}")

# 4. Limpieza Final
# Ordenar por ID
if 'ID_Familia' in df_master.columns:
    df_master = df_master.sort_values('ID_Familia')

# Guardar
df_master.to_excel(OUTPUT_FILE, index=False)
print(f"\n¡ÉXITO! Archivo generado: {OUTPUT_FILE}")
print(f"Tiene {len(df_master)} filas y las columnas: {df_master.columns.tolist()}")