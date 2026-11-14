shader_type canvas_item;
render_mode unshaded;
// Terra incognita: realms the column has not marched through lie under a hatched parchment veil
// with a ragged, slowly breathing edge. A realm's veil burns back when it is first visited.
uniform sampler2D region_tex : filter_nearest, repeat_disable;   // r: region id * 50, g: land
uniform vec4 reveal = vec4(0.0);        // north, east, south, west: 0 hidden .. 1 revealed
uniform float t = 0.0;
const vec2 SZ = vec2(720.0, 400.0);
float hash(vec2 p) { return fract(sin(dot(p, vec2(41.3, 289.1))) * 43758.5453); }
float vnoise(vec2 p) {
	vec2 i = floor(p); vec2 f = fract(p); f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}
void fragment() {
	vec2 p = floor(UV * SZ);
	vec2 rg = texture(region_tex, UV).rg;
	int id = int(round(rg.r * 255.0 / 50.0));
	float rev = 1.0;
	if (id == 1) { rev = reveal.x; } else if (id == 2) { rev = reveal.y; } else if (id == 3) { rev = reveal.z; } else if (id == 4) { rev = reveal.w; }
	float n = vnoise(p / 14.0 + vec2(t * 0.05, 0.0)) * 0.6 + vnoise(p / 5.0) * 0.4;
	float veil = clamp((1.0 - rev) * 1.6 - n * 0.6, 0.0, 1.0);
	if (rg.g < 0.5) { veil = 0.0; }            // the sea itself is always charted
	if (veil < 0.05) { discard; }
	vec3 parch = vec3(0.86, 0.79, 0.62);
	float hatch = mod(p.x + p.y, 4.0) < 1.0 ? 0.88 : 1.0;
	float edge = veil < 0.35 ? 0.75 : 1.0;      // a scorched rim where the veil thins
	vec3 c = parch * hatch;
	if (veil < 0.35) { c = vec3(0.55, 0.38, 0.22); }
	COLOR = vec4(c, clamp(veil * 1.4, 0.0, 0.82) * edge);
}
