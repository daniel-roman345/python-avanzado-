nombre = input("Nombre del jugador: ")

victorias = int(input("Victorias: "))
empates = int(input("Empates: "))
derrotas = int(input("Derrotas: "))

puntaje = victorias * 3 + empates

print("\nResultado")
print("----------------------")
print("Jugador:", nombre)
print("Victorias:", victorias)
print("Empates:", empates)
print("Derrotas:", derrotas)
print("Puntaje final:", puntaje)