import sys
import math
from typing import Any, TYPE_CHECKING
from .interfaces import IHasher

if TYPE_CHECKING:
    from .facade import PythonHashFacade

# Módulo utilizado por CPython para el hashing, típicamente 2**61 - 1 en 64 bits.
_HASH_MODULUS = sys.hash_info.modulus if hasattr(sys, 'hash_info') else (1 << 61) - 1
_UL_MASK = 0xFFFFFFFFFFFFFFFF  # Máscara usada para simular uint64_t en operaciones de hash

class IntegerHasher(IHasher):
    """
    Estrategia para calcular el hash de un entero, replicando el built-in de CPython.
    """
    def hash(self, obj: Any) -> int:
        if not isinstance(obj, int):
            raise TypeError("Se esperaba un número entero")
        
        # En CPython, el hash del entero se calcula sobre el valor absoluto y luego se aplica el signo.
        # Python % operator devuelve valores positivos para divisores positivos, por lo que usamos abs().
        sign = -1 if obj < 0 else 1
        h = (abs(obj) % _HASH_MODULUS) * sign
        
        if h == -1:
            h = -2
            
        return h


class BooleanHasher(IHasher):
    """
    Estrategia para booleanos. Al heredar históricamente de enteros, 
    True se evalúa como 1 y False como 0.
    """
    def hash(self, obj: Any) -> int:
        if not isinstance(obj, bool):
            raise TypeError("Se esperaba un booleano")
        
        # Aprovechamos el IntegerHasher ya que bool es subclase de int
        h = int(obj) % _HASH_MODULUS
        if h == -1:
            h = -2
            
        return h


class FloatHasher(IHasher):
    """
    Estrategia para flotantes replicando el algoritmo 'hash_fraction' de CPython.
    """
    def hash(self, obj: Any) -> int:
        if not isinstance(obj, float):
            raise TypeError("Se esperaba un número de tipo float")
            
        if math.isnan(obj):
            # CPython comúnmente devuelve 0 (o identidad del objeto en puntero) para NaN si no está reescrito.
            # Python hash(float('nan')) en 64-bit utiliza un valor especial guardado en sys.hash_info
            return sys.hash_info.nan if hasattr(sys.hash_info, 'nan') else 0
            
        if math.isinf(obj):
            # El hash de infinito es un valor constante en sys.hash_info
            inf_val = sys.hash_info.inf if hasattr(sys.hash_info, 'inf') else 314159
            return inf_val if obj > 0 else -inf_val
            
        if obj == 0.0:
            return 0
            
        # Extraer mantisa y exponente usando frexp tal como CPython
        sign = 1 if obj > 0 else -1
        m, e = math.frexp(abs(obj))
        
        # Escalar mantisa. Float de Python tiene 53 bits de precisión
        m_int = int(m * (1 << 53))
        e -= 53
        
        # Calcular h = (m_int * 2**e) % _HASH_MODULUS
        if e >= 0:
            h = (m_int << e) % _HASH_MODULUS
        else:
            # Multiplicar por el inverso modular pow(base, exp, mod) en Python => soporta exp < 0 desde Py3.8
            h = (m_int * pow(2, e, _HASH_MODULUS)) % _HASH_MODULUS
            
        h = h * sign
        
        if h == -1:
            h = -2
            
        return h


class TupleHasher(IHasher):
    """
    Estrategia para iterables como tuplas, combinando sus hashes recursivamente
    usando el algoritmo XXPRIME de CPython 3.8+.
    """
    def __init__(self, facade: 'PythonHashFacade'):
        self.facade = facade
        
    def hash(self, obj: Any) -> int:
        if not isinstance(obj, tuple):
            raise TypeError("Se esperaba una tupla")
            
        # Constantes de multiplicación XXPRIME usadas en CPython 3.8+ tuplehash
        _PyHASH_XXPRIME_1 = 11400714785074694791
        _PyHASH_XXPRIME_2 = 14029467366897019727
        _PyHASH_XXPRIME_5 = 2870177450012600261
        
        acc = _PyHASH_XXPRIME_5
        
        # Iterar componentes, hashear con la fachada y combinarlos
        for item in obj:
            lane = self.facade.hash(item) & _UL_MASK
            acc = (acc + (lane * _PyHASH_XXPRIME_2) & _UL_MASK) & _UL_MASK
            acc = ((acc << 31) & _UL_MASK) | (acc >> 33)
            acc = (acc * _PyHASH_XXPRIME_1) & _UL_MASK
            
        acc = (acc + (len(obj) ^ (_PyHASH_XXPRIME_5 ^ 3527539))) & _UL_MASK
        
        # Convertir a signed 64-bit que es lo que Python devuelve en C
        if acc >= 0x8000000000000000:
            acc -= 0x10000000000000000
            
        if acc == -1:
            acc = -2
            
        return acc


class StringHasher(IHasher):
    """
    Estrategia de hashing iterativo para strings.
    NOTA: CPython 3.3+ utiliza SipHash24, cuya semilla generada es aleatoria e inaccesible
    desde el entorno de Python directo. Por consiguiente, esta es una implementación determinista general
    educativa basada en FNV-1a para garantizar tipos pero no igualdad estricta con hash() built-in.
    """
    def hash(self, obj: Any) -> int:
        if not isinstance(obj, str):
            raise TypeError("Se esperaba una cadena de texto (str)")
            
        fnv_prime = 1099511628211
        hash_value = 14695981039346656037
        
        for char in obj.encode('utf-8'):
            hash_value = hash_value ^ char
            hash_value = (hash_value * fnv_prime) & _UL_MASK
            
        # Convertir a firmado
        if hash_value >= 0x8000000000000000:
            hash_value -= 0x10000000000000000
            
        if hash_value == -1:
            hash_value = -2
            
        return hash_value
