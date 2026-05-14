import tkinter as tk
from tkinter import ttk, messagebox
from Generadores.algoritmos import (
    generador_cuadrado_medio, generador_fibonacci,
    generador_congruencial_mixto, generador_congruencial_multiplicativo,
    escalar_valores
)
from Estadistica.pruebas import test_chi_cuadrado, test_correlacion_serial

class TabObligatoriosMixin:
    def mostrar_resultado_obl(self, texto, serie=None, titulo_grafico=""):
        self.txt_obligatorios.delete(1.0, tk.END)
        self.txt_obligatorios.insert(tk.END, texto)

        if serie is not None:
            self.dibujar_grafico_embebido(serie, titulo_grafico, self.frame_graf_obl)
        else:
            for widget in self.frame_graf_obl.winfo_children():
                widget.destroy()
            self.canvas_actual = None

    def construir_tab_obligatorios(self):
        frame_btn = ttk.Frame(self.tab_obligatorios)
        frame_btn.pack(fill=tk.X, padx=10, pady=5)

        f1 = ttk.LabelFrame(frame_btn, text="Ej 1: Cuadrados Medios")
        f1.pack(fill=tk.X, pady=2)
        ttk.Button(f1, text="Degeneración (4567)", command=lambda: self.ej_1_deg(4567)).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(f1, text="Degeneración (1000)", command=lambda: self.ej_1_deg(1000)).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(f1, text="Degeneración (7654)", command=lambda: self.ej_1_deg(7654)).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(f1, text="Serie 4 dig (1234)", command=self.ej_1_4dig).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(f1, text="Serie 6 dig (123456)", command=self.ej_1_6dig).pack(side=tk.LEFT, padx=5, pady=2)

        f23 = ttk.Frame(frame_btn)
        f23.pack(fill=tk.X, pady=2)

        f2 = ttk.LabelFrame(f23, text="Ej 2: Fibonacci")
        f2.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        ttk.Button(f2, text="Fibo (1, 1)", command=self.ej_2_conf1).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(f2, text="Fibo (3, 5)", command=self.ej_2_conf2).pack(side=tk.LEFT, padx=5, pady=2)

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

        f4 = ttk.LabelFrame(f45, text="Ej 4: Congruencial Multiplicativo")
        f4.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(f4, text="📋 Resumen 4", command=self.ej_4_resumen).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(f4, text="Caso A", command=lambda: self.ej_4(17, 203, 10**5, "A")).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(f4, text="Caso B", command=lambda: self.ej_4(19, 211, 10**8, "B")).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(f4, text="Caso C", command=lambda: self.ej_4(3, 221, 10**3, "C")).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(f4, text="Caso D", command=lambda: self.ej_4(7, 5, 64, "D")).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(f4, text="Caso E", command=lambda: self.ej_4(9, 11, 128, "E")).pack(side=tk.LEFT, padx=2, pady=2)

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

        f6 = ttk.LabelFrame(f45, text="Ej 6 y 7: Pruebas Estadísticas")
        f6.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        self.combo_ej67 = ttk.Combobox(f6, values=[
            "Ej 1: Cuadrados Medios", 
            "Ej 2: Fibonacci", 
            "Ej 3: C. Mixto", 
            "Ej 4: C. Multiplicativo"
        ], state="readonly", width=22)
        self.combo_ej67.current(0)
        self.combo_ej67.pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(f6, text="Ejecutar Test", command=self.ej_6_7_individual).pack(side=tk.LEFT, padx=5, pady=2)

        frame_contenido = ttk.Frame(self.tab_obligatorios)
        frame_contenido.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.txt_obligatorios = tk.Text(frame_contenido, width=70, wrap=tk.NONE, font=("Consolas", 9))
        self.txt_obligatorios.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.frame_graf_obl = ttk.Frame(frame_contenido)
        self.frame_graf_obl.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

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

    def ej_6_7_individual(self):
        seleccion = self.combo_ej67.get()
        
        if "Ej 1" in seleccion:
            _, serie = generador_cuadrado_medio(1234, 1000)
            nombre = "Ej 1 - Cuadrados Medios"
        elif "Ej 2" in seleccion:
            _, serie = generador_fibonacci(3, 5, 1024, 1000)
            nombre = "Ej 2 - Fibonacci"
        elif "Ej 3" in seleccion:
            _, serie, _ = generador_congruencial_mixto(7, 5, 24, 100, 1000)
            nombre = "Ej 3 - C. Mixto"
        else:
            _, serie, _ = generador_congruencial_multiplicativo(17, 203, 10**5, 1000)
            nombre = "Ej 4 - C. Multiplicativo"

        separador = "=" * 55
        res = "=== EJERCICIOS 6 y 7: PRUEBAS ESTADÍSTICAS ===\n\n"
        res += f"{separador}\n  {nombre}\n{separador}\n\n"

        res += "[ EJ 6 ] TEST CHI-CUADRADO — Uniformidad (k=10, α=0.05)\n"
        es_uni, chi_c, chi_t, df_chi = test_chi_cuadrado(serie)
        res += df_chi.to_string(index=False) + "\n"
        res += f"\nX² calc = {chi_c:.4f}  |  X² tabla (gl=9, α=0.05) = {chi_t:.4f}\n"
        res += f"=> {'ACEPTA H0 — Serie uniforme' if es_uni else 'RECHAZA H0 — Serie NO uniforme'}\n\n"

        res += "[ EJ 7 ] CORRELACION SERIAL — Independencia\n"
        res += f"  {'h':>3}  {'rho_h':>8}  {'t-calc':>8}  {'t-tabla':>8}  Decision\n"
        res += "  " + "-" * 50 + "\n"
        for h in [1, 2, 3]:
            es_indep, rho, t_c, t_t = test_correlacion_serial(serie, h)
            decision = "Acepta H0" if es_indep else "Rechaza H0"
            res += f"  {h:>3}  {rho:>8.4f}  {t_c:>8.4f}  {t_t:>8.4f}  {decision}\n"
        res += "\n"

        self.mostrar_resultado_obl(res, serie, f"Pruebas — {nombre}")