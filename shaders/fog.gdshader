shader_type canvas_item;
// Thin drifting mist, quantised so it stays "pixel".
uniform vec3 fog_col = vec3(0.8, 0.8, 0.9);
uniform float density = 0.35;
uniform float scroll = 0.0;

float hash(vec2 p) { return fract(sin(dot(p, vec2(41.3, 289.1))) * 43758.5453); }
float noise(vec2 p) {
	vec2 i = floor(p); vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

float bayer2(vec2 a) {
	a = floor(a);
	return fract(a.x / 2.0 + a.y * a.y * 0.75);
}
float bayer4(vec2 a) {
	return bayer2(0.5 * a) * 0.25 + bayer2(a);
}

void fragment() {
	vec2 px = floor(UV * vec2(480.0, 270.0));
	vec2 p = vec2((px.x + scroll * 0.8) / 90.0 + TIME * 0.035, px.y / 26.0);
	float n = noise(p) * 0.6 + noise(p * 2.3 + 7.0) * 0.4;
	float band = smoothstep(0.35, 0.72, UV.y) * (1.0 - smoothstep(0.86, 1.0, UV.y));
	float a = clamp((n - 0.42) * 2.2, 0.0, 1.0) * band * density;
	a = floor(a * 4.0 + bayer4(px)) / 4.0;
	COLOR = vec4(fog_col, a * 0.8);
}
