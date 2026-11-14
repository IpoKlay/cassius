shader_type canvas_item;
// Kingdom-style river: mirrors everything drawn above the waterline, with ripples.
uniform sampler2D screen_tex : hint_screen_texture, filter_nearest, repeat_disable;
uniform float line_v = 0.7;      // waterline in screen UV
uniform vec3 tint = vec3(0.10, 0.16, 0.26);
uniform float scroll = 0.0;
uniform float stretch = 1.15;

void fragment() {
	vec2 suv = SCREEN_UV;
	float depth = suv.y - line_v;            // 0 at the waterline
	float py = floor(suv.y * 270.0);
	float wob = sin(py * 1.7 + TIME * 2.2) * 0.0025 + sin(py * 0.6 - TIME * 1.3) * 0.002;
	wob *= (0.4 + depth * 14.0);
	vec2 m = vec2(suv.x + wob, line_v - depth * stretch - 0.5 / 270.0);
	m.x = floor(m.x * 480.0) / 480.0 + 0.5 / 480.0;
	vec3 refl = texture(screen_tex, m).rgb;
	float fade = clamp(depth * 4.0, 0.0, 1.0);
	vec3 col = mix(refl * 0.9, tint, 0.2 + fade * 0.32);
	// glints: thin bright horizontal dashes drifting sideways
	float gx = floor((suv.x * 480.0 + scroll * 0.3 + TIME * 6.0 * (0.5 + fract(py * 0.37))) / 6.0);
	float g = fract(sin(gx * 12.9898 + py * 78.233) * 43758.5453);
	if (g > 0.955 && depth > 0.004) {
		col += vec3(0.22, 0.24, 0.22) * (1.0 - fade * 0.5);
	}
	// bright rim right at the bank
	if (depth < 0.006) {
		col = mix(col, vec3(0.75, 0.8, 0.85), 0.35);
	}
	COLOR = vec4(col, 1.0);
}
