from pony.orm import Database, Required

db = Database()

class Article(db.Entity):
    pmid = Required(str, unique=True)  # 🔥 clave única real
    title = Required(str)
    abstract = Required(str)

def init_db():
    db.bind(provider='sqlite', filename='articles.db', create_db=True)
    db.generate_mapping(create_tables=True)