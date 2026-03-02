import pandas as pd
import numpy as np

# Configuración
input_file = 'Datos_Totales_Con_Rugosidad.xlsx'
output_file = 'Filas_Faltantes_Tipo2.xlsx'

print("--- GENERANDO DATOS FALTANTES PARA FUENTE TIPO 2 (Familia 54) ---")

# 1. Cargar datos
try:
    df = pd.read_excel(input_file)
except:
    try:
        df = pd.read_csv(input_file, encoding='latin1')
    except:
        print("Error leyendo el archivo original.")
        exit()

df.columns = [c.strip() for c in df.columns]

# 2. Configurar Columnas de Interés (Abbott-Firestone)
col_fuente = 'FUENTE SUP. TIPO 2'
# Estos son los parámetros típicos de la sección Tipo 2
cols_params = ['Sk', 'Spk', 'Svk', 'Smr1', 'Smr2', 'Vmp', 'Vmc', 'Vvc', 'Vvv']

# Verificar que existen
missing_cols = [c for c in cols_params if c not in df.columns]
if missing_cols:
    print(f"Advertencia: No encuentro estas columnas: {missing_cols}")
    # Las quitamos de la lista para que no falle
    cols_params = [c for c in cols_params if c not in missing_cols]

# 3. Extraer ID para filtrar
def extract_id(val):
    try:
        return int(str(val).split('_')[0])
    except:
        return None

df['ID_Tipo2'] = df[col_fuente].apply(extract_id)

# 4. Obtener vecinos (52 y 53) para proyectar la 54
# Lógica: 52 (100mm/s) -> 53 (300mm/s) -> 54 (500mm/s)
# La diferencia de velocidad es constante, así que usamos proyección lineal directa.

vecinos = df[df['ID_Tipo2'].isin([52, 53])].copy()

if vecinos.empty:
    print("ERROR: No encuentro datos de las familias 52 y 53 para poder interpolar.")
    exit()

# Calculamos las medias de los vecinos
medias = vecinos.groupby('ID_Tipo2')[cols_params].mean()

print("Valores promedio de los vecinos encontrados:")
print(medias)

# 5. Cálculo de Proyección (Extrapolación)
# Valor_54 = Valor_53 + (Valor_53 - Valor_52)
# Básicamente: Si subió X cantidad de 52 a 53, asumimos que sube esa misma cantidad a 54.

row_54 = {}

# Datos fijos de la familia 54
row_54[col_fuente] = '54_1_relleno_Tipo2.csv'
row_54['Potencia.5'] = 50
row_54['Frecuencia.5'] = 150
row_54['Velocidad.5'] = 500
row_54['Ancho de Pulso.5'] = 200
# Densidad y Solapamiento aproximados para esa config
row_54['Densidad de energía.5'] = 0.169
row_54['solapamiento.5'] = 93.3

# Rellenar parámetros calculados
if 52 in medias.index and 53 in medias.index:
    val_52 = medias.loc[52]
    val_53 = medias.loc[53]
    
    diff = val_53 - val_52
    estimado_54 = val_53 + diff
    
    # Evitar valores negativos imposibles físicamente (Sk, Spk, etc no pueden ser < 0)
    estimado_54[estimado_54 < 0] = 0
    
    # Asignar al diccionario
    for col in cols_params:
        row_54[col] = estimado_54[col]
        
    # Añadir columna Lc.2 si existe (suele ser constante)
    if 'Lc.2' in df.columns:
         row_54['Lc.2'] = vecinos['Lc.2'].mode()[0] if not vecinos['Lc.2'].mode().empty else 0
         
else:
    print("Error crítico: Faltan datos completos en 52 o 53.")
    exit()

# 6. Crear DataFrame y Guardar
df_result = pd.DataFrame([row_54])

print("\n--- FILA GENERADA PARA FAMILIA 54 ---")
print(df_result[cols_params])

df_result.to_excel(output_file, index=False)
print(f"\n¡Éxito! Archivo guardado: {output_file}")
print("Copia esa fila y pégala en la sección 'FUENTE SUP. TIPO 2' de tu Excel original para la familia 54.")