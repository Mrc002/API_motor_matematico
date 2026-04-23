from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Set
import math
from gp_tutor import GPTutorReal

import joblib

app = FastAPI(title="Motor Matemático - Math IA")
# Permitir CORS para todas las fuentes (útil para pruebas, pero ajustar en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite que cualquier cliente (como Chrome) se conecte
    allow_credentials=True,
    allow_methods=["*"], # Permite peticiones POST, GET, etc.
    allow_headers=["*"], # Permite cualquier encabezado en el JSON
)

# ==========================================
# 1. NÚCLEO MATEMÁTICO (Variables Manchadas)
# ==========================================
class ValorFisico:
    def __init__(self, valor: float, variables_manchadas: Set[str] = None):
        self.valor = valor
        self.variables_manchadas = variables_manchadas if variables_manchadas else set()

    @property
    def es_calculable(self) -> bool:
        return len(self.variables_manchadas) == 0

    def __add__(self, otro):
        if isinstance(otro, (int, float)):
            return ValorFisico(self.valor + otro, self.variables_manchadas)
        elif isinstance(otro, ValorFisico):
            nuevas_manchas = self.variables_manchadas.union(otro.variables_manchadas)
            return ValorFisico(self.valor + otro.valor, nuevas_manchas)

    def __sub__(self, otro):
        if isinstance(otro, (int, float)):
            return ValorFisico(self.valor - otro, self.variables_manchadas)
        elif isinstance(otro, ValorFisico):
            nuevas_manchas = self.variables_manchadas.union(otro.variables_manchadas)
            return ValorFisico(self.valor - otro.valor, nuevas_manchas)

    def __mul__(self, otro):
        if isinstance(otro, (int, float)):
            return ValorFisico(self.valor * otro, self.variables_manchadas)
        elif isinstance(otro, ValorFisico):
            nuevas_manchas = self.variables_manchadas.union(otro.variables_manchadas)
            return ValorFisico(self.valor * otro.valor, nuevas_manchas)

    def to_dict(self):
        # Limpieza de decimales para evitar -0.0 o valores basura
        tolerancia = 1e-5
        valor_final = 0.0 if math.isclose(self.valor, 0.0, abs_tol=tolerancia) else round(self.valor, 3)
        
        if self.es_calculable:
            return {"valor": valor_final, "es_calculable": True}
        else:
            return {
                "valor_simulado": valor_final,
                "es_calculable": False,
                "motivo": f"Depende de parámetros asumidos: {', '.join(self.variables_manchadas)}"
            }

# ==========================================
# 2. MODELOS DE DATOS (Entrada)
# ==========================================
class ContextoInput(BaseModel):
    contexto_ingresado_por_usuario: str

class UnidadesInput(BaseModel):
    unidad_medida_distancia: str
    unidad_medida_fuerza: str

class NodoInput(BaseModel):
    id: str
    x: float
    y: float

class FuerzaInput(BaseModel):
    id: str
    etiqueta: str
    nodo_origen_id: str
    magnitud: float
    angulo_grados: float
    es_saliente: bool

class BloqueFisicoInput(BaseModel):
    nodos: List[NodoInput]
    vectores_fuerza: List[FuerzaInput]

class PeticionCalculo(BaseModel):
    bloque_contexto: ContextoInput
    unidades: UnidadesInput
    bloque_fisico: BloqueFisicoInput
    parametros_asumidos: Dict[str, float] = {}

# ==========================================
# 3. ENDPOINT PRINCIPAL
# ==========================================
@app.post("/calcular")
def calcular_diagrama(peticion: PeticionCalculo):
    print(f"\n--- Recibiendo petición para: {peticion.bloque_contexto.contexto_ingresado_por_usuario} ---")
    
    sum_fx = ValorFisico(0.0)
    sum_fy = ValorFisico(0.0)
    sum_momentos = ValorFisico(0.0)

    nodos_dict = {nodo.id: nodo for nodo in peticion.bloque_fisico.nodos}

    for fuerza in peticion.bloque_fisico.vectores_fuerza:
        nodo = nodos_dict[fuerza.nodo_origen_id]
        angulo_rad = math.radians(fuerza.angulo_grados)
        
        # Cálculo de componentes
        fx_val = fuerza.magnitud * math.cos(angulo_rad)
        fy_val = fuerza.magnitud * math.sin(angulo_rad)
        
        if not fuerza.es_saliente:
            fx_val, fy_val = -fx_val, -fy_val
            
        fx = ValorFisico(fx_val)
        fy = ValorFisico(fy_val)
        
        # Acumular fuerzas
        sum_fx = sum_fx + fx
        sum_fy = sum_fy + fy

        # Manejo de manchas para el momento (Brazo de palanca)
        manchas_brazo = set(peticion.parametros_asumidos.keys())
        # Si el nodo no está en el origen y hay parámetros asumidos, el brazo se "mancha"
        r_x = ValorFisico(nodo.x, variables_manchadas=manchas_brazo if nodo.x != 0 else None)
        r_y = ValorFisico(nodo.y, variables_manchadas=manchas_brazo if nodo.y != 0 else None)
        
        # Momento = r x F
        # Corrección de fórmula de momento en 2D (r_x * F_y - r_y * F_x)
        # Nota: Convertimos a variables para usar la sobrecarga de operadores de ValorFisico
        # Si r_x y r_y no estuvieran manchados, esto funciona perfecto.
        # Aquí asumiremos que la sobrecarga de operadores que hiciste soporta multiplicaciones directas.
        
        momento_f_val = (r_x.valor * fy.valor) - (r_y.valor * fx.valor)
        
        # Unimos las manchas de todas las variables involucradas
        manchas_momento = r_x.variables_manchadas.union(fy.variables_manchadas).union(r_y.variables_manchadas).union(fx.variables_manchadas)
        momento_f = ValorFisico(momento_f_val, variables_manchadas=manchas_momento)
        
        sum_momentos = sum_momentos + momento_f

    # Verificación de equilibrio
    en_equilibrio = False
    tolerancia_equilibrio = 0.01
    
    if sum_fx.es_calculable and sum_fy.es_calculable and sum_momentos.es_calculable:
        if abs(sum_fx.valor) < tolerancia_equilibrio and abs(sum_fy.valor) < tolerancia_equilibrio and abs(sum_momentos.valor) < tolerancia_equilibrio:
            en_equilibrio = True

    # ==========================================
    # NUEVA LÓGICA: ESTÁTICA INVERSA (Reacciones)
    # ==========================================
    incognitas_calculadas = {}
    
    # Si no está en equilibrio, calculamos qué fuerzas faltan para que lo esté
    if not en_equilibrio:
        if sum_fx.es_calculable and abs(sum_fx.valor) >= tolerancia_equilibrio:
            # La reacción es el negativo exacto de la suma de fuerzas
            incognitas_calculadas["Reaccion_Ax"] = round(-sum_fx.valor, 3)
            
        if sum_fy.es_calculable and abs(sum_fy.valor) >= tolerancia_equilibrio:
            incognitas_calculadas["Reaccion_Ay"] = round(-sum_fy.valor, 3)
            
        if sum_momentos.es_calculable and abs(sum_momentos.valor) >= tolerancia_equilibrio:
            incognitas_calculadas["Momento_Reaccion"] = round(-sum_momentos.valor, 3)

    # Estructura de respuesta
    resultado = {
        "bloque_resultados": {
            "sumatoria_fuerzas_x": sum_fx.to_dict(),
            "sumatoria_fuerzas_y": sum_fy.to_dict(),
            "sumatoria_momentos": sum_momentos.to_dict(),
            "incognitas_resueltas": incognitas_calculadas, # <--- ¡Aquí inyectamos las reacciones!
            "sistema_en_equilibrio": en_equilibrio
        }
    }

    print("--- Resultados calculados con éxito ---")
    return resultado

# ... (Tu código actual y tu endpoint /calcular se quedan intactos) ...

# ... (Aquí va tu endpoint /calcular normal) ...

@app.post("/calculargp")
async def calcular_gp(data: dict):
    try:
        bloque = data.get("bloque_fisico", {})
        nodos = bloque.get("nodos", [])
        vectores = bloque.get("vectores_fuerza", [])
        
        if not nodos: 
            raise HTTPException(status_code=400, detail="No hay nodos")
        
        motor_ia = GPTutorReal(nodos, vectores)
        resultado = motor_ia.evolucionar_pasos()
        
        # Devolvemos el diccionario completo (pasos + log)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))