import glob
import re

for file in glob.glob("iaProcess_*.py"):
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
        
    if "import exportador" not in content:
        content = content.replace("import time", "import time\nimport exportador")
        
    pattern = r'(with open\("([^"]+)", \s*"w",\s*encoding="utf-8"\)\s*as\s+f:\s*\n\s*f\.write\(reporte( or "[^"]*")?\)\s*\n\s*print\([^\n]+\))'
    
    def replacer(match):
        full_block = match.group(1)
        txt_path = match.group(2)
        csv_path = txt_path.replace(".txt", ".csv")
        return full_block + f'\n        exportador.guardar_csv(resultados, "{csv_path}")'
        
    content = re.sub(pattern, replacer, content)
    
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)
print("CSV Export agregado.")
