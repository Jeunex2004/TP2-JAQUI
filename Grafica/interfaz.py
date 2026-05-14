import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

# Importaciones para embeber los gráficos de Matplotlib y detectar el cursor
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Importaciones de tu lógica
from Generadores.algoritmos import (
    generador_cuadrado_medio, generador_fibonacci,
    generador_congruencial_mixto, generador_congruencial_multiplicativo,
    escalar_valores
)
from Estadistica.pruebas import test_chi_cuadrado, test_correlacion_serial


class GeneradoresApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TP3 - Generadores Pseudoaleatorios")
        self.root.geometry("1280x750")
        self.serie_actual = []
        self.df_actual = pd.DataFrame()
        self.metodo_actual = ""
        # Variable fundamental para que no se borren los eventos del mouse
        self.canvas_actual = None 

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.tab_manual = ttk.Frame(self.notebook)
        self.tab_pruebas = ttk.Frame(self.notebook)
        self.tab_obligatorios = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_manual, text='Carga Manual')
        self.notebook.add(self.tab_pruebas, text='Pruebas Estadísticas')
        self.notebook.add(self.tab_obligatorios, text='Ejercicios Obligatorios')

        self.construir_tab_manual()
        self.construir_tab_pruebas()
        self.construir_tab_obligatorios()

    # ==========================================
    # FUNCIONES DE GRÁFICOS INTEGRADOS (CON TOOLTIPS SEGUROS)
    # ==========================================
    def dibujar_grafico_embebido(self, serie, titulo, frame_destino):
        # 1. Limpiar gráfico anterior
        for widget in frame_destino.winfo_children():
            widget.destroy()

        if not serie or len(serie) == 0:
            return

        # 2. Crear la figura de Matplotlib
        fig = Figure(figsize=(7, 4), dpi=100)
        
        # Histograma (Uniformidad)
        ax1 = fig.add_subplot(121)
        
        # Verificamos si estamos en una serie normal (0 a 1) o en el Ej 5 (Escalada)
        if min(serie) >= 0.0 and max(serie) <= 1.0:
            rango_hist = (0.0, 1.0)
        else:
            rango_hist = None # Dejamos que Matplotlib lo ajuste solo para el Ej 5

        n, bins, barras = ax1.hist(serie, bins=10, range=rango_hist, edgecolor='black', alpha=0.7)
        ax1.axhline(y=len(serie)/10, color='r', linestyle='dashed', label='F. Esperada')
        ax1.set_title("Histograma", fontsize=10)
        ax1.legend(fontsize=8)

        # Scatter Plot (Independencia)
        ax2 = fig.add_subplot(122)
        puntos_scatter = ax2.scatter(serie[:-1], serie[1:], alpha=0.5, s=10)
        ax2.set_title("Dispersión (Rezago 1)", fontsize=10)
        
        fig.suptitle(titulo, fontsize=12, fontweight='bold')
        fig.tight_layout()

        # --- LÓGICA DE ETIQUETAS FLOTANTES (TOOLTIPS) CORREGIDA ---
        # Usamos xytext=(0, 15) para que siempre floten un poquito arriba del mouse
        annot1 = ax1.annotate("", xy=(0,0), xytext=(0, 15), textcoords="offset points",
                              bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="black", alpha=1.0),
                              arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
                              zorder=100)
        annot1.set_clip_on(False)

        annot2 = ax2.annotate("", xy=(0,0), xytext=(0, 15), textcoords="offset points",
                              bbox=dict(boxstyle="round,pad=0.3", fc="lightcyan", ec="black", alpha=1.0),
                              arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
                              zorder=100)
        annot2.set_clip_on(False)

        def on_hover(event):
            # Si salimos del área de los gráficos, ocultamos las etiquetas
            if event.inaxes is None:
                if annot1.get_visible() or annot2.get_visible():
                    annot1.set_visible(False)
                    annot2.set_visible(False)
                    if self.canvas_actual: self.canvas_actual.draw_idle()
                return

            # Interacción con el Histograma
            if event.inaxes == ax1:
                annot2.set_visible(False)
                for barra in barras:
                    contiene, _ = barra.contains(event)
                    if contiene:
                        x = barra.get_x()
                        ancho = barra.get_width()
                        y = barra.get_height()
                        annot1.xy = (x + ancho / 2, y)
                        
                        # SOLUCIÓN DEL ERROR: Solo cambiamos la alineación (ha)
                        if (x + ancho / 2) > (ax1.get_xlim()[1] * 0.6):
                            annot1.set_ha('right')
                        else:
                            annot1.set_ha('left')

                        texto = f"Frecuencia: {int(y)}\nIntervalo: [{x:.2f}, {x+ancho:.2f}]"
                        annot1.set_text(texto)
                        annot1.set_visible(True)
                        if self.canvas_actual: self.canvas_actual.draw_idle()
                        return
                
                if annot1.get_visible():
                    annot1.set_visible(False)
                    if self.canvas_actual: self.canvas_actual.draw_idle()

            # Interacción con la Dispersión
            elif event.inaxes == ax2:
                annot1.set_visible(False)
                contiene, indices = puntos_scatter.contains(event)
                if contiene and len(indices["ind"]) > 0:
                    idx = indices["ind"][0]
                    pos = puntos_scatter.get_offsets()[idx]
                    annot2.xy = pos
                    
                    # SOLUCIÓN DEL ERROR: Solo cambiamos la alineación (ha)
                    if pos[0] > (ax2.get_xlim()[1] * 0.6):
                        annot2.set_ha('right')
                    else:
                        annot2.set_ha('left')
                        
                    texto = f"U_i: {pos[0]:.4f}\nU_i+1: {pos[1]:.4f}"
                    annot2.set_text(texto)
                    annot2.set_visible(True)
                    if self.canvas_actual: self.canvas_actual.draw_idle()
                else:
                    if annot2.get_visible():
                        annot2.set_visible(False)
                        if self.canvas_actual: self.canvas_actual.draw_idle()

        # 3. Embeber en Tkinter GUARDANDO LA REFERENCIA
        self.canvas_actual = FigureCanvasTkAgg(fig, master=frame_destino)
        self.canvas_actual.draw()
        self.canvas_actual.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Conectamos el evento del mouse al canvas guardado
        self.canvas_actual.mpl_connect("motion_notify_event", on_hover)

    def mostrar_resultado_obl(self, texto, serie=None, titulo_grafico=""):
        self.txt_obligatorios.delete(1.0, tk.END)
        self.txt_obligatorios.insert(tk.END, texto)

        if serie is not None:
            self.dibujar_grafico_embebido(serie, titulo_grafico, self.frame_graf_obl)
        else:
            for widget in self.frame_graf_obl.winfo_children():
                widget.destroy()
            self.canvas_actual = None

    # ==========================================
    # PESTAÑA MANUAL Y PRUEBAS
    # ==========================================
    def construir_tab_manual(self):
        frame_izq = ttk.Frame(self.tab_manual)
        frame_izq.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.frame_graf_manual = ttk.Frame(self.tab_manual)
        self.frame_graf_manual.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(frame_izq, text="Método:").grid(row=0, column=0, padx=5, pady=10, sticky='w')
        self.combo_metodo = ttk.Combobox(frame_izq, values=[
            "Cuadrados Medios", "Fibonacci", "Congruencial Mixto", "Congruencial Multiplicativo"
        ], state="readonly", width=25)
        self.combo_metodo.grid(row=0, column=1, padx=5, pady=10, sticky='w')
        self.combo_metodo.current(0)
        self.combo_metodo.bind("<<ComboboxSelected>>", self.actualizar_campos)

        self.frame_params = ttk.LabelFrame(frame_izq, text="Parámetros")
        self.frame_params.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.entradas = {}
        self.actualizar_campos()

        btn_frame = ttk.Frame(frame_izq)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="1. Generar", command=self.ejecutar_manual).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="2. Ver Gráfico", command=self.mostrar_graficos_manual).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="3. CSV", command=self.exportar_csv).pack(side=tk.LEFT, padx=2)

        frame_escala = ttk.LabelFrame(frame_izq, text="Escalar a [a, b] (opcional)")
        frame_escala.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        ttk.Label(frame_escala, text="a:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_manual_a = ttk.Entry(frame_escala, width=8)
        self.entry_manual_a.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frame_escala, text="b:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_manual_b = ttk.Entry(frame_escala, width=8)
        self.entry_manual_b.grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(frame_escala, text="Aplicar Escala", command=self.escalar_serie_manual).grid(row=0, column=4, padx=5, pady=5)

        self.texto_resultados = tk.Text(frame_izq, height=15, width=50)
        self.texto_resultados.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

    def actualizar_campos(self, event=None):
        for widget in self.frame_params.winfo_children():
            widget.destroy()
        self.entradas.clear()

        metodo = self.combo_metodo.get()
        campos = []
        if metodo == "Cuadrados Medios": campos = [("Semilla (X0)", "semilla"), ("Cantidad (n)", "n")]
        elif metodo == "Fibonacci": campos = [("X0", "x0"), ("X1", "x1"), ("Módulo (m)", "m"), ("Cantidad (n)", "n")]
        elif metodo == "Congruencial Mixto": campos = [("Semilla (X0)", "x0"), ("Multiplicador (a)", "a"), ("Constante (c)", "c"), ("Módulo (m)", "m"), ("Cantidad (n)", "n")]
        elif metodo == "Congruencial Multiplicativo": campos = [("Semilla (X0)", "x0"), ("Multiplicador (a)", "a"), ("Módulo (m)", "m"), ("Cantidad (n)", "n")]

        for i, (label_text, key) in enumerate(campos):
            ttk.Label(self.frame_params, text=label_text).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            ent = ttk.Entry(self.frame_params, width=15)
            ent.grid(row=i, column=1, padx=5, pady=5, sticky='w')
            if key == "n": ent.insert(0, "1000")
            self.entradas[key] = ent

    def ejecutar_manual(self):
        try:
            metodo = self.combo_metodo.get()
            self.metodo_actual = metodo
            n = int(self.entradas["n"].get())

            if metodo == "Cuadrados Medios":
                self.df_actual, self.serie_actual = generador_cuadrado_medio(int(self.entradas["semilla"].get()), n)
            elif metodo == "Fibonacci":
                self.df_actual, self.serie_actual = generador_fibonacci(int(self.entradas["x0"].get()), int(self.entradas["x1"].get()), int(self.entradas["m"].get()), n)
            elif metodo == "Congruencial Mixto":
                self.df_actual, self.serie_actual, _ = generador_congruencial_mixto(int(self.entradas["x0"].get()), int(self.entradas["a"].get()), int(self.entradas["c"].get()), int(self.entradas["m"].get()), n)
            elif metodo == "Congruencial Multiplicativo":
                self.df_actual, self.serie_actual, _ = generador_congruencial_multiplicativo(int(self.entradas["x0"].get()), int(self.entradas["a"].get()), int(self.entradas["m"].get()), n)

            self.texto_resultados.delete(1.0, tk.END)
            self.texto_resultados.insert(tk.END, f"Se generaron {n} valores exitosamente.\n\nPrimeros 20:\n")
            self.texto_resultados.insert(tk.END, self.df_actual.head(20).to_string(index=False))
            messagebox.showinfo("Éxito", "Serie generada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Verifique los datos ingresados: {e}")

    def exportar_csv(self):
        if self.df_actual.empty:
            return messagebox.showwarning("Aviso", "No hay serie para exportar.")
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if filepath:
            self.df_actual.to_csv(filepath, index=False)
            messagebox.showinfo("Éxito", "Datos exportados.")

    def mostrar_graficos_manual(self):
        if not self.serie_actual:
            return messagebox.showwarning("Aviso", "Genere una serie primero.")
        self.dibujar_grafico_embebido(self.serie_actual, self.metodo_actual, self.frame_graf_manual)

    def escalar_serie_manual(self):
        if not self.serie_actual:
            return messagebox.showwarning("Aviso", "Genere una serie primero.")
        try:
            a = float(self.entry_manual_a.get())
            b = float(self.entry_manual_b.get())
        except ValueError:
            return messagebox.showerror("Error", "Ingrese valores numéricos válidos para a y b.")
        if a >= b:
            return messagebox.showerror("Error", "El límite 'a' debe ser menor que 'b'.")

        serie_esc = escalar_valores(self.serie_actual, a, b)
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, f"Serie escalada al intervalo [{a}, {b}]\n")
        self.texto_resultados.insert(tk.END, f"Fórmula: X = {a} + ({b} - {a}) * U\n\n")
        self.texto_resultados.insert(tk.END, f"Primeros 10 valores:\n{[round(v, 4) for v in serie_esc[:10]]}\n\n")
        self.texto_resultados.insert(tk.END, f"Mínimo observado: {round(min(serie_esc), 4)}\n")
        self.texto_resultados.insert(tk.END, f"Máximo observado: {round(max(serie_esc), 4)}\n")
        self.dibujar_grafico_embebido(serie_esc, f"{self.metodo_actual} escalada [{a}, {b}]", self.frame_graf_manual)

    def construir_tab_pruebas(self):
        ttk.Button(self.tab_pruebas, text="Ejecutar Test Chi-Cuadrado y T-Student", command=self.ejecutar_pruebas).pack(pady=10)
        self.texto_pruebas = tk.Text(self.tab_pruebas, height=30, width=90)
        self.texto_pruebas.pack(padx=10, pady=10)

    def ejecutar_pruebas(self):
        if not self.serie_actual:
            return messagebox.showwarning("Aviso", "Primero genere una serie en Carga Manual.")
        
        self.texto_pruebas.delete(1.0, tk.END)
        self.texto_pruebas.insert(tk.END, f"=== ANÁLISIS DE SERIE ({self.metodo_actual}) ===\n\n")
        
        es_uni, chi_c, chi_t, df_chi = test_chi_cuadrado(self.serie_actual)
        self.texto_pruebas.insert(tk.END, "--- TEST CHI-CUADRADO (Uniformidad) ---\n")
        self.texto_pruebas.insert(tk.END, df_chi.to_string(index=False) + "\n")
        self.texto_pruebas.insert(tk.END, f"Chi Calc: {chi_c:.4f} | Chi Tabla: {chi_t:.4f} -> {'ACEPTA' if es_uni else 'RECHAZA'} H0\n\n")

        self.texto_pruebas.insert(tk.END, "--- TEST T-STUDENT (Independencia) ---\n")
        for h in [1, 2, 3]:
            es_indep, rho, t_c, t_t = test_correlacion_serial(self.serie_actual, h)
            res = "Acepta H0" if es_indep else "Rechaza H0"
            self.texto_pruebas.insert(tk.END, f"Rezago h={h} -> Rho: {rho:.4f} | t-calc: {t_c:.4f} | t-tabla: {t_t:.4f} | {res}\n")

    # ==========================================
    # PESTAÑA OBLIGATORIOS (CON TABLAS RESUMEN)
    # ==========================================
    def construir_tab_obligatorios(self):
        frame_btn = ttk.Frame(self.tab_obligatorios)
        frame_btn.pack(fill=tk.X, padx=10, pady=5)

        # Fila 1: Cuadrados Medios
        f1 = ttk.LabelFrame(frame_btn, text="Ej 1: Cuadrados Medios")
        f1.pack(fill=tk.X, pady=2)
        ttk.Button(f1, text="Degeneración (4567)", command=lambda: self.ej_1_deg(4567)).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(f1, text="Degeneración (1000)", command=lambda: self.ej_1_deg(1000)).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(f1, text="Degeneración (7654)", command=lambda: self.ej_1_deg(7654)).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(f1, text="Serie 4 dig (1234)", command=self.ej_1_4dig).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(f1, text="Serie 6 dig (123456)", command=self.ej_1_6dig).pack(side=tk.LEFT, padx=5, pady=2)

        f23 = ttk.Frame(frame_btn)
        f23.pack(fill=tk.X, pady=2)

        # Fila 2: Fibonacci
        f2 = ttk.LabelFrame(f23, text="Ej 2: Fibonacci")
        f2.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        ttk.Button(f2, text="Fibo (1, 1)", command=self.ej_2_conf1).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(f2, text="Fibo (3, 5)", command=self.ej_2_conf2).pack(side=tk.LEFT, padx=5, pady=2)

        # Fila 2: Mixto
        f3 = ttk.LabelFrame(f23, text="Ej 3: Congruencial Mixto")
        f3.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(f3, text="📋 Resumen 3a", command=self.ej_3a_resumen).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(f3, text="Caso A", command=lambda: self.ej_3a(15, 8, 16, 100, "A")).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(f3, text="Caso B", command=lambda: self.ej_3a(13, 50, 17, 100, "B")).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(f3, text="Caso C", command=lambda: self.ej_3a(7, 5, 24, 100, "C")).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(f3, text="Caso D", command=lambda: self.ej_3a(3, 5, 21, 100, "D")).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(f3, text="Caso E", command=lambda: self.ej_3a(8, 9, 13, 100, "E")).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(f3, text="Ej 3b (Serie)", command=self.ej_3b).pack(side=tk.LEFT, padx=5, pady=2)

        f45 = ttk.Frame(frame_btn)
        f45.pack(fill=tk.X, pady=2)

        # Fila 3: Multiplicativo
        f4 = ttk.LabelFrame(f45, text="Ej 4: Congruencial Multiplicativo")
        f4.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(f4, text="📋 Resumen 4", command=self.ej_4_resumen).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(f4, text="Caso A", command=lambda: self.ej_4(17, 203, 10**5, "A")).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(f4, text="Caso B", command=lambda: self.ej_4(19, 211, 10**8, "B")).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(f4, text="Caso C", command=lambda: self.ej_4(3, 221, 10**3, "C")).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(f4, text="Caso D", command=lambda: self.ej_4(7, 5, 64, "D")).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(f4, text="Caso E", command=lambda: self.ej_4(9, 11, 128, "E")).pack(side=tk.LEFT, padx=2, pady=2)

        # Fila 3: Ej5 Escalar
        f5 = ttk.LabelFrame(f45, text="Ej 5: Escalar Intervalo")
        f5.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Label(f5, text="a:").pack(side=tk.LEFT, padx=(5, 0), pady=2)
        self.entry_ej5_a = ttk.Entry(f5, width=6)
        self.entry_ej5_a.insert(0, "5")
        self.entry_ej5_a.pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Label(f5, text="b:").pack(side=tk.LEFT, padx=(5, 0), pady=2)
        self.entry_ej5_b = ttk.Entry(f5, width=6)
        self.entry_ej5_b.insert(0, "20")
        self.entry_ej5_b.pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(f5, text="Escalar", command=self.ej_5).pack(side=tk.LEFT, padx=5, pady=2)

        # Ej 6 y 7
        f6 = ttk.LabelFrame(f45, text="Ej 6 y 7")
        f6.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Button(f6, text="Pruebas a Todos", command=self.ej_6_7).pack(side=tk.LEFT, padx=5, pady=2)

        frame_contenido = ttk.Frame(self.tab_obligatorios)
        frame_contenido.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.txt_obligatorios = tk.Text(frame_contenido, width=45)
        self.txt_obligatorios.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.frame_graf_obl = ttk.Frame(frame_contenido)
        self.frame_graf_obl.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # --- LÓGICA DE LOS BOTONES ---
    def ej_1_deg(self, semilla):
        df, serie = generador_cuadrado_medio(semilla, 50)
        res = f"=== Ej 1: Degeneración (Semilla {semilla}) ===\n\nPrimeros 20 términos:\n"
        res += df.head(20).to_string(index=False)
        self.mostrar_resultado_obl(res, serie, f"Degeneración (Semilla {semilla})")

    def ej_1_4dig(self):
        df, serie = generador_cuadrado_medio(1234, 1000)
        res = "=== Ej 1: Semilla 4 dig (1234) ===\n\nPrimeros 20:\n" + df.head(20).to_string(index=False)
        self.mostrar_resultado_obl(res, serie, "Cuadrados Medios (4 dígitos)")

    def ej_1_6dig(self):
        df, serie = generador_cuadrado_medio(123456, 1000)
        res = "=== Ej 1: Semilla 6 dig (123456) ===\n\nPrimeros 20:\n" + df.head(20).to_string(index=False)
        self.mostrar_resultado_obl(res, serie, "Cuadrados Medios (6 dígitos)")

    def ej_2_conf1(self):
        df, serie = generador_fibonacci(1, 1, 100, 1000)
        res = "=== Ej 2: Fibo (X0=1, X1=1, m=100) ===\n\nPrimeros 20:\n" + df.head(20).to_string(index=False)
        self.mostrar_resultado_obl(res, serie, "Fibonacci (Conf 1)")

    def ej_2_conf2(self):
        df, serie = generador_fibonacci(3, 5, 1024, 1000)
        res = "=== Ej 2: Fibo (X0=3, X1=5, m=1024) ===\n\nPrimeros 20:\n" + df.head(20).to_string(index=False)
        self.mostrar_resultado_obl(res, serie, "Fibonacci (Conf 2)")

    def ej_3a_resumen(self):
        casos = [("A", 15, 8, 16, 100), ("B", 13, 50, 17, 100), ("C", 7, 5, 24, 100), ("D", 3, 5, 21, 100), ("E", 8, 9, 13, 100)]
        res = "=== Ej 3a: Tabla Resumen de Períodos ===\n\n"
        res += "Caso\tX0\tFórmula\t\t\tPeríodo\n"
        res += "-"*60 + "\n"
        for nombre, x0, a, c, m in casos:
            _, _, p = generador_congruencial_mixto(x0, a, c, m, m + 5)
            formula = f"X=({a}X+{c})mod{m}"
            res += f"{nombre}\t{x0}\t{formula:<15}\t{p if p else 'No repite'}\n"
        res += "\n(Presiona los botones Caso A, B, C... para ver su gráfica individual)"
        self.mostrar_resultado_obl(res, None)

    def ej_3a(self, x0, a, c, m, nombre_caso):
        df, serie, p = generador_congruencial_mixto(x0, a, c, m, min(m+5, 10000))
        res = f"=== Ej 3a: Caso {nombre_caso} ===\n"
        res += f"X0 = {x0}\nFórmula: X_n+1 = ({a}*X_n + {c}) mod {m}\n"
        res += f"Período detectado: {p if p else 'No repite'}\n\n"
        res += "Primeros 20 valores:\n" + df.head(20).to_string(index=False)
        
        serie_grafico = serie if len(serie) <= 1000 else serie[:1000]
        self.mostrar_resultado_obl(res, serie_grafico, f"C. Mixto - Caso {nombre_caso}")

    def ej_3b(self):
        df, serie, p = generador_congruencial_mixto(7, 5, 24, 100, 1000)
        res = f"=== Ej 3b: Serie C. Mixto ===\nPeríodo detectado: {p}\n\nPrimeros 20:\n" + df.head(20).to_string(index=False)
        self.mostrar_resultado_obl(res, serie, "Congruencial Mixto (Serie 1000)")

    def ej_4_resumen(self):
        casos = [("A", 17, 203, 10**5), ("B", 19, 211, 10**8), ("C", 3, 221, 10**3), ("D", 7, 5, 64), ("E", 9, 11, 128)]
        res = "=== Ej 4: Tabla Resumen de Períodos ===\n\n"
        res += "Caso\tX0\tFórmula\t\t\tPeríodo\n"
        res += "-"*55 + "\n"
        for nombre, x0, a, m in casos:
            _, _, p = generador_congruencial_multiplicativo(x0, a, m, min(m+5, 100000))
            formula = f"X=({a}X)mod{m}"
            res += f"{nombre}\t{x0}\t{formula:<15}\t{p if p else '> 100K'}\n"
        res += "\n(Presiona los botones Caso A, B, C... para ver su gráfica individual)"
        self.mostrar_resultado_obl(res, None)

    def ej_4(self, x0, a, m, nombre_caso):
        df, serie, p = generador_congruencial_multiplicativo(x0, a, m, min(m+5, 100000))
        res = f"=== Ej 4: Caso {nombre_caso} ===\n"
        res += f"X0 = {x0}\nFórmula: X_n+1 = ({a}*X_n) mod {m}\n"
        res += f"Período detectado: {p if p else '> 100K (Calculo truncado)'}\n\n"
        res += "Primeros 20 valores:\n" + df.head(20).to_string(index=False)
        
        serie_grafico = serie if len(serie) <= 1000 else serie[:1000]
        self.mostrar_resultado_obl(res, serie_grafico, f"C. Multiplicativo - Caso {nombre_caso}")

    def ej_5(self):
        try:
            a = float(self.entry_ej5_a.get())
            b = float(self.entry_ej5_b.get())
        except ValueError:
            return messagebox.showerror("Error", "Ingrese valores numéricos válidos para a y b.")
        if a >= b:
            return messagebox.showerror("Error", "El límite 'a' debe ser menor que 'b'.")

        _, serie_base, _ = generador_congruencial_mixto(7, 5, 24, 100, 1000)
        serie_esc = escalar_valores(serie_base, a, b)

        res = f"=== Ej 5: Escalar al intervalo [{a}, {b}] ===\n\n"
        res += f"Generador base: Congruencial Mixto (X0=7, a=5, c=24, m=100)\n"
        res += f"Fórmula: X = {a} + ({b} - {a}) * U\n\n"
        res += f"Primeros 10 valores escalados:\n"
        res += f"{[round(v, 4) for v in serie_esc[:10]]}\n\n"
        res += f"Mínimo observado: {round(min(serie_esc), 4)}\n"
        res += f"Máximo observado: {round(max(serie_esc), 4)}\n"
        self.mostrar_resultado_obl(res, serie_esc, f"Serie Escalada [{a}, {b}]")

    def ej_6_7(self):
        series = {
            "Ej1 - Cuadrados Medios": generador_cuadrado_medio(1234, 1000)[1],
            "Ej2 - Fibonacci": generador_fibonacci(3, 5, 1024, 1000)[1],
            "Ej3 - C. Mixto": generador_congruencial_mixto(7, 5, 24, 100, 1000)[1],
            "Ej4 - C. Multiplicativo": generador_congruencial_multiplicativo(17, 203, 10**5, 1000)[1]
        }
        separador = "=" * 55
        res = "=== EJERCICIOS 6 y 7: PRUEBAS ESTADÍSTICAS ===\n\n"

        for nombre, serie in series.items():
            res += f"{separador}\n  {nombre}\n{separador}\n\n"

            # EJ 6: Chi-cuadrado — tabla completa
            res += "[ EJ 6 ] TEST CHI-CUADRADO — Uniformidad (k=10, α=0.05)\n"
            es_uni, chi_c, chi_t, df_chi = test_chi_cuadrado(serie)
            res += df_chi.to_string(index=False) + "\n"
            res += f"\nX² calc = {chi_c:.4f}  |  X² tabla (gl=9, α=0.05) = {chi_t:.4f}\n"
            res += f"=> {'ACEPTA H0 — Serie uniforme' if es_uni else 'RECHAZA H0 — Serie NO uniforme'}\n\n"

            # EJ 7: Correlación serial — tabla resumen
            res += "[ EJ 7 ] CORRELACION SERIAL — Independencia\n"
            res += f"  {'h':>3}  {'rho_h':>8}  {'t-calc':>8}  {'t-tabla':>8}  Decision\n"
            res += "  " + "-" * 50 + "\n"
            for h in [1, 2, 3]:
                es_indep, rho, t_c, t_t = test_correlacion_serial(serie, h)
                decision = "Acepta H0" if es_indep else "Rechaza H0"
                res += f"  {h:>3}  {rho:>8.4f}  {t_c:>8.4f}  {t_t:>8.4f}  {decision}\n"
            res += "\n"

        self.mostrar_resultado_obl(res, series["Ej4 - C. Multiplicativo"], "Dispersion Rezago 1 — C. Multiplicativo")