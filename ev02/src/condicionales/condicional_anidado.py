"""
Ejercicio: condicionales anidados.

Se solicita la nota de un aprendiz (0 a 5) y su asistencia en
porcentaje. Con condicionales anidados se determina si aprueba,
si debe presentar plan de mejoramiento o si reprueba.
"""


def evaluar(nota: float, asistencia: float) -> str:
    if 0 <= nota <= 5 and 0 <= asistencia <= 100:
        if nota >= 3.5:
            if asistencia >= 80:
                resultado = "Aprobado"
            else:
                resultado = "Aprobado con observacion por asistencia"
        else:
            if asistencia >= 80:
                resultado = "Plan de mejoramiento"
            else:
                resultado = "Reprobado"
    else:
        resultado = "Datos fuera de rango"
    return resultado


def main():
    nota = float(input("Ingresa la nota (0.0 a 5.0): "))
    asistencia = float(input("Ingresa la asistencia (0 a 100): "))

    resultado = evaluar(nota, asistencia)
    print(f"Resultado: {resultado}")


if __name__ == "__main__":
    main()
