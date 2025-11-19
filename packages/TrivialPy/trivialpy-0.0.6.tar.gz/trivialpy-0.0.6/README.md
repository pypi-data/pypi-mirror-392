# TrivialPy

![alt text](https://raw.githubusercontent.com/cvcvrril/trivialpy/refs/heads/main/trivialpy.png)

**TrivialPy** es un juego de preguntas y respuestas desarrollado en Python; vamos, un Trivial Pursuit de toda la vida pero hecho en Python.<br>
Versión: 0.0.6

## Índice
* [Reglas](#reglas)
* [Instalación](#instalación)
* [Funcionamiento](#funcionamiento)
* [Estructura](#estructura)

## Funcionamiento
Tres opciones en el menú principal:
1. Jugar
2. Reglas
3. Salir

### Jugar
Se inicia el juego de forma normal.
Se pregunta por el nombre del jugador y se inicia el juego.
```
Introduzca su nombre: Pepe
¡¡Disfruta del juego Pepe!!

¿Preparado?
¿Listo?
¡Ya!

El dado ha sacado un 3
-------------------------

* Categoría: Historia *
¿Qué muro cayó en 1989?
A. Muro de Berlín
B. Muro de China
C. Muro de Adriano
D. Muro de Jerusalén
> Introduzca la opción correcta (A, B, C, D):
```

### Reglas
Se muestran las reglas del juego.


### Salir
Se sale del juego.


## Reglas
Juego de **un solo jugador**. <br>
Para ganar la partida el jugador debe de acertar **6 preguntas**.<br>
Se emplea un dado virtual (del 1 al 6) para decidir la categoría de la pregunta. <br>
Se contará el tiempo en el que tarde el jugador en completar la partida (se mostrará en los detalles de la partida finalizada).<br>
El jugador debe de elegir de entre una de las cuatro opciones; A, B, C, D.

## Instalación

El proyecto se encuentra en la plataforma [TestPiPy](https://test.pypi.org/project/TrivialPy/). <br>
Escriba lo siguiente en su entorno Python:
```
pip install -i https://test.pypi.org/simple/ TrivialPy
```

## Estructura

```
trivialpython/
├─ trivialpython/
│  ├─ __init__.py
|  ├─ preguntas.py
│  └─ main.py
├─ README.md
├─ LICENSE
└─ pyproject.toml
```