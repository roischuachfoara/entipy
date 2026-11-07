import glfw
import OpenGL.GL as gl

from slimgui import imgui
from slimgui.integrations.glfw import GlfwRenderer

import sys
import os

dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(dir))

from entipy import entity, component, scene, system, components, systems

def main():
    # Initialize GLFW
    if not glfw.init():
        raise RuntimeError("Could not initialize GLFW")

    # macOS requires forward-compatible OpenGL
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)

    # Create window
    window = glfw.create_window(
        1000, 700, "Python ECS Example", None, None
    )

    if not window:
        glfw.terminate()
        raise RuntimeError("Could not create GLFW window")

    glfw.make_context_current(window)
    glfw.swap_interval(1)

    # Initialize ImGui
    imgui.create_context()
    renderer = GlfwRenderer(window)

    # create scene
    m = scene.Scene()

    #add entities
    entitiesCount = 10
    for i in range (0,entitiesCount):
        id = i + 1
        sid = 'obj ' + str(id)
        e = entity.Entity(id)
        m.add_entity(e)

        # add components
        m.add_component(e, components.component_name.ComponentName(sid))
        m.add_component(e, components.component_counter.ComponentCounter())
    
    # add systems
    m.add_system(systems.system_inctement_ui.SystemIncrementUI())

    # Main loop
    while not glfw.window_should_close(window):
        glfw.poll_events()

        gl.glClearColor(0.12, 0.12, 0.15, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        renderer.new_frame()
        imgui.new_frame()

        # Update systems
        m.update_systems()

        imgui.render()
        renderer.render(imgui.get_draw_data())

        glfw.swap_buffers(window)

    # Cleanup
    renderer.shutdown()
    imgui.destroy_context(None)

    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()