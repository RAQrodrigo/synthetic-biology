import os
from pony.orm import Database, Required

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'articles.db')

db = Database()

class Article(db.Entity):
    """
    Modelo de la entidad 'Article' para la base de datos que almacena información de PubMed.
    Contiene un PMID único, título y resumen del artículo.
    """
    pmid = Required(str, unique=True) 
    title = Required(str)
    abstract = Required(str)

def init_db():
    """
    Inicializa la conexión con la base de datos SQLite 'articles.db' ubicada en el directorio 'data/' 
    y mapea las entidades definidas.
    """
    db.bind(provider='sqlite', filename=DB_PATH, create_db=True)
    db.generate_mapping(create_tables=True)