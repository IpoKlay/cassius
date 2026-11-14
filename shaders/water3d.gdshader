shader_type spatial;
render_mode unshaded;
// Flat-shaded river for the tilted 3D march: banded depth colour + drifting pixel glints.
uniform vec3 shallow = vec3(0.16, 0.26, 0.36);
uniform vec3 deep = vec3(0.05, 0.09, 0.17);
uniform vec3 tint = vec3(1.0, 1.0, 1.0);
uniform float bank_z = 4.6;
varying vec3 wp;

void vertex() {
	wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float d = clamp((wp.z - bank_z) / 5.0, 0.0, 1.0);
	d = floor(d * 5.0) / 5.0;
	vec3 col = mix(shallow, deep, d);
	float row = floor(wp.z * 11.0);
	float cell = floor((wp.x * 22.0 + TIME * 7.0 * (0.4 + fract(row * 0.37))) / 6.0);
	float n = fract(sin(cell * 12.9898 + row * 78.233) * 43758.5453);
	if (n > 0.955) {
		col += vec3(0.16, 0.17, 0.15);
	}
	if (wp.z - bank_z < 0.12) {
		col = mix(col, vec3(0.7, 0.78, 0.84), 0.45);
	}
	ALBEDO = col * tint;
}
