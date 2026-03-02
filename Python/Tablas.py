import pandas as pd

# 1. Cargar el archivo original (asegúrate de que el nombre del archivo sea correcto)
file_path = 'Datos_Totales_Con_Rugosidad.xlsx'
# Prueba con 'latin1' que lee casi todo lo que viene de Windows
df = pd.read_excel(file_path)

# 2. Seleccionar solo las columnas necesarias de la sección de Ángulos
# Ajustamos los nombres según tu CSV original
cols_needed = ['FUENTE RUG. LINEA', 'Rz', 'Potencia.3', 'Frecuencia.3', 'Velocidad.3', 'Ancho de Pulso.3', 'Densidad de energía.3','solapamiento.3']
df_angle = df[cols_needed].copy()

# 3. Limpieza de datos
# Eliminar filas donde no haya datos de ángulo
df_angle = df_angle.dropna(subset=['Rz'])
# Rellenar los nombres de archivo hacia abajo (ffill) por si hay celdas vacías en la columna FUENTE
df_angle['FUENTE RUG. LINEA'] = df_angle['FUENTE RUG. LINEA'].ffill()

# 4. Lógica de Agrupación por Familia
# Extraemos el número antes del primer guion bajo ("1_1..." -> 1)
def extract_family(filename):
    try:
        return int(str(filename).split('_')[0])
    except:
        return None

df_angle['ID_Familia'] = df_angle['FUENTE RUG. LINEA'].apply(extract_family)

# Eliminamos filas donde no se pudo identificar la familia
df_angle = df_angle.dropna(subset=['ID_Familia'])

# 5. Agrupar y Calcular Promedios
# - Ra: Calculamos la media (mean)
# - El resto de parámetros: Tomamos el primer valor (first) ya que son constantes para la misma familia
df_resumen = df_angle.groupby('ID_Familia').agg({
    'Rz': 'mean',
    'Potencia.3': 'first',
    'Frecuencia.3': 'first',
    'Velocidad.3': 'first',
    'Ancho de Pulso.3': 'first',
    'Densidad de energía.3': 'first',
    'solapamiento.3': 'first'
}).reset_index()

# 6. Renombrar columnas para que queden profesionales en el Excel
df_resumen.columns = [
    'ID_Familia', 
    'Rz_Promedio (µm)', 
    'Potencia (W)', 
    'Frecuencia (kHz)', 
    'Velocidad (mm/s)', 
    'Ancho_Pulso (ns)',
    'Densidad_Energia (J/cm²)', 
    'Solapamiento (%)'
]

# 7. Ordenar por ID de familia para tener los datos secuenciales (1 a 81)
df_resumen = df_resumen.sort_values('ID_Familia')

# 8. Exportar a Excel (.xlsx)
output_file = 'Graficos_Rz.xlsx'
df_resumen.to_excel(output_file, index=False)

print(f"¡Éxito! Se ha creado el archivo '{output_file}' con {len(df_resumen)} filas de datos promediados.")
print("Verifica que tienes 81 filas de datos (sin contar el encabezado).")