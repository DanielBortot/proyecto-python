from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T', bound='ValueObjectRoot')

class ValueObjectRoot(ABC, Generic[T]):
    
    @abstractmethod
    def equals(self, value: T) -> bool:
        pass