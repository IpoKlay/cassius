shader_type canvas_item;
// Aerial perspective for a backdrop strip: the further away, the more it melts into the horizon colour.
uniform vec3 fog_col = vec3(0.8, 0.8, 0.85);
uniform float amount = 0.3;
// lighter at the top edge of the strip (mist hangs over the far ridges), heavier toward its foot
uniform float top_boost = 0.15;

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	float k = clamp(amount + top_boost * (1.0 - UV.y), 0.0, 1.0);
	COLOR = vec4(mix(c.rgb, fog_col, k), c.a) * vec4(1.0, 1.0, 1.0, COLOR.a);
}
