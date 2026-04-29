import os
import sys
import time
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# Diccionario de Modelos: Nombre en UI -> (Script, Archivo de Salida)
MODELOS = {
    "1. ChatGPT 5.4 Mini (OpenRouter)": ("iaProcess_ChatGPT_5_4.py", "outputs/metaanalisis_chatgpt_5_4_mini.txt"),
    "2. GPT-OSS (OpenRouter)": ("iaProcess_GPT.py", "outputs/metaanalisis_gpt_oss.txt"),
    "3. Claude (OpenRouter)": ("iaProcess_Claude.py", "outputs/metaanalisis_claude.txt"),
    "4. Claude Nativo": ("iaProcess_Claude_native.py", "outputs/metaanalisis_claude_nativo.txt"),
    "5. Gemini (OpenRouter)": ("iaProcess_Gemi.py", "outputs/metaanalisis_gemini_openrouter.txt"),
    "6. Llama (Groq/OpenRouter)": ("iaProcess_Llama.py", "outputs/metaanalisis_llama_groq.txt"),
    "7. Cohere": ("iaProcess_Cohere.py", "outputs/metaanalisis_cohere.txt"),
    "8. Qwen 3": ("iaProcess_Qwen.py", "outputs/metaanalisis_qwen.txt"),
}

def ejecutar_script():
    modelo = var_seleccion.get()
    if not modelo:
        messagebox.showwarning("Atención", "Por favor selecciona un modelo primero.")
        return
        
    script, output_file = MODELOS[modelo]
    
    # Verificamos si el script correspondiente existe
    if not os.path.exists(script):
        messagebox.showerror("Error", f"No se encontró el script: {script}\nAsegúrate de estar ejecutando la interfaz desde la carpeta src.")
        return

    # Extraemos solo el nombre limpio para mostrar
    nombre_limpio = modelo.split('. ', 1)[1] if '. ' in modelo else modelo

    # Bloquear interfaz temporalmente
    btn_iniciar.config(state="disabled", bg="#95a5a6", cursor="arrow")
    lbl_estado.config(text=f"Procesando con {nombre_limpio}...\n(Revisa tu consola CMD para el progreso)", fg="blue")
    lbl_tiempo.config(text="Tiempo transcurrido: 00:00")
    root.update()

    start_time = time.time()
    procesando = True
    progress_bar.start(25) # Animación más fluida

    def actualizar_tiempo():
        if procesando:
            elapsed = int(time.time() - start_time)
            mins, secs = divmod(elapsed, 60)
            lbl_tiempo.config(text=f"⏱️ Tiempo transcurrido: {mins:02d}:{secs:02d}")
            root.after(1000, actualizar_tiempo)

    actualizar_tiempo()

    def hilo_proceso():
        nonlocal procesando
        try:
            # Ejecuta el script usando el mismo ejecutable de Python (el del venv actual)
            subprocess.run([sys.executable, script], check=True)
            
            lbl_estado.config(text="¡Análisis finalizado con éxito!\nAbriendo resultados...", fg="green")
            
            # os.startfile funciona exclusivamente de maravilla en Windows
            ruta_absoluta = os.path.abspath(output_file)
            if os.path.exists(ruta_absoluta):
                os.startfile(ruta_absoluta)
            else:
                messagebox.showwarning("Atención", f"El proceso terminó pero no se encontró el reporte:\n{output_file}")
                
        except subprocess.CalledProcessError:
            lbl_estado.config(text="El proceso terminó con errores.", fg="red")
            messagebox.showerror("Error", "Hubo un error durante la ejecución. Revisa la consola para más detalles.")
        except Exception as e:
            lbl_estado.config(text="Error inesperado.", fg="red")
            messagebox.showerror("Error", str(e))
        finally:
            procesando = False
            progress_bar.stop() # Detiene y reinicia la barra
            # Restaurar botón
            btn_iniciar.config(state="normal", bg="#3498db", cursor="hand2")

    # Se usa hilo para evitar que se congele "No Responde" mientras procesa
    threading.Thread(target=hilo_proceso, daemon=True).start()

# --- CONFIGURACIÓN VISUAL (TKINTER) ---
root = tk.Tk()
root.title("Panel de Control - Análisis IA")
root.geometry("400x340")
root.resizable(False, False)

# Configurar un poco el estilo nativo
style = ttk.Style()
style.configure("TButton", font=("Arial", 11, "bold"), padding=10)

# Título Principal
lbl_titulo = tk.Label(root, text="🔬 Analizador de Abstracts", font=("Arial", 16, "bold"), fg="#2c3e50")
lbl_titulo.pack(pady=20)

lbl_instruccion = tk.Label(root, text="Selecciona el modelo de IA que deseas usar:", font=("Arial", 10))
lbl_instruccion.pack(pady=5)

var_seleccion = tk.StringVar(value="")

combo_modelos = ttk.Combobox(root, textvariable=var_seleccion, values=list(MODELOS.keys()), state="readonly", font=("Arial", 11), width=28)
combo_modelos.pack(pady=10)
combo_modelos.current(0) # Selecciona el primero por defecto

# Crear un contenedor inferior para botones y labels
frame_inferior = tk.Frame(root)
frame_inferior.pack(side="bottom", fill="x", pady=20)

# Label de estado que va cambiando (height=2 evita saltos visuales)
lbl_estado = tk.Label(frame_inferior, text="Esperando selección...", font=("Arial", 10, "italic"), fg="gray", justify="center", height=2)
lbl_estado.pack(pady=5)

lbl_tiempo = tk.Label(frame_inferior, text="", font=("Arial", 9, "bold"), fg="#d35400")
lbl_tiempo.pack(pady=5)

progress_bar = ttk.Progressbar(frame_inferior, orient="horizontal", length=250, mode="indeterminate")
progress_bar.pack(pady=5)

# Botón Iniciar (Destacado, tipo standard tk.Button para evitar glitches en Windows 11)
btn_iniciar = tk.Button(frame_inferior, text="🚀 INICIAR ANÁLISIS", font=("Arial", 11, "bold"), bg="#3498db", fg="white", relief="raised", padx=15, pady=5, cursor="hand2", command=ejecutar_script)
btn_iniciar.pack(pady=5)

# Renderizar la ventana
root.mainloop()
