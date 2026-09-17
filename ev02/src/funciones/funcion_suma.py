"""
Ejercicio: funcion con parametros y valor de retorno.

Se definen funciones para sumar dos numeros y para sumar una
cantidad variable de numeros usando *args.
"""


def sumar(a: float, b: float) -> float:
    return a + b


def sumar_varios(*numeros: float) -> float:
    total = 0
    for numero in numeros:
        total += numero
    return total


def main():
    a = float(input("Primer numero: "))
    b = float(input("Segundo numero: "))
    print(f"La suma de {a} + {b} = {sumar(a, b)}")

    print("Suma de varios numeros: 1 + 2 + 3 + 4 + 5 =", sumar_varios(1, 2, 3, 4, 5))


if __name__ == "__main__":
    main()
