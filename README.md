# Custom Python Hasher

Una implementación de la función hash (`hash()`) de Python desde cero ("a pedal"), utilizando principios de Programación Orientada a Objetos (OOP) y estándares PEP.

## Descripción

Este proyecto implementa un sistema flexible para hashear diferentes tipos de datos nativos de Python utilizando el **Patrón Facade (Fachada)** y el **Patrón Strategy (Estrategia)**. La clase `PythonHashFacade` actúa como el punto de entrada principal, que delega el cálculo real del hash a diferentes estrategias de implementación basadas en el tipo del objeto proporcionado.

Tipos soportados de forma nativa por las estrategias:
- `int` (Enteros)
- `float` (Flotantes)
- `bool` (Booleanos)
- `str` (Cadenas de texto)
- `tuple` (Tuplas)

Para cualquier otro tipo no reconocido, el sistema hace un _fallback_ a la función `hash()` incorporada ("built-in") de Python.

## Estructura del Proyecto

```text
hash/
├── hasher/
│   ├── __init__.py
│   ├── facade.py       # Interfaz principal (PythonHashFacade)
│   ├── interfaces.py   # Interfaces base (IHasher)
│   └── strategies.py   # Implementaciones concretas de hashing por tipo
├── tests/              # Pruebas unitarias
├── run_tests.py        # Script para ejecutar comparaciones entre el hasher custom y built-in
└── README.md
```

## Uso

Importa `PythonHashFacade` desde el módulo hasher:

```python
from hasher.facade import PythonHashFacade

hasher = PythonHashFacade()

# Hashing de diferentes tipos
hash_int = hasher.hash(42)
hash_str = hasher.hash("Hello World")
hash_tuple = hasher.hash((1, 2, 3))

print(f"Hash de int: {hash_int}")
print(f"Hash de str: {hash_str}")
```

## Ejecución de Pruebas

Puedes ejecutar la suite de comprobación para validar que la implementación customizada produce los mismos resultados que el `hash()` provisto por el lenguaje original de Python:

```bash
python run_tests.py
```

Esto generará un archivo `results.json` con cualquier posible discrepancia encontrada durante la ejecución de las pruebas. Alternativamente, para la validación automática utilizando PyTest:

```bash
pytest tests/
```
