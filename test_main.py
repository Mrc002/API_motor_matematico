import pytest
from fastapi.testclient import TestClient
from main import app, ValorFisico  # Importamos tu app y tu clase desde main.py

# ==========================================
# CONFIGURACIÓN DEL CLIENTE DE PRUEBAS
# ==========================================
# TestClient simula ser la app de Flutter enviando peticiones
client = TestClient(app)

# ==========================================
# 1. PRUEBAS UNITARIAS (Lógica Matemática)
# ==========================================

def test_valor_fisico_operaciones_limpias():
    """Prueba que dos variables limpias generen un resultado limpio"""
    fuerza = ValorFisico(20.0)
    distancia = ValorFisico(5.0)
    
    momento = fuerza * distancia
    
    assert momento.valor == 100.0
    assert momento.es_calculable == True
    assert len(momento.variables_manchadas) == 0

def test_valor_fisico_propagacion_mancha():
    """Prueba la propagación de incertidumbre (Variables Manchadas)"""
    # Fuerza limpia
    fuerza = ValorFisico(20.0)
    # Distancia manchada porque fue asumida
    distancia_asumida = ValorFisico(10.0, variables_manchadas={"longitud_viga"})
    
    momento = fuerza * distancia_asumida
    
    # El valor matemático debe calcularse igual (20 * 10)
    assert momento.valor == 200.0
    # Pero DEBE estar manchado
    assert momento.es_calculable == False
    assert "longitud_viga" in momento.variables_manchadas

# ==========================================
# 2. PRUEBAS DE INTEGRACIÓN (Endpoint API)
# ==========================================

def test_endpoint_calcular_con_parametros_asumidos():
    """Prueba que la API procese el JSON, detecte la mancha y devuelva el formato correcto"""
    
    # 1. Preparamos el JSON simulando a Flutter
    payload_flutter = {
        "fuerzas": [
            {
                "magnitud": 20,
                "angulo_grados": 335,
                "es_saliente": True
            }
        ],
        "parametros_asumidos": {
            "longitud_viga": 10.0
        },
        "distancia_aplicacion_fuerza": 9.0
    }

    # 2. Disparamos la petición POST al endpoint
    response = client.post("/calcular", json=payload_flutter)

    # 3. Verificamos que el servidor respondió con código 200 (OK)
    assert response.status_code == 200
    
    # 4. Analizamos la respuesta JSON
    data = response.json()
    resultados = data["resultados_motor"]
    
    # A) La sumatoria en Y debe ser calculable (limpia)
    assert resultados["sumatoria_fuerzas_y"]["es_calculable"] == True
    # Verificamos la precisión del cálculo trigonométrico (20 * sin(335°))
    assert resultados["sumatoria_fuerzas_y"]["valor"] == -8.452
    
    # B) El momento DEBE ser no calculable (manchado por longitud_viga)
    assert resultados["momento"]["es_calculable"] == False
    assert resultados["momento"]["valor_simulado"] == -84.524
    assert "longitud_viga" in resultados["momento"]["motivo"]