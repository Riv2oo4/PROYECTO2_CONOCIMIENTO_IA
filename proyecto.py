from logic_project import *
import itertools
import random
import time
import matplotlib.pyplot as plt
import numpy as np

COLORES = ["azul", "rojo", "blanco", "negro", "verde", "purpura"]
LONGITUD_CODIGO = 4

class LogicaMastermind:
    def __init__(self):
        self.conocimiento = None
        self.combinaciones_restantes = None
        self.intentos = 0
        self.historial = []  
        self.tamanios_espacio_busqueda = []  
        self.inicializar_conocimiento()
        
    def inicializar_conocimiento(self):
        self.simbolos = {}
        for pos in range(LONGITUD_CODIGO):
            for color in COLORES:
                self.simbolos[(pos, color)] = Symbol(f"pos{pos}_{color}")
        
        conjunciones = []
        
        for pos in range(LONGITUD_CODIGO):
            colores_posicion = [self.simbolos[(pos, color)] for color in COLORES]
            conjunciones.append(Or(*colores_posicion))
            
            for i, color1 in enumerate(COLORES):
                for color2 in COLORES[i+1:]:
                    conjunciones.append(
                        Implication(
                            self.simbolos[(pos, color1)], 
                            Not(self.simbolos[(pos, color2)])
                        )
                    )
        
        self.conocimiento = And(*conjunciones)
        
        self.combinaciones_restantes = list(itertools.product(COLORES, repeat=LONGITUD_CODIGO))
        self.tamanios_espacio_busqueda = [len(self.combinaciones_restantes)]  
        print(f"Tamaño inicial del espacio de búsqueda: {len(self.combinaciones_restantes)}")
        
    def calcular_retroalimentacion(self, intento, codigo_secreto):
        coincidencias_exactas = sum(1 for g, s in zip(intento, codigo_secreto) if g == s)
        
        conteo_colores_intento = {color: intento.count(color) for color in COLORES}
        conteo_colores_secreto = {color: codigo_secreto.count(color) for color in COLORES}
        
        coincidencias_totales_color = sum(min(conteo_colores_intento.get(color, 0), 
                                     conteo_colores_secreto.get(color, 0)) 
                                 for color in COLORES)
        
        coincidencias_solo_color = coincidencias_totales_color - coincidencias_exactas
        
        return coincidencias_exactas, coincidencias_solo_color
    
    def actualizar_conocimiento(self, intento, coincidencias_exactas, coincidencias_solo_color):
        self.intentos += 1
        self.historial.append((intento, coincidencias_exactas, coincidencias_solo_color))
        
        nuevas_combinaciones = []
        for combinacion in self.combinaciones_restantes:
            exactas_calculadas, color_calculadas = self.calcular_retroalimentacion(intento, combinacion)
            if exactas_calculadas == coincidencias_exactas and color_calculadas == coincidencias_solo_color:
                nuevas_combinaciones.append(combinacion)
        
        self.combinaciones_restantes = nuevas_combinaciones
        self.tamanios_espacio_busqueda.append(len(self.combinaciones_restantes))  # Seguimiento del tamaño del espacio de búsqueda
        print(f"Espacio de búsqueda reducido a {len(self.combinaciones_restantes)} combinaciones")
        
        if len(self.combinaciones_restantes) < 1000:  
            restriccion_retroalimentacion = self.crear_restriccion_retroalimentacion(intento, coincidencias_exactas, coincidencias_solo_color)
            if restriccion_retroalimentacion:
                self.conocimiento.add(restriccion_retroalimentacion)
    
    def crear_restriccion_retroalimentacion(self, intento, coincidencias_exactas, coincidencias_solo_color):
        if coincidencias_exactas == 0:
            restricciones_no_exactas = []
            for pos, color in enumerate(intento):
                restricciones_no_exactas.append(Not(self.simbolos[(pos, color)]))
            return And(*restricciones_no_exactas)
        
        if coincidencias_exactas == LONGITUD_CODIGO:
            restricciones_solucion = []
            for pos, color in enumerate(intento):
                restricciones_solucion.append(self.simbolos[(pos, color)])
            return And(*restricciones_solucion)
        
        return None
    
    def elegir_siguiente_intento(self):
        if not self.combinaciones_restantes:
            raise Exception("No quedan combinaciones válidas. Puede haber un error en la retroalimentación.")
        
        if self.intentos == 0:
            return ('azul', 'rojo', 'verde', 'blanco')
        
        if len(self.combinaciones_restantes) <= 10:
            return random.choice(self.combinaciones_restantes)
        
        return random.choice(self.combinaciones_restantes)
    
    def graficar_reduccion_espacio_busqueda(self):
        try:
            plt.figure(figsize=(10, 6))
            
            if not self.tamanios_espacio_busqueda:
                print("Error: No hay datos de espacio de búsqueda para graficar.")
                return
                
            valores_x = list(range(len(self.tamanios_espacio_busqueda)))
            
            plt.plot(valores_x, self.tamanios_espacio_busqueda, marker='o', linestyle='-', color='blue')
            plt.title('Reducción del Espacio de Búsqueda')
            plt.xlabel('Número de Intentos')
            plt.ylabel('Tamaño del Espacio de Búsqueda')
            plt.grid(True)
            plt.xticks(valores_x)
            
            for i, tamanio in enumerate(self.tamanios_espacio_busqueda):
                plt.annotate(f"{tamanio}", (i, tamanio), textcoords="offset points", xytext=(0,10), ha='center')
            
            plt.ylim(bottom=0)
            
            plt.savefig('reduccion_espacio_busqueda.png')
            print("Gráfica guardada como 'reduccion_espacio_busqueda.png'")
            
            plt.show()
        except Exception as e:
            print(f"Error al generar la gráfica: {e}")
            print("Intente instalar matplotlib con 'pip install matplotlib' si no lo tiene instalado.")
    
    def resolver_automatico(self, codigo_secreto, silencioso=False):
        if not silencioso:
            print(f"Código secreto: {codigo_secreto}")
        
        while True:
            intento = self.elegir_siguiente_intento()
            if not silencioso:
                print(f"Intento #{self.intentos + 1}: {intento}")
            
            coincidencias_exactas, coincidencias_solo_color = self.calcular_retroalimentacion(intento, codigo_secreto)
            if not silencioso:
                print(f"Retroalimentación: {coincidencias_exactas} coincidencias exactas, {coincidencias_solo_color} colores correctos en posición incorrecta")
            
            self.actualizar_conocimiento(intento, coincidencias_exactas, coincidencias_solo_color)
            
            if coincidencias_exactas == LONGITUD_CODIGO:
                if not silencioso:
                    print(f"¡Solución encontrada en {self.intentos} intentos!")
                return self.intentos, self.historial
            
            if not self.combinaciones_restantes:
                if not silencioso:
                    print("Error: No quedan combinaciones válidas.")
                return None
    
    def modo_interactivo(self):
        print("=== Solucionador de Mastermind - Modo Interactivo ===")
        print("Colores disponibles: azul, rojo, blanco, negro, verde, purpura")
        print("Piensa en un código secreto de 4 colores (pueden repetirse) y responderé a las preguntas.")
        
        while True:
            try:
                intento = self.elegir_siguiente_intento()
                print(f"\nIntento #{self.intentos + 1}: {intento}")
                
                while True:
                    try:
                        entrada_exactas = input("Ingrese número de coincidencias exactas (color correcto, posición correcta): ")
                        if not entrada_exactas.strip():
                            print("Error: No se ingresó ningún valor. Por favor, intente de nuevo.")
                            continue
                        
                        entrada_exactas = int(entrada_exactas)
                        
                        entrada_color = input("Ingrese número de colores correctos en posición incorrecta: ")
                        if not entrada_color.strip():
                            print("Error: No se ingresó ningún valor. Por favor, intente de nuevo.")
                            continue
                            
                        entrada_color = int(entrada_color)
                        
                        if entrada_exactas < 0 or entrada_color < 0:
                            print("Error: Los valores no pueden ser negativos. Por favor, intente de nuevo.")
                            continue
                            
                        if entrada_exactas + entrada_color > LONGITUD_CODIGO:
                            print(f"Error: La suma de coincidencias no puede ser mayor que {LONGITUD_CODIGO}. Por favor, intente de nuevo.")
                            continue
                            
                        break
                    except ValueError:
                        print("Error: Por favor, ingrese solo números enteros.")
                
                self.actualizar_conocimiento(intento, entrada_exactas, entrada_color)
                
                if entrada_exactas == LONGITUD_CODIGO:
                    print(f"\n¡Solución encontrada en {self.intentos} intentos!")
                    print("\nGenerando gráfica de reducción del espacio de búsqueda...")
                    self.graficar_reduccion_espacio_busqueda()
                    return self.intentos
                
                if not self.combinaciones_restantes:
                    print("\nError: No quedan combinaciones válidas. Puede haber un error en la retroalimentación proporcionada.")
                    
                    while True:
                        try:
                            reiniciar = input("¿Desea reiniciar el juego? (s/n): ").lower()
                            if reiniciar == 's':
                                self.__init__()
                                return self.modo_interactivo()
                            elif reiniciar == 'n':
                                return None
                            else:
                                print("Por favor, responda 's' o 'n'.")
                        except Exception:
                            print("Error en la entrada. Por favor, responda 's' o 'n'.")
            
            except KeyboardInterrupt:
                print("\n\nJuego interrumpido por el usuario.")
                return None
            except Exception as e:
                print(f"\nError inesperado: {e}")
                print("Reiniciando el juego...")
                self.__init__()
                return self.modo_interactivo()

def ejecutar_200_juegos():
    print("=== Análisis de 200 juegos automáticos ===")
    print("Generando y resolviendo 200 códigos aleatorios...")
    
    total_juegos = 200
    conteo_intentos = []
    max_intentos = 0
    todos_tamanios_espacio_busqueda = []
    
    paso_progreso = total_juegos // 20
    
    tiempo_inicio = time.time()
    
    for i in range(total_juegos):
        if i % paso_progreso == 0 or i == total_juegos - 1:
            porcentaje = (i + 1) / total_juegos * 100
            print(f"Progreso: {porcentaje:.1f}% - Juego {i+1}/{total_juegos}")
        
        codigo_secreto = tuple(random.choices(COLORES, k=LONGITUD_CODIGO))
        
        solucionador = LogicaMastermind()
        intentos, _ = solucionador.resolver_automatico(codigo_secreto, silencioso=True)
        
        conteo_intentos.append(intentos)
        if intentos > max_intentos:
            max_intentos = intentos
        
        for j, tamanio in enumerate(solucionador.tamanios_espacio_busqueda):
            while len(todos_tamanios_espacio_busqueda) <= j:
                todos_tamanios_espacio_busqueda.append([])
            todos_tamanios_espacio_busqueda[j].append(tamanio)
    
    tiempo_fin = time.time()
    
    promedio_intentos = sum(conteo_intentos) / len(conteo_intentos)
    min_intentos = min(conteo_intentos)
    
    promedio_tamanios_espacio_busqueda = [sum(tamanios) / len(tamanios) for tamanios in todos_tamanios_espacio_busqueda]
    
    print("\n=== Resultados del Análisis ===")
    print(f"Tiempo total: {tiempo_fin - tiempo_inicio:.2f} segundos")
    print(f"Promedio de intentos necesarios: {promedio_intentos:.2f}")
    print(f"Mínimo de intentos: {min_intentos}")
    print(f"Máximo de intentos: {max_intentos}")
    
    plt.figure(figsize=(10, 6))
    plt.hist(conteo_intentos, bins=range(min_intentos, max_intentos + 2), alpha=0.7, color='blue', edgecolor='black')
    plt.title('Distribución de Intentos para Resolver el Juego')
    plt.xlabel('Número de Intentos')
    plt.ylabel('Frecuencia')
    plt.grid(True, alpha=0.3)
    plt.savefig('distribucion_intentos.png')
    print("Gráfica de distribución de intentos guardada como 'distribucion_intentos.png'")
    plt.close()
    
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(promedio_tamanios_espacio_busqueda)), promedio_tamanios_espacio_busqueda, marker='o', linestyle='-', color='green')
    plt.title('Espacio de Búsqueda Promedio por Intento')
    plt.xlabel('Número de Intento')
    plt.ylabel('Tamaño Promedio del Espacio de Búsqueda')
    plt.grid(True)
    plt.xticks(range(len(promedio_tamanios_espacio_busqueda)))
    
    for i, tamanio in enumerate(promedio_tamanios_espacio_busqueda):
        plt.annotate(f"{tamanio:.1f}", (i, tamanio), textcoords="offset points", xytext=(0,10), ha='center')
    
    plt.savefig('promedio_espacio_busqueda.png')
    print("Gráfica de espacio de búsqueda promedio guardada como 'promedio_espacio_busqueda.png'")
    plt.close()
    
    return promedio_intentos, promedio_tamanios_espacio_busqueda

def principal():
    try:
        print("=== Solucionador de Mastermind ===")
        print("1. Modo Automático")
        print("2. Modo Interactivo")
        print("3. Análisis de 200 juegos")
        
        opcion = ""
        while opcion not in ["1", "2", "3"]:
            opcion = input("Seleccione modo (1/2/3): ")
            if opcion not in ["1", "2", "3"]:
                print("Opción inválida. Por favor, seleccione 1, 2 o 3.")
        
        if opcion == "1":
            solucionador = LogicaMastermind()
            while True:
                try:
                    entrada_secreto = input(f"Ingrese el código secreto (colores separados por coma de {COLORES}): ")
                    secreto = tuple(color.strip() for color in entrada_secreto.split(","))
                    
                    if len(secreto) != LONGITUD_CODIGO:
                        print(f"Error: El código debe tener exactamente {LONGITUD_CODIGO} colores.")
                        continue
                    
                    colores_invalidos = [c for c in secreto if c not in COLORES]
                    if colores_invalidos:
                        print(f"Error: Colores inválidos: {', '.join(colores_invalidos)}.")
                        print(f"Colores permitidos: {', '.join(COLORES)}")
                        continue
                    
                    break
                except Exception as e:
                    print(f"Error en la entrada: {e}. Por favor, intente de nuevo.")
            
            try:
                tiempo_inicio = time.time()
                intentos, historial = solucionador.resolver_automatico(secreto)
                tiempo_fin = time.time()
                
                print(f"\nSolución encontrada en {intentos} intentos")
                print(f"Tiempo transcurrido: {tiempo_fin - tiempo_inicio:.2f} segundos")
                
                print("\nReducción del espacio de búsqueda:")
                espacio_inicial = len(list(itertools.product(COLORES, repeat=LONGITUD_CODIGO)))
                print(f"Espacio inicial: {espacio_inicial} combinaciones")
                
                for i, (intento, exactas, solo_color) in enumerate(historial):
                    if i+1 < len(solucionador.tamanios_espacio_busqueda):
                        restantes = solucionador.tamanios_espacio_busqueda[i+1]
                        print(f"Después del intento {i+1}: {restantes} combinaciones")
                
                print("\nGenerando gráfica de reducción del espacio de búsqueda...")
                solucionador.graficar_reduccion_espacio_busqueda()
            
            except Exception as e:
                print(f"Error durante la ejecución del modo automático: {e}")
            
        elif opcion == "2":
            solucionador = LogicaMastermind()
            try:
                solucionador.modo_interactivo()
            except Exception as e:
                print(f"Error durante la ejecución del modo interactivo: {e}")
        
        elif opcion == "3":
            ejecutar_200_juegos()
        
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido por el usuario.")
    except Exception as e:
        print(f"Error inesperado: {e}")


if __name__ == "__main__":
    principal()