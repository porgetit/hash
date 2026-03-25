from typing import Any
from .interfaces import IHasher
from .strategies import IntegerHasher, FloatHasher, BooleanHasher, StringHasher, TupleHasher


class PythonHashFacade:
    """
    Fachada central para despachar la función de hash según el tipo de objeto.
    Utiliza un diccionario Interno (Strategy pattern map) para resolver la clase correcta.
    """
    def __init__(self) -> None:
        self._strategies = {
            int: IntegerHasher(),
            float: FloatHasher(),
            bool: BooleanHasher(),
            str: StringHasher(),
        }
        # El hasher de tuplas requiere de la fachada para resolver el hash de sus elementos internos
        self._strategies[tuple] = TupleHasher(self)

    def hash(self, obj: Any) -> int:
        """
        Encuentra el 'Estratega Hasher' correspondiente para el tipo de elemento
        y calcula el hash numérico. Si el tipo no está mapeado, se usa el hash() base de Python
        como fallback.
        
        :param obj: Objeto a hashear.
        :return: Entero que representa el valor hash.
        """
        obj_type = type(obj)
        
        if obj_type in self._strategies:
            strategy: IHasher = self._strategies[obj_type]
            return strategy.hash(obj)
            
        # Fallback para tipos desconocidos (e.g., frozensets, clases de usuario, etc.)
        return hash(obj)
