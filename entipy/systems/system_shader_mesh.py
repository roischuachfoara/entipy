from slimgui import imgui

from ..pattern.entity import Entity
from ..pattern.component import Component
from ..pattern.system import System
from ..components.component_name import ComponentName
from ..components.component_mesh import ComponentMesh
from ..components.component_transform import ComponentTransform
from ..utilities.utilities import Utilities
from ..rendering.shader import Shader
from ..rendering.gpu_mesh import GPUMesh

import os
import numpy as np

class SystemShaderMesh(System):
    __shader : Shader = None
    __gpu_meshes: dict[Entity, GPUMesh] = {}

    def __init__(self):
        super().__init__()
        fpFragShader = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','shaders','basic.frag')
        fpVertShader = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','shaders','basic.vert')
        self.__shader = Shader.from_files(fpVertShader, fpFragShader)
        self.__gpu_meshes = {}
        self.__view = np.eye(4, dtype=np.float32)
        self.__projection = np.eye(4, dtype=np.float32)

    def __model_matrix(self, componentTransform : ComponentTransform):
        # Translation
        T = np.eye(4, dtype=np.float32)
        T[:3, 3] = [componentTransform.position[0,0], componentTransform.position[0,1], componentTransform.position[0,2]]

        # Rotation
        cx, sxr = np.cos(componentTransform.rotation[0,0]), np.sin(componentTransform.rotation[0,0])
        cy, syr = np.cos(componentTransform.rotation[0,1]), np.sin(componentTransform.rotation[0,1])
        cz, szr = np.cos(componentTransform.rotation[0,2]), np.sin(componentTransform.rotation[0,2])

        Rx = np.array([
            [1, 0, 0, 0],
            [0, cx, -sxr, 0],
            [0, sxr, cx, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        Ry = np.array([
            [cy, 0, syr, 0],
            [0, 1, 0, 0],
            [-syr, 0, cy, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        Rz = np.array([
            [cz, -szr, 0, 0],
            [szr, cz, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        # Scale
        S = np.diag([componentTransform.scale[0,0], componentTransform.scale[0,1], componentTransform.scale[0,2], 1]).astype(np.float32)

        return T @ Rz @ Ry @ Rx @ S

    def update(self, scene : dict[Entity, list[Component]]):
        self.__shader.use()
    
        for entity, components in scene.items():
            componentName = Utilities.try_get_component(components, ComponentName)
            componentMesh = Utilities.try_get_component(components, ComponentMesh)
            componentTransform = Utilities.try_get_component(components, ComponentTransform)

            if componentMesh is None or componentName is None or componentTransform is None:
                continue

            if componentMesh.vertices is None or componentMesh.indices is None or componentMesh.normals is None:
                continue

            if entity not in self.__gpu_meshes:
                self.__gpu_meshes[entity] = GPUMesh(componentMesh)

            model = self.__model_matrix(componentTransform)
            mvp = self.__projection @ self.__view @ model

            self.__shader.set_mat4("u_model", model)
            self.__shader.set_mat4("u_mvp", mvp)

            self.__gpu_meshes[entity].draw()

        self.__shader.use_done()