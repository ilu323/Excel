import pandas as pd
import os

def generar_latex_comparativa_escalas_fijas():
    # --- CONFIGURACIÓN ---
    archivo_datos = 'Datos_Completos_TFM.csv'
    archivo_salida = "Codigo_Latex_Comparativa_Escalas_Fijas.txt"
    
    # --- 1. CARGA DE DATOS ---
    if not os.path.exists(archivo_datos):
        print(f"ERROR: No existe el archivo '{archivo_datos}' en esta carpeta.")
        return

    df = pd.read_csv(archivo_datos)
    
    # Filtro: Solo Solapamiento
    df = df[df['Tipo_Variable_X'].astype(str).str.contains('Solap', case=False, na=False)]
    
    # Limpieza
    df['Valor_X'] = pd.to_numeric(df['Valor_X'], errors='coerce')
    df['Valor_Y'] = pd.to_numeric(df['Valor_Y'], errors='coerce')
    df = df.dropna(subset=['Valor_X', 'Valor_Y'])
    
    anchos_pulso = sorted(df['Ancho_Pulso'].unique())
    num_pulsos = len(anchos_pulso)
    
    # --- 2. ESTRUCTURA ---
    estructura = {
        "Variables Geométricas": ["Altura_Rebaba", "Angulo", "Profundidad"],
        "Rugosidad de Perfil (R)": [
            "Ra", "Rc", "Rdq", "Rku", "Rmax", "Rp", "Rq", "Rsk", "Rsm", "Rv", "Rz"
        ],
        "Rugosidad Superficial (S)": [
            "Sa", "S10z", "Sq", "Sp", "Sdq", "Sdr", "Sk", "Sku", "Spk", "Ssk", "Sv", "Svk"
        ]
    }

    # --- 3. GENERACIÓN ---
    lines = []
    lines.append("% --- CÓDIGO CON ESCALAS FIJAS POR VARIABLE ---")
    
    for familia, variables in estructura.items():
        lines.append(f"\n% ================= {familia} =================")
        lines.append(f"\\section{{{familia}}}")
        
        for var in variables:
            # ---------------------------------------------------------
            # PASO CLAVE: Calcular límites GLOBALES para esta variable
            # ---------------------------------------------------------
            datos_variable = df[df['Parametro_Analizado'] == var]
            
            if datos_variable.empty:
                continue # Si no hay datos de esta variable, saltamos
                
            # Calcular Min/Max Globales
            g_min_y = datos_variable['Valor_Y'].min()
            g_max_y = datos_variable['Valor_Y'].max()
            g_min_x = datos_variable['Valor_X'].min()
            g_max_x = datos_variable['Valor_X'].max()
            
            # Añadir un margen (padding) del 10% para que no quede pegado
            rango_y = g_max_y - g_min_y
            if rango_y == 0: rango_y = 1.0 # Evitar división por cero si es línea plana
            
            margen_y = rango_y * 0.1
            limite_ymin = g_min_y - margen_y
            limite_ymax = g_max_y + margen_y
            
            # Para X (Solapamiento) solemos querer un margen pequeño
            limite_xmin = g_min_x - 2 
            limite_xmax = g_max_x + 2
            
            # ---------------------------------------------------------
            
            lines.append(f"\\begin{{frame}}{{Análisis: {var}}}")
            lines.append(r"  \vspace{-0.2cm}") 
            lines.append(r"  \makebox[\textwidth][c]{") 
            lines.append(r"    \begin{columns}[t]") 
            
            # Ajuste de anchos de columna
            if num_pulsos >= 3:
                col_width = "0.32" 
                unit = "\\paperwidth"
            elif num_pulsos == 2:
                col_width = "0.48"
                unit = "\\textwidth"
            else:
                col_width = "0.95"
                unit = "\\textwidth"

            for i, pulso in enumerate(anchos_pulso):
                subset = df[(df['Ancho_Pulso'] == pulso) & (df['Parametro_Analizado'] == var)]
                
                lines.append(f"      \\begin{{column}}{{{col_width}{unit}}}")
                lines.append(r"        \centering")
                lines.append(f"        {{\\scriptsize \\textbf{{{pulso}}}}}\\\\") 
                
                if subset.empty:
                    lines.append(r"        \vspace{1.5cm} \textit{\tiny Sin datos}")
                    lines.append(r"      \end{column}")
                    if i < num_pulsos - 1: lines.append(r"      \hfill")
                    continue

                lines.append(r"        \begin{tikzpicture}")
                lines.append(r"          \begin{axis}[")
                lines.append(r"            width=0.95\linewidth,")
                lines.append(r"            height=4.0cm,") 
                lines.append(r"            grid=major,")
                lines.append(r"            grid style={dashed, gray!30},")
                lines.append(r"            xlabel={Solapamiento (\%)},")
                lines.append(r"            ylabel={$\mu$m},")
                # --- APLICACIÓN DE LÍMITES GLOBALES ---
                lines.append(f"            ymin={limite_ymin:.2f}, ymax={limite_ymax:.2f},")
                lines.append(f"            xmin={limite_xmin:.2f}, xmax={limite_xmax:.2f},")
                # --------------------------------------
                lines.append(r"            label style={font=\tiny},")       
                lines.append(r"            tick label style={font=\tiny},")  
                lines.append(r"            legend style={font=\tiny, at={(0.5,1.1)}, anchor=south, draw=none, fill=none, column sep=2pt},") 
                lines.append(r"            legend columns=-1,")
                lines.append(r"          ]")

                grupos = sorted(subset['Grupo'].unique())
                colores = {'P30': 'blue', 'P50': 'red', 'P70': 'olive'}
                marcas = {'P30': 'square*', 'P50': '*', 'P70': 'triangle*'}

                for grp in grupos:
                    color = colores.get(grp, 'black')
                    marca = marcas.get(grp, '*')
                    datos_grp = subset[subset['Grupo'] == grp].sort_values(by='Valor_X')
                    
                    coords = ""
                    for _, row in datos_grp.iterrows():
                        coords += f"({row['Valor_X']:.1f},{row['Valor_Y']:.2f}) "
                    
                    lines.append(f"            \\addplot[color={color}, mark={marca}, mark size=1.2pt] coordinates {{ {coords} }};")
                    lines.append(f"            \\addlegendentry{{{grp}}}")

                lines.append(r"          \end{axis}")
                lines.append(r"        \end{tikzpicture}")
                lines.append(r"      \end{column}")
                
                if i < num_pulsos - 1:
                     lines.append(r"      \hfill") 

            lines.append(r"    \end{columns}")
            lines.append(r"  } % Fin makebox")
            lines.append(r"\end{frame}")
            lines.append("") 

    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"¡HECHO! Generado '{archivo_salida}'.")
    print("Ahora todas las gráficas de una misma variable comparten eje Y y X.")

if __name__ == "__main__":
    generar_latex_comparativa_escalas_fijas()