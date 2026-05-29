PROMPT_INDIVIDUAL_TAXONOMIA = """Extrae la taxonomía del microorganismo del siguiente texto científico en ESPAÑOL.
Responde estrictamente con este formato JSON. Si hay múltiples microorganismos, devuelve una lista de diccionarios bajo 'microorganismos':
{
  "microorganismos": [
    {
      "Dominio": "Dominio aquí o N/D",
      "Filo": "Filo o N/D",
      "Clase": "Clase o N/D",
      "Orden": "Orden o N/D",
      "Familia": "Familia o N/D",
      "Genero": "Género o N/D"
    }
  ]
}
Texto: {abstract}"""

PROMPT_INDIVIDUAL_BIORREMEDIACION = """Extrae información del siguiente abstract científico en ESPAÑOL.
Responde estrictamente con este formato JSON:
{
  "organismo": "Género y especie",
  "usa_hongos": "Sí/No",
  "tecnica": "Método principal",
  "bioremediacion": "Sí/No (contaminante)",
  "localizacion": "País o región",
  "hallazgo": "Resultado principal"
}
Abstract: {abstract}"""

PROMPT_GLOBAL_ESTANDAR = """Actúa como analista científico. Genera un reporte detallado en ESPAÑOL basado en la estructura de los datos:
1. Estadísticas de Taxonomía (Dominio, Filo, Clase, Orden, Familia, Género)
2. Conclusión global
Datos: {datos}"""

PROMPT_GLOBAL_TABLAS = """Actúa como analista de datos científicos. Basado en los datos proporcionados, genera un reporte usando Markdown en ESPAÑOL.
Genera una TABLA de Taxonomía de todos los microorganismos hallados (Dominio, Filo, Clase, Orden, Familia, Genero).
Agrega una muy breve conclusión global al final.
Datos: {datos}"""

PROMPT_GLOBAL_COHERE = """Actúa como un analista científico de alto nivel. Basado en los siguientes datos extraídos de abstracts, genera un reporte estructurado y visualmente claro en ESPAÑOL. 
Es OBLIGATORIO que incluyas tablas Markdown (cuadros) para resumir la información de manera elegante.
Estructura requerida:
1. **Estadística de organismos**: Crea un cuadro (Markdown table) con las columnas 'Organismo' y 'Frecuencia/Apariciones'.
2. **Uso de hongos**: Un resumen analítico sobre el protagonismo de los hongos en estos estudios.
3. **Mapa de Biorremediación**: Crea una tabla cruzada detallando 'Contaminante', 'Organismo asociado' y 'Técnica utilizada'.
4. **Conclusión Global**: Una síntesis profesional sobre el estado del arte y hacia dónde apunta la investigación.
Datos a procesar: 
{datos}"""

# Cada modelo tiene:
#   tipo_api: "openrouter" | "anthropic" | "cohere"
#   model_id: ID del modelo en la API
#   model_id_global: (opcional) modelo distinto para el metaanálisis global
#   api_key_var: variable de entorno para la API key
#   output_prefix: prefijo para archivos de salida
#   tipo_prompt: "estandar" | "tablas"
#   prompt_individual_defecto: prompt por defecto para análisis individual
#   prompt_global_defecto: prompt por defecto para metaanálisis
#   max_tokens: (opcional) límite de tokens
#   delay: (opcional) segundos entre requests
#   retries: (opcional) reintentos ante error

MODELOS = {
    "ChatGPT 5.4 Mini (OpenRouter)": {
        "tipo_api": "openrouter",
        "model_id": "openai/gpt-5.4-mini",
        "api_key_var": "OPENROUTER_API_KEY",
        "output_prefix": "metaanalisis_chatgpt_5_4_mini",
        "tipo_prompt": "estandar",
        "prompt_individual_defecto": PROMPT_INDIVIDUAL_BIORREMEDIACION,
        "prompt_global_defecto": PROMPT_GLOBAL_ESTANDAR,
        "max_tokens": 1500,
        "retries": 3,
        "delay": 2,
    },
    "GPT-OSS (OpenRouter)": {
        "tipo_api": "openrouter",
        "model_id": "openai/gpt-oss-120b:free",
        "api_key_var": "OPENROUTER_API_KEY",
        "output_prefix": "metaanalisis_gpt_oss",
        "tipo_prompt": "estandar",
        "prompt_individual_defecto": PROMPT_INDIVIDUAL_BIORREMEDIACION,
        "prompt_global_defecto": PROMPT_GLOBAL_ESTANDAR,
        "max_tokens": 1500,
        "retries": 3,
        "delay": 2,
    },
    "Claude (OpenRouter)": {
        "tipo_api": "openrouter",
        "model_id": "anthropic/claude-3-haiku",
        "api_key_var": "OPENROUTER_API_KEY",
        "output_prefix": "metaanalisis_claude",
        "tipo_prompt": "tablas",
        "prompt_individual_defecto": PROMPT_INDIVIDUAL_BIORREMEDIACION,
        "prompt_global_defecto": PROMPT_GLOBAL_TABLAS,
        "retries": 5,
        "delay": 2,
    },
    "Claude Nativo": {
        "tipo_api": "anthropic",
        "model_id": "claude-3-haiku-20240307",
        "api_key_var": "ANTHROPIC_API_KEY",
        "output_prefix": "metaanalisis_claude_nativo",
        "tipo_prompt": "tablas",
        "prompt_individual_defecto": PROMPT_INDIVIDUAL_BIORREMEDIACION,
        "prompt_global_defecto": PROMPT_GLOBAL_TABLAS,
        "max_tokens": 1000,
        "retries": 5,
        "delay": 2,
    },
    "Gemini (OpenRouter)": {
        "tipo_api": "openrouter",
        "model_id": "google/gemini-2.5-flash",
        "api_key_var": "OPENROUTER_API_KEY",
        "output_prefix": "metaanalisis_gemini_openrouter",
        "tipo_prompt": "estandar",
        "prompt_individual_defecto": PROMPT_INDIVIDUAL_BIORREMEDIACION,
        "prompt_global_defecto": PROMPT_GLOBAL_ESTANDAR,
        "max_tokens": 1500,
        "retries": 3,
        "delay": 2,
    },
    "Llama (Groq/OpenRouter)": {
        "tipo_api": "openrouter",
        "model_id": "meta-llama/llama-3.3-70b-instruct",
        "api_key_var": "OPENROUTER_API_KEY",
        "output_prefix": "metaanalisis_llama_groq",
        "tipo_prompt": "estandar",
        "prompt_individual_defecto": PROMPT_INDIVIDUAL_TAXONOMIA,
        "prompt_global_defecto": PROMPT_GLOBAL_ESTANDAR,
        "max_tokens": 1500,
        "retries": 3,
        "delay": 2,
    },
    "Cohere": {
        "tipo_api": "cohere",
        "model_id": "command-r-08-2024",
        "model_id_global": "command-r-plus-08-2024",
        "api_key_var": "COHERE_API_KEY",
        "output_prefix": "metaanalisis_cohere",
        "tipo_prompt": "tablas",
        "prompt_individual_defecto": PROMPT_INDIVIDUAL_BIORREMEDIACION,
        "prompt_global_defecto": PROMPT_GLOBAL_COHERE,
        "retries": 3,
        "delay": 5,
    },
    "Qwen 3": {
        "tipo_api": "openrouter",
        "model_id": "qwen/qwen3-coder:free",
        "api_key_var": "OPENROUTER_API_KEY",
        "output_prefix": "metaanalisis_qwen",
        "tipo_prompt": "estandar",
        "prompt_individual_defecto": PROMPT_INDIVIDUAL_BIORREMEDIACION,
        "prompt_global_defecto": PROMPT_GLOBAL_ESTANDAR,
        "retries": 5,
        "delay": 2,
    },
}
