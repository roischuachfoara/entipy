from ..pattern.component import Component
from dataclasses import dataclass
import numpy as np

@dataclass
class ComponentMesh(Component):
    vertices : np.ndarray = None
    indices : np.ndarray = None
    normals : np.ndarray = None
    uvs : np.ndarray = None

    def __init__(self, vertices : np.ndarray = None, indices : np.ndarray = None, normals : np.ndarray = None, uvs : np.ndarray = None):
        self.vertices = vertices
        self.indices = indices
        self.normals = normals
        self.uvs = uvs