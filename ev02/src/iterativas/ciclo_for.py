"""
Ejercicio: ciclo for.

Recorre una lista de nombres y los imprime numerados. Ademas
muestra el uso de range() para recorrer un rango de numeros.
"""


def main():
    nombres = ["Ana", "Luis", "Carla", "Mateo", "Sofia"]

    print("Lista de aprendices:")
    for indice, nombre in enumerate(nombres, start=1):
        print(f"{indice}. {nombre}")

    print("\nNumeros del 1 al 10 usando range():")
    for numero in range(1, 11):
        print(numero, end=" ")
    print()


if __name__ == "__main__":
    main()
