from ..pattern.component import Component
from dataclasses import dataclass

@dataclass
class ComponentCounter(Component):
    cnt : int = 0

    def __init__(self, cnt : int = 0):
        self.cnt = cnt