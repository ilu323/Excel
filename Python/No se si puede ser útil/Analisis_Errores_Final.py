import pandas as pd
import os

# CONFIGURACIÓN
archivo_entrada = 'Errores_Por_Bloque.xlsx'  # Tu archivo actual
archivo_salida = 'Errores_Ordenados_Por_Familia.xlsx' # El nuevo archivo ordenado

def ordenar_excel():
    print(f"Leyendo archivo: {archivo_entrada}...")
    
    try:
        # Leer todas las hojas del Excel al mismo tiempo
        # sheet_name=None devuelve un diccionario {'NombreHoja': DataFrame}
        xls = pd.read_excel(archivo_entrada, sheet_name=None)
    except FileNotFoundError:
        print(f"Error: No encuentro el archivo '{archivo_entrada}'. Asegúrate de que está en la misma carpeta.")
        return
    except Exception as e:
        print(f"Error leyendo el Excel: {e}")
        return

    # Crear un nuevo Excel Writer
    with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
        # Iterar sobre cada hoja encontrada
        for nombre_hoja, df in xls.items():
            print(f"Procesando hoja: {nombre_hoja}...")
            
            # Verificar si existe la columna 'Familia_ID' para ordenar
            if 'Familia_ID' in df.columns:
                # Ordenar ascendente (1, 2, 3...)
                df_ordenado = df.sort_values(by='Familia_ID', ascending=True)
            else:
                # Si no tiene ID (ej. alguna hoja de resumen raro), dejarla igual
                df_ordenado = df
                print(f"  -> Aviso: La hoja '{nombre_hoja}' no tiene columna 'Familia_ID', se copia igual.")

            # Guardar en el nuevo Excel
            df_ordenado.to_excel(writer, sheet_name=nombre_hoja, index=False)
            
    print(f"\n¡Listo! Archivo guardado como: {archivo_salida}")

if __name__ == "__main__":
    ordenar_excel()