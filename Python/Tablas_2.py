import pandas as pd
import xlsxwriter

# 1. Configuración
input_file = 'Graficos_Rq.xlsx'
output_file = 'Analisis_Unificado_3Parametros_Rq.xlsx'

# 2. Cargar datos
try:
    df = pd.read_excel(input_file)
except:
    try:
        df = pd.read_csv(input_file, encoding='latin1')
    except:
        df = pd.read_csv(input_file, encoding='utf-8')

# Limpieza básica
df.columns = [c.strip() for c in df.columns]
col_densidad_raw = [c for c in df.columns if 'Densidad' in c][0]
df.rename(columns={col_densidad_raw: 'Densidad_Energia'}, inplace=True)
if 'Solapamiento (%)' in df.columns:
    df.rename(columns={'Solapamiento (%)': 'Solapamiento'}, inplace=True)

# Redondear para facilitar agrupación exacta
df['Densidad_Group'] = df['Densidad_Energia'].round(4)
df['Solapamiento_Group'] = df['Solapamiento'].round(1)

# 3. Excel Writer
writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
workbook = writer.book
worksheet = workbook.add_worksheet('Analisis Unificado')
writer.sheets['Analisis Unificado'] = worksheet

# Estilos
fmt_title = workbook.add_format({'bold': True, 'font_size': 16, 'font_color': '#2F5597', 'align': 'center'})
fmt_section = workbook.add_format({'bold': True, 'font_size': 14, 'font_color': '#2F5597', 'bottom': 2, 'bottom_color': '#2F5597'})
fmt_sub = workbook.add_format({'bold': True, 'font_size': 11, 'italic': True, 'font_color': '#595959'})
fmt_header = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D9E1F2', 'border': 1})
fmt_num = workbook.add_format({'align': 'center', 'border': 1, 'num_format': '0.00'})
fmt_pct = workbook.add_format({'align': 'center', 'border': 1, 'num_format': '0.0'})

row = 1
worksheet.write(row, 0, "ANÁLISIS UNIFICADO: 3 PARÁMETROS_Ra", fmt_title)
row += 3

# === PARTE A: EFECTO DEL SOLAPAMIENTO (Comparando Anchos de Pulso) ===
worksheet.write(row, 0, "A) EFECTO DEL SOLAPAMIENTO (A Densidad Constante)", fmt_section)
row += 2

# Agrupar por Densidad Única
densidades = sorted(df['Densidad_Group'].unique())

for dens in densidades:
    df_sub = df[df['Densidad_Group'] == dens]
    
    # Pivotar para tener Anchos de Pulso en columnas
    pivot_table = df_sub.pivot_table(index='Solapamiento_Group', 
                                     columns='Ancho_Pulso (ns)', 
                                     values='Rq')
    
    # Si hay pocos datos, saltamos
    if pivot_table.empty or len(pivot_table) < 2:
        continue
        
    worksheet.write(row, 0, f"• Densidad Fija: {dens:.4f} J/cm²", fmt_sub)
    row += 1
    
    # Escribir cabeceras
    worksheet.write(row, 0, "Solapamiento (%)", fmt_header)
    pulsos = sorted(pivot_table.columns)
    for i, p in enumerate(pulsos):
        worksheet.write(row, 1+i, f"Rq ({int(p)}ns)", fmt_header)
        
    # Escribir datos
    start_row = row + 1
    for solape, row_data in pivot_table.iterrows():
        row += 1
        worksheet.write(row, 0, solape, fmt_pct)
        for i, p in enumerate(pulsos):
            val = row_data[p]
            worksheet.write(row, 1+i, val, fmt_num)
    end_row = row
    
    # Gráfico
    chart = workbook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
    
    colors = ['#4472C4', '#ED7D31', '#A5A5A5'] # Azul, Naranja, Gris
    markers = ['circle', 'diamond', 'square']
    
    for i, p in enumerate(pulsos):
        chart.add_series({
            'name': f'{int(p)} ns',
            'categories': ['Analisis Unificado', start_row, 0, end_row, 0], # X
            'values':     ['Analisis Unificado', start_row, 1+i, end_row, 1+i], # Y
            'marker':     {'type': markers[i % 3], 'size': 6},
            'line':       {'color': colors[i % 3], 'width': 2}
        })
        
    chart.set_title({'name': f'Densidad = {dens:.2f} J/cm²'})
    chart.set_x_axis({'name': 'Solapamiento (%)'})
    chart.set_y_axis({'name': 'Rq'})
    chart.set_size({'width': 450, 'height': 280})
    
    worksheet.insert_chart(start_row - 1, 1+len(pulsos)+1, chart)
    row += 14

# === PARTE B: EFECTO DE LA DENSIDAD (Comparando Anchos de Pulso) ===
worksheet.write(row, 0, "B) EFECTO DE LA DENSIDAD DE ENERGÍA (A Solapamiento Constante)", fmt_section)
row += 2

overlaps = sorted(df['Solapamiento_Group'].unique())

for ov_val in overlaps:
    df_sub = df[df['Solapamiento_Group'] == ov_val]
    
    pivot_table = df_sub.pivot_table(index='Densidad_Group', 
                                     columns='Ancho_Pulso (ns)', 
                                     values='Rq')
    
    if pivot_table.empty or len(pivot_table) < 2:
        continue
        
    worksheet.write(row, 0, f"• Solapamiento Fijo: ~{ov_val}%", fmt_sub)
    row += 1
    
    worksheet.write(row, 0, "Densidad (J/cm²)", fmt_header)
    pulsos = sorted(pivot_table.columns)
    for i, p in enumerate(pulsos):
        worksheet.write(row, 1+i, f"Rq ({int(p)}ns)", fmt_header)
        
    start_row = row + 1
    for dens, row_data in pivot_table.iterrows():
        row += 1
        worksheet.write(row, 0, dens, fmt_num)
        for i, p in enumerate(pulsos):
            val = row_data[p]
            worksheet.write(row, 1+i, val, fmt_num)
    end_row = row
    
    chart = workbook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
    
    for i, p in enumerate(pulsos):
        chart.add_series({
            'name': f'{int(p)} ns',
            'categories': ['Analisis Unificado', start_row, 0, end_row, 0],
            'values':     ['Analisis Unificado', start_row, 1+i, end_row, 1+i],
            'marker':     {'type': markers[i % 3], 'size': 6},
            'line':       {'color': colors[i % 3], 'width': 2}
        })
        
    chart.set_title({'name': f'Solapamiento = {ov_val}%'})
    chart.set_x_axis({'name': 'Densidad (J/cm²)'})
    chart.set_y_axis({'name': 'Rq'})
    chart.set_size({'width': 450, 'height': 280})
    
    worksheet.insert_chart(start_row - 1, 1+len(pulsos)+1, chart)
    row += 14

writer.close()
print(f"¡Éxito! Archivo generado: {output_file}")