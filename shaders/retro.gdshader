shader_type canvas_item;
// "Old fresco" grade for the road: pulls every pixel into an earthy, limited palette
// (ochres, terracotta, olive, faded lapis, bone), warms and softens it, and darkens the corners.
// Sits above the world and the river, below the menus.
uniform sampler2D screen_tex : hint_screen_texture, filter_nearest;
uniform float strength = 0.9;      // 0 = untouched, 1 = full palette lock
uniform float warmth = 0.3;
uniform float vignette = 0.45;
const int N = 44;
const vec3 PAL[44] = vec3[44](
	vec3(0.102, 0.078, 0.063),
	vec3(0.169, 0.125, 0.094),
	vec3(0.239, 0.173, 0.125),
	vec3(0.329, 0.251, 0.173),
	vec3(0.431, 0.329, 0.220),
	vec3(0.541, 0.424, 0.282),
	vec3(0.659, 0.541, 0.361),
	vec3(0.784, 0.667, 0.471),
	vec3(0.886, 0.800, 0.612),
	vec3(0.949, 0.902, 0.769),
	vec3(0.165, 0.149, 0.188),
	vec3(0.243, 0.227, 0.267),
	vec3(0.353, 0.333, 0.376),
	vec3(0.486, 0.471, 0.502),
	vec3(0.635, 0.612, 0.596),
	vec3(0.227, 0.141, 0.133),
	vec3(0.361, 0.188, 0.157),
	vec3(0.518, 0.251, 0.180),
	vec3(0.659, 0.353, 0.227),
	vec3(0.784, 0.478, 0.290),
	vec3(0.847, 0.604, 0.416),
	vec3(0.910, 0.722, 0.533),
	vec3(0.722, 0.439, 0.416),
	vec3(0.173, 0.204, 0.157),
	vec3(0.227, 0.290, 0.165),
	vec3(0.275, 0.314, 0.227),
	vec3(0.337, 0.408, 0.227),
	vec3(0.400, 0.439, 0.298),
	vec3(0.478, 0.541, 0.282),
	vec3(0.541, 0.565, 0.392),
	vec3(0.627, 0.659, 0.376),
	vec3(0.133, 0.165, 0.212),
	vec3(0.243, 0.314, 0.376),
	vec3(0.369, 0.455, 0.518),
	vec3(0.416, 0.541, 0.627),
	vec3(0.541, 0.627, 0.659),
	vec3(0.604, 0.706, 0.753),
	vec3(0.784, 0.831, 0.800),
	vec3(0.290, 0.188, 0.282),
	vec3(0.416, 0.290, 0.384),
	vec3(0.541, 0.353, 0.416),
	vec3(0.549, 0.416, 0.455),
	vec3(0.973, 0.941, 0.847),
	vec3(0.055, 0.043, 0.039)
);

float bayer4(vec2 p) {
	int x = int(mod(p.x, 4.0));
	int y = int(mod(p.y, 4.0));
	float m[16] = float[16](0.0, 8.0, 2.0, 10.0, 12.0, 4.0, 14.0, 6.0, 3.0, 11.0, 1.0, 9.0, 15.0, 7.0, 13.0, 5.0);
	return m[x + y * 4] / 16.0 - 0.5;
}

float dist2(vec3 a, vec3 b) {
	vec3 d = a - b;
	// weighted so greens/browns separate the way the eye expects
	return d.r * d.r * 0.3 + d.g * d.g * 0.59 + d.b * d.b * 0.11 + abs(dot(d, vec3(0.3, 0.59, 0.11))) * 0.05;
}

void fragment() {
	vec2 px = floor(SCREEN_UV * vec2(480.0, 270.0));
	vec3 c = texture(screen_tex, SCREEN_UV).rgb;
	// age it: take the edge off the saturation, warm toward ochre, lift the blacks a touch
	float l = dot(c, vec3(0.299, 0.587, 0.114));
	vec3 g = mix(c, vec3(l), 0.18);
	g = mix(g, g * vec3(1.08, 0.98, 0.82) + vec3(0.025, 0.015, 0.0), warmth);
	g = g * 0.94 + 0.03;
	// ordered dither before snapping, so gradients break into stipple like an old print
	g += bayer4(px) * 0.035;
	vec3 best = PAL[0];
	float bd = 99.0;
	for (int i = 0; i < N; i++) {
		float d = dist2(g, PAL[i]);
		if (d < bd) { bd = d; best = PAL[i]; }
	}
	vec3 outc = mix(c, best, strength);
	// soft vignette, quantised to keep it "pixel"
	vec2 q = SCREEN_UV - 0.5;
	float v = 1.0 - dot(q * vec2(1.0, 1.25), q * vec2(1.0, 1.25)) * vignette * 2.0;
	v = floor(v * 12.0 + bayer4(px) + 0.5) / 12.0;
	COLOR = vec4(outc * clamp(v, 0.55, 1.0), 1.0);
}
