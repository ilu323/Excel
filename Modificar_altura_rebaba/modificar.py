import pandas as pd
import numpy as np

# Configuración de archivos
input_file = 'Altura_Rebaba_Individual_Por_Ranura.xlsx'
output_file = 'Datos_Profundidad.xlsx' # Nombre del nuevo archivo

print(f"--- PROCESANDO: {input_file} ---")

# 1. Cargar el archivo con los datos individuales
try:
    df = pd.read_excel(input_file)
except:
    # Intento alternativo por si es un CSV con extensión .xlsx
    try:
        df = pd.read_csv(input_file, encoding='latin1')
    except:
        print(f"ERROR: No se puede leer el archivo {input_file}")
        exit()

# Limpiar espacios en nombres de columnas
df.columns = [c.strip() for c in df.columns]

# 2. Verificar columnas necesarias
required_cols = ['ID_Familia', 'Profundidad']
if not all(col in df.columns for col in required_cols):
    print(f"ERROR: Faltan columnas clave. Se requieren: {required_cols}")
    print(f"Columnas encontradas: {df.columns.tolist()}")
    exit()

# 3. Agrupar por Familia y Calcular Promedios
# Agrupamos por ID_Familia y:
# - Altura_Rebaba: Calculamos la media (mean)
# - Resto de parámetros: Tomamos el primer valor (first) ya que son constantes para la familia
print("Calculando promedios por familia...")

df_agrupado = df.groupby('ID_Familia').agg({
    'Profundidad': 'mean',
    'Potencia (W)': 'first',
    'Frecuencia (kHz)': 'first',
    'Velocidad (mm/s)': 'first',
    'Ancho_Pulso (ns)': 'first',
    'Densidad_Energia': 'first',
    'Solapamiento': 'first'
}).reset_index()

# 4. Renombrar columnas para que coincidan con el formato deseado
df_agrupado = df_agrupado.rename(columns={
    'Profundidad': 'Profundidad (µm)' # Añadimos la unidad al nombre
})

# 5. Ordenar y Guardar
df_agrupado = df_agrupado.sort_values('ID_Familia')

# Guardar en Excel
df_agrupado.to_excel(output_file, index=False)

print(f"¡Éxito! Archivo generado: {output_file}")
print(f"Se han procesado {len(df)} filas individuales en {len(df_agrupado)} familias.")