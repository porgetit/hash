import math
import sys
import pytest

from hasher.facade import PythonHashFacade


@pytest.fixture
def hasher() -> PythonHashFacade:
    return PythonHashFacade()

def test_integer_hashing(hasher: PythonHashFacade):
    # Probar integers que den el mismo hash que CPython
    test_cases = [
        0, 1, 42, -1, -42, 
        sys.maxsize, -sys.maxsize,
        (1 << 61), (1 << 61) - 1, (1 << 61) + 1,
        10**100, -10**100  # Large integers
    ]
    for n in test_cases:
        assert hasher.hash(n) == hash(n), f"Fallo al comparar entero: {n}"

def test_boolean_hashing(hasher: PythonHashFacade):
    assert hasher.hash(True) == hash(True)
    assert hasher.hash(False) == hash(False)

def test_float_hashing(hasher: PythonHashFacade):
    test_cases = [
        0.0, -0.0, 1.0, -1.0, 
        3.14159, -3.14159,
        0.333333333, -0.333333333,
        math.inf, -math.inf,
        1e50, 1e-50
    ]
    for f in test_cases:
        assert hasher.hash(f) == hash(f), f"Fallo al comparar flotante: {f}"
        
    # Tratamiento especial de NaN (dado que suele basarse en su id en memoria)
    # Python CPython `hash(float('nan'))` usualmente == 0 if no overwritten id() logic,
    # probaremos simplemente que se devuelve un int 
    assert isinstance(hasher.hash(float('nan')), int)

def test_string_hashing(hasher: PythonHashFacade):
    # Al ser strings manejados de manera especial por SipHash24, 
    # nuestro hasher es determinista y no coincidirá con CPython's randomized built-in hash.
    # Solo validamos que devuelva int de 64 bits y su comportamiento sea consistente.
    s1 = "Hola Mundo"
    s2 = "Hola Mundo"
    s3 = "Mundo Hola"
    
    h1 = hasher.hash(s1)
    h2 = hasher.hash(s2)
    h3 = hasher.hash(s3)
    
    assert isinstance(h1, int)
    assert h1 == h2
    assert h1 != h3

def test_tuple_hashing(hasher: PythonHashFacade):
    # La validación de tuplas puede fallar si la versión de Python usa constantes 
    # diferentes a las implementadas (XXPRIME vs SIP).
    # No obstante, probaremos si en esta versión las tuplas igualan a CPython's hash.
    test_cases = [
        (),
        (1,),
        (1, 2),
        (1, 2, 3),
        (True, False, 1.0, 2.0),
        (-1, 0, 1),
        ((1, 2), (3, 4))
    ]
    
    for t in test_cases:
        assert hasher.hash(t) == hash(t), f"Fallo al comparar tupla: {t}"
