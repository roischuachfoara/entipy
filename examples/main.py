import sys
import os

dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(dir))

from entipy import entity, component, scene, system, components, systems

def main():
    m = scene.Scene()
    for i in range (0,100):
        id = i + 1
        sid = 'obj ' + str(id)

        # create entity
        e = entity.Entity(id)
        m.add_entity(e)

        # add components
        m.add_component(e, components.component_name.ComponentName(sid))
        m.add_component(e, components.component_counter.ComponentCounter())
    
    # add systems
    m.add_system(systems.system_increment.SystemIncrement())
    
    while(True):
        m.update_entities()


if __name__ == "__main__":
    main()