from .entity import Entity
from .component import Component
from .system import System

class Scene:
    def __init__(self) -> None:
        self.m_EC : dict[Entity, list[Component]] = {}
        self.m_Systems : list[System] = []

    def add_entity(self, entity : Entity) -> None:
        if not isinstance(entity, Entity):
            raise ValueError(f'Entity must be type of {str(Entity)}.')
        if entity in self.m_EC:
            raise ValueError(f'Entity with id {entity.id} already exists.')
        self.m_EC[entity] = []
    
    def remove_entity(self, entity : Entity) -> None:
        if not isinstance(entity, Entity):
            raise ValueError(f'Entity must be type of {str(Entity)}.')
        if entity not in self.m_EC:
            raise ValueError(f'Entity with id {entity.id} does not exists.')
        self.m_EC.pop(entity)

    def add_component(self, entity : Entity, component : Component) -> None:
        if not isinstance(entity, Entity):
            raise ValueError(f'Entity must be type of {str(Entity)}.')
        if not isinstance(component, Component):
            raise ValueError(f'Component must be type of {str(Component)}.')
        if entity not in self.m_EC:
            raise ValueError(f'Entity with id {entity.id} does not exists.')
        if component in self.m_EC[entity]:
            raise ValueError(f'Component is already assigned to entity.')
        self.m_EC[entity].append(component)

    def remove_component(self, entity : Entity, componenet : Component) -> None:
        raise NotImplementedError('Not implemented yet.')

    def add_system(self, system : System):
        if not isinstance(system, System):
            raise ValueError(f'System must be type of {str(System)}.')
        if system in self.m_Systems:
            raise ValueError(f'System already exists.')
        self.m_Systems.append(system)

    def remove_system(self, system : System):
        raise NotImplementedError('Not implemented yet.')

    def update_systems(self):
        for e in self.m_EC:
            for s in self.m_Systems:
                s.update(e, self.m_EC[e])