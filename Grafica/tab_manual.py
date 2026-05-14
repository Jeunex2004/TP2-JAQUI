import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from Generadores.algoritmos import (
    generador_cuadrado_medio, generador_fibonacci,
    generador_congruencial_mixto, generador_congruencial_multiplicativo,
    escalar_valores
)

class TabManualMixin:
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

        self.texto_resultados = tk.Text(frame_izq, height=15, width=55, font=("Consolas", 10))
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
            self.df_actual.to_csv(filepath, index=False, sep=';')
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
        self.df_actual[f'Escalado [{a}, {b}]'] = serie_esc

        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, f"Serie escalada al intervalo [{a}, {b}]\n")
        self.texto_resultados.insert(tk.END, f"Fórmula: X = {a} + ({b} - {a}) * U\n\n")
        self.texto_resultados.insert(tk.END, f"Primeros 10 valores:\n{[round(v, 4) for v in serie_esc[:10]]}\n\n")
        self.texto_resultados.insert(tk.END, f"Mínimo observado: {round(min(serie_esc), 4)}\n")
        self.texto_resultados.insert(tk.END, f"Máximo observado: {round(max(serie_esc), 4)}\n")
        self.dibujar_grafico_embebido(serie_esc, f"{self.metodo_actual} escalada [{a}, {b}]", self.frame_graf_manual)