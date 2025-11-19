import random

class Atleta:
    # Constructor para inicializar el nombre y la marca personal del atleta
    def __init__(self, nombre, marcaPersonal):
        self.nombre = nombre
        self.marcaPersonal = marcaPersonal

    '''
    Metodo para simular un salto durante el entrenamiento, se calcula un salto aleatorio entre 3.0 y 7.0 metros redondeado a 2 decimales
    y se devuelve el salto.
    '''
    def realizarSaltoEntrenamiento(self):

        saltoEntrenamiento = round(random.uniform(3.0, 7.0),2)

        print(f"El atleta {self.nombre} ha realizado un salto de {saltoEntrenamiento}m.")
        return saltoEntrenamiento

    '''
    Metodo para simular un salto durante la competicion, se calcula un salto aleatorio entre 4.0 y 8.0 metros redondeado a 2 decimales
    y se devuelve el salto.
    '''
    def realizarSaltoCompeticion(self):
        
        saltoCompeticion = round(random.uniform(4.0, 8.0),2)

        print(f"El salto de {self.nombre} es de {saltoCompeticion}m.")
        return saltoCompeticion
    
class Entrenamiento:
    def __init__(self):
        pass
    
    # Metodo entrenar que simula una sesion de entrenamiento para un atleta, se inicializa la altura en 4.50 metros.
    def entrenar(self, jugador):
        alturaEntreno = 4.50
        saltosValidos = 0
        saltosNulos = 0

        print(f"\nEntrenamiento del atleta {jugador.nombre} comienza con el listón en la altura {alturaEntreno}m.")
        #Se usa un for in range para realizar 15 intentos de salto
        for intento in range(1,16):
            alturaEntreno = round(alturaEntreno,2)
            print(f"\nIntento {intento}:")
            # En cada intento se llama a resalizarSaltoEntrenamiento para obtener el salto realizado
            salto = jugador.realizarSaltoEntrenamiento()

            # Si el salto es mayor o igual a la altura del liston, se suman 20cm a la altura del liston y se cuenta como salto valido
            if salto >= alturaEntreno:
                print(f"Buen salto, has superado el liston en {alturaEntreno}m.")
                print(f"Sube el listón 20cm.")
                alturaEntreno += 0.20
                saltosValidos += 1

            # Si el salto es menor a la altura del liston, se suman 5cm a la altura del liston y se cuenta como salto nulo
            elif salto < alturaEntreno:
                print(f"Vaya... no has superado el liston en {alturaEntreno}m.")
                print(f"Sube el listón 5cm.")
                alturaEntreno += 0.05
                saltosNulos += 1

        # Al final se muestran los resultados del entrenamiento.
        print(f"\nEntrenamiento finalizado!!")
        print(f"El atleta {jugador.nombre} ha hecho {saltosValidos} válidos y {saltosNulos} nulos")

class Competicion:
    def __init__(self):
        pass
    
    # Metodo para realizar un intento de salto en la competicion.
    def realizarIntento(self, jugador, alturaListon):

        # Se redondea la altura del liston a 2 decimales y se muestra por pantalla
        alturaListon = round(alturaListon,2)
        print(f"El atleta {jugador.nombre} intenta saltar {alturaListon}m.")
        
        salto = jugador.realizarSaltoCompeticion()
        
        # Si el salto es mayor o igual a la altura del liston, se actualiza la marca personal si es necesario y se devuelve True
        if salto >= alturaListon:
            print(f"Altura {alturaListon}m superada, salto de {salto}m.")
            if salto > jugador.marcaPersonal:
                jugador.marcaPersonal = salto
                print(f"¡¡{salto}m nueva marca personal!!")
            return True
        
        # Si el salto es menor a la altura del liston, se devuelve False
        else:
            print(f"Salto en {alturaListon}m nulo, salto de {salto}m.")
            return False
    
    # Metodo para gestionar la competicion entre dos atletas, se inicializa la altura en 5.0 metros, se cuentan los fallos y se registran los mejores saltos en variables.
    def competir(self, jugador1, jugador2):
        altura_actual = 5.0
        fallos1 = 0
        fallos2 = 0
        mejor_salto_j1 = 0
        mejor_salto_j2 = 0

        print(f"\nComienza la competición entre {jugador1.nombre} y {jugador2.nombre}")
        print(f"Altura inicial: {altura_actual:.2f}m.")

        # Bucle while que se ejecuta mientras que no haya 3 fallos consecutivos en alguno de los 2 jugadores.
        while fallos1 < 3 or fallos2 < 3:

            #Si el jugador 1 no ha tenido 3 fallos consecutivos, realiza su intento
            if fallos1 < 3:
                print(f"\nTurno de {jugador1.nombre}")
                exito = self.realizarIntento(jugador1, altura_actual)

                # Si lo salta con exito, se reinician los fallos a 0, se suman 10 cm de altura y se actualiza el mejor salto del atleta. 
                if exito:
                    fallos1 = 0
                    altura_actual += 0.10
                    mejor_salto_j1 = altura_actual

                # Si no lo salta, se incrementa en 1 los fallos consecutivos.
                else:
                    fallos1 += 1
                    print(f"{jugador1.nombre} lleva {fallos1} fallos consecutivos.")

            # Si ambos jugadores tienen 3 fallos consecutivos, se sale del bucle
            if fallos1 >= 3 and fallos2 >= 3:
                break
            
            # Si el jugador 2 no ha tenido 3 fallos consecutivos, realiza su intento, lo mismo que el jugador 1 pero para el jugador 2
            if fallos2 < 3:
                print(f"\nTurno de {jugador2.nombre}")
                exito = self.realizarIntento(jugador2, altura_actual)
                if exito:
                    fallos2 = 0
                    altura_actual += 0.10
                    mejor_salto_j2 = altura_actual
                else:
                    fallos2 += 1
                    print(f"{jugador2.nombre} lleva {fallos2} fallos consecutivos.")

            if fallos1 >= 3 and fallos2 >= 3:
                break
        
        # Se termina la competicion y se muestran los resultados finales
        print("\nCompetición terminada\n")
        self.mostrarPodio(jugador1, mejor_salto_j1, jugador2, mejor_salto_j2)

    # Metodo para mostrar el podio y anunciar el ganador o si hay empate, se usa formateo de texto para alinear las columnas de la tabla.
    def mostrarPodio(self, jugador1, salto1, jugador2, salto2):
        print("Resultados finales:")
        print("----------------------------------------")
        print(f"{'Jugador':<15} | {'Altura conseguida (m)':>20}")
        print("----------------------------------------")
        print(f"{jugador1.nombre:<15} | {salto1:>20.2f}")
        print(f"{jugador2.nombre:<15} | {salto2:>20.2f}")
        print("----------------------------------------")

        # if para determinar el ganador o si hay empate
        if salto1 > salto2:
            print(f"\n{jugador1.nombre} gana la competición!")
        elif salto2 > salto1:
            print(f"\n{jugador2.nombre} gana la competición!")
        else:
            print("\nEmpate técnico entre ambos atletas")

class Main:
    # Constructor para inicializar la lista de atletas, el entrenamiento y la competicion.
    def __init__(self):
        self.atletas = [
            Atleta("Aitor", 5.20),
            Atleta("Asier", 5.10),
            Atleta("Joritz", 5.30)
        ]
        self.entrenamiento = Entrenamiento()
        self.competicion = Competicion()

    # Metodo para mostrar el menu principal del programa, con las opciones Entrenar, Competir y Salir.
    def mostrar_menu(self):
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Entrenar")
        print("2. Competir")
        print("3. Salir")

    # Metodo para seleccionar un atleta de la lista, mostrando sus nombres y marcas personales. Este metodo se usa para el entrenamiento.
    def seleccionar_atleta(self):
        print("\nSelecciona un atleta:")
        # Se crea un indice para numerar los atletas
        indice = 1
        # Se recorre la lista de atletas mostrando su nombre y marca personal con un for.
        for atleta in self.atletas:
            print(f"{indice}. {atleta.nombre} (Marca: {atleta.marcaPersonal}m)")
            # Se aumenta el indice en 1 para que el siguiente atleta tenga el numero correcto.
            indice += 1

        # Se usa un bucle while para que el usuario seleccione el número del atleta válido.
        while True:
            try:
                # Se le pide al usuario que introduzca el número del atleta.
                opcion = int(input("Número del atleta: "))
                # Si el número es mayor o igual a 1 y menor o igual al número de atletas, se devuelve el atleta seleccionado menos 1 para que asi devuelva el numero de la lista correcto
                if 1 <= opcion <= len(self.atletas):
                    return self.atletas[opcion - 1]
                else:
                    print("Número fuera de rango.")
            # Se usa un try except para capturar errores de valor en caso de que el usuario no introduzca un número entero.
            except ValueError:
                print("Entrada no válida, introduce un número entero.")

    # Metodo para seleccionar dos atletas diferentes de la lista, este metodo se usa para la competicion.
    def seleccionar_dos_atletas(self):
        print("\nSelecciona dos atletas:")
        indice = 1
        for atleta in self.atletas:
            print(f"{indice}. {atleta.nombre} (Marca: {atleta.marcaPersonal}m)")
            indice += 1

        # Se vuelve a usar un bucle while para que el usuario seleccione dos números válidos y diferentes.
        while True:

            # Se usa un try except para capturar errores de valor en caso de que el usuario no introduzca números enteros.
            try:
                # Se le pide al usuario que introduzca los números de los dos atletas y se les resta 1 para que devuelvan el número correcto de la lista.
                a1 = int(input("Atleta 1: ")) - 1
                a2 = int(input("Atleta 2: ")) - 1

                # En caso de que los números sean iguales, se le avisa al usuario y se vuelve a pedir la selección.
                if a1 == a2:
                    print("Debes elegir atletas diferentes.")
                    continue
                # Si los números están dentro del rango válido, se devuelven los dos atletas seleccionados.
                if 0 <= a1 < len(self.atletas) and 0 <= a2 < len(self.atletas):
                    return self.atletas[a1], self.atletas[a2]
                else:
                    print("Algún número no es válido.")
            except ValueError:
                print("Debes introducir números enteros.")

    # Metodo para ejecutar el programa, mostrando el menu y gestionando las opciones seleccionadas por el usuario.
    def ejecutar(self):
        while True:
            self.mostrar_menu()
            opcion = input("Elige una opción: ")

            # Se le pide al usuario que seleccione una opción y se usa un try except para capturar errores de valor.
            try:
                # Si la opción es 1, se selecciona un atleta y se llama al metodo entrenar.
                if opcion == "1":
                    atleta = self.seleccionar_atleta()
                    self.entrenamiento.entrenar(atleta)
                
                # Si la opción es 2, se seleccionan dos atletas y se llama al metodo competir.
                elif opcion == "2":
                    atleta1, atleta2 = self.seleccionar_dos_atletas()
                    self.competicion.competir(atleta1, atleta2)

                # Si la opción es 3, se sale del programa.
                elif opcion == "3":
                    print("Saliendo del programa...")
                    break
                else:
                    print("Opción no válida. Intenta nuevamente.")
            except ValueError:
                    print("Debes introducir un número entero.")

# Se ejecuta el programa.
if __name__ == "__main__":
    programa = Main()
    programa.ejecutar()