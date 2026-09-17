"""
Ejercicio: ciclo while.

Solicita un numero al usuario y va restando hasta llegar a cero,
mostrando la cuenta regresiva. Tambien muestra un ejemplo con
una bandera booleana para salir del bucle.
"""


def cuenta_regresiva(inicio: int) -> None:
    print(f"Cuenta regresiva desde {inicio}:")
    while inicio >= 0:
        print(inicio, end=" ")
        inicio -= 1
    print("\nDespegue!")


def menu_salir():
    salir = False
    while not salir:
        opcion = input("Escribe 'salir' para terminar o cualquier otra tecla para continuar: ")
        if opcion.lower() == "salir":
            salir = True
        else:
            print("Sigues en el bucle...")
    print("Fuera del bucle.")


def main():
    inicio = int(input("Ingresa un numero entero positivo: "))
    cuenta_regresiva(inicio)
    menu_salir()


if __name__ == "__main__":
    main()
