import sys
import os

dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(dir))

from entipy import entity, component, scene, system, components, systems

def main():
    # create scene
    m = scene.Scene()

    #add entities
    for i in range (0,100):
        id = i + 1
        sid = 'obj ' + str(id)
        e = entity.Entity(id)
        m.add_entity(e)

        # add components
        m.add_component(e, components.component_name.ComponentName(sid))
        m.add_component(e, components.component_counter.ComponentCounter())
    
    # add systems
    m.add_system(systems.system_increment.SystemIncrement())
    
    #main loop
    while(True):
        m.update_systems()

if __name__ == "__main__":
    main()