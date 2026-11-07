from abc import ABC, abstractmethod
from .entity import Entity
from .component import Component

class System(ABC):
    @abstractmethod
    def update(self, scene : dict[Entity, list[Component]]):
        pass 