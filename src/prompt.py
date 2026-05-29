"""Prompt único para clasificación de microorganismos.
Cambiá SOLO este archivo para modificar qué datos extrae la IA en todos los modelos."""

PROMPT_CLASIFICACION = """Extrae los siguientes datos de cada microorganismo encontrado en el texto cientifico en ESPAÑOL.
Responde estrictamente con este formato JSON. Si hay múltiples microorganismos, devuelve una lista de diccionarios bajo 'microorganismos':
{
  "microorganismos": [
    {
      "Dominio": "valor o N/D",
      "Filo": "valor o N/D",
      "Clase": "valor o N/D",
      "Orden": "valor o N/D",
      "Familia": "valor o N/D",
      "Genero": "valor o N/D",
      "Especie": "valor o N/D",
      "Cepa": "valor o N/D",
      "Fuente de la muestra de microorganismos": "valor o N/D",
      "Microbial Origin": "valor o N/D",
      "Ciudad y Pais de toma de muestra": "valor o N/D"
    }
  ]
}
Texto: {abstract}"""
