import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import pandas as pd
from tabulate import tabulate

# ==========================================
# LÓGICA MATEMÁTICA Y ESTADÍSTICA
# ==========================================

def generador_cuadrado_medio(semilla, n_iteraciones):
    resultados = []
    x_actual = semilla
    digitos = len(str(semilla))
    
    for i in range(n_iteraciones):
        cuadrado = x_actual ** 2
        cuadrado_str = str(cuadrado).zfill(digitos * 2)
        inicio = digitos // 2
        fin = inicio + digitos
        centro_str = cuadrado_str[inicio:fin]
        
        x_siguiente = int(centro_str)
        u_i = x_siguiente / (10 ** digitos)
        
        resultados.append({
            'i': i + 1, 'X_i': x_actual, 'X_i^2': cuadrado, 
            'Dig_Centrales': centro_str, 'U_i': u_i
        })
        x_actual = x_siguiente
        
    return pd.DataFrame(resultados), [r['U_i'] for r in resultados]

def generador_fibonacci(x0, x1, m, n_iteraciones):
    resultados = []
    secuencia = [x0, x1]
    
    for i in range(n_iteraciones):
        x_siguiente = (secuencia[-1] + secuencia[-2]) % m
        u_i = x_siguiente / m
        
        resultados.append({
            'i': i + 1, 'X_i-1': secuencia[-2], 'X_i': secuencia[-1], 
            'X_i+1': x_siguiente, 'U_i': u_i
        })
        secuencia.append(x_siguiente)
        
    return pd.DataFrame(resultados), [r['U_i'] for r in resultados]

def generador_congruencial_mixto(x0, a, c, m, n_iteraciones):
    resultados = []
    x_actual = x0
    valores_vistos = {}
    periodo = None
    buscar_periodo = True
    
    for i in range(n_iteraciones):
        x_siguiente = (a * x_actual + c) % m
        u_i = x_siguiente / m
        
        resultados.append({
            'i': i + 1, 'X_i': x_actual, 'aX_i+c': a * x_actual + c, 
            'X_i+1': x_siguiente, 'U_i': u_i
        })
        
        # Límite de seguridad para evitar desbordes de memoria en periodos enormes (ej: m=10^8)
        if buscar_periodo and periodo is None:
            if x_actual in valores_vistos:
                periodo = i - valores_vistos[x_actual]
            else:
                if len(valores_vistos) < 100000:
                    valores_vistos[x_actual] = i
                else:
                    buscar_periodo = False # Detiene la búsqueda si es muy grande
                
        x_actual = x_siguiente
        
    return pd.DataFrame(resultados), [r['U_i'] for r in resultados], periodo

def generador_congruencial_multiplicativo(x0, a, m, n_iteraciones):
    return generador_congruencial_mixto(x0, a, 0, m, n_iteraciones)

def escalar_valores(serie_u, a, b):
    return [a + (b - a) * u for u in serie_u]

def test_chi_cuadrado(serie_u, k=10, alpha=0.05):
    n = len(serie_u)
    if n == 0: return False, 0, 0, pd.DataFrame()
    frec_esperadas = n / k
    frec_observadas, bordes = np.histogram(serie_u, bins=k, range=(0, 1))
    
    chi_calc = np.sum(((frec_observadas - frec_esperadas) ** 2) / frec_esperadas)
    chi_tabla = stats.chi2.ppf(1 - alpha, k - 1)
    es_uniforme = chi_calc < chi_tabla
    
    datos = [[f"[{bordes[i]:.1f}-{bordes[i+1]:.1f})", frec_observadas[i], frec_esperadas, 
              (frec_observadas[i]-frec_esperadas)**2 / frec_esperadas] for i in range(k)]
    df_chi = pd.DataFrame(datos, columns=["Intervalo", "f_o", "f_e", "((fo-fe)^2)/fe"])
    
    return es_uniforme, chi_calc, chi_tabla, df_chi

def test_correlacion_serial(serie_u, rezago_h, alpha=0.05):
    n = len(serie_u)
    if n - rezago_h - 2 <= 0: return False, 0, 0, 0
    
    sumatoria = sum(serie_u[i] * serie_u[i + rezago_h] for i in range(n - rezago_h))
    rho_h = ((1 / (n - rezago_h)) * sumatoria - 0.25) / (1 / 12)
    
    if abs(rho_h) >= 1.0: return False, rho_h, float('inf'), 0
    
    t_calc = (rho_h * np.sqrt(n - rezago_h - 2)) / np.sqrt(1 - rho_h**2)
    t_tabla = stats.t.ppf(1 - alpha / 2, n - rezago_h - 2)
    es_independiente = abs(t_calc) < t_tabla
    
    return es_independiente, rho_h, t_calc, t_tabla

# ==========================================
# INTERFAZ GRÁFICA (GUI)
# ==========================================

class GeneradoresApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TP3 - Generadores Pseudoaleatorios")
        self.root.geometry("850x700")
        self.serie_actual = []
        self.df_actual = pd.DataFrame()
        self.metodo_actual = ""

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

    # --- PESTAÑA MANUAL ---
    def construir_tab_manual(self):
        ttk.Label(self.tab_manual, text="Método:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.combo_metodo = ttk.Combobox(self.tab_manual, values=[
            "Cuadrados Medios", "Fibonacci", "Congruencial Mixto", "Congruencial Multiplicativo"
        ], state="readonly", width=30)
        self.combo_metodo.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        self.combo_metodo.current(0)
        self.combo_metodo.bind("<<ComboboxSelected>>", self.actualizar_campos)

        self.frame_params = ttk.LabelFrame(self.tab_manual, text="Parámetros de Entrada")
        self.frame_params.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        self.entradas = {}
        self.actualizar_campos()

        btn_frame = ttk.Frame(self.tab_manual)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="1. Generar Serie", command=self.ejecutar_manual).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="2. Ver Gráficos", command=self.mostrar_graficos).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="3. Exportar los 1000 datos a CSV", command=self.exportar_csv).pack(side=tk.LEFT, padx=5)

        self.texto_resultados = tk.Text(self.tab_manual, height=18, width=90)
        self.texto_resultados.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

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
            ent = ttk.Entry(self.frame_params)
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
            self.texto_resultados.insert(tk.END, f"Se generaron {n} valores exitosamente.\n")
            self.texto_resultados.insert(tk.END, f"Según la consigna, se muestran los primeros 20:\n\n")
            self.texto_resultados.insert(tk.END, self.df_actual.head(20).to_string(index=False))
            messagebox.showinfo("Éxito", "Serie generada. Puede ver los gráficos, exportar o realizar pruebas.")
        except Exception as e:
            messagebox.showerror("Error", f"Verifique los datos ingresados: {e}")

    def exportar_csv(self):
        if self.df_actual.empty:
            messagebox.showwarning("Aviso", "No hay serie generada para exportar.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filepath:
            self.df_actual.to_csv(filepath, index=False)
            messagebox.showinfo("Éxito", f"Datos exportados a {filepath}")

    def mostrar_graficos(self):
        if not self.serie_actual: return
        plt.figure(figsize=(10, 4))
        plt.subplot(1, 2, 1)
        plt.hist(self.serie_actual, bins=10, edgecolor='black', alpha=0.7)
        plt.axhline(y=len(self.serie_actual)/10, color='r', linestyle='dashed', label='F. Esperada')
        plt.title("Histograma (Uniformidad)")
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.scatter(self.serie_actual[:-1], self.serie_actual[1:], alpha=0.5, s=10)
        plt.title("Dispersión (Independencia)")
        plt.tight_layout()
        plt.show()

    # --- PESTAÑA PRUEBAS ---
    def construir_tab_pruebas(self):
        ttk.Button(self.tab_pruebas, text="Ejecutar Test Chi-Cuadrado y T-Student", command=self.ejecutar_pruebas).pack(pady=10)
        self.texto_pruebas = tk.Text(self.tab_pruebas, height=30, width=90)
        self.texto_pruebas.pack(padx=10, pady=10)

    def ejecutar_pruebas(self):
        if not self.serie_actual:
            messagebox.showwarning("Aviso", "Primero genere una serie en Carga Manual.")
            return
        
        self.texto_pruebas.delete(1.0, tk.END)
        self.texto_pruebas.insert(tk.END, f"=== ANÁLISIS DE SERIE ({self.metodo_actual}) ===\n\n")
        
        es_uni, chi_c, chi_t, df_chi = test_chi_cuadrado(self.serie_actual)
        self.texto_pruebas.insert(tk.END, "--- TEST CHI-CUADRADO (Uniformidad) ---\n")
        self.texto_pruebas.insert(tk.END, df_chi.to_string(index=False) + "\n")
        self.texto_pruebas.insert(tk.END, f"Chi Calc: {chi_c:.4f} | Chi Tabla: {chi_t:.4f} -> {'ACEPTA H0' if es_uni else 'RECHAZA H0'}\n\n")

        self.texto_pruebas.insert(tk.END, "--- TEST T-STUDENT (Independencia) ---\n")
        for h in [1, 2, 3]:
            es_indep, rho, t_c, t_t = test_correlacion_serial(self.serie_actual, h)
            res = "Acepta H0" if es_indep else "Rechaza H0"
            self.texto_pruebas.insert(tk.END, f"Rezago h={h} -> Rho: {rho:.4f} | t-calc: {t_c:.4f} | t-tabla: {t_t:.4f} | {res}\n")

    # --- PESTAÑA OBLIGATORIOS ---
    def construir_tab_obligatorios(self):
        lbl = ttk.Label(self.tab_obligatorios, text="Ejecución de Casos de la Guía Práctica", font=("Arial", 12, "bold"))
        lbl.grid(row=0, column=0, columnspan=2, pady=10)

        # Botones distribuidos en grilla
        ttk.Button(self.tab_obligatorios, text="Ej 1: Cuadrados Medios", command=self.ej_1).grid(row=1, column=0, pady=5, padx=10, sticky='ew')
        ttk.Button(self.tab_obligatorios, text="Ej 2: Fibonacci", command=self.ej_2).grid(row=1, column=1, pady=5, padx=10, sticky='ew')
        
        ttk.Button(self.tab_obligatorios, text="Ej 3a: Cálculo Períodos (Mixto)", command=self.ej_3a).grid(row=2, column=0, pady=5, padx=10, sticky='ew')
        ttk.Button(self.tab_obligatorios, text="Ej 3b: Serie de 1000 (Mixto)", command=self.ej_3b).grid(row=2, column=1, pady=5, padx=10, sticky='ew')
        
        ttk.Button(self.tab_obligatorios, text="Ej 4: Multiplicativo", command=self.ej_4).grid(row=3, column=0, pady=5, padx=10, sticky='ew')
        ttk.Button(self.tab_obligatorios, text="Ej 5: Escalar Intervalos", command=self.ej_5).grid(row=3, column=1, pady=5, padx=10, sticky='ew')
        
        ttk.Button(self.tab_obligatorios, text="Ej 6 y 7: Pruebas sobre Ej 3b", command=self.ej_6_7).grid(row=4, column=0, columnspan=2, pady=5, padx=10, sticky='ew')

    def mostrar_resultado(self, titulo, texto):
        top = tk.Toplevel(self.root)
        top.title(titulo)
        txt = tk.Text(top, height=25, width=90)
        txt.pack(padx=10, pady=10)
        txt.insert(tk.END, texto)

    def ej_1(self):
        res = "Resultados Ejercicio 1 (Cuadrados Medios):\n"
        for s in [4567, 1000, 7654]:
            df, _ = generador_cuadrado_medio(s, 50)
            res += f"\n--- Semilla {s} (Primeros 10 y Últimos 3 de 50)---\n"
            res += df.head(10).to_string(index=False) + "\n...\n" + df.tail(3).to_string(index=False) + "\n"
        self.mostrar_resultado("Ejercicio 1", res)

    def ej_2(self):
        res = "Resultados Ejercicio 2 (Fibonacci - 1000 iteraciones):\n\n"
        configs = [(1, 1, 100), (3, 5, 1024)]
        for x0, x1, m in configs:
            df, _ = generador_fibonacci(x0, x1, m, 1000)
            res += f"--- Configuración X0={x0}, X1={x1}, m={m} (Primeros 20) ---\n"
            res += df.head(20).to_string(index=False) + "\n\n"
        self.mostrar_resultado("Ejercicio 2", res)

    def ej_3a(self):
        casos = [(15, 8, 16, 100), (13, 50, 17, 100), (7, 5, 24, 100), (3, 5, 21, 100), (8, 9, 13, 100)]
        res = "Resultados Ej 3a (Períodos C. Mixto):\n\nX0\t a\t c\t m\t Período Detectado\n" + "-"*50 + "\n"
        for x0, a, c, m in casos:
            _, _, p = generador_congruencial_mixto(x0, a, c, m, m + 5)
            res += f"{x0}\t {a}\t {c}\t {m}\t {p if p else 'No repite'}\n"
        self.mostrar_resultado("Ejercicio 3a", res)

    def ej_3b(self):
        # Caso c) del 3a: X0=7, a=5, c=24, m=100
        df, serie, p = generador_congruencial_mixto(7, 5, 24, 100, 1000)
        res = f"Resultados Ej 3b (C. Mixto Caso c - 1000 iteraciones):\nPeríodo detectado: {p}\n\n"
        res += "--- Primeros 20 términos ---\n" + df.head(20).to_string(index=False)
        self.mostrar_resultado("Ejercicio 3b", res)

    def ej_4(self):
        casos = [(17, 203, 10**5), (19, 211, 10**8), (3, 221, 10**3), (7, 5, 64), (9, 11, 128)]
        res = "Resultados Ej 4 (Multiplicativo):\n\nX0\t a\t m\t Período\n" + "-"*40 + "\n"
        for x0, a, m in casos:
            # Buscamos periodo limitando a 100k para no congelar la UI en 10^8
            _, _, p = generador_congruencial_multiplicativo(x0, a, m, min(m+5, 100000))
            res += f"{x0}\t {a}\t {m}\t {p if p else '> 100000 (Calculo truncado)'}\n"
        self.mostrar_resultado("Ejercicio 4", res)

    def ej_5(self):
        # Generamos una serie aleatoria cualquiera para usar de base
        _, serie_base, _ = generador_congruencial_mixto(15, 8, 16, 100, 1000)
        intervalos = [(5, 20), (100, 500), (0.5, 3.0)]
        res = "Resultados Ej 5 (Escalado de valores):\n\n"
        for a, b in intervalos:
            serie_esc = escalar_valores(serie_base, a, b)
            res += f"--- Intervalo [{a}, {b}] ---\nPrimeros 5 valores: {[round(v, 2) for v in serie_esc[:5]]}\n"
            res += f"Mínimo observado: {round(min(serie_esc), 2)} | Máximo: {round(max(serie_esc), 2)}\n\n"
        self.mostrar_resultado("Ejercicio 5", res)

    def ej_6_7(self):
        # Usamos la serie del Ej 3b para probar
        _, serie, _ = generador_congruencial_mixto(7, 5, 24, 100, 1000)
        
        es_uni, chi_c, chi_t, df_chi = test_chi_cuadrado(serie)
        res = "--- EJ 6: TEST CHI-CUADRADO (Sobre serie de Ej 3b) ---\n"
        res += df_chi.to_string(index=False) + f"\n\nChi Calc: {chi_c:.4f} | Chi Tabla: {chi_t:.4f} -> {'ACEPTA H0' if es_uni else 'RECHAZA'}\n\n"
        
        res += "--- EJ 7: TEST T-STUDENT (Correlación Serial) ---\n"
        for h in [1, 2, 3]:
            es_indep, rho, t_c, t_t = test_correlacion_serial(serie, h)
            res += f"h={h} | Rho: {rho:.4f} | t-calc: {t_c:.4f} | t-tabla: {t_t:.4f} -> {'Acepta H0' if es_indep else 'Rechaza'}\n"
            
        self.mostrar_resultado("Ejercicios 6 y 7", res)

if __name__ == "__main__":
    root = tk.Tk()
    app = GeneradoresApp(root)
    root.mainloop()