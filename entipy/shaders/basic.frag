#version 150

in vec3 v_normal;
in vec3 v_position;
out vec4 frag_color;

void main()
{
    vec3 normal = normalize(v_normal);
    // light the side that faces the camera, also for open meshes / flipped triangles
    if (!gl_FrontFacing)
        normal = -normal;

    // head light slightly above-left of the camera: follows the orbit, never lights the back side only
    vec3 light_direction = normalize(vec3(-0.3, 0.5, 1.0));
    vec3 view_direction = normalize(-v_position);
    vec3 half_direction = normalize(light_direction + view_direction);

    float diffuse = max(dot(normal, light_direction), 0.0);
    float specular = pow(max(dot(normal, half_direction), 0.0), 48.0);

    float ambient = 0.20;
    vec3 base_color = vec3(0.25, 0.65, 0.95);
    vec3 color = base_color * (ambient + diffuse * 0.75) + vec3(0.25) * specular;
    frag_color = vec4(color, 1.0);
}
