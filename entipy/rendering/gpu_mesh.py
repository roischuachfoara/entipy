from ..components.component_mesh import ComponentMesh

import OpenGL.GL as gl
import numpy as np
import ctypes

class GPUMesh:

    def __init__(self, mesh : ComponentMesh):
        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)
        self.ebo = gl.glGenBuffers(1)

        # Combine positions and normals
        vertices = np.concatenate(
            (mesh.vertices, mesh.normals),
            axis=1
        ).astype(np.float32)

        indices = mesh.indices.flatten().astype(np.uint32)

        self.index_count = len(indices)

        # Bind VAO
        gl.glBindVertexArray(self.vao)

        # Upload vertices
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            vertices.nbytes,
            vertices,
            gl.GL_STATIC_DRAW
        )

        # Upload indices
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        gl.glBufferData(
            gl.GL_ELEMENT_ARRAY_BUFFER,
            indices.nbytes,
            indices,
            gl.GL_STATIC_DRAW
        )

        stride = 6 * 4  # 6 floats * 4 bytes

        # Position (location 0)
        gl.glVertexAttribPointer(
            0, 3, gl.GL_FLOAT, gl.GL_FALSE,
            stride, ctypes.c_void_p(0)
        )
        gl.glEnableVertexAttribArray(0)

        # Normal (location 1)
        gl.glVertexAttribPointer(
            1, 3, gl.GL_FLOAT, gl.GL_FALSE,
            stride, ctypes.c_void_p(12)
        )
        gl.glEnableVertexAttribArray(1)

        gl.glBindVertexArray(0)

    def draw(self):
        gl.glBindVertexArray(self.vao)

        gl.glDrawElements(
            gl.GL_TRIANGLES,
            self.index_count,
            gl.GL_UNSIGNED_INT,
            None
        )

        gl.glBindVertexArray(0)

    def destroy(self):
        gl.glDeleteVertexArrays(1, [self.vao])
        gl.glDeleteBuffers(1, [self.vbo])
        gl.glDeleteBuffers(1, [self.ebo])