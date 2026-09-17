"""
Ejercicio: funciones para calcular area y perimetro.

Se definen funciones para calcular area y perimetro de un
rectangulo. Se muestra el resultado en una funcion main().
"""


def area_rectangulo(base: float, altura: float) -> float:
    return base * altura


def perimetro_rectangulo(base: float, altura: float) -> float:
    return 2 * (base + altura)


def main():
    base = float(input("Ingresa la base del rectangulo: "))
    altura = float(input("Ingresa la altura del rectangulo: "))

    if base <= 0 or altura <= 0:
        print("La base y la altura deben ser positivas.")
        return

    area = area_rectangulo(base, altura)
    perimetro = perimetro_rectangulo(base, altura)

    print(f"Area del rectangulo: {area}")
    print(f"Perimetro del rectangulo: {perimetro}")


if __name__ == "__main__":
    main()
