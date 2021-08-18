import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from PIL import Image
 
 
def main():
    if not glfw.init():
        return
 
    window = glfw.create_window(720, 600, "Pyopengl Texturing Rectangle", None, None)
 
    if not window:
        glfw.terminate()
        return
 
    glfw.make_context_current(window)
 
 
                   #positions        colors               texture coords
    rectangle = [-0.5, -0.5, 0.0,   1.0, 0.0, 0.0,          0.0, 0.0,
            0.5, -0.5, 0.0,         0.0, 1.0, 0.0,          1.0, 0.0,
            0.5, 0.5, 0.0,          0.0, 0.0, 1.0,          1.0, 1.0,
            -0.5, 0.5, 0.0,         1.0, 1.0, 1.0,           0.0, 1.0]
 
   
    # convert to 32bit float
 
    rectangle = np.array(rectangle, dtype=np.float32)
 
 
    indices = [0,1,2,
              2,3,0]
 
    indices = np.array(indices, dtype = np.uint32)
 
    VERTEX_SHADER = """
 
           #version 330
 
           in vec3 position;
           in vec3 color;
           in vec2 InTexCoords;
           
           out vec3 newColor;
           out vec2 OutTexCoords;
 
           void main() {
 
            gl_Position = vec4(position, 1.0);
            newColor = color;
            OutTexCoords = InTexCoords;
 
             }
 
 
       """
 
    FRAGMENT_SHADER = """
        #version 330
 
         in vec3 newColor;
         in vec2 OutTexCoords;
         
         out vec4 outColor;
         uniform sampler2D samplerTex;
 
        void main() {
 
           outColor = texture(samplerTex, OutTexCoords);
 
        }
 
    """
 
    # Compile The Program and shaders
 
    shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
                                              OpenGL.GL.shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER))
 
    # Create Buffer object in gpu
    VBO = glGenBuffers(1)
    # Bind the buffer
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, 128, rectangle, GL_STATIC_DRAW)
 
 
    #Create EBO
    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices, GL_STATIC_DRAW)
 
 
 
    # get the position from  shader
    position = glGetAttribLocation(shader, 'position')
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
    glEnableVertexAttribArray(position)
 
    # get the color from  shader
    color = glGetAttribLocation(shader, 'color')
    glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
    glEnableVertexAttribArray(color)
 
    texCoords = glGetAttribLocation(shader, "InTexCoords")
    glVertexAttribPointer(texCoords,2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))
    glEnableVertexAttribArray(texCoords)
 
    #Creating Texture
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    # texture wrapping params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    # texture filtering params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
 
    image = Image.open("wood.jpg")
    img_data = np.array(list(image.getdata()), np.uint8)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 512, 512, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
 
 
    glUseProgram(shader)
 
    glClearColor(1.0, 0.0, 0.0, 1.0)
 
    while not glfw.window_should_close(window):
        glfw.poll_events()
 
        glClear(GL_COLOR_BUFFER_BIT)
 
        # Draw Rectangle
 
        glDrawElements(GL_TRIANGLES,6, GL_UNSIGNED_INT,  None)
 
        glfw.swap_buffers(window)
 
    glfw.terminate()
 
 
if __name__ == "__main__":
    main()