from database import Article, init_db
from pony.orm import db_session

init_db()

@db_session
def mostrar_primeros_10():
    articulos = Article.select()[:10]

    for a in articulos:
        print("\nPMID:", a.pmid)
        print("TITLE:", a.title)
        print("ABSTRACT:", a.abstract[:200], "...")  # recorto para que no sea gigante

mostrar_primeros_10()