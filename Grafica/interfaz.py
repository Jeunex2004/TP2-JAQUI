import tkinter as tk
from tkinter import ttk
import pandas as pd

# Importar nuestras piezas modulares (Mixins) desde los nuevos archivos
from Grafica.graficos import GraficosMixin
from Grafica.tab_manual import TabManualMixin
from Grafica.tab_pruebas import TabPruebasMixin
from Grafica.tab_obligatorios import TabObligatoriosMixin

# La clase principal "hereda" todas las funciones de los módulos automáticamente
class GeneradoresApp(GraficosMixin, TabManualMixin, TabPruebasMixin, TabObligatoriosMixin):
    def __init__(self, root):
        self.root = root
        self.root.title("TP2 - Generadores Pseudoaleatorios")
        self.root.geometry("1280x750")
        
        # Variables de estado compartidas en todo el programa
        self.serie_actual = []
        self.df_actual = pd.DataFrame()
        self.metodo_actual = ""
        self.canvas_actual = None 

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Creación de las pestañas visuales
        self.tab_manual = ttk.Frame(self.notebook)
        self.tab_pruebas = ttk.Frame(self.notebook)
        self.tab_obligatorios = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_manual, text='Carga Manual')
        self.notebook.add(self.tab_pruebas, text='Pruebas Estadísticas')
        self.notebook.add(self.tab_obligatorios, text='Ejercicios Obligatorios')

        # Estas funciones vienen de los archivos tab_manual.py, tab_pruebas.py y tab_obligatorios.py
        self.construir_tab_manual()
        self.construir_tab_pruebas()
        self.construir_tab_obligatorios()