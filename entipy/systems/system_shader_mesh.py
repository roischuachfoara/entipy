from slimgui import imgui

from ..pattern.entity import Entity
from ..pattern.component import Component
from ..pattern.system import System
from ..components.component_name import ComponentName
from ..components.component_mesh import ComponentMesh
from ..utilities.utilities import Utilities
from ..rendering.shader import Shader
from ..rendering.gpu_mesh import GPUMesh

import os

class SystemShaderMesh(System):
    __shader : Shader = None
    __gpu_meshes: dict[Entity, GPUMesh] = {}

    def __init__(self):
        super().__init__()
        fpFragShader = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','shaders','basic.frag')
        fpVertShader = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','shaders','basic.vert')
        self.__shader = Shader.from_files(fpVertShader, fpFragShader)
        self.__gpu_meshes = {}

    def update(self, scene : dict[Entity, list[Component]]):
        self.__shader.use()
    
        for entity, components in scene.items():
            componentName = Utilities.try_get_component(components, ComponentName)
            componentMesh = Utilities.try_get_component(components, ComponentMesh)

            if componentMesh is None or componentName is None:
                continue

            if componentMesh.vertices is None or componentMesh.indices is None or componentMesh.normals is None:
                continue

            if entity not in self.__gpu_meshes:
                self.__gpu_meshes[entity] = GPUMesh(componentMesh)

            self.__gpu_meshes[entity].draw()

        self.__shader.use_done()