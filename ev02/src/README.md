# EV02 - Fundamentos de Python: estructuras de control y funciones

Proyecto que integra los tres bloques de la guia: **condicionales**,
**iterativas** y **funciones**, organizados dentro de `src/`.

## Estructura del proyecto

```
ev02/
└── src/
    ├── condicionales/
    │   ├── if_simple.py
    │   ├── if_elif_else.py
    │   └── condicional_anidado.py
    ├── iterativas/
    │   ├── ciclo_for.py
    │   ├── ciclo_while.py
    │   ├── suma_numeros.py
    │   └── tabla_multiplicar.py
    ├── funciones/
    │   ├── funcion_saludo.py
    │   ├── funcion_suma.py
    │   ├── funcion_area_rectangulo.py
    │   └── funcion_factorial.py
    ├── menu_principal.py
    └── README.md
```

## Requisitos

- Python 3.x instalado.
- Un editor de codigo (VS Code, PyCharm, etc.).

## Como ejecutar

Cada ejercicio se puede correr por separado desde la carpeta `src/`:

```bash
cd ev02/src

# Condicionales
python3 condicionales/if_simple.py
python3 condicionales/if_elif_else.py
python3 condicionales/condicional_anidado.py

# Iterativas
python3 iterativas/ciclo_for.py
python3 iterativas/ciclo_while.py
python3 iterativas/suma_numeros.py
python3 iterativas/tabla_multiplicar.py

# Funciones
python3 funciones/funcion_saludo.py
python3 funciones/funcion_suma.py
python3 funciones/funcion_area_rectangulo.py
python3 funciones/funcion_factorial.py
```

Tambien se puede usar el menu que agrupa todos los ejercicios:

```bash
cd ev02/src
python3 menu_principal.py
```

## Descripcion de los ejercicios

### Condicionales (`src/condicionales/`)

- **if_simple.py**: pide un numero e informa si es positivo.
- **if_elif_else.py**: clasifica un numero como positivo, negativo o
  cero, y determina si es par o impar.
- **condicional_anidado.py**: evalua nota y asistencia con condicionales
  anidados para decidir aprobado / plan de mejoramiento / reprobado.

### Iterativas (`src/iterativas/`)

- **ciclo_for.py**: recorre una lista con `enumerate()` y muestra un
  rango de numeros con `range()`.
- **ciclo_while.py**: cuenta regresiva y bucle controlado con una
  bandera booleana.
- **suma_numeros.py**: suma acumulativa de 1 hasta n y promedio.
- **tabla_multiplicar.py**: imprime la tabla de multiplicar de un
  numero dado.

### Funciones (`src/funciones/`)

- **funcion_saludo.py**: funcion `saludar()` con parametro opcional
  para el idioma.
- **funcion_suma.py**: funciones `sumar()` y `sumar_varios(*args)`.
- **funcion_area_rectangulo.py**: calcula area y perimetro de un
  rectangulo.
- **funcion_factorial.py**: factorial iterativo y recursivo.

## Autor

Daniel Roman — Aprendiz SENA
