# synthetic-biology

Clasificación de papers científicos usando IA. Extraé información estructurada de PDFs y exportala a CSV listo para Google Sheets.

## Estructura

```
synthetic-biology/
├── data/               # Base de datos SQLite (artículos de PubMed)
├── outputs/            # Resultados: CSVs (clasificación) y .txt (reportes)
│   ├── metaanalisis_llama_groq.csv
│   └── ...
├── legacy/             # Scripts antiguos (funcionales, mantenidos por compatibilidad)
│   ├── iaProcess_Llama.py
│   ├── iaProcess_Qwen.py
│   ├── ...
│   ├── fix_paths.py
│   └── clean_scripts.py
├── src/                # Código principal
│   ├── __init__.py
│   ├── interfaz.py           # Interfaz gráfica (Tkinter) — entrada principal
│   ├── procesador_ia.py      # Motor unificado PDF → IA → CSV (también usable por CLI)
│   ├── config_modelos.py     # Configuración de los 8 modelos IA
│   ├── pdf_utils.py          # Extracción de texto de PDFs
│   ├── exportador.py         # Exportación a CSV (UTF-8 BOM, ;)
│   ├── database.py           # Modelo ORM de base de datos
│   ├── main.py               # Buscador de artículos en PubMed
│   ├── Printdb.py            # Debug: muestra primeros registros de la DB
│   └── csvtolist.py          # Conversor CSV → HTML
├── .env                # API keys (NO se sube a git)
├── .gitignore
├── requirements.txt
└── README.md
```

## Uso

### Interfaz gráfica (recomendado)

```bash
venv\Scripts\python.exe src/interfaz.py
```

1. Seleccioná un modelo de IA
2. Elegí un PDF
3. Dejá marcado **"Solo clasificación estructurada (CSV)"** para obtener solo datos, sin texto narrativo
4. Click en INICIAR

### Línea de comandos

```bash
venv\Scripts\python.exe src/procesador_ia.py "ruta/al/paper.pdf" "Llama (Groq/OpenRouter)"
```

Ver todos los modelos disponibles:

```bash
venv\Scripts\python.exe src/procesador_ia.py
```

### Actualizar base de datos desde PubMed

```bash
venv\Scripts\python.exe src/main.py --query "synthetic biology"
```

## Modelos disponibles

| Nombre | API | API Key en .env |
|--------|-----|-----------------|
| ChatGPT 5.4 Mini | OpenRouter | OPENROUTER_API_KEY |
| GPT-OSS | OpenRouter (gratis) | OPENROUTER_API_KEY |
| Claude | OpenRouter | OPENROUTER_API_KEY |
| Claude Nativo | Anthropic | ANTHROPIC_API_KEY |
| Gemini | OpenRouter | OPENROUTER_API_KEY |
| Llama 3.3 | OpenRouter | OPENROUTER_API_KEY |
| Cohere | Cohere | COHERE_API_KEY |
| Qwen 3 | OpenRouter (gratis) | OPENROUTER_API_KEY |
