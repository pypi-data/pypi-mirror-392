'''
Se importan:
    random para sacar de forma aleatoria una de las preguntas de cada categoría.
'''

import random

'''
En este archivo se almacenan todas preguntas de cada categoría.
Se establece un índice, y se define un array con la pregunta, otro array con las posibles respuestas, y la respuesta correcta.
Todo ello se procesa en la función quest_builder().
'''

quest_geo = {
1: ['¿Cuál es el río más largo de España?', ["A. Duero", "B. Tajo", "C. Miño", "D. Guadiana"], "B"],
2: ['¿En qué continente se encuentra el desierto del Sahara?', ["A. Asia", "B. África", "C. América", "D. Oceanía"], "B"],
3: ['¿Cuál es la capital de Canadá?', ["A. Toronto", "B. Ottawa", "C. Montreal", "D. Vancouver"], "B"],
4: ['¿Qué océano baña las costas de Chile?', ["A. Atlántico", "B. Índico", "C. Pacífico", "D. Ártico"], "C"],
5: ['¿Cuál es el país más grande del mundo?', ["A. Canadá", "B. Rusia", "C. China", "D. Estados Unidos"], "B"],
6: ['¿En qué país se encuentra la Torre Eiffel?', ["A. Italia", "B. Francia", "C. España", "D. Bélgica"], "B"],
7: ['¿Qué cordillera separa Europa de Asia?', ["A. Andes", "B. Alpes", "C. Urales", "D. Himalaya"], "C"],
8: ['¿Cuál es la capital de Australia?', ["A. Sidney", "B. Melbourne", "C. Canberra", "D. Brisbane"], "C"],
9: ['¿Qué mar separa Europa de África?', ["A. Caribe", "B. Mediterráneo", "C. Rojo", "D. Negro"], "B"],
10: ['¿Dónde se encuentra el monte Kilimanjaro?', ["A. Sudáfrica", "B. Tanzania", "C. Kenia", "D. Etiopía"], "B"],
}

quest_entr = {
1: ['¿Quién interpretó a Jack en "Titanic"?', ["A. Brad Pitt", "B. Leonardo DiCaprio", "C. Tom Cruise", "D. Matt Damon"], "B"],
2: ['¿Qué serie tiene como protagonista a un profesor llamado Walter White?', ["A. The Sopranos", "B. Breaking Bad", "C. Lost", "D. Dexter"], "B"],
3: ['¿Qué famoso mago tiene una cicatriz en forma de rayo?', ["A. Harry Potter", "B. Gandalf", "C. Merlin", "D. Dumbledore"], "A"],
4: ['¿Qué saga de películas incluye a Darth Vader?', ["A. Star Wars", "B. Star Trek", "C. Matrix", "D. Alien"], "A"],
5: ['¿Quién creó el personaje de Mickey Mouse?', ["A. Walt Disney", "B. Stan Lee", "C. Matt Groening", "D. Steven Spielberg"], "A"],
6: ['¿Qué banda británica lanzó el álbum "Abbey Road"?', ["A. The Rolling Stones", "B. The Beatles", "C. Queen", "D. Pink Floyd"], "B"],
7: ['¿Qué actor protagoniza la saga "Misión Imposible"?', ["A. Tom Cruise", "B. Bruce Willis", "C. Matt Damon", "D. Keanu Reeves"], "A"],
8: ['¿Qué personaje de Disney pierde un zapato de cristal?', ["A. Blancanieves", "B. Cenicienta", "C. Ariel", "D. Bella"], "B"],
9: ['¿Cuál es el nombre del parque temático inspirado en las películas de dinosaurios?', ["A. DinoWorld", "B. Jurassic Park", "C. Prehistoric Land", "D. Lost World"], "B"],
10: ['¿Qué película animada tiene como protagonista a un pez llamado Nemo?', ["A. Buscando a Nemo", "B. La Sirenita", "C. Shark Tale", "D. Nemo Adventure"], "A"],
}

quest_historia = {
1: ['¿En qué año llegó el hombre a la Luna?', ["A. 1969", "B. 1970", "C. 1959", "D. 1972"], "A"],
2: ['¿En qué año llegó Cristobal Colón a América?', ["A. 1999", "B. 2024", "C. 1492", "D. 1000"], "C"],
3: ['¿Quién fue el primer emperador romano?', ["A. Julio César", "B. Augusto", "C. Nerón", "D. Trajano"], "B"],
4: ['¿En qué año comenzó la Segunda Guerra Mundial?', ["A. 1936", "B. 1939", "C. 1941", "D. 1945"], "B"],
5: ['¿Qué civilización construyó las pirámides de Egipto?', ["A. Azteca", "B. Romana", "C. Egipcia", "D. Maya"], "C"],
6: ['¿Quién fue el líder del movimiento independentista indio?', ["A. Nehru", "B. Gandhi", "C. Bose", "D. Patel"], "B"],
7: ['¿Cuál fue la capital del Imperio Inca?', ["A. Cuzco", "B. Lima", "C. Quito", "D. Machu Picchu"], "A"],
8: ['¿En qué país se inició la Revolución Industrial?', ["A. Francia", "B. Inglaterra", "C. Alemania", "D. Estados Unidos"], "B"],
9: ['¿Qué muro cayó en 1989?', ["A. Muro de Berlín", "B. Muro de China", "C. Muro de Adriano", "D. Muro de Jerusalén"], "A"],
10: ['¿Quién fue el primer presidente de los Estados Unidos?', ["A. Thomas Jefferson", "B. Abraham Lincoln", "C. George Washington", "D. John Adams"], "C"],
}

quest_art = {
1: ['¿Quién pintó "La Mona Lisa"?', ["A. Miguel Ángel", "B. Leonardo da Vinci", "C. Rafael", "D. Botticelli"], "B"],
2: ['¿Quién escribió "Don Quijote de la Mancha"?', ["A. Lope de Vega", "B. Calderón de la Barca", "C. Cervantes", "D. Quevedo"], "C"],
3: ['¿Qué pintor es famoso por cortarse una oreja?', ["A. Dalí", "B. Van Gogh", "C. Picasso", "D. Monet"], "B"],
4: ['¿Quién escribió "Romeo y Julieta"?', ["A. Shakespeare", "B. Dickens", "C. Tolstoi", "D. Hugo"], "A"],
5: ['¿Qué estilo artístico se asocia a Salvador Dalí?', ["A. Impresionismo", "B. Cubismo", "C. Surrealismo", "D. Barroco"], "C"],
6: ['¿Quién pintó "El Guernica"?', ["A. Goya", "B. Picasso", "C. Dalí", "D. Miró"], "B"],
7: ['¿Qué escultor creó "El David"?', ["A. Bernini", "B. Miguel Ángel", "C. Donatello", "D. Rodin"], "B"],
8: ['¿Qué poeta escribió "Veinte poemas de amor y una canción desesperada"?', ["A. Neruda", "B. Lorca", "C. Benedetti", "D. Machado"], "A"],
9: ['¿Qué novela comienza con "En un lugar de la Mancha..."?', ["A. El Lazarillo", "B. Don Quijote", "C. La Celestina", "D. Crimen y castigo"], "B"],
10: ['¿Qué compositor es autor de "La flauta mágica"?', ["A. Mozart", "B. Beethoven", "C. Bach", "D. Vivaldi"], "A"],
}

quest_cienc = {
1: ['¿Cuál es el planeta más grande del sistema solar?', ["A. Saturno", "B. Júpiter", "C. Urano", "D. Neptuno"], "B"],
2: ['¿Qué gas respiran los seres humanos?', ["A. Dióxido de carbono", "B. Oxígeno", "C. Nitrógeno", "D. Hidrógeno"], "B"],
3: ['¿Qué órgano bombea la sangre en el cuerpo?', ["A. Pulmón", "B. Riñón", "C. Corazón", "D. Hígado"], "C"],
4: ['¿Qué estudia la botánica?', ["A. Los animales", "B. Las plantas", "C. Las rocas", "D. Las bacterias"], "B"],
5: ['¿Qué partícula tiene carga negativa?', ["A. Protón", "B. Neutrón", "C. Electrón", "D. Ión"], "C"],
6: ['¿Qué científico propuso la teoría de la relatividad?', ["A. Newton", "B. Einstein", "C. Galileo", "D. Hawking"], "B"],
7: ['¿Cómo se llama el proceso por el cual las plantas producen su alimento?', ["A. Fotosíntesis", "B. Digestión", "C. Fermentación", "D. Respiración"], "A"],
8: ['¿Cuál es el metal más ligero?', ["A. Oro", "B. Litio", "C. Aluminio", "D. Sodio"], "B"],
9: ['¿Qué planeta es conocido como el planeta rojo?', ["A. Venus", "B. Marte", "C. Mercurio", "D. Júpiter"], "B"],
10: ['¿Qué tipo de sangre es el donante universal?', ["A. A+", "B. B-", "C. AB+", "D. O-"], "D"],
}

quest_dep = {
1: ['¿Qué deporte se puede practicar al estilo mariposa?', ["A. Beisbol", "B. Tenis", "C. Natación", "D. Fútbol"], "C"],
2: ['¿Cuántos jugadores hay en un equipo de fútbol en el campo?', ["A. 10", "B. 11", "C. 12", "D. 9"], "B"],
3: ['¿Qué país ganó el Mundial de fútbol 2010?', ["A. Alemania", "B. Brasil", "C. España", "D. Italia"], "C"],
4: ['¿En qué deporte se usa una raqueta?', ["A. Baloncesto", "B. Tenis", "C. Golf", "D. Rugby"], "B"],
5: ['¿Qué deporte se practica en Wimbledon?', ["A. Tenis", "B. Golf", "C. Cricket", "D. Fútbol"], "A"],
6: ['¿En qué deporte destacó Michael Jordan?', ["A. Atletismo", "B. Baloncesto", "C. Boxeo", "D. Fútbol"], "B"],
7: ['¿Qué país organiza los Juegos Olímpicos de 2024?', ["A. Japón", "B. Francia", "C. Estados Unidos", "D. China"], "B"],
8: ['¿Qué jugador de fútbol es conocido como "La Pulga"?', ["A. Cristiano Ronaldo", "B. Messi", "C. Neymar", "D. Mbappé"], "B"],
9: ['¿Cuántos sets se necesitan ganar para vencer en un partido de tenis masculino de Grand Slam?', ["A. 2", "B. 3", "C. 4", "D. 5"], "B"],
10: ['¿En qué deporte se realiza un "strike"?', ["A. Béisbol", "B. Bolos", "C. Cricket", "D. Hockey"], "B"],
}

general = {
1: ["Geografía", quest_geo],
2: ["Entretenimiento", quest_entr],
3: ["Historia", quest_historia],
4: ["Arte y Literatura", quest_art],
5: ["Ciencia y Naturaleza", quest_cienc],
6: ["Deportes", quest_dep],
}

'''
Funciones donde se decide la pregunta y se manda la pregunta a procesar al constructor.
'''

def dic_geo():
    index2 = random.randint(1, 10)
    pregunta = quest_geo[index2]
    return quest_builder(pregunta)

def dic_entr():
    index2 = random.randint(1, 10)
    pregunta = quest_entr[index2]
    return quest_builder(pregunta)

def dic_historia():
    index2 = random.randint(1, 10)
    pregunta = quest_historia[index2]
    return quest_builder(pregunta)

def dic_art():
    index2 = random.randint(1, 10)
    pregunta = quest_art[index2]
    return quest_builder(pregunta)

def dic_cienc():
    index2 = random.randint(1, 10)
    pregunta = quest_cienc[index2]
    return quest_builder(pregunta)

def dic_dep():
    index2 = random.randint(1, 10)
    pregunta = quest_dep[index2]
    return quest_builder(pregunta)

'''
El constructor de las preguntas.
Recibe la pregunta y la trocea por partes; la pregunta, las posibles respuestas y la respuesta correcta.
También es la función que se encarga de preguntarle al jugador la respuesta correcta.
Devuelve un booleano, lo que en la función de juego se procesa en si ha acertado o no.
'''

def quest_builder(pregunta):

    res_input = False

    print(pregunta[0])
    opciones = pregunta[1]
    res = pregunta[2]
    print(opciones[0])
    print(opciones[1])
    print(opciones[2])
    print(opciones[3])
    while not res_input:
        res_jug = input("> Introduzca la opción correcta (A, B, C, D): ")

        if res_jug.upper() not in ["A", "B", "C", "D"]:
            print(f"Introduzca una opción válida.")
        else:
            res_input = True    
            if res_jug.upper() == res:
                print(f"¡Respuesta correcta!")
                return True
            else:
                print(f"Respuesta incorrecta :(")
                return False