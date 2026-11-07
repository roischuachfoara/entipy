from slimgui import imgui

from ..pattern.entity import Entity
from ..pattern.component import Component
from ..pattern.system import System
from ..components.component_name import ComponentName
from ..components.component_counter import ComponentCounter
from ..utilities.utilities import Utilities

class SystemIncrementUI(System):
    def update(self, scene : dict[Entity, list[Component]]):
        for entity, components in scene.items():
            componentName = Utilities.try_get_component(components, ComponentName)
            componentCounter = Utilities.try_get_component(components, ComponentCounter)

            if componentCounter is not None and componentName is not None:
                imgui.set_next_window_size(
                    (400, 250),
                    imgui.Cond.FIRST_USE_EVER
                )

                imgui.begin(componentName.name)

                imgui.separator()

                if imgui.button("Click to increment"):
                    componentCounter.cnt += 1
                
                imgui.text(f'{componentCounter.cnt}')
                imgui.end()