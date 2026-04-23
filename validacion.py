# validacion.py
from gplearn.genetic import SymbolicRegressor
import numpy as np

# Evaluar en datos de prueba
y_pred = modelo_ax.predict(X_test)
error = np.mean(np.abs(y_pred - y_test))
print(f"Error promedio: {error:.4f} N")

# Imprimir el árbol como fórmula legible
print("\nÁrbol completo:")
print(modelo_ax._program)

# Comparar con la fórmula teórica
print("\nFórmula teórica: Reaccion_Ax = -fx_total")
print(f"R² del modelo: {modelo_ax.score(X_test, y_test):.6f}")
# Si R² ≈ 1.0, el GP redescubrió la física exacta