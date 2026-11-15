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