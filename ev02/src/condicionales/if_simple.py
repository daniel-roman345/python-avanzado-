"""
Ejercicio: uso de la estructura condicional simple (if).

Se pide un numero al usuario y se informa si es positivo.
"""


def main():
    entrada = input("Ingresa un numero: ")
    numero = float(entrada)

    if numero > 0:
        print(f"El numero {numero} es positivo.")

    print("Fin del programa.")


if __name__ == "__main__":
    main()
