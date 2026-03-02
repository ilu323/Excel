import pandas as pd
import numpy as np
import os

# --- 1. Configuración de Archivos ---
archivo_datos = 'Datos_Totales_Con_Rugosidad.xlsx'
archivo_doe = 'DOE.xlsx'

# --- Función Robusta de Carga ---
def cargar_archivo_robusto(ruta):
    """Intenta cargar como Excel, y si falla, como CSV."""
    try:
        # Intento 1: Excel estándar
        return pd.read_excel(ruta)
    except Exception as e_excel:
        print(f"No se pudo leer '{ruta}' como Excel estándar. Probando otros métodos...")
        try:
            # Intento 2: Especificando el motor openpyxl
            return pd.read_excel(ruta, engine='openpyxl')
        except:
            try:
                # Intento 3: Leer como CSV (aunque se llame .xlsx)
                # A veces los archivos son CSVs "disfrazados"
                return pd.read_csv(ruta, sep=None, engine='python')
            except Exception as e_csv:
                raise ValueError(f"ERROR CRÍTICO: No se pudo leer el archivo '{ruta}'. "
                                 f"Verifica que no esté abierto y que sea un Excel o CSV válido.\n"
                                 f"Detalle error: {e_excel}")

# Cargar los datos usando la función segura
print("Cargando archivos...")
df_datos = cargar_archivo_robusto(archivo_datos)
df_doe = cargar_archivo_robusto(archivo_doe)
print("Archivos cargados correctamente.")

# --- 2. Preparar el Mapa de Referencia (DOE) ---
doe_map = df_doe.set_index('E')[['Potencia (%)', 'Frecuencia (KHz)', 'Velocidad de Barrido (mm/s)', 'Ancho de Pulso (ns)']]

# ==========================================
# PROCESAMIENTO TABLA 1 (FUENTE BASE)
# ==========================================
def extraer_id_base(nombre_archivo):
    try:
        s = str(nombre_archivo)
        if s.endswith('.csv'):
            return int(s.replace('.csv', ''))
        return np.nan
    except ValueError:
        return np.nan

df_datos['temp_id_1'] = df_datos['FUENTE BASE'].apply(extraer_id_base)

df_datos['Potencia'] = df_datos['temp_id_1'].map(doe_map['Potencia (%)'])
df_datos['Frecuencia'] = df_datos['temp_id_1'].map(doe_map['Frecuencia (KHz)'])
df_datos['Velocidad'] = df_datos['temp_id_1'].map(doe_map['Velocidad de Barrido (mm/s)'])
df_datos['Ancho de Pulso'] = df_datos['temp_id_1'].map(doe_map['Ancho de Pulso (ns)'])

# ==========================================
# PROCESAMIENTO TABLA 3 (FUENTE ANGLE)
# ==========================================
# El usuario solicitó rellenar datos basados en la estructura de nombres de FUENTE ANGLE

def extraer_id_angle(nombre_archivo):
    """
    Convierte '1_1_angle.csv' -> 1
    Toma todo lo que hay antes del primer guion bajo '_'.
    """
    try:
        s = str(nombre_archivo)
        if pd.isna(s) or s == 'nan':
            return np.nan
        # Dividimos por '_' y tomamos el primer elemento
        primer_numero = s.split('_')[0]
        return int(primer_numero)
    except (ValueError, IndexError):
        return np.nan

# 1. Extraemos el ID de la columna 'FUENTE ANGLE'
# Asegúrate de que esta columna exista en tu Excel.
if 'FUENTE SUP. TIPO 2' in df_datos.columns:
    df_datos['temp_id_angle'] = df_datos['FUENTE SUP. TIPO 2'].apply(extraer_id_angle)

    # 2. Rellenamos las columnas correspondientes (Sufijo .2 para Angle)
    df_datos['Potencia.5'] = df_datos['temp_id_angle'].map(doe_map['Potencia (%)'])
    df_datos['Frecuencia.5'] = df_datos['temp_id_angle'].map(doe_map['Frecuencia (KHz)'])
    df_datos['Velocidad.5'] = df_datos['temp_id_angle'].map(doe_map['Velocidad de Barrido (mm/s)'])
    df_datos['Ancho de Pulso.5'] = df_datos['temp_id_angle'].map(doe_map['Ancho de Pulso (ns)'])
    
    # Limpieza columna temporal
    df_datos.drop(columns=['temp_id_angle'], inplace=True, errors='ignore')
else:
    print("AVISO: No se encontró la columna 'FUENTE SUP. TIPO 2'. Saltando ese paso.")


# ==========================================
# LIMPIEZA FINAL Y GUARDADO
# ==========================================

# Eliminamos las columnas auxiliares restantes
df_datos.drop(columns=['temp_id_1'], inplace=True, errors='ignore')

# Guardar
# Si el archivo original era un CSV disfrazado, esto lo convertirá en un Excel real (.xlsx)
# lo cual es mejor para evitar errores futuros.
try:
    df_datos.to_excel(archivo_datos, index=False)
    print(f"ÉXITO: Archivo '{archivo_datos}' modificado y guardado.")
except PermissionError:
    print(f"ERROR: No se pudo guardar '{archivo_datos}'. Cierra el archivo si lo tienes abierto en Excel e inténtalo de nuevo.")