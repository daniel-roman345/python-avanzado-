"""
Ejercicio: funcion factorial.

Calcula el factorial de un numero entero no negativo, tanto
en version iterativa como recursiva, para ilustrar el uso de
funciones que se llaman a si mismas.
"""


def factorial_iterativo(n: int) -> int:
    resultado = 1
    for i in range(2, n + 1):
        resultado *= i
    return resultado


def factorial_recursivo(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial_recursivo(n - 1)


def main():
    n = int(input("Ingresa un numero entero no negativo: "))

    if n < 0:
        print("El numero debe ser mayor o igual a cero.")
        return

    print(f"Factorial iterativo de {n}: {factorial_iterativo(n)}")
    print(f"Factorial recursivo de {n}: {factorial_recursivo(n)}")


if __name__ == "__main__":
    main()
