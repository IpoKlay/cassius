shader_type canvas_item;
render_mode unshaded;
// The realm map's sea: a flat four-tone network of moving water marks, sparkle dashes,
// and surf lines that run up to the coast and break. Land pixels are left exactly as painted.
uniform sampler2D shore_tex : filter_nearest, repeat_disable;   // r: distance to land /32, g: 1 = sea
uniform float t = 0.0;
const vec2 SZ = vec2(720.0, 400.0);

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float vnoise(vec2 p) {
	vec2 i = floor(p); vec2 f = fract(p); f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}
vec2 ridges(vec2 p, float tt) {
	vec2 flow = p - vec2(2.0, 0.6) * tt;
	flow += vec2(sin(flow.y * 0.19 + tt * 0.24), sin(flow.x * 0.15 - tt * 0.2)) * 3.0;
	vec2 warp = vec2(vnoise(flow / 11.0), vnoise(flow / 15.0 + 19.0)) - 0.5;
	vec2 q = (flow + warp * 10.0) / vec2(16.0, 10.0);
	vec2 cell = floor(q); vec2 lc = fract(q);
	float a = 20.0; float b = 20.0;
	for (int y = -1; y <= 1; y++) {
		for (int x = -1; x <= 1; x++) {
			vec2 o = vec2(float(x), float(y));
			vec2 id = cell + o;
			vec2 sd = vec2(hash(id), hash(id + 37.0));
			vec2 site = 0.5 + (sd - 0.5) * 0.64 + sin(sd * 6.283 + tt * 0.5) * 0.1;
			vec2 dl = o + site - lc;
			float d = dot(dl, dl);
			if (d < a) { b = a; a = d; } else { b = min(b, d); }
		}
	}
	return vec2(sqrt(b) - sqrt(a), vnoise(flow / vec2(30.0, 20.0) + 11.0));
}
void fragment() {
	vec4 col = texture(TEXTURE, UV);
	vec2 sh = texture(shore_tex, UV).rg;
	if (sh.g > 0.5) {
		vec2 p = floor(UV * SZ);
		float tt = floor(t * 10.0) / 10.0;
		float depth = sh.r * 32.0;
		if (depth > 2.5) {
			vec2 r = ridges(p, tt);
			float w = 0.05 + r.y * 0.11;
			if (r.x < w) {
				col.rgb = mix(col.rgb, vec3(0.2, 0.42, 0.55), 0.55);
				if (r.x < w * 0.5) { col.rgb = mix(col.rgb, vec3(0.28, 0.52, 0.62), 0.5); }
			}
			// little sparkle dashes drifting with the current
			float row = p.y;
			float gx = floor((p.x + tt * 5.0 * (0.6 + fract(row * 0.37))) / 5.0);
			float g = hash(vec2(gx, row));
			if (g > 0.985 && mod(row, 3.0) < 1.0) { col.rgb = mix(col.rgb, vec3(0.75, 0.88, 0.9), 0.7); }
		}
		// surf: a crest that runs in to the beach, pauses, and falls back broken
		vec2 q = floor(p / 2.0) * 2.0;
		float patch = vnoise(q / 90.0);
		float cyc = fract(t / (5.0 + patch * 3.0) + vnoise(q / 140.0 + 31.0) * 2.0);
		float front = cyc < 0.5 ? mix(12.0, 1.5, cyc / 0.5) : mix(1.5, 9.0, clamp((cyc - 0.55) / 0.3, 0.0, 1.0));
		front = floor(front);
		bool crest = abs(depth - front) < 0.9;
		bool broken = hash(floor(p / vec2(5.0, 3.0))) > (cyc < 0.55 ? 0.2 : 0.5);
		if (cyc < 0.85 && crest && broken && depth < 13.0) {
			col.rgb = cyc < 0.55 ? vec3(0.82, 0.92, 0.9) : vec3(0.55, 0.75, 0.76);
		}
	}
	COLOR = col;
}
