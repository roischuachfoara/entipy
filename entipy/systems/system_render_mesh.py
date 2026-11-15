from slimgui import imgui

from ..pattern.entity import Entity
from ..pattern.component import Component
from ..pattern.system import System
from ..components.component_name import ComponentName
from ..components.component_mesh import ComponentMesh
from ..utilities.utilities import Utilities

class SystemRenderMesh(System):
    __filepath : str = ''

    def update(self, scene : dict[Entity, list[Component]]):
        for entity, components in scene.items():
            componentName = Utilities.try_get_component(components, ComponentName)
            componentMesh = Utilities.try_get_component(components, ComponentMesh)

            if componentMesh is not None and componentName is not None:
                pass