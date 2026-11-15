from ..pattern.component import Component
from dataclasses import dataclass
import numpy as np

@dataclass
class ComponentMesh(Component):
    vertices : np.ndarray
    triangles : np.ndarray
    normals : np.ndarray

    def __init__(self, vertices : np.ndarray, triangles : np.ndarray, normals : np.ndarray):
        self.vertices = vertices
        self.triangles = triangles
        self.normals = normals