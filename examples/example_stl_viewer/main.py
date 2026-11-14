import glfw
import OpenGL.GL as gl

from slimgui import imgui
from slimgui.integrations.glfw import GlfwRenderer

import sys
import os

dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(dir))
sys.path.append(os.path.join(os.path.dirname(dir),'..'))

from entipy import entity, component, scene, system, components, systems

def apply_minimal_dark_theme():
    imgui.style_colors_dark()

    style = imgui.get_style()

    # Spacing
    style.window_padding = (16.0, 16.0)
    style.frame_padding = (10.0, 7.0)
    style.item_spacing = (10.0, 10.0)
    style.item_inner_spacing = (8.0, 6.0)
    style.indent_spacing = 20.0
    style.scrollbar_size = 12.0
    style.grab_min_size = 8.0

    # Rounding
    style.window_rounding = 8.0
    style.child_rounding = 6.0
    style.frame_rounding = 5.0
    style.popup_rounding = 6.0
    style.scrollbar_rounding = 6.0
    style.grab_rounding = 5.0
    style.tab_rounding = 5.0

    # Borders
    style.window_border_size = 0.0
    style.child_border_size = 1.0
    style.frame_border_size = 0.0
    style.popup_border_size = 1.0

    # Colors
    colors = style.colors

    colors[imgui.Col.TEXT] = (0.90, 0.91, 0.93, 1.0)
    colors[imgui.Col.TEXT_DISABLED] = (0.48, 0.50, 0.54, 1.0)

    colors[imgui.Col.WINDOW_BG] = (0.075, 0.080, 0.095, 1.0)
    colors[imgui.Col.CHILD_BG] = (0.095, 0.100, 0.115, 1.0)
    colors[imgui.Col.POPUP_BG] = (0.105, 0.110, 0.125, 1.0)

    colors[imgui.Col.BORDER] = (0.19, 0.20, 0.22, 1.0)

    colors[imgui.Col.FRAME_BG] = (0.14, 0.15, 0.17, 1.0)
    colors[imgui.Col.FRAME_BG_HOVERED] = (0.19, 0.21, 0.24, 1.0)
    colors[imgui.Col.FRAME_BG_ACTIVE] = (0.22, 0.24, 0.28, 1.0)

    colors[imgui.Col.BUTTON] = (0.16, 0.17, 0.20, 1.0)
    colors[imgui.Col.BUTTON_HOVERED] = (0.22, 0.24, 0.28, 1.0)
    colors[imgui.Col.BUTTON_ACTIVE] = (0.25, 0.28, 0.33, 1.0)

    colors[imgui.Col.HEADER] = (0.16, 0.20, 0.27, 1.0)
    colors[imgui.Col.HEADER_HOVERED] = (0.20, 0.25, 0.33, 1.0)
    colors[imgui.Col.HEADER_ACTIVE] = (0.23, 0.30, 0.40, 1.0)

    colors[imgui.Col.CHECK_MARK] = (0.30, 0.57, 0.95, 1.0)
    colors[imgui.Col.SLIDER_GRAB] = (0.30, 0.57, 0.95, 1.0)
    colors[imgui.Col.SLIDER_GRAB_ACTIVE] = (0.40, 0.65, 1.0, 1.0)

    colors[imgui.Col.SEPARATOR] = (0.19, 0.20, 0.22, 1.0)

    colors[imgui.Col.TITLE_BG] = (0.075, 0.080, 0.095, 1.0)
    colors[imgui.Col.TITLE_BG_ACTIVE] = (0.075, 0.080, 0.095, 1.0)

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
    window = glfw.create_window(1000, 700, "Python STL Viewer", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Could not create GLFW window")
    glfw.make_context_current(window)
    glfw.swap_interval(1)

    # Initialize ImGui
    imgui.create_context()
    apply_minimal_dark_theme()

    renderer = GlfwRenderer(window)

    # create scene
    m = scene.Scene()

    #add entities
    id = 0
    sid = f'loader {id}'
    e = entity.Entity(id)
    m.add_entity(e)
    m.add_component(e, components.component_name.ComponentName(sid))
    m.add_component(e, components.component_filepath.ComponentFilepath())
    
    # add systems
    m.add_system(systems.system_ui_set_filepath.SystemUISetFilepath())

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