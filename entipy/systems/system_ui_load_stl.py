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
    __filepaths : dict[Entity, str] = {}

    def update(self, scene : dict[Entity, list[Component]]):
        for entity, components in scene.items():
            componentName = Utilities.try_get_component(components, ComponentName)
            componentFilepath = Utilities.try_get_component(components, ComponentFilepath)
            componentMesh = Utilities.try_get_component(components, ComponentMesh)
            
            if entity not in self.__filepaths:
                self.__filepaths[entity] = str()

            if componentFilepath is not None and componentName is not None and componentMesh is not None:
                #UI
                imgui.set_next_window_size(
                    (400, 250),
                    imgui.Cond.FIRST_USE_EVER
                )

                imgui.begin(componentName.name)

                imgui.separator()
                imgui.text("Filepath:")

                clicked, txt = imgui.input_text( label=' ', text=self.__filepaths[entity], flags=imgui.InputTextFlags.NONE)
                if clicked:
                    if os.path.exists(txt):
                        self.__filepaths[entity] = txt
                    else:
                        self.__filepaths[entity] = str()
                        
                if imgui.button("load") and len(self.__filepaths[entity]) > 0:
                    #load stl and store in mesh component
                    componentFilepath.filepath = self.__filepaths[entity]

                    #TODO COULD BE MOVED TO THREAD
                    stl = stl_mesh.Mesh.from_file(self.__filepaths[entity])
                    triangles = stl.vectors.reshape(-1, 3, 3)
                    vertices, inverse = np.unique(triangles.reshape(-1, 3), axis=0, return_inverse=True)
                    indices = inverse.reshape(-1, 3)
                    normals = np.zeros_like(vertices, dtype=np.float32)

                    for triangle, normal in zip(indices, stl.normals):
                        for vertex_index in triangle:
                            normals[vertex_index] += normal

                    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
                    normals = np.divide(normals, lengths, out=np.zeros_like(normals), where=lengths > 0)

                    componentMesh.vertices = vertices.astype(np.float32)
                    componentMesh.indices = indices.astype(np.uint32)
                    componentMesh.normals = normals.astype(np.float32)

                imgui.end()