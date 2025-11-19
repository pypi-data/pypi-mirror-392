PROYECTO DE SIMULACION DE SALTO CON PERTIGA

Simulación en Python de sesiones de entrenamiento y competición de atletas de salto con pértiga.
Incluye gestión de atletas, intentos de salto, fallos, alturas progresivas y determinación automática del ganador en las competiciones.


Caracteristicas principales del programa:

    - Atleta: Tiene el nombre y la marca personal del atleta. Metodos para simular entrenamiento y competición.

    - Entrenamiento: 15 saltos, altura inicial en 4.50 metros, si haces un salto válido el listón sube 20cm, si haces un salto nulo el listón sube 5cm. Se generan saltos con alturas aleatorias entre 3.0 y 7.0 metros. Registra los saltos nulos y válidos, al terminar el entrenamiento los muestra por pantalla.

    - Competición: Seleccionas 2 atletas para que compitan entre si. Si un atleta hace 3 nulos consecutivos en la misma altura, es eliminado. Se inicia la competición en 5.00 metros, va subiendo 10cm por cada salto válido. Se generan saltos con alturas aleatorias entre 4.0 y 8.0 metros. Se actualiza la marca personal del atleta en caso de que uno mejore su marca personal. Una vez terminada la competición semuestra el podio y dice quien ha ganado la competición.

    - Menú interactivo: Hay varias opciones, entrenar un atleta, hacer una competición entre dos atletas y por último salir del programa.


Como ejecutar el programa desde la raíz del proyecto:

    Abrir la terminal y colocarse en la raíz del proyecto, una vez en la raíz se ejecuta el siguiente comando:
    
        python ProyectoUT2/main.py