
import sys
import math
import ctypes

import glfw
import numpy as np
import OpenGL.GL as gl

from stl import mesh
from slimgui import imgui
from slimgui.integrations.glfw import GlfwRenderer

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

BACKGROUND = (0.12, 0.13, 0.16, 1.0)


# ---------------------------------------------------------
# Matrix utilities
# ---------------------------------------------------------

def perspective(fov, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov) / 2.0)

    return np.array([
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / (near - far),
         (2 * far * near) / (near - far)],
        [0, 0, -1, 0]
    ], dtype=np.float32)


def look_at(eye, target, up):
    forward = target - eye
    forward /= np.linalg.norm(forward)

    right = np.cross(forward, up)
    right /= np.linalg.norm(right)

    up = np.cross(right, forward)

    return np.array([
        [right[0], right[1], right[2], -np.dot(right, eye)],
        [up[0], up[1], up[2], -np.dot(up, eye)],
        [-forward[0], -forward[1], -forward[2],
         np.dot(forward, eye)],
        [0, 0, 0, 1]
    ], dtype=np.float32)


def rotation_matrix(angle_x, angle_y):
    x = math.radians(angle_x)
    y = math.radians(angle_y)

    rx = np.array([
        [1, 0, 0, 0],
        [0, math.cos(x), -math.sin(x), 0],
        [0, math.sin(x), math.cos(x), 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

    ry = np.array([
        [math.cos(y), 0, math.sin(y), 0],
        [0, 1, 0, 0],
        [-math.sin(y), 0, math.cos(y), 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

    return ry @ rx


# ---------------------------------------------------------
# OpenGL shaders
# ---------------------------------------------------------

VERTEX_SHADER = """
#version 150

in vec3 a_position;
in vec3 a_normal;

uniform mat4 u_mvp;
uniform mat4 u_model;

out vec3 v_normal;

void main()
{
    gl_Position = u_mvp * vec4(a_position, 1.0);
    v_normal = mat3(u_model) * a_normal;
}
"""

FRAGMENT_SHADER = """
#version 150

in vec3 v_normal;

out vec4 frag_color;

void main()
{
    vec3 normal = normalize(v_normal);

    vec3 light_direction = normalize(
        vec3(0.5, 0.8, 1.0)
    );

    float diffuse = max(
        dot(normal, light_direction),
        0.0
    );

    float ambient = 0.25;

    vec3 base_color = vec3(0.25, 0.65, 0.95);

    vec3 color = base_color * (ambient + diffuse * 0.75);

    frag_color = vec4(color, 1.0);
}
"""


def compile_shader(source, shader_type):
    shader = gl.glCreateShader(shader_type)

    gl.glShaderSource(shader, source)
    gl.glCompileShader(shader)

    if not gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
        error = gl.glGetShaderInfoLog(shader)
        raise RuntimeError(error.decode())

    return shader


def create_shader_program():
    vertex = compile_shader(
        VERTEX_SHADER,
        gl.GL_VERTEX_SHADER
    )

    fragment = compile_shader(
        FRAGMENT_SHADER,
        gl.GL_FRAGMENT_SHADER
    )

    program = gl.glCreateProgram()

    gl.glAttachShader(program, vertex)
    gl.glAttachShader(program, fragment)

    gl.glBindAttribLocation(program, 0, "a_position")
    gl.glBindAttribLocation(program, 1, "a_normal")

    gl.glLinkProgram(program)

    if not gl.glGetProgramiv(program, gl.GL_LINK_STATUS):
        error = gl.glGetProgramInfoLog(program)
        raise RuntimeError(error.decode())

    gl.glDeleteShader(vertex)
    gl.glDeleteShader(fragment)

    return program


# ---------------------------------------------------------
# STL loader
# ---------------------------------------------------------

class STLModel:

    def __init__(self):
        self.vao = None
        self.vbo = None
        self.vertex_count = 0
        self.filename = ""
        self.dimensions = np.zeros(3)
        self.triangle_count = 0

    def load(self, filename):

        print(f"Loading STL: {filename}")

        stl_data = mesh.Mesh.from_file(filename)

        triangles = stl_data.vectors.astype(np.float32)

        # Calculate the center of the model.
        all_vertices = triangles.reshape(-1, 3)

        minimum = all_vertices.min(axis=0)
        maximum = all_vertices.max(axis=0)

        center = (minimum + maximum) / 2.0

        self.dimensions = maximum - minimum

        # Center model at the origin.
        triangles -= center

        # Normalize model size.
        max_dimension = float(np.max(self.dimensions))

        if max_dimension > 0:
            triangles /= max_dimension

        # Calculate face normals.
        edge1 = triangles[:, 1] - triangles[:, 0]
        edge2 = triangles[:, 2] - triangles[:, 0]

        normals = np.cross(edge1, edge2)

        lengths = np.linalg.norm(
            normals,
            axis=1,
            keepdims=True
        )

        normals = np.divide(
            normals,
            lengths,
            out=np.zeros_like(normals),
            where=lengths > 0
        )

        # Repeat each face normal for its three vertices.
        normals = np.repeat(normals[:, None, :], 3, axis=1)

        # Interleave positions and normals.
        vertices = np.concatenate(
            [triangles, normals],
            axis=2
        ).astype(np.float32)

        vertices = vertices.reshape(-1, 6)

        self.vertex_count = len(vertices)
        self.triangle_count = len(triangles)
        self.filename = filename

        # Upload mesh to GPU.
        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.vao)

        gl.glBindBuffer(
            gl.GL_ARRAY_BUFFER,
            self.vbo
        )

        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            vertices.nbytes,
            vertices,
            gl.GL_STATIC_DRAW
        )

        # Position attribute.
        gl.glEnableVertexAttribArray(0)

        gl.glVertexAttribPointer(
            0,
            3,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            24,
            ctypes.c_void_p(0)
        )

        # Normal attribute.
        gl.glEnableVertexAttribArray(1)

        gl.glVertexAttribPointer(
            1,
            3,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            24,
            ctypes.c_void_p(12)
        )

        gl.glBindVertexArray(0)

        print("STL loaded successfully!")
        print(f"Triangles: {self.triangle_count}")
        print(f"Dimensions: {self.dimensions}")

    def draw(self):

        if self.vao is None:
            return

        gl.glBindVertexArray(self.vao)

        gl.glDrawArrays(
            gl.GL_TRIANGLES,
            0,
            self.vertex_count
        )

        gl.glBindVertexArray(0)

    def destroy(self):

        if self.vbo is not None:
            gl.glDeleteBuffers(1, [self.vbo])

        if self.vao is not None:
            gl.glDeleteVertexArrays(1, [self.vao])


# ---------------------------------------------------------
# Application
# ---------------------------------------------------------

class STLViewer:

    def __init__(self):

        self.model = STLModel()

        self.angle_x = 20.0
        self.angle_y = 30.0

        self.zoom = 2.5

        self.wireframe = False

        self.dragging = False
        self.last_mouse = None

        self.shader = None

    def initialize(self):

        if not glfw.init():
            raise RuntimeError("Could not initialize GLFW")

        # macOS requires a forward-compatible core profile.
        glfw.window_hint(
            glfw.CONTEXT_VERSION_MAJOR, 3
        )

        glfw.window_hint(
            glfw.CONTEXT_VERSION_MINOR, 2
        )

        glfw.window_hint(
            glfw.OPENGL_PROFILE,
            glfw.OPENGL_CORE_PROFILE
        )

        glfw.window_hint(
            glfw.OPENGL_FORWARD_COMPAT,
            glfw.TRUE
        )

        window = glfw.create_window(
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            "Python STL Viewer",
            None,
            None
        )

        if not window:
            glfw.terminate()
            raise RuntimeError("Could not create GLFW window")

        self.window = window

        glfw.make_context_current(window)
        glfw.swap_interval(1)

        # OpenGL initialization.
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)

        gl.glClearColor(*BACKGROUND)

        self.shader = create_shader_program()

        # Initialize SlimGUI.
        imgui.create_context()

        self.gui_renderer = GlfwRenderer(window)

        print("OpenGL:", gl.glGetString(gl.GL_VERSION).decode())

    def load_model(self, filename):

        self.model.load(filename)

    def render_model(self, width, height):

        if self.model.vao is None:
            return

        aspect = width / max(height, 1)

        projection = perspective(
            45.0,
            aspect,
            0.01,
            100.0
        )

        view = look_at(
            np.array([0, 0, self.zoom], dtype=np.float32),
            np.array([0, 0, 0], dtype=np.float32),
            np.array([0, 1, 0], dtype=np.float32)
        )

        model_matrix = rotation_matrix(
            self.angle_x,
            self.angle_y
        )

        mvp = projection @ view @ model_matrix

        gl.glUseProgram(self.shader)

        # NumPy matrices are row-major. Transpose before upload.
        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self.shader, "u_mvp"),
            1,
            gl.GL_FALSE,
            np.ascontiguousarray(mvp.T)
        )

        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self.shader, "u_model"),
            1,
            gl.GL_FALSE,
            np.ascontiguousarray(model_matrix.T)
        )

        if self.wireframe:
            gl.glPolygonMode(
                gl.GL_FRONT_AND_BACK,
                gl.GL_LINE
            )
        else:
            gl.glPolygonMode(
                gl.GL_FRONT_AND_BACK,
                gl.GL_FILL
            )

        self.model.draw()

        gl.glPolygonMode(
            gl.GL_FRONT_AND_BACK,
            gl.GL_FILL
        )

        gl.glUseProgram(0)

    # -----------------------------------------------------
    # GUI
    # -----------------------------------------------------

    def render_gui(self):

        imgui.set_next_window_size(
            (300, 300),
            imgui.Cond.FIRST_USE_EVER
        )

        imgui.begin("STL Viewer Controls")

        imgui.text("Model information")
        imgui.separator()

        if self.model.vao is not None:

            imgui.text(f"File: {self.model.filename}")

            imgui.text(
                f"Triangles: {self.model.triangle_count:,}"
            )

            dims = self.model.dimensions

            imgui.text(
                f"Size: {dims[0]:.2f}, "
                f"{dims[1]:.2f}, {dims[2]:.2f}"
            )

        else:
            imgui.text("No STL model loaded")

        imgui.separator()

        if imgui.button("Reset camera"):
            self.angle_x = 20.0
            self.angle_y = 30.0
            self.zoom = 2.5

        if imgui.button("Toggle wireframe"):
            self.wireframe = not self.wireframe

        imgui.separator()

        imgui.text("Mouse: drag to rotate")
        imgui.text("Scroll: zoom")
        imgui.text("ESC: exit")

        imgui.end()

    # -----------------------------------------------------
    # Mouse controls
    # -----------------------------------------------------

    def handle_mouse(self):

        io = imgui.get_io()

        x, y = glfw.get_cursor_pos(self.window)

        pressed = glfw.get_mouse_button(
            self.window,
            glfw.MOUSE_BUTTON_LEFT
        ) == glfw.PRESS

        if pressed and not io.want_capture_mouse:

            if self.last_mouse is not None:

                dx = x - self.last_mouse[0]
                dy = y - self.last_mouse[1]

                self.angle_y += dx * 0.5
                self.angle_x += dy * 0.5

            self.last_mouse = (x, y)

        else:
            self.last_mouse = None

    def handle_scroll(self, window, xoffset, yoffset):

        io = imgui.get_io()

        if not io.want_capture_mouse:
            self.zoom -= yoffset * 0.15
            self.zoom = max(0.5, min(self.zoom, 20.0))

    # -----------------------------------------------------
    # Main loop
    # -----------------------------------------------------

    def run(self, filename=None):

        self.initialize()

        if filename is not None:
            self.load_model(filename)

        glfw.set_scroll_callback(
            self.window,
            self.handle_scroll
        )

        while not glfw.window_should_close(self.window):

            glfw.poll_events()

            if glfw.get_key(
                self.window,
                glfw.KEY_ESCAPE
            ) == glfw.PRESS:
                break

            self.handle_mouse()

            # Get framebuffer size (important for Retina Macs).
            width, height = glfw.get_framebuffer_size(
                self.window
            )

            gl.glViewport(0, 0, width, height)

            gl.glClear(
                gl.GL_COLOR_BUFFER_BIT |
                gl.GL_DEPTH_BUFFER_BIT
            )

            # Render 3D scene.
            self.render_model(width, height)

            # Render GUI.
            self.gui_renderer.new_frame()
            imgui.new_frame()

            self.render_gui()

            imgui.render()

            self.gui_renderer.render(
                imgui.get_draw_data()
            )

            glfw.swap_buffers(self.window)

        self.cleanup()

    def cleanup(self):

        self.model.destroy()

        self.gui_renderer.shutdown()

        imgui.destroy_context(None)

        glfw.destroy_window(self.window)
        glfw.terminate()


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":

    viewer = STLViewer()

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = (
            '/Users/martinwalchshoferwalchshofer/'
            'Documents/GitHub/entipy/testdata/stl/Teapot.stl'
        )

    viewer.run(filename)