import glob
import re

for file in glob.glob("iaProcess_*.py"):
    with open(file, "r", encoding="utf-8") as f:
        data = f.read()

    # 1. Update fallback prints logic
    data = data.replace("No hay artículos.", "No se seleccionó ningún archivo PDF.")
    data = data.replace("No hay artículos en la base de datos.", "No se seleccionó ningún archivo PDF.")
    data = data.replace("No hay artÃ\xadculos en la base de datos.", "No se seleccionó ningún archivo PDF.")
    data = data.replace("No hay artÃ\xadculos.", "No se seleccionó ningún archivo PDF.")
    
    # 2. Add outputs/ to paths if missing. We only care about txt and csv files.
    # Eg. "metaanalisis_gemini.txt" -> "outputs/metaanalisis_gemini.txt"
    # We must match strings that DO NOT start with outputs/
    # This regex looks for exactly quotes containing a filename that starts with "metaanalisis"
    # and ends in .txt or .csv
    
    data = re.sub(r'\"metaanalisis_([^\"\/\\]+)\.(txt|csv)\"', r'"outputs/metaanalisis_\1.\2"', data)
    
    with open(file, "w", encoding="utf-8") as f:
        f.write(data)

print("Paths y prints arreglados.")
