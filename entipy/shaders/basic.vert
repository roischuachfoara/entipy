#version 150

in vec3 a_position;
in vec3 a_normal;

uniform mat4 u_mvp;
uniform mat4 u_model_view;
uniform mat3 u_normal_matrix;

// both in view space, so the light can follow the camera
out vec3 v_normal;
out vec3 v_position;

void main()
{
    v_position = (u_model_view * vec4(a_position, 1.0)).xyz;
    v_normal = u_normal_matrix * a_normal;
    gl_Position = u_mvp * vec4(a_position, 1.0);
}
