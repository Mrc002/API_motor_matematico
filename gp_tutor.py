import random

class GPTutor:
    def __init__(self, nodos_data, vectores_data):
        self.nodos = nodos_data
        self.vectores = vectores_data

        # Genes posibles: las tres ecuaciones de equilibrio estático
        self.genes_posibles = ["SUM_FX", "SUM_FY"]
        for nodo in self.nodos:
            nodo_id = nodo.get("id", "Origen")
            self.genes_posibles.append(f"SUM_MOMENTO_{nodo_id}")

    def _crear_individuo(self):
        # Un individuo válido SIEMPRE incluye SUM_FX y SUM_FY
        # El tercer gen es un momento en algún nodo (si existe) o el mejor disponible
        genes_momento = [g for g in self.genes_posibles if g.startswith("SUM_MOMENTO_")]
        tercer_gen = random.choice(genes_momento) if genes_momento else "SUM_FX"
        individuo = ["SUM_FX", "SUM_FY", tercer_gen]
        random.shuffle(individuo)
        return individuo

    def evaluar_fitness(self, individuo):
        puntaje = 1000
        tipos_usados = set()      # Para penalizar tipos repetidos (ej. 2 momentos)
        genes_usados = set()      # Para penalizar el mismo gen exacto repetido

        tiene_fx = "SUM_FX" in individuo
        tiene_fy = "SUM_FY" in individuo

        # FIX: penalización fuerte si no tiene las sumatorias básicas
        if not tiene_fx:
            puntaje -= 400
        if not tiene_fy:
            puntaje -= 400

        for paso in individuo:
            # FIX: penalizar gen repetido exacto
            if paso in genes_usados:
                puntaje -= 200
            genes_usados.add(paso)

            # FIX: penalizar el mismo TIPO de ecuación repetida
            tipo = "MOMENTO" if paso.startswith("SUM_MOMENTO_") else paso
            if tipo in tipos_usados:
                puntaje -= 150   # dos momentos en distinto nodo: penaliza pero no elimina
            tipos_usados.add(tipo)

            # Premiar momento en nodo con más fuerzas concurrentes
            if paso.startswith("SUM_MOMENTO_"):
                nodo_id = paso.replace("SUM_MOMENTO_", "")
                fuerzas_en_nodo = sum(
                    1 for v in self.vectores
                    if v.get("nodo_origen_id") == nodo_id
                )
                puntaje += 100 + (fuerzas_en_nodo * 50)
            elif paso in ["SUM_FX", "SUM_FY"]:
                puntaje += 80

        return puntaje

    def cruzar_y_mutar(self, padre1, padre2):
        # Cruce en punto 1
        hijo = [padre1[0], padre2[1], random.choice([padre1[2], padre2[2]])]

        # Mutación (15% de probabilidad)
        if random.random() < 0.15:
            idx = random.randint(0, 2)
            hijo[idx] = random.choice(self.genes_posibles)

        # FIX: reparación post-mutación — garantizar que SUM_FX y SUM_FY estén presentes
        for requerido in ["SUM_FX", "SUM_FY"]:
            if requerido not in hijo:
                # Reemplazar un gen de momento (si existe) o el gen menos valioso
                idx_reemplazar = next(
                    (i for i, g in enumerate(hijo) if g.startswith("SUM_MOMENTO_")),
                    random.randint(0, 2)
                )
                hijo[idx_reemplazar] = requerido

        return hijo

    def entrenar_y_obtener_mejor_ruta(self, generaciones=50, tamaño_poblacion=50):
        poblacion = [self._crear_individuo() for _ in range(tamaño_poblacion)]

        for _ in range(generaciones):
            poblacion.sort(key=lambda ind: self.evaluar_fitness(ind), reverse=True)
            mejores = poblacion[:10]

            nueva_poblacion = list(mejores)
            while len(nueva_poblacion) < tamaño_poblacion:
                p1, p2 = random.sample(mejores, 2)
                nueva_poblacion.append(self.cruzar_y_mutar(p1, p2))

            poblacion = nueva_poblacion

        mejor_individuo = poblacion[0]
        return self._traducir_adn_a_instrucciones(mejor_individuo)

    def _traducir_adn_a_instrucciones(self, adn_campeon):
        instrucciones = []
        for i, gen in enumerate(adn_campeon):
            if gen == "SUM_FX":
                instrucciones.append(
                    f"Paso {i+1}: Plantear la sumatoria de fuerzas en X (ΣFx = 0) "
                    f"descomponiendo cada vector en su componente horizontal."
                )
            elif gen == "SUM_FY":
                instrucciones.append(
                    f"Paso {i+1}: Plantear la sumatoria de fuerzas en Y (ΣFy = 0) "
                    f"descomponiendo cada vector en su componente vertical."
                )
            elif gen.startswith("SUM_MOMENTO_"):
                nodo = gen.replace("SUM_MOMENTO_", "")
                instrucciones.append(
                    f"Paso {i+1}: Aplicar sumatoria de momentos respecto al {nodo} "
                    f"(ΣM_{nodo} = 0) para eliminar las reacciones concurrentes en ese punto "
                    f"y reducir el número de incógnitas."
                )

        instrucciones.append(
            "Paso final: Con las ecuaciones anteriores, resolver el sistema algebraico "
            "para obtener las reacciones desconocidas en los apoyos."
        )
        return instrucciones