import tkinter as tk
from tkinter import ttk, messagebox
from Estadistica.pruebas import test_chi_cuadrado, test_correlacion_serial

class TabPruebasMixin:
    def construir_tab_pruebas(self):
        ttk.Button(self.tab_pruebas, text="Ejecutar Test Chi-Cuadrado y T-Student", command=self.ejecutar_pruebas).pack(pady=10)
        self.texto_pruebas = tk.Text(self.tab_pruebas, height=30, width=100, font=("Consolas", 10))
        self.texto_pruebas.pack(padx=10, pady=10)

    def ejecutar_pruebas(self):
        if not self.serie_actual:
            return messagebox.showwarning("Aviso", "Primero genere una serie en Carga Manual.")
        
        self.texto_pruebas.delete(1.0, tk.END)
        self.texto_pruebas.insert(tk.END, f"=== ANÁLISIS DE SERIE ({self.metodo_actual}) ===\n\n")
        
        es_uni, chi_c, chi_t, df_chi = test_chi_cuadrado(self.serie_actual)
        self.texto_pruebas.insert(tk.END, "--- TEST CHI-CUADRADO (Uniformidad) ---\n")
        self.texto_pruebas.insert(tk.END, df_chi.to_string(index=False) + "\n")
        self.texto_pruebas.insert(tk.END, f"\nChi Calc: {chi_c:.4f} | Chi Tabla: {chi_t:.4f} -> {'ACEPTA' if es_uni else 'RECHAZA'} H0\n\n")

        self.texto_pruebas.insert(tk.END, "--- TEST T-STUDENT (Independencia) ---\n")
        self.texto_pruebas.insert(tk.END, f"  {'h':>3}  {'rho_h':>8}  {'t-calc':>8}  {'t-tabla':>8}  Decision\n")
        self.texto_pruebas.insert(tk.END, "  " + "-" * 50 + "\n")
        for h in [1, 2, 3]:
            es_indep, rho, t_c, t_t = test_correlacion_serial(self.serie_actual, h)
            decision = "Acepta H0" if es_indep else "Rechaza H0"
            self.texto_pruebas.insert(tk.END, f"  {h:>3}  {rho:>8.4f}  {t_c:>8.4f}  {t_t:>8.4f}  {decision}\n")