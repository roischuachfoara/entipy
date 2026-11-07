from ..pattern.entity import Entity
from ..pattern.component import Component
from ..pattern.system import System
from ..components.component_counter import ComponentCounter
from ..components.component_name import ComponentName
from ..utilities.utilities import Utilities

class SystemIncrement(System):
    def update(self, entity : Entity,  components : list[Component]):
        componentName = Utilities.try_get_component(components, ComponentName)
        componentCounter = Utilities.try_get_component(components, ComponentCounter)

        if componentCounter is not None and componentName is not None:
            componentCounter.cnt += 1
            print(f'Entity: {componentName.name} Counter {componentCounter.cnt}')