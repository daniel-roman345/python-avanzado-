"""
Ejercicio: suma de numeros con estructuras iterativas.

Suma los numeros del 1 hasta n usando un ciclo for y luego
calcula el promedio.
"""


def sumar_hasta(n: int) -> int:
    total = 0
    for numero in range(1, n + 1):
        total += numero
    return total


def main():
    n = int(input("Hasta que numero deseas sumar? "))

    if n < 1:
        print("El numero debe ser mayor o igual a 1.")
        return

    total = sumar_hasta(n)
    promedio = total / n

    print(f"La suma de 1 hasta {n} es: {total}")
    print(f"El promedio es: {promedio:.2f}")


if __name__ == "__main__":
    main()
