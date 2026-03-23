from Bio import Entrez
from dotenv import load_dotenv
import os
import time
import csv
import sys
import argparse
from pony.orm import db_session
from pony.orm.core import TransactionIntegrityError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'abstracts.csv')
from pony.orm import db_session
from pony.orm.core import TransactionIntegrityError


from database import Article, init_db
load_dotenv()
init_db()

EMAIL = os.environ["EMAIL"]
BATCH_SIZE = 10
MAX_RESULTS = 50

def main(query):
    """
    Punto de entrada principal para buscar artículos en PubMed a partir de una query,
    extraer los resultados por lotes mediante XML, limpiar y guardar cada abstract
    tanto en una base de datos local como en un archivo CSV.
    """
    Entrez.email = EMAIL
    # Entrez.api_key = os.environ.get("NCBI_API_KEY") # Altamente recomendado

    # 1. Buscar papers
    search_handle = Entrez.esearch(db="pubmed", term=query, retmax=MAX_RESULTS)
    search_results = Entrez.read(search_handle)
    id_list = search_results.get("IdList", [])

    print(f"IDs encontrados: {len(id_list)}")

    all_articles_data = []

    # 2. Traer y procesar en batches
    for i in range(0, len(id_list), BATCH_SIZE):
        batch_ids = id_list[i:i+BATCH_SIZE]
        
        try:
            fetch_handle = Entrez.efetch(db="pubmed", id=batch_ids, retmode="xml")
            records = Entrez.read(fetch_handle)
        except Exception as e:
            print(f"Error en fetch: {e}")
            continue

        batch_data = []
        for article in records.get("PubmedArticle", []):
            try:
                medline = article["MedlineCitation"]
                article_info = medline["Article"]
                pmid = str(medline["PMID"])
                title = article_info.get("ArticleTitle", "Sin título")

                # --- Parseo Robusto de Abstract ---
                abstract_text = ""
                if "Abstract" in article_info:
                    abstract_parts = article_info["Abstract"]["AbstractText"]
                    # PubMed a veces devuelve una lista de strings o una lista de objetos String con atributos
                    abstract_text = " ".join([str(part) for part in abstract_parts])

                if abstract_text.strip():
                    item = {"pmid": pmid, "title": title, "abstract": abstract_text}
                    batch_data.append(item)
                    all_articles_data.append(item)

            except KeyError as e:
                print(f"Estructura XML inesperada en PMID {pmid if 'pmid' in locals() else 'unknown'}: {e}")

        # 3. Guardar en DB por cada batch (más seguro)
        save_to_db(batch_data)
        time.sleep(0.3) # Respetar rate limit

    # 4. Guardar en CSV final
    save_to_csv(all_articles_data)

@db_session
def save_to_db(data):
    """
    Recibe una lista de diccionarios con datos de artículos y los inserta de manera
    segura en la base de datos omitiendo aquellos que ya existen registrados (comparando PMID).
    """
    for art in data:
        try:
            # Usamos get o try-except para evitar duplicados
            if not Article.exists(pmid=art["pmid"]):
                Article(pmid=art["pmid"], title=art["title"], abstract=art["abstract"])
        except Exception as e:
            print(f"Error guardando {art['pmid']}: {e}")

def save_to_csv(data):
    """
    Exporta la recopilación final de todos los artículos extraídos de PubMed
    (PMID, título, abstract) a un archivo `abstracts.csv` en el directorio de `data`.
    """
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["pmid", "title", "abstract"])
        writer.writeheader()
        writer.writerows(data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Pubmed process")
    parser.add_argument("--query", required=True, help="Querys a filtrar")
    args = parser.parse_args()
    main(args.query)