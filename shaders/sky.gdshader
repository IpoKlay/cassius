shader_type canvas_item;
// Banded, ordered-dithered dusk gradient with sun/moon disc and stars.
uniform vec3 top_col = vec3(0.1, 0.1, 0.3);
uniform vec3 bot_col = vec3(0.9, 0.5, 0.3);
uniform vec3 orb_col = vec3(1.0, 0.9, 0.7);
uniform vec2 orb_pos = vec2(0.7, 0.3);
uniform float night = 0.0;
uniform float bands = 14.0;

float bayer(vec2 p) {
	int x = int(mod(p.x, 4.0));
	int y = int(mod(p.y, 4.0));
	int i = x + y * 4;
	float m[16] = float[16](0.0, 8.0, 2.0, 10.0, 12.0, 4.0, 14.0, 6.0, 3.0, 11.0, 1.0, 9.0, 15.0, 7.0, 13.0, 5.0);
	return m[i] / 16.0;
}

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void fragment() {
	vec2 px = floor(UV * vec2(480.0, 190.0));
	float t = UV.y;
	float q = floor(t * bands + bayer(px)) / bands;
	vec3 col = mix(top_col, bot_col, clamp(q, 0.0, 1.0));
	// stars
	float s = hash(px);
	if (s > 0.9965 && UV.y < 0.75) {
		float tw = 0.6 + 0.4 * sin(TIME * 2.0 + s * 900.0);
		col = mix(col, vec3(1.0, 0.97, 0.9), night * tw);
	}
	// orb (sun by day, moon by night), hard pixel edge with a dithered halo
	vec2 d = (UV - orb_pos) * vec2(480.0, 190.0);
	float r = length(d);
	if (r < 9.0) {
		col = orb_col;
	} else if (r < 30.0) {
		float h = (1.0 - (r - 9.0) / 21.0) * 0.45;
		if (h > bayer(px)) {
			col = mix(col, orb_col, 0.35);
		}
	}
	COLOR = vec4(col, 1.0);
}
