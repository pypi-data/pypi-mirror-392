'''
Se importan:
    random para los dados.
    time para contar los segundos que tarda el jugador en finalizar la partida.
    Módulo preguntas (como p) donde se encuentran las preguntas y sus funciones.
'''

import random
import time
from . import preguntas as p

'''
Se establecen las siguientes variables globales:
    nom_jugador : para establecer el nombre de jugador en cada partida y poderse
    usar en lar tarjetas finales.
    preg : el número de preguntas respondidas, ya hayan sido acertadas como
    falladas.
'''

nom_jugador = ''
preg = 0
tiempo = 0

'''
|----------------|
|JUEGO TRIVIALPY |
|----------------|

Preguntas almacenadas en diccionarios de las categorías, junto con sus respuestas.
Sólo 1 jugador (de momento).
El jugador deberá de acertar 6 preguntas de diferentes temáticas.
Se usa un dado, del 1 al 6, para saber la categoría, de entre las siguientes:.


    Categorías
    -----------
    1. Geografía.
    2. Entretenimiento.
    3. Historia.
    4. Arte y Literatura.
    5. Ciencia y Naturaleza.
    6. Deportes.

El jugador deberá de responder correctamente para que cuente, eligiendo entre A, B, C, D.
Otra entrada no será válida.

'''

def reglas():

    print(f"-------------------------")
    print(f"          REGLAS          ")
    print(f"-------------------------\n")

    print("""   El juego consiste en una serie de preguntas de distintas categorías,
    el jugador deberá de responder correctamente, eligiendo entre A, B, C o D.
        
    La partida finaliza cuando el jugador haya respondido correctamente 6
    preguntas.
        
    Al final de la partida se mostrarán los resultados; nombre del jugador,
    preguntas respondidas en total y el tiempo empleado.
    """)


'''
Esta es la tarjeta final donde se recogen los datos de cada partida; nombre, 
preguntas respondidas y el tiempo empleado.
El tiempo se calcula desde que se inicia el juego, hasta que el jugador acierta
la sexta pregunta.
'''

def resumen(preg, nom_jugador, tiempo):

    print(f"-------------------------")
    print(f"   FIN    DEL    JUEGO    ")
    print(f"-------------------------\n")
    print(f"Nombre jugador: {nom_jugador}")
    print(f"Preguntas respondidas: {preg}")
    print(f"Tiempo empleado: {tiempo:.2f} s \n")
    print(f"¡Muchas gracias por jugar! :) \n")
    print(f"-------------------------\n")
    inicio()

'''
Donde se ejecuta todo el juego.
'''

def jugar():

    aciertos = 0
    preg = 0


    name_input = False

    while name_input == False:
        nom_jugador = input("Introduzca su nombre: ")
        if not nom_jugador:
            print(f"Introduzca un nombre válido.")
        else:
            name_input = True

    print(f"¡¡Disfruta del juego {nom_jugador}!!\n")
    print(f"¿Preparado?")
    time.sleep(0.75)
    print(f"¿Listo?")
    time.sleep(0.75)
    print(f"¡Ya!\n")
    time.sleep(0.75)
    inicio = time.time()

    while aciertos < 6:
        try:
            dado = random.randint(1, 6)
            print(f"El dado ha sacado un {dado}")
            print(f"-------------------------\n")
            match dado:
                case 1:
                    print(f"* Categoría: Geografía *")
                    res = p.dic_geo()
                case 2:
                    print(f"* Categoría: Entretenimiento *")
                    res = p.dic_entr()
                case 3:
                    print(f"* Categoría: Historia *")
                    res = p.dic_historia()
                case 4:
                    print(f"* Categoría: Arte y Literatura *")
                    res = p.dic_art()
                case 5:
                    print(f"* Categoría: Ciencia y Naturaleza *")
                    res = p.dic_cienc()
                case 6:
                    print(f"* Categoría: Deportes *")
                    res = p.dic_dep()
                case _:
                    print(f"* Categoría: None *")
            if(res == True):
                aciertos = aciertos + 1
            preg = preg + 1
            print(f"{nom_jugador} llevas {aciertos} aciertos. \n")
        except(ValueError):
            print(f"Valor no válido. Por favor introduzca una opción correcta.")
    fin = time.time()
    tiempo = fin - inicio
    resumen(preg, nom_jugador, tiempo)

'''
El menú de inicio, donde tendremos que elegir entre tres opciones:
    1. El juego.
    2. Las reglas del juego.
    3. Salir del programa.
'''

def inicio():

    print(r"""  _______   _       _       _ _____       
 |__   __| (_)     (_)     | |  __ \      
    | |_ __ ___   ___  __ _| | |__) |   _ 
    | | '__| \ \ / / |/ _` | |  ___/ | | |
    | | |  | |\ V /| | (_| | | |   | |_| |
    |_|_|  |_| \_/ |_|\__,_|_|_|    \__, |
                                     __/ |
                                    |___/ 
 """)
    
    print(f"Bienvenido al Trivial!")
    print(f"Creado por: Inés Martínez")

    salir_juego = False

    while salir_juego == False:

        print(f"-------------------------\n")
        print(f"1. Jugar")
        print(f"2. Reglas")
        print(f"3. Salir")
        print(f"-------------------------\n")

        try:
            sel = int(input("¿Qué desea hacer?: "))
            match sel:
                case 1:
                    jugar()
                case 2:
                    reglas()
                case 3:
                    salir_juego = True
                case _:
                    print(f"Introduzca una opción válida")        
        except(ValueError):
            print(f"Valor no válido. Por favor introduzca una opción correcta.")

    if salir_juego:
        print(f"Hasta pronto !!")
        print(""" 𐔌՞ ܸ.ˬ.ܸ՞𐦯 """)

'''
Donde se llama a la función principal (inicio())
'''

if __name__ == "__main__":
    inicio()
