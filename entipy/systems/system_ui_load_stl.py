from slimgui import imgui

from ..pattern.entity import Entity
from ..pattern.component import Component
from ..pattern.system import System
from ..components.component_name import ComponentName
from ..components.component_filepath import ComponentFilepath
from ..utilities.utilities import Utilities

class SystemUILoadSTL(System):
    __filepath : str = ''

    def update(self, scene : dict[Entity, list[Component]]):
        for entity, components in scene.items():
            componentName = Utilities.try_get_component(components, ComponentName)
            componentFilepath = Utilities.try_get_component(components, ComponentFilepath)

            if componentFilepath is not None and componentName is not None:
                imgui.set_next_window_size(
                    (400, 250),
                    imgui.Cond.FIRST_USE_EVER
                )

                imgui.begin(componentName.name)

                imgui.separator()
                imgui.text("Filepath:")

                clicked, txt = imgui.input_text( label=' ', text=self.__filepath, flags=imgui.InputTextFlags.NONE)
                if clicked:
                    self.__filepath = txt
                if imgui.button("load"):
                    #TODO VALIDATE FILEPATH
                    componentFilepath.filepath = ''    
                
                imgui.end()