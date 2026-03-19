import json
import os

def crear_payload(contexto, nodos, fuerzas):
    return {
        "bloque_contexto": {"contexto_ingresado_por_usuario": contexto},
        "unidades": {"unidad_medida_distancia": "m", "unidad_medida_fuerza": "N"},
        "bloque_fisico": {"nodos": nodos, "vectores_fuerza": fuerzas},
        "parametros_asumidos": {}
    }

def guardar_caso(num, payload):
    ruta = f"casos_prueba/caso_{str(num).zfill(2)}.json"
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)

os.makedirs('casos_prueba', exist_ok=True)

# ==========================================
# 🟢 CATEGORÍA 1: FUERZAS BÁSICAS (NODO ÚNICO)
# ==========================================
# Caso 1: La caja original (500N hacia abajo)
guardar_caso(1, crear_payload("Caja de 500N colgando", 
    [{"id": "A", "x": 0.0, "y": 0.0}], 
    [{"id": "F1", "etiqueta": "Peso", "nodo_origen_id": "A", "magnitud": 500.0, "angulo_grados": 270.0, "es_saliente": True}]))

# Caso 2: Equilibrio perfecto en Y (500N arriba, 500N abajo)
guardar_caso(2, crear_payload("Caja sostenida en equilibrio", 
    [{"id": "A", "x": 0.0, "y": 0.0}], 
    [{"id": "F1", "etiqueta": "Peso", "nodo_origen_id": "A", "magnitud": 500.0, "angulo_grados": 270.0, "es_saliente": True},
     {"id": "F2", "etiqueta": "Grua", "nodo_origen_id": "A", "magnitud": 500.0, "angulo_grados": 90.0, "es_saliente": True}]))

# Caso 3: Desequilibrio en X (Tirando a la derecha)
guardar_caso(3, crear_payload("Tirando de una caja a la derecha", 
    [{"id": "A", "x": 0.0, "y": 0.0}], 
    [{"id": "F1", "etiqueta": "Tiro", "nodo_origen_id": "A", "magnitud": 200.0, "angulo_grados": 0.0, "es_saliente": True}]))

# Caso 4: Fuerza Entrante vs Saliente (es_saliente = False)
guardar_caso(4, crear_payload("Fuerza empujando el nodo (entrante)", 
    [{"id": "A", "x": 0.0, "y": 0.0}], 
    [{"id": "F1", "etiqueta": "Empuje", "nodo_origen_id": "A", "magnitud": 100.0, "angulo_grados": 0.0, "es_saliente": False}]))

# ==========================================
# 🟡 CATEGORÍA 2: ÁNGULOS Y TRIGONOMETRÍA
# ==========================================
# Caso 5: Ángulo de 45 grados (Componentes X y Y iguales)
guardar_caso(5, crear_payload("Fuerza a 45 grados", 
    [{"id": "A", "x": 0.0, "y": 0.0}], 
    [{"id": "F1", "etiqueta": "Diagonal", "nodo_origen_id": "A", "magnitud": 100.0, "angulo_grados": 45.0, "es_saliente": True}]))

# Caso 6: Ángulo en el segundo cuadrante (135 grados)
guardar_caso(6, crear_payload("Fuerza hacia arriba y a la izquierda", 
    [{"id": "A", "x": 0.0, "y": 0.0}], 
    [{"id": "F1", "etiqueta": "Diagonal 2", "nodo_origen_id": "A", "magnitud": 100.0, "angulo_grados": 135.0, "es_saliente": True}]))

# Caso 7: Suma de tres fuerzas concurrentes
guardar_caso(7, crear_payload("Tres fuerzas en el origen", 
    [{"id": "A", "x": 0.0, "y": 0.0}], 
    [{"id": "F1", "etiqueta": "Der", "nodo_origen_id": "A", "magnitud": 100.0, "angulo_grados": 0.0, "es_saliente": True},
     {"id": "F2", "etiqueta": "Arr", "nodo_origen_id": "A", "magnitud": 100.0, "angulo_grados": 90.0, "es_saliente": True},
     {"id": "F3", "etiqueta": "Diag", "nodo_origen_id": "A", "magnitud": 141.42, "angulo_grados": 225.0, "es_saliente": True}])) # Debería dar casi equilibrio

# Caso 8: Ángulo negativo (Ej. -90 grados en vez de 270)
guardar_caso(8, crear_payload("Prueba de ángulo negativo", 
    [{"id": "A", "x": 0.0, "y": 0.0}], 
    [{"id": "F1", "etiqueta": "Abajo", "nodo_origen_id": "A", "magnitud": 50.0, "angulo_grados": -90.0, "es_saliente": True}]))

# ==========================================
# 🟠 CATEGORÍA 3: MOMENTOS Y TORQUES (MÚLTIPLES NODOS)
# ==========================================
# Caso 9: Brazo de palanca en X (Llave inglesa horizontal)
guardar_caso(9, crear_payload("Llave inglesa horizontal", 
    [{"id": "Origen", "x": 0.0, "y": 0.0}, {"id": "Mango", "x": 5.0, "y": 0.0}], 
    [{"id": "F1", "etiqueta": "Empuje", "nodo_origen_id": "Mango", "magnitud": 100.0, "angulo_grados": 90.0, "es_saliente": True}]))

# Caso 10: Brazo de palanca en Y (Llave inglesa vertical)
guardar_caso(10, crear_payload("Llave inglesa vertical", 
    [{"id": "Origen", "x": 0.0, "y": 0.0}, {"id": "Mango", "x": 0.0, "y": 5.0}], 
    [{"id": "F1", "etiqueta": "Empuje", "nodo_origen_id": "Mango", "magnitud": 100.0, "angulo_grados": 0.0, "es_saliente": True}]))

# Caso 11: Fuerza alineada al brazo (No genera momento)
guardar_caso(11, crear_payload("Tirando desde el eje (sin torque)", 
    [{"id": "Origen", "x": 0.0, "y": 0.0}, {"id": "Mango", "x": 5.0, "y": 0.0}], 
    [{"id": "F1", "etiqueta": "Tiro paralelo", "nodo_origen_id": "Mango", "magnitud": 100.0, "angulo_grados": 0.0, "es_saliente": True}]))

# Caso 12: Subibaja en equilibrio (Dos fuerzas, momentos cancelados)
guardar_caso(12, crear_payload("Subibaja equilibrado", 
    [{"id": "Nino1", "x": -2.0, "y": 0.0}, {"id": "Centro", "x": 0.0, "y": 0.0}, {"id": "Nino2", "x": 2.0, "y": 0.0}], 
    [{"id": "F1", "etiqueta": "Peso1", "nodo_origen_id": "Nino1", "magnitud": 300.0, "angulo_grados": 270.0, "es_saliente": True},
     {"id": "F2", "etiqueta": "Peso2", "nodo_origen_id": "Nino2", "magnitud": 300.0, "angulo_grados": 270.0, "es_saliente": True}]))

# Caso 13: Subibaja desequilibrado
guardar_caso(13, crear_payload("Subibaja con un adulto y un niño", 
    [{"id": "Adulto", "x": -2.0, "y": 0.0}, {"id": "Nino", "x": 2.0, "y": 0.0}], 
    [{"id": "F1", "etiqueta": "PesoAdulto", "nodo_origen_id": "Adulto", "magnitud": 800.0, "angulo_grados": 270.0, "es_saliente": True},
     {"id": "F2", "etiqueta": "PesoNino", "nodo_origen_id": "Nino", "magnitud": 300.0, "angulo_grados": 270.0, "es_saliente": True}]))

# Caso 14: Fuerza diagonal causando traslación Y rotación
guardar_caso(14, crear_payload("Fuerza diagonal en un extremo", 
    [{"id": "Origen", "x": 0.0, "y": 0.0}, {"id": "Extremo", "x": 10.0, "y": 5.0}], 
    [{"id": "F1", "etiqueta": "Empuje Diag", "nodo_origen_id": "Extremo", "magnitud": 50.0, "angulo_grados": 45.0, "es_saliente": True}]))

# ==========================================
# 🔴 CATEGORÍA 4: CASOS LÍMITE (QA TESTING)
# ==========================================
# Caso 15: Fuerza de magnitud cero
guardar_caso(15, crear_payload("Magnitud cero (No debe hacer nada)", 
    [{"id": "A", "x": 0.0, "y": 0.0}], 
    [{"id": "F1", "etiqueta": "Fantasma", "nodo_origen_id": "A", "magnitud": 0.0, "angulo_grados": 45.0, "es_saliente": True}]))

# Caso 16: Coordenadas negativas para nodos
guardar_caso(16, crear_payload("Nodos en cuadrantes negativos", 
    [{"id": "A", "x": -5.5, "y": -10.2}], 
    [{"id": "F1", "etiqueta": "Fuerza", "nodo_origen_id": "A", "magnitud": 100.0, "angulo_grados": 0.0, "es_saliente": True}]))

# Caso 17: Ángulo exagerado (>360 grados)
guardar_caso(17, crear_payload("Angulo de 450 grados (equivale a 90)", 
    [{"id": "A", "x": 0.0, "y": 0.0}], 
    [{"id": "F1", "etiqueta": "Rotacion Loca", "nodo_origen_id": "A", "magnitud": 100.0, "angulo_grados": 450.0, "es_saliente": True}]))

# Caso 18: Fuerzas microscópicas (Prueba de tolerancias y decimales)
guardar_caso(18, crear_payload("Fuerzas super pequeñas", 
    [{"id": "A", "x": 0.0, "y": 0.0}], 
    [{"id": "F1", "etiqueta": "Micro", "nodo_origen_id": "A", "magnitud": 0.000005, "angulo_grados": 90.0, "es_saliente": True}]))

# Caso 19: Fuerzas masivas (Prueba de desbordamiento)
guardar_caso(19, crear_payload("Fuerzas gigantescas", 
    [{"id": "A", "x": 0.0, "y": 0.0}], 
    [{"id": "F1", "etiqueta": "Macro", "nodo_origen_id": "A", "magnitud": 9999999.9, "angulo_grados": 270.0, "es_saliente": True}]))

# Caso 20: 10 Fuerzas en el mismo nodo
guardar_caso(20, crear_payload("Estrella de 10 fuerzas", 
    [{"id": "A", "x": 0.0, "y": 0.0}], 
    [{"id": f"F{i}", "etiqueta": "Radio", "nodo_origen_id": "A", "magnitud": 10.0, "angulo_grados": i * 36.0, "es_saliente": True} for i in range(10)]))

print("✅ ¡Los 20 archivos JSON han sido generados y llenados con éxito en la carpeta 'casos_prueba'!")