"""
Ejercicio: definicion y uso de funciones.

Se define una funcion saludar() que recibe un nombre y un
idioma opcional, y devuelve un saludo personalizado.
"""


def saludar(nombre: str, idioma: str = "es") -> str:
    if idioma == "es":
        mensaje = f"Hola {nombre}, bienvenido/a!"
    elif idioma == "en":
        mensaje = f"Hello {nombre}, welcome!"
    else:
        mensaje = f"Hi {nombre}!"
    return mensaje


def main():
    nombre = input("Cual es tu nombre? ")
    idioma = input("Idioma (es/en): ") or "es"

    print(saludar(nombre, idioma))


if __name__ == "__main__":
    main()
