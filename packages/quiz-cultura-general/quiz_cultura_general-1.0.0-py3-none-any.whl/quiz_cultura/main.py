#Método que tiene el test con preguntas y respuestas
def test():
    preguntas = [
        {
            "pregunta": "1. ¿Cuándo llegó Cristóbal Colón a América?",
            "opciones": {
                "A": "1500",
                "B": "1492",
                "C": "1942",
                "D": "1782"
            },
            "respuesta_correcta": "B"
        },
        {
            "pregunta": "2. ¿Cuál es el planeta más grande del sistema solar?",
            "opciones": {
                "A": "Sol",
                "B": "Jupiter",
                "C": "Marte",
                "D": "Saturno"
            },
            "respuesta_correcta": "B"
        },
        {
            "pregunta": "3. ¿Cuál es la montaña más alta del mundo?",
            "opciones": {
                "A": "Teide",
                "B": "Kilmanjaro",
                "C": "Vinson",
                "D": "Everest"
            },
            "respuesta_correcta": "D"
        },
        {
            "pregunta": "4. ¿Qué película de animación fue la primera en ser nominada al Oscar a mejor película?",
            "opciones": {
                "A": "Toy Story",
                "B": "Buscando a Nemo",
                "C": "Shrek",
                "D": "La Bella y la Bestia"
            },
            "respuesta_correcta": "D"
        },
        {
            "pregunta": "5. ¿Quién es el autor de la obra La Odisea?",
            "opciones": {
                "A": "Shakespeare",
                "B": "Homero",
                "C": "Cervantes",
                "D": "J.K.Rowling"
            },
            "respuesta_correcta": "B"
        },
        {
            "pregunta": "6. ¿A qué teoría se debe la revolución científica propiciada por Darwin?",
            "opciones": {
                "A": "La teoría genética",
                "B": "La teoría de la evolución",
                "C": "La teoría de la biología moderna",
                "D": "La teoría de la relatividad"
            },
            "respuesta_correcta": "B"
        },
        {
            "pregunta": "7. ¿Quién es considerado el padre de la filosofía?",
            "opciones": {
                "A": "San Agustin",
                "B": "Platón",
                "C": "Sócrates",
                "D": "Aristóteles"
            },
            "respuesta_correcta": "C"
        },
        {
            "pregunta": "8. ¿Qué canción de Queen se convirtió en un éxito mundial en 1975?",
            "opciones": {
                "A": "We Will Rock You",
                "B": "Bohemian Rhapsody",
                "C": "Another One Bites The Dust",
                "D": "Killer Queen"
            },
            "respuesta_correcta": "B"
        }
    ]
    return preguntas


#Menú principal en el que se muestra el quizz
def main():
    cont = 0
    preg = test()

    print("---BIENVENIDO AL QUIZ DE CULTURA GENERAL---")
    print("Vamos a empezar!")
    print("¡RECUERDA!:Debes introducir siempre letras para responder a las preguntas")
    
    # Comprobar cuantos números quiere el usuario
    while True:
        try:
            num = int(input("¿Cuántas preguntas quieres? (Hay un máximo de 8). Escribe la opción con números: "))
            if num < 1 or num > 8:
                print("Error: debes elegir un número del 1 al 8")
                continue
            break 
        except ValueError:
            print("Error: debes introducir números no letras")
    
    #Realizar el quiz
    for i in range(num):
        pregunta = preg[i]
        print(pregunta["pregunta"])
        for letra, opc in pregunta["opciones"].items():
            print(f"{letra}. {opc}")
        try:
            respuesta_usuario = input("Tu respuesta: ").upper()
            if respuesta_usuario == pregunta["respuesta_correcta"]:
                print("Perfecto! Sigue así")
                cont += 1
            else:
                print("Te has equivocado!;(. Pero no te deprimas sigue intentándolo")
        except:
            print("Error: ha ocurrido un problema")
    
    #Mostrar resultados finales
    print(f"\nHas acertado {cont} de {num} preguntas.")
    if cont == num:
        print("¡Wow has acertado todas, se te da realmente bien!")
    else:
        print("Cuando quieras prueba de nuevo tus conocimientos ;)")
    print("Fin del quizz!!")

if __name__ == "__main__":
    main()