import csv

def guardar_csv(resultados, output_path="outputs/resultados.csv"):
    if not resultados:
        return
        
    filas = []
    headers_vistos = set()
    
    for res in resultados:
        if isinstance(res, dict) and "microorganismos" in res:
            lista_micro = res.get("microorganismos", [])
        elif isinstance(res, list):
            lista_micro = res
        elif isinstance(res, dict):
            lista_micro = [res]
        else:
            continue
            
        for micro in lista_micro:
            if isinstance(micro, dict):
                # Limpiar saltos de linea o espacios molestos
                micro_limpio = {k: str(v).strip().replace('\n', ' ') for k, v in micro.items()}
                filas.append(micro_limpio)
                for k in micro_limpio.keys():
                    headers_vistos.add(k)
                    
    orden_base = ["Dominio", "Filo", "Clase", "Orden", "Familia", "Genero", "Especie", "Cepa"]
    headers_finales = []
    
    for h in orden_base:
        if h in headers_vistos:
            headers_finales.append(h)
            headers_vistos.remove(h)
            
    headers_finales.extend(sorted(list(headers_vistos)))
    
    if not filas:
        return
        
    try:
        # utf-8-sig importa excelente en Excel mostrando acentos
        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=headers_finales, delimiter=';')
            writer.writeheader()
            for fila in filas:
                writer.writerow(fila)
        print(f"\n[OK] CSV detallado creado en: {output_path}")
    except Exception as e:
        print(f"\n[ERROR] Falló al guardar CSV: {e}")
