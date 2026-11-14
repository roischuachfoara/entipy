from ..pattern.component import Component
from dataclasses import dataclass

@dataclass
class ComponentFilepath(Component):
    filepath : str = ''

    def __init__(self, filepath : str = ''):
        self.filepath = filepath