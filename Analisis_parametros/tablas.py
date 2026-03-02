import pandas as pd
import os
import glob

def procesar_archivos_excel():
    # 1. Configuración
    directorio_actual = os.getcwd()
    patron_archivos = os.path.join(directorio_actual, "Analisis_*.xlsx")
    archivos = glob.glob(patron_archivos)
    
    datos_totales = []
    
    print(f"Buscando archivos en: {directorio_actual}")
    print(f"Se encontraron {len(archivos)} archivos para procesar.\n")

    # 2. Iterar sobre cada archivo Excel
    for archivo_path in archivos:
        nombre_archivo = os.path.basename(archivo_path)
        
        # Extraer el nombre de la variable Y del nombre del archivo (ej. Analisis_Ra.xlsx -> Ra)
        # Asumimos formato "Analisis_Variable.xlsx"
        try:
            variable_y_global = nombre_archivo.replace("Analisis_", "").replace(".xlsx", "")
        except:
            variable_y_global = nombre_archivo
            
        print(f"Procesando: {nombre_archivo} (Variable: {variable_y_global})...")
        
        try:
            # Leer el excel completo sin encabezados (header=None) para procesarlo manualmente
            df = pd.read_excel(archivo_path, header=None, engine='openpyxl')
            
            ancho_pulso_actual = None
            
            # 3. Recorrer el archivo fila por fila
            i = 0
            while i < len(df):
                fila = df.iloc[i]
                celda_0 = str(fila[0]).strip()
                
                # A. Detectar Ancho de Pulso
                if "ANCHO DE PULSO" in celda_0.upper():
                    # Formato esperado: "ANCHO DE PULSO: 100 ns"
                    partes = celda_0.split(':')
                    if len(partes) > 1:
                        ancho_pulso_actual = partes[1].strip()
                    i += 1
                    continue
                
                # B. Detectar Encabezados de Tablas (Solap_ o Dens_)
                # Buscamos en toda la fila si alguna celda contiene "Solap_" o "Dens_"
                es_encabezado = False
                indices_columnas = [] # Guardará tuplas (col_x, col_y, nombre_grupo)
                
                for col_idx in range(len(fila)):
                    valor_celda = str(fila[col_idx]).strip()
                    if "Solap_" in valor_celda or "Dens_" in valor_celda:
                        es_encabezado = True
                        # Asumimos que la estructura es Columna X (Encabezado) y Columna X+1 (Datos Y)
                        if col_idx + 1 < len(fila):
                            indices_columnas.append((col_idx, col_idx + 1, valor_celda))
                
                if es_encabezado and indices_columnas:
                    # Estamos en una fila de encabezado, los datos empiezan en la siguiente fila (i+1)
                    j = i + 1
                    while j < len(df):
                        fila_datos = df.iloc[j]
                        celda_datos_0 = str(fila_datos[0]).strip()
                        
                        # Criterios de parada de lectura de datos:
                        # 1. Encontrar otro "ANCHO DE PULSO"
                        # 2. Encontrar separadores (---)
                        # 3. Encontrar otro encabezado (Solap/Dens)
                        # 4. Fin del archivo
                        
                        if "ANCHO" in celda_datos_0.upper():
                            break
                        if "-----" in celda_datos_0:
                            break
                            
                        # Verificar si esta fila es un nuevo encabezado
                        es_nuevo_encabezado = False
                        for col_check in range(len(fila_datos)):
                            val_check = str(fila_datos[col_check]).strip()
                            if "Solap_" in val_check or "Dens_" in val_check:
                                es_nuevo_encabezado = True
                                break
                        if es_nuevo_encabezado:
                            break

                        # Extraer datos de las columnas identificadas
                        datos_encontrados_en_fila = False
                        for (col_x, col_y, nombre_header) in indices_columnas:
                            val_x = fila_datos[col_x]
                            val_y = fila_datos[col_y]
                            
                            # Verificar que sean datos válidos (no vacíos ni strings de encabezado)
                            if pd.notna(val_x) and pd.notna(val_y) and not isinstance(val_x, str):
                                # Parsear nombre del grupo: Solap_P30 -> Tipo: Solap, Grupo: P30
                                partes_nombre = nombre_header.split('_')
                                tipo_x = partes_nombre[0] # Solap o Dens
                                grupo = partes_nombre[-1] # P30, P50, P70
                                
                                datos_totales.append({
                                    'Archivo': nombre_archivo,
                                    'Parametro_Analizado': variable_y_global, # Ra, Rc, Altura_Rebaba
                                    'Ancho_Pulso': ancho_pulso_actual,
                                    'Tipo_Variable_X': tipo_x, # Solap o Dens
                                    'Grupo': grupo,            # P30, P50, P70
                                    'Valor_X': val_x,
                                    'Valor_Y': val_y
                                })
                                datos_encontrados_en_fila = True
                        
                        # Si la fila estaba totalmente vacía de datos útiles, igual avanzamos
                        j += 1
                    
                    # Al terminar de leer el bloque de datos, saltamos el índice principal 'i'
                    # para no volver a leer esas filas
                    i = j 
                    continue

                i += 1

        except Exception as e:
            print(f"ERROR procesando {nombre_archivo}: {e}")

    # 4. Guardar a CSV
    if datos_totales:
        df_final = pd.DataFrame(datos_totales)
        output_file = os.path.join(directorio_actual, "Datos_Completos_TFM.csv")
        df_final.to_csv(output_file, index=False, encoding='utf-8-sig') # utf-8-sig para que Excel lo abra bien con tildes
        print(f"\n¡ÉXITO! Se extrajeron {len(df_final)} filas de datos.")
        print(f"Archivo guardado en: {output_file}")
        
        # Mostrar una vista previa
        print("\nVista previa de los datos:")
        print(df_final.head())
    else:
        print("\nNo se encontraron datos. Verifica la estructura de los archivos.")

if __name__ == "__main__":
    procesar_archivos_excel()