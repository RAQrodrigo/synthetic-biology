from database import Article, init_db
from pony.orm import db_session

init_db()

@db_session
def mostrar_primeros_10():
    """
    Recupera y muestra por consola los primeros 10 artículos almacenados en la base de datos,
    imprimiendo sus respectivos PMID, títulos y un fragmento corto del abstract.
    """
    articulos = Article.select()[:10]

    for a in articulos:
        print("\nPMID:", a.pmid)
        print("TITLE:", a.title)
        print("ABSTRACT:", a.abstract[:200], "...")  # recorto para que no sea gigante

mostrar_primeros_10()