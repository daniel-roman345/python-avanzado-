"""
Menu principal de la EV02.

Permite ejecutar cualquiera de los ejercicios de estructuras
condicionales, iterativas y funciones desde una sola consola.
"""

from condicionales import if_simple, if_elif_else, condicional_anidado
from iterativas import ciclo_for, ciclo_while, suma_numeros, tabla_multiplicar
from funciones import (
    funcion_saludo,
    funcion_suma,
    funcion_area_rectangulo,
    funcion_factorial,
)


OPCIONES = {
    "1": ("Condicionales - if simple", if_simple.main),
    "2": ("Condicionales - if/elif/else", if_elif_else.main),
    "3": ("Condicionales - anidado", condicional_anidado.main),
    "4": ("Iterativas - ciclo for", ciclo_for.main),
    "5": ("Iterativas - ciclo while", ciclo_while.main),
    "6": ("Iterativas - suma numeros", suma_numeros.main),
    "7": ("Iterativas - tabla multiplicar", tabla_multiplicar.main),
    "8": ("Funciones - saludo", funcion_saludo.main),
    "9": ("Funciones - suma", funcion_suma.main),
    "10": ("Funciones - area rectangulo", funcion_area_rectangulo.main),
    "11": ("Funciones - factorial", funcion_factorial.main),
}


def mostrar_menu():
    print("\n=== EV02 - Fundamentos de Python ===")
    for clave, (nombre, _) in OPCIONES.items():
        print(f"  {clave}. {nombre}")
    print("  0. Salir")


def main():
    while True:
        mostrar_menu()
        opcion = input("Elige una opcion: ").strip()

        if opcion == "0":
            print("Hasta luego!")
            break

        if opcion in OPCIONES:
            _, funcion = OPCIONES[opcion]
            print()
            funcion()
        else:
            print("Opcion no valida, intenta de nuevo.")


if __name__ == "__main__":
    main()
