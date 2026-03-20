import requests
import json
import os
import math

URL = "https://api-motor-matematico.onrender.com/calcular"
CARPETA = "casos_prueba"

# ==========================================
# EL ORÁCULO COMPLETO (20 Casos de Prueba)
# ==========================================
ORACULO = {
    "caso_01.json": {"Fx": 0.0, "Fy": -500.0, "M": 0.0, "Eq": False, "Reacciones": {"Reaccion_Ay": 500.0}},
    "caso_02.json": {"Fx": 0.0, "Fy": 0.0, "M": 0.0, "Eq": True, "Reacciones": {}},
    "caso_03.json": {"Fx": 200.0, "Fy": 0.0, "M": 0.0, "Eq": False, "Reacciones": {"Reaccion_Ax": -200.0}},
    "caso_04.json": {"Fx": -100.0, "Fy": 0.0, "M": 0.0, "Eq": False, "Reacciones": {"Reaccion_Ax": 100.0}},
    "caso_05.json": {"Fx": 70.71, "Fy": 70.71, "M": 0.0, "Eq": False, "Reacciones": {"Reaccion_Ax": -70.71, "Reaccion_Ay": -70.71}},
    "caso_06.json": {"Fx": -70.71, "Fy": 70.71, "M": 0.0, "Eq": False, "Reacciones": {"Reaccion_Ax": 70.71, "Reaccion_Ay": -70.71}},
    "caso_07.json": {"Fx": 0.0, "Fy": 0.0, "M": 0.0, "Eq": True, "Reacciones": {}},
    "caso_08.json": {"Fx": 0.0, "Fy": -50.0, "M": 0.0, "Eq": False, "Reacciones": {"Reaccion_Ay": 50.0}},
    "caso_09.json": {"Fx": 0.0, "Fy": 100.0, "M": 500.0, "Eq": False, "Reacciones": {"Reaccion_Ay": -100.0, "Momento_Reaccion": -500.0}},
    "caso_10.json": {"Fx": 100.0, "Fy": 0.0, "M": -500.0, "Eq": False, "Reacciones": {"Reaccion_Ax": -100.0, "Momento_Reaccion": 500.0}},
    "caso_11.json": {"Fx": 100.0, "Fy": 0.0, "M": 0.0, "Eq": False, "Reacciones": {"Reaccion_Ax": -100.0}},
    "caso_12.json": {"Fx": 0.0, "Fy": -600.0, "M": 0.0, "Eq": False, "Reacciones": {"Reaccion_Ay": 600.0}},
    "caso_13.json": {"Fx": 0.0, "Fy": -1100.0, "M": 1000.0, "Eq": False, "Reacciones": {"Reaccion_Ay": 1100.0, "Momento_Reaccion": -1000.0}},
    "caso_14.json": {"Fx": 35.35, "Fy": 35.35, "M": 176.78, "Eq": False, "Reacciones": {"Reaccion_Ax": -35.35, "Reaccion_Ay": -35.35, "Momento_Reaccion": -176.78}},
    "caso_15.json": {"Fx": 0.0, "Fy": 0.0, "M": 0.0, "Eq": True, "Reacciones": {}},
    "caso_16.json": {"Fx": 100.0, "Fy": 0.0, "M": 1020.0, "Eq": False, "Reacciones": {"Reaccion_Ax": -100.0, "Momento_Reaccion": -1020.0}},
    "caso_17.json": {"Fx": 0.0, "Fy": 100.0, "M": 0.0, "Eq": False, "Reacciones": {"Reaccion_Ay": -100.0}},
    "caso_18.json": {"Fx": 0.0, "Fy": 0.0, "M": 0.0, "Eq": True, "Reacciones": {}},
    "caso_19.json": {"Fx": 0.0, "Fy": -9999999.9, "M": 0.0, "Eq": False, "Reacciones": {"Reaccion_Ay": 9999999.9}},
    "caso_20.json": {"Fx": 0.0, "Fy": 0.0, "M": 0.0, "Eq": True, "Reacciones": {}}
}

# --- Funciones de Evaluación Inteligentes ---
def calificar(esperado, real, es_booleano=False):
    if es_booleano:
        return True if esperado == real else False
    if real is None:
        return False
    return math.isclose(esperado, float(real), abs_tol=0.1)

def comparar_reacciones(dicc_esperado, dicc_real):
    if dicc_esperado.keys() != dicc_real.keys():
        return False
    for clave in dicc_esperado:
        if not math.isclose(dicc_esperado[clave], float(dicc_real[clave]), abs_tol=0.1):
            return False
    return True

# --- Motor de Ejecución de Pruebas ---
def ejecutar_prueba(archivo_seleccionado, modo_silencioso=False):
    ruta_completa = os.path.join(CARPETA, archivo_seleccionado)
    with open(ruta_completa, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    # === BLOQUE DE MANEJO DE ERRORES Y TIMEOUT ===
    try:
        respuesta = requests.post(URL, json=payload, timeout=50.0)
    except requests.exceptions.Timeout:
        if not modo_silencioso: 
            print(f"❌ ERROR DE TIEMPO: La API tardó más de 5 segundos en responder ({archivo_seleccionado}).")
        return False
    except requests.exceptions.ConnectionError:
        if not modo_silencioso: 
            print(f"❌ ERROR DE CONEXIÓN: No se pudo conectar a FastAPI. ¿Está encendido el servidor? ({archivo_seleccionado}).")
        return False
    except Exception as e:
        if not modo_silencioso: 
            print(f"❌ ERROR CRÍTICO en {archivo_seleccionado}: {e}")
        return False
    # ===================================================

    if respuesta.status_code != 200:
        if not modo_silencioso: print(f"❌ Error HTTP {respuesta.status_code} en {archivo_seleccionado}")
        return False

    datos = respuesta.json().get('bloque_resultados', {})
    fx_real = datos.get('sumatoria_fuerzas_x', {}).get('valor', 0)
    fy_real = datos.get('sumatoria_fuerzas_y', {}).get('valor', 0)
    m_real = datos.get('sumatoria_momentos', {}).get('valor', 0)
    eq_real = datos.get('sistema_en_equilibrio')
    reacciones_reales = datos.get('incognitas_resueltas', {})

    if not modo_silencioso:
        print(f"\n📊 RESULTADOS PARA {archivo_seleccionado}:")
        print(f"   Fx : {fx_real} N | Fy : {fy_real} N | M : {m_real} N·m | Eq : {eq_real}")
        print(f"   Reacciones: {reacciones_reales}")

    if archivo_seleccionado in ORACULO:
        esp = ORACULO[archivo_seleccionado]
        pasa_fx = calificar(esp['Fx'], fx_real)
        pasa_fy = calificar(esp['Fy'], fy_real)
        pasa_m = calificar(esp['M'], m_real)
        pasa_eq = calificar(esp['Eq'], eq_real, es_booleano=True)
        pasa_reac = comparar_reacciones(esp["Reacciones"], reacciones_reales)
        
        todo_pasa = pasa_fx and pasa_fy and pasa_m and pasa_eq and pasa_reac

        if not modo_silencioso:
            print("\n ⚖️  EVALUACIÓN AUTOMÁTICA (QA)")
            print(f"   Fx: {'🟢 PASS' if pasa_fx else f'🔴 FAIL (Esp: {esp['Fx']})'}")
            print(f"   Fy: {'🟢 PASS' if pasa_fy else f'🔴 FAIL (Esp: {esp['Fy']})'}")
            print(f"   M : {'🟢 PASS' if pasa_m else f'🔴 FAIL (Esp: {esp['M']})'}")
            print(f"   Eq: {'🟢 PASS' if pasa_eq else f'🔴 FAIL (Esp: {esp['Eq']})'}")
            print(f"   Reacciones: {'🟢 PASS' if pasa_reac else f'🔴 FAIL (Esp: {esp['Reacciones']})'}\n")
        
        return todo_pasa
    return False

# ==========================================
# LÓGICA DEL MENÚ
# ==========================================
if not os.path.exists(CARPETA):
    print(f"❌ No se encontró la carpeta '{CARPETA}'.")
    exit()

archivos = sorted([f for f in os.listdir(CARPETA) if f.endswith('.json')])

print("\n" + "="*45)
print(" 🧪 BATERÍA DE PRUEBAS AUTOMATIZADA")
print("="*45)
print("  [0] 🚀 EJECUTAR TODOS LOS CASOS (RUN ALL)")
print("-" * 45)
for i, archivo in enumerate(archivos):
    marca = "⭐" if archivo in ORACULO else "  "
    print(f"  [{i + 1}] {marca} {archivo}")
print("="*45)

opcion = input("\n👉 Ingresa el número (0 para TODOS, 'q' para salir): ")
if opcion.lower() == 'q': exit()

if opcion == '0':
    print("\n🚀 Ejecutando batería completa...\n")
    pasados = 0
    fallados = []
    
    for archivo in archivos:
        if archivo in ORACULO:
            resultado = ejecutar_prueba(archivo, modo_silencioso=True)
            if resultado:
                print(f"✅ {archivo} -> PASS")
                pasados += 1
            else:
                print(f"❌ {archivo} -> FAIL")
                fallados.append(archivo)
                
    print("\n" + "="*45)
    print(f" 🏆 REPORTE FINAL: {pasados}/{len(ORACULO)} PASARON")
    print("="*45)
    if fallados:
        print("⚠️ Casos que fallaron y debes revisar:")
        for f in fallados:
            print(f"   - {f}")
else:
    try:
        indice = int(opcion) - 1
        archivo_seleccionado = archivos[indice]
        ejecutar_prueba(archivo_seleccionado, modo_silencioso=False)
    except Exception as e:
        print(f"❌ Error: {e}")