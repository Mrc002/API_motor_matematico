# data_generator.py
import math
import random
import pandas as pd

def generar_caso():
    """Genera un sistema aleatorio y lo resuelve con el motor exacto."""
    n_vectores = random.randint(2, 5)
    vectores = []
    
    for i in range(n_vectores):
        magnitud = random.uniform(100, 1000)
        angulo = random.uniform(0, 360)
        x_nodo = random.uniform(-5, 5)
        y_nodo = random.uniform(-5, 5)
        vectores.append({
            "magnitud": magnitud,
            "angulo_grados": angulo,
            "x_nodo": x_nodo,
            "y_nodo": y_nodo,
        })
    
    # Resolver con el motor exacto (la verdad)
    sum_fx = sum(v["magnitud"] * math.cos(math.radians(v["angulo_grados"]))
                 for v in vectores)
    sum_fy = sum(v["magnitud"] * math.sin(math.radians(v["angulo_grados"]))
                 for v in vectores)
    sum_m  = sum(
        v["x_nodo"] * v["magnitud"] * math.sin(math.radians(v["angulo_grados"])) -
        v["y_nodo"] * v["magnitud"] * math.cos(math.radians(v["angulo_grados"]))
        for v in vectores
    )
    
    return {
        # Features que el GP va a ver
        "fx_total": sum_fx,
        "fy_total": sum_fy,
        "momento_total": sum_m,
        "n_vectores": n_vectores,
        "magnitud_max": max(v["magnitud"] for v in vectores),
        # Targets — lo que el GP debe aprender a predecir
        "reaccion_ax": -sum_fx,
        "reaccion_ay": -sum_fy,
        "reaccion_m":  -sum_m,
    }

# Generar 5000 casos
casos = [generar_caso() for _ in range(5000)]
df = pd.DataFrame(casos)
df.to_csv("datos_entrenamiento.csv", index=False)