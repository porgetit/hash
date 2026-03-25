from abc import ABC, abstractmethod
from typing import Any


class IHasher(ABC):
    """
    Interfaz abstracta para las estrategias de hashing.
    Obliga a que cada hasher concreto implemente el método `hash`.
    """

    @abstractmethod
    def hash(self, obj: Any) -> int:
        """
        Calcula el valor hash para el objeto dado.

        :param obj: El objeto a hashear.
        :return: El valor entero del hash.
        """
        pass
