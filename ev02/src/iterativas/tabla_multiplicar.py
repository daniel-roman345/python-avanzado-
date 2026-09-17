"""
Ejercicio: tabla de multiplicar.

Imprime la tabla de multiplicar de un numero pedido al usuario,
usando un ciclo for del 1 al 10.
"""


def imprimir_tabla(numero: int) -> None:
    print(f"Tabla de multiplicar del {numero}:")
    for i in range(1, 11):
        resultado = numero * i
        print(f"{numero} x {i} = {resultado}")


def main():
    numero = int(input("Ingresa el numero de la tabla a mostrar: "))
    imprimir_tabla(numero)


if __name__ == "__main__":
    main()
