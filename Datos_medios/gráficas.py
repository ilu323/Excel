import pandas as pd
import xlsxwriter

# ==========================================
#   CONFIGURACIÓN
# ==========================================
# Nombre del archivo de entrada (Promedios)
INPUT_FILE = 'Datos_Altura_Rebaba.xlsx' 

# Nombre del archivo de salida
OUTPUT_FILE = 'Analisis_Grafico_Final_Promedios.xlsx'

# Palabra clave para encontrar la columna Y (ej: 'Altura', 'Rebaba', 'Sa', 'Profundidad')
PARAMETRO_KEY = 'Altura_Rebaba' 

# Configuración del Eje X para Solapamiento (Lienzo 0-120)
X_MIN_SOLAP = 0
X_MAX_SOLAP = 120

# ==========================================

print(f"--- GENERANDO GRÁFICOS PARA: {INPUT_FILE} ---")

# 1. Cargar Datos
try:
    # Intentamos leer Excel
    df = pd.read_excel(INPUT_FILE)
except:
    try:
        # Fallback para CSV
        df = pd.read_csv(INPUT_FILE, encoding='latin1')
    except Exception as e:
        print(f"ERROR CRÍTICO: No se puede leer {INPUT_FILE}. {e}")
        exit()

# Limpieza de nombres de columnas (quitar espacios extra)
df.columns = [c.strip() for c in df.columns]

# --- 2. Identificación Automática de Columnas ---
def find_col(keyword, columns):
    matches = [c for c in columns if keyword.lower() in c.lower()]
    return matches[0] if matches else None

# Buscar columna Y (Parametro)
col_y = find_col(PARAMETRO_KEY, df.columns)
if not col_y:
    print(f"ERROR: No encuentro columna que contenga '{PARAMETRO_KEY}'")
    exit()

# Buscar otras columnas clave
col_potencia = find_col('Potencia', df.columns)
col_ancho = find_col('Ancho', df.columns) # Busca "Ancho..."
col_solap = find_col('Solapamiento', df.columns)
col_densidad = find_col('Densidad', df.columns)

print(f"Columnas detectadas:")
print(f" - Y: {col_y}")
print(f" - Potencia: {col_potencia}")
print(f" - Ancho Pulso: {col_ancho}")
print(f" - Solapamiento: {col_solap}")
print(f" - Densidad: {col_densidad}")

# 3. Configurar Excel Writer
writer = pd.ExcelWriter(OUTPUT_FILE, engine='xlsxwriter')
workbook = writer.book
worksheet = workbook.add_worksheet('Graficos')
writer.sheets['Graficos'] = worksheet

# Estilos
style_title = workbook.add_format({'bold': True, 'font_size': 14, 'font_color': '#2F5597'})
style_header = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D9E1F2', 'border': 1})
style_cell = workbook.add_format({'align': 'center'})

# 4. Generar Gráficos
anchos_unicos = sorted(df[col_ancho].unique())
potencias_unicas = sorted(df[col_potencia].unique())

# Mapeo de colores (Azul, Rojo, Verde)
# Asignamos: Potencia mas baja -> Azul, Media -> Rojo, Alta -> Verde
colores_hex = ['#0000FF', '#FF0000', '#00B050'] # P30, P50, P70
mapa_colores = {p: colores_hex[i % 3] for i, p in enumerate(potencias_unicas)}

row_cursor = 0

for ancho in anchos_unicos:
    # Filtrar por Ancho de Pulso
    df_ancho = df[df[col_ancho] == ancho]
    
    worksheet.write(row_cursor, 0, f"ANCHO DE PULSO: {ancho} ns", style_title)
    row_cursor += 2
    
    # === A) GRÁFICO SOLAPAMIENTO vs PARAMETRO ===
    # Preparamos datos para el gráfico
    start_row = row_cursor + 1
    col_idx = 0
    
    chart_solap = workbook.add_chart({'type': 'scatter'})
    
    for pot in potencias_unicas:
        # Extraer datos de la serie (Potencia X)
        subset = df_ancho[df_ancho[col_potencia] == pot]
        if subset.empty: continue
        
        # Escribir en Excel para alimentar el gráfico
        worksheet.write(start_row, col_idx, f"Solap_P{pot}", style_header)
        worksheet.write(start_row, col_idx+1, f"Y_P{pot}", style_header)
        
        for r, (x, y) in enumerate(zip(subset[col_solap], subset[col_y])):
            worksheet.write(start_row+1+r, col_idx, x, style_cell)
            worksheet.write(start_row+1+r, col_idx+1, y, style_cell)
            
        # Añadir serie al gráfico
        num_rows = len(subset)
        chart_solap.add_series({
            'name': f'P{pot}',
            'categories': ['Graficos', start_row+1, col_idx, start_row+num_rows, col_idx],
            'values':     ['Graficos', start_row+1, col_idx+1, start_row+num_rows, col_idx+1],
            'marker':     {'type': 'circle', 'size': 6, 
                           'fill': {'color': mapa_colores[pot]}, 
                           'border': {'color': mapa_colores[pot]}},
            'line':       {'none': True}, # Solo puntos
        })
        col_idx += 2
        
    # Configurar Ejes y Tamaño
    chart_solap.set_title({'name': f'Solapamiento vs {PARAMETRO_KEY} ({ancho} ns)'})
    chart_solap.set_x_axis({
        'name': 'Solapamiento (%)', 
        'min': X_MIN_SOLAP, 
        'max': X_MAX_SOLAP,
        'major_gridlines': {'visible': False}
    })
    chart_solap.set_y_axis({
        'name': PARAMETRO_KEY, 
        'major_gridlines': {'visible': True, 'line': {'color': '#D9D9D9'}}
    })
    chart_solap.set_size({'width': 450, 'height': 300})
    
    worksheet.insert_chart(row_cursor, col_idx + 1, chart_solap)
    
    # === B) GRÁFICO DENSIDAD vs PARAMETRO ===
    # Movemos cursor para el siguiente bloque
    row_cursor += 20 
    start_row = row_cursor + 1
    col_idx = 0
    
    chart_dens = workbook.add_chart({'type': 'scatter'})
    
    for pot in potencias_unicas:
        subset = df_ancho[df_ancho[col_potencia] == pot]
        if subset.empty: continue
        
        worksheet.write(start_row, col_idx, f"Dens_P{pot}", style_header)
        worksheet.write(start_row, col_idx+1, f"Y_P{pot}", style_header)
        
        for r, (x, y) in enumerate(zip(subset[col_densidad], subset[col_y])):
            worksheet.write(start_row+1+r, col_idx, x, style_cell)
            worksheet.write(start_row+1+r, col_idx+1, y, style_cell)
            
        num_rows = len(subset)
        chart_dens.add_series({
            'name': f'P{pot}',
            'categories': ['Graficos', start_row+1, col_idx, start_row+num_rows, col_idx],
            'values':     ['Graficos', start_row+1, col_idx+1, start_row+num_rows, col_idx+1],
            'marker':     {'type': 'circle', 'size': 6, 
                           'fill': {'color': mapa_colores[pot]}, 
                           'border': {'color': mapa_colores[pot]}},
            'line':       {'none': True},
        })
        col_idx += 2
        
    chart_dens.set_title({'name': f'Densidad vs {PARAMETRO_KEY} ({ancho} ns)'})
    chart_dens.set_x_axis({'name': 'Densidad de Energía (J/cm²)'})
    chart_dens.set_y_axis({'name': PARAMETRO_KEY, 'major_gridlines': {'visible': True, 'line': {'color': '#D9D9D9'}}})
    chart_dens.set_size({'width': 450, 'height': 300})
    
    worksheet.insert_chart(row_cursor, col_idx + 1, chart_dens)
    
    # Espacio para siguiente ancho de pulso
    row_cursor += 25

writer.close()
print(f"¡HECHO! Archivo generado: {OUTPUT_FILE}")