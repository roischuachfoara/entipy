
import glfw
import OpenGL.GL as gl

from slimgui import imgui
from slimgui.integrations.glfw import GlfwRenderer

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
        1000, 700, "Slimgui + OpenGL", None, None
    )

    if not window:
        glfw.terminate()
        raise RuntimeError("Could not create GLFW window")

    glfw.make_context_current(window)
    glfw.swap_interval(1)

    # Initialize ImGui
    imgui.create_context()
    renderer = GlfwRenderer(window)

    counter = 0

    # Main loop
    while not glfw.window_should_close(window):
        glfw.poll_events()

        # Clear OpenGL framebuffer
        gl.glClearColor(0.12, 0.12, 0.15, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        # Start ImGui frame
        renderer.new_frame()
        imgui.new_frame()

        # Build UI
        imgui.set_next_window_size(
            (400, 250),
            imgui.Cond.FIRST_USE_EVER
        )

        imgui.begin("My First Slimgui Application")

        imgui.text("Hello from Python 3.13!")
        imgui.separator()

        if imgui.button("Click me!"):
            counter += 1

        imgui.text(f"Button clicked: {counter} times")

        imgui.end()

        # Render UI
        imgui.render()
        renderer.render(imgui.get_draw_data())

        # Present frame
        glfw.swap_buffers(window)

    # Cleanup
    renderer.shutdown()
    imgui.destroy_context(None)

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()