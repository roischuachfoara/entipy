import OpenGL.GL as gl
import numpy as np

class Shader:
    @staticmethod
    def from_files(vertex_path, fragment_path):
        with open(vertex_path, "r", encoding="utf-8") as f:
            vertex_source = f.read()

        with open(fragment_path, "r", encoding="utf-8") as f:
            fragment_source = f.read()

        return Shader(vertex_source, fragment_source)

    def __init__(self, vertex_source, fragment_source):
        self.program = self.__create_program(
            vertex_source,
            fragment_source
        )

    def __compile_shader(self, source, shader_type):
        shader = gl.glCreateShader(shader_type)
        gl.glShaderSource(shader, source)
        gl.glCompileShader(shader)

        if not gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
            error = gl.glGetShaderInfoLog(shader)
            raise ValueError(error.decode())

        return shader

    def __create_program(self, vertex_source, fragment_source):
        vertex = self.__compile_shader(vertex_source, gl.GL_VERTEX_SHADER)
        fragment = self.__compile_shader(fragment_source, gl.GL_FRAGMENT_SHADER)

        program = gl.glCreateProgram()
        gl.glAttachShader(program, vertex)
        gl.glAttachShader(program, fragment)

        gl.glBindAttribLocation(program, 0, "a_position")
        gl.glBindAttribLocation(program, 1, "a_normal")

        gl.glLinkProgram(program)

        if not gl.glGetProgramiv(program, gl.GL_LINK_STATUS):
            error = gl.glGetProgramInfoLog(program)
            raise ValueError(error.decode())

        gl.glDeleteShader(vertex)
        gl.glDeleteShader(fragment)

        return program

    def use(self):
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glUseProgram(self.program)
    
    def use_done(self):
        gl.glUseProgram(0)

    def destroy(self):
        gl.glDeleteProgram(self.program)

    def get_uniform_location(self, name):
        return gl.glGetUniformLocation(self.program, name)

    # matrices are row-major numpy arrays (M @ v), hence transpose=GL_TRUE
    def set_mat4(self, name, matrix):
        location = self.get_uniform_location(name)

        gl.glUniformMatrix4fv(
            location,
            1,
            gl.GL_TRUE,
            np.asarray(matrix, dtype=np.float32)
        )

    def set_mat3(self, name, matrix):
        location = self.get_uniform_location(name)

        gl.glUniformMatrix3fv(
            location,
            1,
            gl.GL_TRUE,
            np.asarray(matrix, dtype=np.float32)
        )