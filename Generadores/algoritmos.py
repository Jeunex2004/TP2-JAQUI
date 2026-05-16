import pandas as pd

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
        
        if buscar_periodo and periodo is None:
            if x_actual in valores_vistos:
                periodo = i - valores_vistos[x_actual]
            else:
                if len(valores_vistos) < 100000:
                    valores_vistos[x_actual] = i
                else:
                    buscar_periodo = False 
                
        x_actual = x_siguiente
        
    return pd.DataFrame(resultados), [r['U_i'] for r in resultados], periodo

def generador_congruencial_multiplicativo(x0, a, m, n_iteraciones):
    return generador_congruencial_mixto(x0, a, 0, m, n_iteraciones)

# Función para escalar los valores de la serie U a un rango [a, b]

def escalar_valores(serie_u, a, b):
    return [a + (b - a) * u for u in serie_u]