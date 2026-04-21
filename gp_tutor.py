import random

class GPTutor:
    def __init__(self, nodos_data, vectores_data):
        self.nodos = nodos_data
        self.vectores = vectores_data
        
        # 1. Definir los "Genes" (Las posibles operaciones matemáticas)
        self.genes_posibles = ["SUM_FX", "SUM_FY"]
        for nodo in self.nodos:
            nodo_id = nodo.get("id", "Origen")
            self.genes_posibles.append(f"SUM_MOMENTO_{nodo_id}")

    def _crear_individuo(self):
        # Un individuo es una secuencia aleatoria de 3 pasos
        return [random.choice(self.genes_posibles) for _ in range(3)]

    def evaluar_fitness(self, individuo):
        puntaje = 1000 
        pasos_usados = set()

        for paso in individuo:
            if paso in pasos_usados:
                puntaje -= 100 # Penaliza pasos repetidos
            pasos_usados.add(paso)
            
            # Heurística: Hacer sumatoria de momentos en un nodo suele ser muy útil
            if paso.startswith("SUM_MOMENTO_"):
                puntaje += 200 
            elif paso in ["SUM_FX", "SUM_FY"]:
                puntaje += 50
                
        return puntaje

    def cruzar_y_mutar(self, padre1, padre2):
        # Cruce simple
        hijo = [padre1[0], padre2[1], random.choice([padre1[2], padre2[2]])]
        # Mutación (20% de probabilidad)
        if random.random() < 0.2:
            hijo[random.randint(0, 2)] = random.choice(self.genes_posibles)
        return hijo

    def entrenar_y_obtener_mejor_ruta(self, generaciones=50, tamaño_poblacion=50):
        # 1. Generar población inicial
        poblacion = [self._crear_individuo() for _ in range(tamaño_poblacion)]

        for _ in range(generaciones):
            # 2. Evaluar
            poblacion.sort(key=lambda ind: self.evaluar_fitness(ind), reverse=True)
            
            # 3. Seleccionar a los mejores (Top 10)
            mejores = poblacion[:10]
            
            # 4. Reproducir
            nueva_poblacion = list(mejores)
            while len(nueva_poblacion) < tamaño_poblacion:
                p1, p2 = random.sample(mejores, 2)
                nueva_poblacion.append(self.cruzar_y_mutar(p1, p2))
                
            poblacion = nueva_poblacion

        # Retornar el mejor individuo traducido a texto
        mejor_individuo = poblacion[0]
        return self._traducir_adn_a_instrucciones(mejor_individuo)

    def _traducir_adn_a_instrucciones(self, adn_campeon):
        instrucciones = []
        for i, gen in enumerate(adn_campeon):
            if gen == "SUM_FX":
                instrucciones.append(f"Paso {i+1}: Realizar sumatoria de fuerzas en el eje X (ΣFx = 0).")
            elif gen == "SUM_FY":
                instrucciones.append(f"Paso {i+1}: Plantear equilibrio de fuerzas en el eje Y (ΣFy = 0).")
            elif gen.startswith("SUM_MOMENTO_"):
                nodo = gen.replace("SUM_MOMENTO_", "")
                instrucciones.append(f"Paso {i+1}: Aplicar Sumatoria de Momentos en el {nodo} (ΣM = 0) para anular fuerzas concurrentes.")
        
        instrucciones.append("Paso Final: Resolver el sistema de ecuaciones resultante para encontrar las reacciones.")
        return instrucciones