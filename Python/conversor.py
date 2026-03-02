import pandas as pd
import numpy as np

# Nombres de archivo
archivo_datos = 'Datos_Totales_Con_Rugosidad.xlsx'
archivo_doe = 'DOE.xlsx'

# Cargar datos
df_datos = pd.read_excel(archivo_datos) # Asumiendo formato Excel original
df_doe = pd.read_excel(archivo_doe)

# Preparar mapeo del DOE (usando columna 'E' como índice)
doe_map = df_doe.set_index('E')[['Potencia (%)', 'Frecuencia (KHz)', 'Velocidad de Barrido (mm/s)', 'Ancho de Pulso (ns)']]

# Función para extraer el ID del nombre del archivo (ej: '1.csv' -> 1)
def extraer_id(nombre_archivo):
    try:
        s = str(nombre_archivo)
        if s.endswith('.csv'):
            return int(s.replace('.csv', ''))
        return np.nan
    except ValueError:
        return np.nan

# Crear columna temporal de ID
df_datos['temp_id'] = df_datos['FUENTE BASE'].apply(extraer_id)

# Rellenar columnas mapeando el ID con los datos del DOE
df_datos['Potencia'] = df_datos['temp_id'].map(doe_map['Potencia (%)'])
df_datos['Frecuencia'] = df_datos['temp_id'].map(doe_map['Frecuencia (KHz)'])
df_datos['Velocidad'] = df_datos['temp_id'].map(doe_map['Velocidad de Barrido (mm/s)'])
df_datos['Ancho de Pulso'] = df_datos['temp_id'].map(doe_map['Ancho de Pulso (ns)'])

# Eliminar columna auxiliar
df_datos.drop(columns=['temp_id'], inplace=True)

# Sobrescribir el archivo original
df_datos.to_excel(archivo_datos, index=False)

print(f"Archivo '{archivo_datos}' modificado y guardado correctamente.")