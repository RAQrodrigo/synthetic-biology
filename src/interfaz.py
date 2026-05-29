import os
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

os.chdir(os.path.dirname(os.path.abspath(__file__)))

import procesador_ia
import config_modelos

def on_combo_change(event=None):
    modelo = var_seleccion.get()
    if not modelo:
        return
    config = config_modelos.MODELOS[modelo]
    txt_indiv.delete("1.0", tk.END)
    txt_indiv.insert(tk.END, config["prompt_individual_defecto"])
    txt_global.delete("1.0", tk.END)
    txt_global.insert(tk.END, config["prompt_global_defecto"])

def toggle_reporte_texto():
    if var_solo_clasificacion.get():
        txt_global.config(state="disabled", bg="#f0f0f0")
    else:
        txt_global.config(state="normal", bg="#fdfdfd")

def ejecutar_analisis():
    modelo = var_seleccion.get()
    if not modelo:
        messagebox.showwarning("Atención", "Selecciona un modelo primero.")
        return

    pdf_path = var_pdf_path.get().strip()
    if not pdf_path:
        messagebox.showwarning("Atención", "Selecciona un archivo PDF primero.")
        return

    if not os.path.exists(pdf_path):
        messagebox.showerror("Error", f"No se encuentra el PDF:\n{pdf_path}")
        return

    solo_clasificacion = var_solo_clasificacion.get()
    prompt_indiv = txt_indiv.get("1.0", tk.END).strip()
    prompt_global = txt_global.get("1.0", tk.END).strip()

    btn_iniciar.config(state="disabled", bg="#95a5a6", cursor="arrow")
    lbl_estado.config(text="Procesando... (Revisa la consola para el progreso)", fg="blue")
    lbl_tiempo.config(text="Tiempo transcurrido: 00:00")
    root.update()

    start_time = time.time()
    procesando = True
    progress_bar.start(15)

    def actualizar_tiempo():
        if procesando:
            elapsed = int(time.time() - start_time)
            mins, secs = divmod(elapsed, 60)
            lbl_tiempo.config(text=f"Tiempo transcurrido: {mins:02d}:{secs:02d}")
            root.after(1000, actualizar_tiempo)

    actualizar_tiempo()

    def hilo():
        nonlocal procesando
        try:
            resultados, csv_path = procesador_ia.procesar_pdf(
                ruta_pdf=pdf_path,
                nombre_modelo=modelo,
                prompt_individual=prompt_indiv,
                prompt_global=prompt_global,
                generar_reporte=not solo_clasificacion,
            )

            if csv_path:
                lbl_estado.config(
                    text=f"Finalizado. CSV guardado en:\n{csv_path}",
                    fg="green",
                )
                root.after(500, lambda: os.startfile(os.path.abspath(csv_path)))
            else:
                lbl_estado.config(text="No se obtuvieron resultados.", fg="orange")

        except Exception as e:
            lbl_estado.config(text="Error durante el análisis.", fg="red")
            messagebox.showerror("Error", str(e))

        finally:
            procesando = False
            progress_bar.stop()
            btn_iniciar.config(state="normal", bg="#3498db", cursor="hand2")

    threading.Thread(target=hilo, daemon=True).start()

root = tk.Tk()
root.title("Analizador de Papers - Clasificacion IA")
root.geometry("620x680")
root.resizable(False, False)

style = ttk.Style()
style.configure("TButton", font=("Arial", 11, "bold"), padding=10)

lbl_titulo = tk.Label(root, text="Analizador de Papers", font=("Arial", 16, "bold"), fg="#2c3e50")
lbl_titulo.pack(pady=10)

frame_superior = tk.Frame(root)
frame_superior.pack(fill="x", padx=40)

lbl_modelo = tk.Label(frame_superior, text="Modelo de IA:", font=("Arial", 10))
lbl_modelo.pack(anchor="w")

var_seleccion = tk.StringVar(value="")
lista_modelos = list(config_modelos.MODELOS.keys())
combo_modelos = ttk.Combobox(
    frame_superior, textvariable=var_seleccion,
    values=lista_modelos, state="readonly",
    font=("Arial", 11), width=48,
)
combo_modelos.pack(anchor="w", pady=5)
combo_modelos.bind("<<ComboboxSelected>>", on_combo_change)

var_pdf_path = tk.StringVar(value="")

def seleccionar_pdf():
    filepath = filedialog.askopenfilename(
        title="Seleccionar archivo PDF",
        filetypes=[("Archivos PDF", "*.pdf")]
    )
    if filepath:
        var_pdf_path.set(filepath)

frame_pdf = tk.Frame(root)
frame_pdf.pack(fill="x", padx=40, pady=5)

lbl_pdf = tk.Label(frame_pdf, text="Archivo PDF a analizar:", font=("Arial", 10, "bold"))
lbl_pdf.pack(anchor="w")

frame_pdf_inner = tk.Frame(frame_pdf)
frame_pdf_inner.pack(fill="x", pady=2)

ent_pdf_path = tk.Entry(frame_pdf_inner, textvariable=var_pdf_path, state="readonly", width=45)
ent_pdf_path.pack(side="left", fill="x", expand=True, padx=(0, 5))

btn_seleccionar_pdf = tk.Button(frame_pdf_inner, text="Examinar...", command=seleccionar_pdf, bg="#ecf0f1")
btn_seleccionar_pdf.pack(side="left")

var_solo_clasificacion = tk.BooleanVar(value=True)

cb_solo_clasificacion = tk.Checkbutton(
    root,
    text="Solo clasificacion estructurada (CSV). Sin reporte de texto.",
    variable=var_solo_clasificacion,
    command=toggle_reporte_texto,
    font=("Arial", 9),
)
cb_solo_clasificacion.pack(anchor="w", padx=40, pady=(10, 0))

frame_prompts = tk.Frame(root)
frame_prompts.pack(fill="both", expand=True, padx=40, pady=5)

lbl_indiv = tk.Label(
    frame_prompts,
    text="Prompt individual (usa {abstract}):",
    font=("Arial", 9, "bold"), fg="#34495e",
)
lbl_indiv.pack(anchor="w")
txt_indiv = tk.Text(
    frame_prompts, font=("Consolas", 10), height=8,
    bg="#fdfdfd", wrap="word", relief="groove",
)
txt_indiv.pack(fill="x", pady=2)

lbl_global = tk.Label(
    frame_prompts,
    text="Prompt reporte global (usa {datos}):",
    font=("Arial", 9, "bold"), fg="#34495e",
)
lbl_global.pack(anchor="w", pady=(8, 0))
txt_global = tk.Text(
    frame_prompts, font=("Consolas", 10), height=7,
    bg="#f0f0f0", wrap="word", relief="groove",
)
txt_global.pack(fill="x", pady=2)
txt_global.config(state="disabled")

frame_inferior = tk.Frame(root)
frame_inferior.pack(side="bottom", fill="x", pady=10)

lbl_estado = tk.Label(
    frame_inferior,
    text="Selecciona un PDF y un modelo, luego inicia el analisis.",
    font=("Arial", 10, "italic"), fg="gray",
    justify="center", height=2,
)
lbl_estado.pack(pady=2)

lbl_tiempo = tk.Label(frame_inferior, text="", font=("Arial", 9, "bold"), fg="#d35400")
lbl_tiempo.pack(pady=2)

progress_bar = ttk.Progressbar(frame_inferior, orient="horizontal", length=300, mode="indeterminate")
progress_bar.pack(pady=2)

btn_iniciar = tk.Button(
    frame_inferior,
    text="INICIAR ANALISIS",
    font=("Arial", 11, "bold"), bg="#3498db", fg="white",
    relief="raised", padx=20, pady=5, cursor="hand2",
    command=ejecutar_analisis,
)
btn_iniciar.pack(pady=5)

if lista_modelos:
    combo_modelos.current(0)
    on_combo_change(None)

root.mainloop()
