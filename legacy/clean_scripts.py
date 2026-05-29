import glob
import re

for file in glob.glob("iaProcess_*.py"):
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Remove pony and database imports
    content = re.sub(r"from pony\.orm import db_session\n?", "", content)
    content = re.sub(r"from database import Article, init_db\n?", "", content)
    
    # Remove init_db() calls
    content = re.sub(r"^\s*init_db\(\)\n?", "", content, flags=re.MULTILINE)
    
    # Replace obtener_articulos() with non-DB version
    # The current version has @db_session ... def obtener_articulos(): ... return [a for a in todos if a.abstract and a.abstract.strip() != ""]
    # We want to replace it entirely
    
    replacement = '''def obtener_articulos():
    import os, json
    import pdf_utils
    class VirtualArticle:
        def __init__(self, pmid, abstract):
            self.pmid = pmid
            self.abstract = abstract

    ruta_custom = "outputs/.custom_prompts.json"
    if os.path.exists(ruta_custom):
        try:
            with open(ruta_custom, "r", encoding="utf-8") as f:
                data = json.load(f)
                pdf_path = data.get("pdf_path", "")
                if pdf_path and os.path.exists(pdf_path):
                    texto = pdf_utils.extraer_texto_pdf(pdf_path)
                    if texto.strip():
                        return [VirtualArticle("PDF_Local", texto)]
        except Exception as e:
            pass
    return []'''
    
    content = re.sub(r"@db_session\s+def obtener_articulos\(\):.*?return \[a for a in todos if a\.abstract and a\.abstract\.strip\(\) != \"\"\]", replacement, content, flags=re.DOTALL)
    
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)

print("Archivos limpiados.")
