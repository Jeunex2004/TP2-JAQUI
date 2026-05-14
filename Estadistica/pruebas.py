import numpy as np
import scipy.stats as stats
import pandas as pd

def test_chi_cuadrado(serie_u, k=10, alpha=0.05):
    n = len(serie_u)
    if n == 0: return False, 0, 0, pd.DataFrame()
    frec_esperadas = n / k
    frec_observadas, bordes = np.histogram(serie_u, bins=k, range=(0, 1))
    
    chi_calc = np.sum(((frec_observadas - frec_esperadas) ** 2) / frec_esperadas)
    chi_tabla = stats.chi2.ppf(1 - alpha, k - 1)
    es_uniforme = chi_calc < chi_tabla
    
    datos = []
    for i in range(k):
        fo = frec_observadas[i]
        fe = frec_esperadas
        dif = fo - fe
        datos.append([f"[{bordes[i]:.2f}-{bordes[i+1]:.2f})", fo, round(fe, 2),
                       round(dif, 2), round(dif**2, 2), round(dif**2 / fe, 4)])
    df_chi = pd.DataFrame(datos, columns=["Intervalo", "fi", "npi", "fi-npi", "(fi-npi)²", "(fi-npi)²/npi"])
    
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