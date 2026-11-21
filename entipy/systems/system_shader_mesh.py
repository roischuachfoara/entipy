from slimgui import imgui

from ..pattern.entity import Entity
from ..pattern.component import Component
from ..pattern.system import System
from ..components.component_name import ComponentName
from ..components.component_mesh import ComponentMesh
from ..components.component_transform import ComponentTransform
from ..utilities.utilities import Utilities
from ..rendering.shader import Shader
from ..rendering.gpu_mesh import GPUMesh

import os
import numpy as np
import OpenGL.GL as gl

class SystemShaderMesh(System):
    __ORBIT_SPEED = 0.008 
    __ZOOM_STEP = 0.85 
    __MAX_PITCH = np.radians(89.0)

    def __init__(self, fov_y_deg : float = 45.0):
        super().__init__()
        shader_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'shaders')
        self.__shader = Shader.from_files(os.path.join(shader_dir, 'basic.vert'), os.path.join(shader_dir, 'basic.frag'))
        self.__gpu_meshes : dict[Entity, GPUMesh] = {}
        self.__gpu_sources : dict[Entity, np.ndarray] = {}

        self.__fov_y = np.radians(fov_y_deg)
        self.__yaw = np.radians(-60.0)
        self.__pitch = np.radians(25.0)
        self.__distance = 5.0
        self.__target = np.zeros(3, dtype=np.float32)
        self.__scene_center = np.zeros(3, dtype=np.float32)
        self.__scene_radius = 1.0

    def __model_matrix(self, componentTransform : ComponentTransform):
        T = np.eye(4, dtype=np.float32)
        T[:3, 3] = [componentTransform.position[0,0], componentTransform.position[0,1], componentTransform.position[0,2]]
        cx, sxr = np.cos(componentTransform.rotation[0,0]), np.sin(componentTransform.rotation[0,0])
        cy, syr = np.cos(componentTransform.rotation[0,1]), np.sin(componentTransform.rotation[0,1])
        cz, szr = np.cos(componentTransform.rotation[0,2]), np.sin(componentTransform.rotation[0,2])

        Rx = np.array([
            [1, 0, 0, 0],
            [0, cx, -sxr, 0],
            [0, sxr, cx, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        Ry = np.array([
            [cy, 0, syr, 0],
            [0, 1, 0, 0],
            [-syr, 0, cy, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        Rz = np.array([
            [cz, -szr, 0, 0],
            [szr, cz, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        S = np.diag([componentTransform.scale[0,0], componentTransform.scale[0,1], componentTransform.scale[0,2], 1]).astype(np.float32)

        return T @ Rz @ Ry @ Rx @ S

    @staticmethod
    def __look_at(eye, target, up):
        f = target - eye
        f = f / np.linalg.norm(f)
        s = np.cross(f, up)
        s = s / np.linalg.norm(s)
        u = np.cross(s, f)

        V = np.eye(4, dtype=np.float32)
        V[0, :3], V[1, :3], V[2, :3] = s, u, -f
        V[:3, 3] = [-np.dot(s, eye), -np.dot(u, eye), np.dot(f, eye)]
        return V

    @staticmethod
    def __perspective(fov_y, aspect, near, far):
        f = 1.0 / np.tan(fov_y * 0.5)
        P = np.zeros((4, 4), dtype=np.float32)
        P[0, 0] = f / aspect
        P[1, 1] = f
        P[2, 2] = (far + near) / (near - far)
        P[2, 3] = 2.0 * far * near / (near - far)
        P[3, 2] = -1.0
        return P

    @staticmethod
    def __world_bounds(vertices, model):
        lo, hi = vertices.min(axis=0), vertices.max(axis=0)
        corners = np.array([[x, y, z, 1.0] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])], dtype=np.float32)
        world = (model @ corners.T).T[:, :3]
        return world.min(axis=0), world.max(axis=0)

    def __frame(self, drawables, aspect):
        bounds = [self.__world_bounds(mesh.vertices, model) for _, mesh, model in drawables]
        lo = np.min([b[0] for b in bounds], axis=0)
        hi = np.max([b[1] for b in bounds], axis=0)

        self.__scene_center = (lo + hi) * 0.5
        self.__scene_radius = max(float(np.linalg.norm(hi - lo)) * 0.5, 1e-6)
        self.__target = self.__scene_center.copy()

        fov_x = 2.0 * np.arctan(np.tan(self.__fov_y * 0.5) * aspect)
        fov = min(self.__fov_y, fov_x)
        self.__distance = self.__scene_radius / np.sin(fov * 0.5) * 1.05

    def __eye_axes(self):
        cp, sp = np.cos(self.__pitch), np.sin(self.__pitch)
        cy, sy = np.cos(self.__yaw), np.sin(self.__yaw)
        backward = np.array([cp * cy, cp * sy, sp], dtype=np.float32)
        right = np.array([-sy, cy, 0.0], dtype=np.float32)
        up = np.cross(backward, right)
        return backward, right, up

    def __handle_input(self):
        io = imgui.get_io()
        if io.want_capture_mouse:
            return False

        dx, dy = io.mouse_delta
        if imgui.is_mouse_down(imgui.MouseButton.LEFT):
            self.__yaw -= dx * self.__ORBIT_SPEED
            self.__pitch = float(np.clip(self.__pitch + dy * self.__ORBIT_SPEED, -self.__MAX_PITCH, self.__MAX_PITCH))

        if imgui.is_mouse_down(imgui.MouseButton.RIGHT) or imgui.is_mouse_down(imgui.MouseButton.MIDDLE):
            _, right, up = self.__eye_axes()
            height = max(io.display_size[1], 1.0)
            world_per_pixel = 2.0 * self.__distance * np.tan(self.__fov_y * 0.5) / height
            self.__target = self.__target + (-dx * right + dy * up) * world_per_pixel

        if io.mouse_wheel != 0.0:
            self.__distance = max(self.__distance * self.__ZOOM_STEP ** io.mouse_wheel, self.__scene_radius * 1e-3)

        return imgui.is_mouse_double_clicked(imgui.MouseButton.LEFT)

    def update(self, scene : dict[Entity, list[Component]]):
        reframe = self.__handle_input()

        drawables = []
        for entity, components in scene.items():
            componentName = Utilities.try_get_component(components, ComponentName)
            componentMesh = Utilities.try_get_component(components, ComponentMesh)
            componentTransform = Utilities.try_get_component(components, ComponentTransform)

            if componentMesh is None or componentName is None or componentTransform is None:
                continue

            if componentMesh.vertices is None or componentMesh.indices is None or componentMesh.normals is None:
                continue

            if self.__gpu_sources.get(entity) is not componentMesh.vertices:
                if entity in self.__gpu_meshes:
                    self.__gpu_meshes[entity].destroy()
                self.__gpu_meshes[entity] = GPUMesh(componentMesh)
                self.__gpu_sources[entity] = componentMesh.vertices
                reframe = True

            drawables.append((entity, componentMesh, self.__model_matrix(componentTransform)))

        live = {entity for entity, _, _ in drawables}
        for entity in [e for e in self.__gpu_meshes if e not in live]:
            self.__gpu_meshes.pop(entity).destroy()
            self.__gpu_sources.pop(entity, None)

        if not drawables:
            return

        _, _, width, height = gl.glGetIntegerv(gl.GL_VIEWPORT)
        if width <= 0 or height <= 0:  # minimized
            return
        aspect = width / height

        if reframe:
            self.__frame(drawables, aspect)

        backward, _, _ = self.__eye_axes()
        eye = self.__target + backward * self.__distance
        view = self.__look_at(eye, self.__target, np.array([0.0, 0.0, 1.0], dtype=np.float32))

        center_depth = float(np.dot(eye - self.__scene_center, backward))
        far = max(center_depth + self.__scene_radius * 1.1, 1e-3)
        near = max(center_depth - self.__scene_radius * 1.1, far * 1e-4)
        projection = self.__perspective(self.__fov_y, aspect, near, far)

        self.__shader.use()

        for entity, _, model in drawables:
            model_view = view @ model
            self.__shader.set_mat4("u_mvp", projection @ model_view)
            self.__shader.set_mat4("u_model_view", model_view)
            self.__shader.set_mat3("u_normal_matrix", np.linalg.inv(model_view[:3, :3]).T)
            self.__gpu_meshes[entity].draw()

        self.__shader.use_done()
