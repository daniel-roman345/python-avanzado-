"""
Ejercicio: estructura condicional if / elif / else.

Se clasifica un numero como positivo, negativo o cero, y ademas
se determina si es par o impar cuando corresponde.
"""


def clasificar(numero: float) -> str:
    if numero > 0:
        clase = "positivo"
    elif numero < 0:
        clase = "negativo"
    else:
        clase = "cero"
    return clase


def main():
    entrada = input("Ingresa un numero entero: ")
    numero = int(entrada)

    clase = clasificar(numero)
    print(f"El numero {numero} es {clase}.")

    if numero != 0:
        if numero % 2 == 0:
            print("Ademas es par.")
        else:
            print("Ademas es impar.")


if __name__ == "__main__":
    main()
