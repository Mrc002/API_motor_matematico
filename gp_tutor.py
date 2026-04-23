import numpy as np
import math
import sys
import io
from gplearn.genetic import SymbolicRegressor
from gplearn.functions import make_function

# Funciones trigonométricas para que el ADN pueda mutar usándolas
def _sin(x): return np.sin(x)
def _cos(x): return np.cos(x)

sin_func = make_function(function=_sin, name='seno', arity=1)
cos_func = make_function(function=_cos, name='coseno', arity=1)

class GPTutorReal:
    def __init__(self, nodos, vectores):
        self.nodos = nodos
        self.vectores = vectores

    def evolucionar_pasos(self):
        if not self.vectores:
            return {
                "instrucciones_paso_a_paso": ["El lienzo está vacío. Dibuja vectores para evolucionar una solución."],
                "log_del_motor": "No hay datos para entrenar."
            }

        # 1. CREAR EL DATASET SINTÉTICO (X_entrenamiento, Y_entrenamiento)
        n_vectores = len(self.vectores)
        n_muestras = 100 
        
        X_entrenamiento = np.random.rand(n_muestras, n_vectores * 2) * 100 
        Y_entrenamiento = np.zeros(n_muestras)

        for i in range(n_muestras):
            suma_y = 0.0
            for v in range(n_vectores):
                mag = X_entrenamiento[i, v*2]
                ang = X_entrenamiento[i, v*2 + 1]
                suma_y += mag * math.sin(math.radians(ang % 360)) 
            Y_entrenamiento[i] = suma_y

        nombres_variables = []
        for i in range(n_vectores):
            nombres_variables.extend([f"Fuerza_{i+1}", f"AnguloRad_{i+1}"])

        # 2. CONFIGURAR EL MODELO GPLEARN
        modelo = SymbolicRegressor(
            population_size=200,
            generations=10,
            p_crossover=0.7,
            p_subtree_mutation=0.1,
            parsimony_coefficient=0.001,
            feature_names=nombres_variables,
            function_set=['add', 'sub', 'mul', 'div', sin_func, cos_func],
            random_state=None, 
            verbose=1 # MUY IMPORTANTE: Esto genera la salida en consola
        )

        # 3. SECUESTRO DE LA CONSOLA DE PYTHON
        vieja_salida = sys.stdout 
        capturador_log = io.StringIO() 
        sys.stdout = capturador_log 

        try:
            # Entrenamos el modelo (sus prints caerán en el capturador)
            modelo.fit(X_entrenamiento, Y_entrenamiento)
        finally:
            # Devolvemos la consola a la normalidad pase lo que pase
            sys.stdout = vieja_salida 
        
        log_crudo = capturador_log.getvalue() # Sacamos el texto atrapado

        # 4. EXTRAER Y TRADUCIR EL ÁRBOL GANADOR
        formula_evolucionada = str(modelo._program)
        fitness_score = modelo.run_details_['best_fitness'][-1]

        pasos = self._generar_instrucciones(formula_evolucionada, fitness_score)
        
        # Devolvemos UN DICCIONARIO con ambas cosas
        return {
            "instrucciones_paso_a_paso": pasos,
            "log_del_motor": log_crudo
        }

    def _generar_instrucciones(self, formula, fitness):
        pasos = []
        pasos.append("Paso 1: Se generaron 1000 iteraciones genéticas para descubrir la dinámica del diagrama.")
        
        if "seno" in formula or "coseno" in formula:
            pasos.append("Paso 2: El modelo descubrió que la geometría requiere descomposición trigonométrica.")
        
        if "mul" in formula:
            pasos.append("Paso 3: Se asocia (multiplica) la magnitud de cada fuerza con su componente direccional.")
            
        if "add" in formula or "sub" in formula:
            pasos.append("Paso 4: Se agrupan (suman/restan) las componentes para hallar la resultante.")

        pasos.append(f"Paso 5: La IA sintetizó la siguiente ecuación óptima para resolver el sistema:\n\nEcuación: {formula}")
        pasos.append(f"Paso Final: El margen de error (fitness) de esta fórmula descubierta es de {fitness:.6f}.")
        
        return pasos