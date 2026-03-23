import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def csv_a_reporte_html(archivo_csv, archivo_salida=None):
    if archivo_salida is None:
        archivo_salida = os.path.join(BASE_DIR, 'reports', 'reporte_articulos.html')
    """
    Lee un archivo CSV con artículos de PubMed y genera un reporte estructurado en formato 
    HTML usando la librería Pandas y estilos CSS predefinidos.
    """
    try:
        # 1. Leer el CSV
        df = pd.read_csv(archivo_csv)
        
        # 2. Crear un estilo CSS básico para que se vea moderno
        estilo_css = """
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f4f7f6; }
            h2 { color: #2c3e50; text-align: center; }
            table { width: 100%; border-collapse: collapse; background-color: white; box-shadow: 0 2px 15px rgba(0,0,0,0.1); }
            th { background-color: #2980b9; color: white; padding: 15px; text-align: left; }
            td { padding: 12px 15px; border-bottom: 1px solid #ddd; vertical-align: top; }
            tr:hover { background-color: #f1f1f1; }
            .pmid { font-weight: bold; color: #e67e22; }
            .title { font-weight: bold; color: #2c3e50; font-size: 1.1em; }
            .abstract { font-size: 0.95em; line-height: 1.5; color: #555; text-align: justify; }
        </style>
        """
        
        # 3. Convertir los datos a HTML
        # Usamos clases personalizadas para que el CSS funcione
        html_table = df.to_html(index=False, classes="tablita")
        
        # 4. Ensamblar el archivo final
        html_final = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Reporte de Artículos PubMed</title>
            {estilo_css}
        </head>
        <body>
            <h2>Resumen de Investigación: {len(df)} Artículos Encontrados</h2>
            {html_table}
        </body>
        </html>
        """
        
        # 5. Guardar el archivo
        with open(archivo_salida, "w", encoding="utf-8") as f:
            f.write(html_final)
            
        print(f"¡Listo! Se ha creado '{archivo_salida}'. Ábrelo con tu navegador favorito.")
        
    except Exception as e:
        print(f"Error al procesar el CSV: {e}")

if __name__ == "__main__":
    # Asegúrate de que el nombre coincida con tu archivo generado anteriormente
    csv_a_reporte_html(os.path.join(BASE_DIR, 'data', 'abstracts.csv'))