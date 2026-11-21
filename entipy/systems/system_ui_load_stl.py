from slimgui import imgui

from ..pattern.entity import Entity
from ..pattern.component import Component
from ..pattern.system import System
from ..components.component_name import ComponentName
from ..components.component_filepath import ComponentFilepath
from ..components.component_mesh import ComponentMesh
from ..utilities.utilities import Utilities

import os
import numpy as np
from stl import mesh as stl_mesh

class SystemUILoadSTL(System):
    def __init__(self):
        super().__init__()
        self.__filepaths : dict[Entity, str] = {}  # text field contents per entity
        self.__errors : dict[Entity, str] = {}

    @staticmethod
    def load_stl(filepath : str, componentMesh : ComponentMesh):
        stl = stl_mesh.Mesh.from_file(filepath)
        triangles = stl.vectors.reshape(-1, 3, 3)
        vertices, inverse = np.unique(triangles.reshape(-1, 3), axis=0, return_inverse=True)
        indices = inverse.reshape(-1, 3)

        # smooth normals: sum the (area weighted) face normals of all triangles sharing a vertex
        normals = np.zeros_like(vertices, dtype=np.float32)
        np.add.at(normals, indices.ravel(), np.repeat(stl.normals, 3, axis=0))

        lengths = np.linalg.norm(normals, axis=1, keepdims=True)
        normals = np.divide(normals, lengths, out=np.zeros_like(normals), where=lengths > 0)

        # assign new arrays (the render system re-uploads when the vertex array changes)
        componentMesh.indices = indices.astype(np.uint32)
        componentMesh.normals = normals.astype(np.float32)
        componentMesh.vertices = vertices.astype(np.float32)

    def update(self, scene : dict[Entity, list[Component]]):
        for entity, components in scene.items():
            componentName = Utilities.try_get_component(components, ComponentName)
            componentFilepath = Utilities.try_get_component(components, ComponentFilepath)
            componentMesh = Utilities.try_get_component(components, ComponentMesh)

            if componentFilepath is None or componentName is None or componentMesh is None:
                continue

            if entity not in self.__filepaths:
                self.__filepaths[entity] = componentFilepath.filepath

            #UI
            imgui.set_next_window_size(
                (400, 250),
                imgui.Cond.FIRST_USE_EVER
            )

            imgui.begin(componentName.name)

            imgui.separator()
            imgui.text("Filepath:")

            changed, txt = imgui.input_text('##filepath', self.__filepaths[entity])
            if changed:
                self.__filepaths[entity] = txt

            if imgui.button("load"):
                #TODO COULD BE MOVED TO THREAD
                filepath = self.__filepaths[entity].strip().strip('"')  # allow pasted "Copy as path" values
                if not os.path.isfile(filepath):
                    self.__errors[entity] = f'File not found: {filepath}'
                else:
                    try:
                        self.load_stl(filepath, componentMesh)
                        componentFilepath.filepath = filepath
                        self.__errors[entity] = ''
                    except Exception as ex:
                        self.__errors[entity] = f'Could not load STL: {ex}'

            if self.__errors.get(entity):
                imgui.text_colored((0.95, 0.40, 0.35, 1.0), self.__errors[entity])
            elif componentMesh.indices is not None:
                imgui.text_disabled(f'{len(componentMesh.indices)} triangles, {len(componentMesh.vertices)} vertices')

            imgui.end()
