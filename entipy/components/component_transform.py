from ..pattern.component import Component
from dataclasses import dataclass
import numpy as np

@dataclass
class ComponentTransform(Component):
    position: np.ndarray
    rotation: np.ndarray
    scale: np.ndarray

    def __init__(self, position : np.ndarray = np.zeros((1, 3), dtype=float), rotation : np.ndarray = np.zeros((1, 3), dtype=float), scale : np.ndarray = np.ones((1, 3), dtype=float)):
        self.position = position
        self.rotation = rotation
        self.scale = scale