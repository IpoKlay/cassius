shader_type canvas_item;
render_mode unshaded;

uniform sampler2D water_mask : filter_nearest, repeat_disable;
uniform vec4 west : source_color;
uniform vec4 north : source_color;
uniform vec4 south : source_color;
uniform vec4 east : source_color;

uniform float weather_time = 0.0;
const vec2 WEATHER_GRID = vec2(360.0, 156.0);

float cell_hash(vec2 id) {
	return fract(sin(dot(id, vec2(127.1, 311.7))) * 43758.5453);
}

// Each cell carries one flake, leaf, ember or star. Quantized coordinates retain hard pixel edges.
float particles(vec2 point, vec2 cell_size, vec2 drift, float seed, int kind) {
	vec2 traveling = point - drift;
	vec2 cell = floor(traveling / cell_size);
	float a = cell_hash(cell + seed);
	float b = cell_hash(cell + seed + 29.0);
	vec2 center = floor(vec2(0.12 + a * 0.70, 0.14 + b * 0.68) * cell_size);
	vec2 delta = floor(mod(traveling, cell_size)) - center;
	vec2 d = abs(delta);
	if (kind == 0) {
		// Torn off the canopy: a tip with a thicker leaf blade.
		float tip = sin(weather_time * 6.0 + a * 18.0) > 0.0 ? 1.0 : -1.0;
		return (d.x <= 1.0 && delta.y == 0.0) || (delta.x == tip && delta.y == -1.0) ? 0.82 : 0.0;
	}
	if (kind == 1) {
		float streak = a > 0.58 ? 2.0 : 0.0;
		return (delta.y == 0.0 && d.x <= streak) || (a > 0.74 && d.x <= 1.0 && delta.y == 1.0) ? 0.80 + 0.20 * b : 0.0;
	}
	if (kind == 2) {
		float blink = 0.46 + 0.54 * max(0.0, sin(weather_time * 7.0 + b * 19.0));
		return d.x == 0.0 && d.y <= (a > 0.65 ? 1.0 : 0.0) ? blink : 0.0;
	}
	float glow = pow(max(0.0, sin(weather_time * 2.1 + b * 24.0)), 2.0);
	return d.x + d.y <= (a > 0.77 ? 1.0 : 0.0) ? glow : 0.0;
}

vec3 weather_ink(vec3 base, vec2 p, vec4 weights) {
	float t = weather_time;
	if (weights.y > 0.01) {
		float snow = particles(p, vec2(15.0, 10.0), floor(vec2(46.0, 13.0) * t), 7.0, 1);
		float far_snow = particles(p, vec2(9.0, 7.0), floor(vec2(24.0, 8.0) * t), 18.0, 1);
		float squall = smoothstep(0.24, 0.95, sin(p.x * 0.051 - p.y * 0.13 - t * 2.8));
		base = mix(base, vec3(0.72, 0.87, 0.92), weights.y * squall * 0.19);
		base = mix(base, vec3(0.98, 1.0, 1.0), weights.y * max(snow * 0.96, far_snow * 0.54));
	}
	if (weights.x > 0.01) {
		float gust = sin(p.y * 0.14 - t * 2.0);
		float leaf = particles(p, vec2(15.0, 11.0), floor(vec2(35.0 * t, 8.0 * t + gust * 3.5)), 23.0, 0);
		float glint = smoothstep(0.72, 1.0, sin(p.x * 0.12 + p.y * 0.07 - t * 5.0));
		base = mix(base, vec3(0.79, 0.90, 0.43), weights.x * max(0.27 * glint, 0.96 * leaf));
	}
	if (weights.z > 0.01) {
		vec2 tile = floor((p + vec2(7.0, 9.0)) / vec2(45.0, 29.0));
		vec2 local = mod(p + vec2(7.0, 9.0), vec2(45.0, 29.0)) - vec2(22.0, 14.0);
		float wave = sin(t * 3.8 + cell_hash(tile + 43.0) * 22.0) * 0.5 + 0.5;
		float pool = max(0.0, 1.0 - length(local / vec2(20.0, 14.0)));
		float hearths = floor(pool * (2.0 + 4.0 * wave) * 4.0) / 24.0;
		float embers = particles(p, vec2(12.0, 14.0), floor(vec2(15.0, -31.0) * t), 39.0, 2);
		base = mix(base, vec3(0.50, 0.22, 0.17), weights.z * (1.0 - hearths) * 0.21);
		base = mix(base, vec3(1.0, 0.70, 0.23), weights.z * hearths * 0.69);
		base = mix(base, vec3(1.0, 0.91, 0.50), weights.z * embers * 0.90);
	}
	if (weights.w > 0.01) {
		float ribbon = sin(p.y * 0.15 + sin(p.x * 0.043 + t * 0.85) * 1.7 - t * 1.35);
		float wisps = 0.48 + 0.52 * sin(p.x * 0.077 + p.y * 0.032 - t * 1.4);
		float haze = floor(smoothstep(0.10, 0.95, ribbon) * wisps * 5.0) / 5.0;
		float stars = particles(p, vec2(12.0, 10.0), floor(vec2(-6.0, 4.0) * t), 57.0, 3);
		base = mix(base, vec3(0.46, 0.27, 0.76), weights.w * haze * 0.51);
		base = mix(base, vec3(0.99, 0.90, 1.0), weights.w * stars * 0.97);
	}
	return base;
}

// Blend only near territory boundaries. The atlas's existing shade and water pixels stay legible.
void fragment() {
	vec4 terrain = texture(TEXTURE, UV);
	vec2 point = floor(UV / TEXTURE_PIXEL_SIZE) * TEXTURE_PIXEL_SIZE;
	float w = distance(point, vec2(0.17, 0.36));
	float n = distance(point, vec2(0.52, 0.12));
	float s = distance(point, vec2(0.375, 0.70));
	float e = distance(point, vec2(0.83, 0.45));
	float nearest = min(min(w, n), min(s, e));
	vec4 weights = 1.0 - smoothstep(vec4(0.0), vec4(0.021), vec4(w, n, s, e) - nearest);
	vec3 hue = (west.rgb * weights.x + north.rgb * weights.y + south.rgb * weights.z + east.rgb * weights.w)
		/ dot(weights, vec4(1.0));
	float value = dot(terrain.rgb, vec3(0.299, 0.587, 0.114));
	float hue_value = dot(hue, vec3(0.299, 0.587, 0.114));
	vec3 tinted = clamp(hue * (0.32 + 0.83 * value / max(hue_value, 0.1)), 0.0, 1.0);
	float land = 1.0 - texture(water_mask, UV).g;
	vec3 base = mix(terrain.rgb, tinted, land * 0.80);
	if (land > 0.5) {
		base = weather_ink(base, floor(UV * WEATHER_GRID), weights / dot(weights, vec4(1.0)));
	}
	COLOR = vec4(base, terrain.a);
}
