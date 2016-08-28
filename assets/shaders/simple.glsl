---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

attribute vec3  v_pos;
attribute vec2  v_uv;

uniform mat4 modelview_mat;
uniform mat4 projection_mat;
uniform vec3 offset;

varying vec2 uv_vec;

void main (void) {
    vec4 pos = modelview_mat * vec4(v_pos+offset,1.0);
    gl_Position = projection_mat * pos;
    uv_vec = v_uv;
}


---FRAGMENT SHADER-----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

varying vec4 frag_color;
varying vec2 uv_vec;

uniform sampler2D tex;

void main (void){
    vec4 color = texture2D(tex, uv_vec);
    gl_FragColor = color;
}
