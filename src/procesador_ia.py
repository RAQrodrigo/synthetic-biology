import os
import time
import json
import exportador
import pdf_utils
import config_modelos
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


class VirtualArticle:
    def __init__(self, pmid, abstract):
        self.pmid = pmid
        self.abstract = abstract


def _crear_cliente(config):
    tipo = config["tipo_api"]
    key = os.environ.get(config["api_key_var"])
    if not key:
        raise ValueError(f"Falta API key: {config['api_key_var']} en .env")
    if tipo == "openrouter":
        from openai import OpenAI
        return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=key)
    elif tipo == "anthropic":
        from anthropic import Anthropic
        return Anthropic(api_key=key)
    elif tipo == "cohere":
        import cohere
        return cohere.Client(key)
    raise ValueError(f"Tipo API desconocido: {tipo}")


def _llamar_ia(cliente, config, prompt, es_json=False):
    tipo = config["tipo_api"]
    model_id = config["model_id"]
    retries = config.get("retries", 3)
    delay = config.get("delay", 2)
    max_tokens = config.get("max_tokens", 1000)

    for attempt in range(retries):
        try:
            if tipo == "openrouter":
                kwargs = {
                    "model": model_id,
                    "messages": [
                        {"role": "system", "content": "Eres un sistema de extracción de información científica preciso y estricto."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0,
                }
                if es_json:
                    kwargs["response_format"] = {"type": "json_object"}
                if max_tokens:
                    kwargs["max_tokens"] = max_tokens
                completion = cliente.chat.completions.create(**kwargs)
                return completion.choices[0].message.content

            elif tipo == "anthropic":
                message = cliente.messages.create(
                    model=model_id,
                    max_tokens=max_tokens or 1000,
                    temperature=0,
                    system="Eres un sistema de extracción de información científica preciso y estricto.",
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text

            elif tipo == "cohere":
                response = cliente.chat(model=model_id, message=prompt)
                return response.text

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate" in error_str.lower():
                print(f"  Rate limit. Esperando 15s... (Intento {attempt+1}/{retries})")
                time.sleep(15)
            else:
                print(f"  Error API: {e}")
                if attempt == retries - 1:
                    return None
                time.sleep(delay)
    return None


def _parsear_json(respuesta):
    if not respuesta:
        return None
    try:
        texto = respuesta.strip()
        if texto.startswith("```json"):
            texto = texto[7:]
        if texto.startswith("```"):
            texto = texto[3:]
        if texto.endswith("```"):
            texto = texto[:-3]
        return json.loads(texto.strip())
    except json.JSONDecodeError:
        print(f"  [ERROR] No se pudo parsear JSON. Respuesta: {respuesta[:100]}...")
        return None


def analizar_individual(cliente, config, abstract, prompt_custom=None):
    prompt_base = prompt_custom or config["prompt_individual_defecto"]
    prompt = prompt_base.replace("{abstract}", abstract)
    respuesta = _llamar_ia(cliente, config, prompt, es_json=True)
    return _parsear_json(respuesta)


def generar_reporte_global(cliente, config, resultados, prompt_custom=None):
    if not resultados:
        return None
    prompt_base = prompt_custom or config["prompt_global_defecto"]
    prompt = prompt_base.replace("{datos}", json.dumps(resultados))
    model_id_backup = config.get("model_id_global")
    if model_id_backup:
        config = {**config, "model_id": model_id_backup}
    return _llamar_ia(cliente, config, prompt, es_json=False)


def obtener_articulos_desde_pdf(ruta_pdf):
    texto = pdf_utils.extraer_texto_pdf(ruta_pdf)
    if not texto.strip():
        print("El PDF está vacío o no se pudo leer.")
        return []
    return [VirtualArticle("PDF_Local", texto)]


def procesar_pdf(
    ruta_pdf,
    nombre_modelo,
    prompt_individual=None,
    prompt_global=None,
    generar_reporte=True,
    max_articulos=20,
):
    if nombre_modelo not in config_modelos.MODELOS:
        raise ValueError(f"Modelo '{nombre_modelo}' no encontrado")
    config = config_modelos.MODELOS[nombre_modelo]
    prefix = config["output_prefix"]

    print(f"--- {nombre_modelo} ---")
    print(f"Extrayendo texto del PDF: {ruta_pdf}")
    articulos = obtener_articulos_desde_pdf(ruta_pdf)[:max_articulos]
    if not articulos:
        print("No se pudo extraer texto del PDF.")
        return [], None

    print(f"Texto extraído: {len(articulos[0].abstract)} caracteres")
    cliente = _crear_cliente(config)
    resultados = []

    for i, art in enumerate(articulos):
        print(f"[{i+1}/{len(articulos)}] Analizando...", end=" ", flush=True)
        resultado = analizar_individual(cliente, config, art.abstract, prompt_individual)
        if resultado:
            resultados.append(resultado)
            print("[OK]")
        else:
            print("[ERROR]")
        if i < len(articulos) - 1:
            time.sleep(config.get("delay", 2))

    csv_path = os.path.join(OUTPUT_DIR, f"{prefix}.csv")

    if resultados:
        exportador.guardar_csv(resultados, csv_path)
        print(f"\n[OK] CSV: {csv_path}")

        reporte = None
        txt_path = None
        if generar_reporte:
            print("Generando reporte de texto...")
            reporte = generar_reporte_global(cliente, config, resultados, prompt_global)
            if reporte:
                txt_path = os.path.join(OUTPUT_DIR, f"{prefix}.txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(reporte)
                print(f"[OK] Reporte: {txt_path}")
    else:
        print("\nNo se obtuvieron resultados.")
        csv_path = None

    return resultados, csv_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python src/procesador_ia.py <ruta_pdf> <nombre_modelo>")
        print(f"Modelos: {', '.join(config_modelos.MODELOS.keys())}")
        sys.exit(1)
    ruta = sys.argv[1]
    modelo = sys.argv[2]
    if not os.path.exists(ruta):
        print(f"PDF no encontrado: {ruta}")
        sys.exit(1)
    if modelo not in config_modelos.MODELOS:
        print(f"Modelo '{modelo}' no válido")
        sys.exit(1)
    procesar_pdf(ruta, modelo)
