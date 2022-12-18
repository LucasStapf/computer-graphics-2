import objects_classes as obj
import glfw
from OpenGL.GL import *
import numpy as np
import glm
import math
from PIL import Image


glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE);
altura = 1600
largura = 1200
window = glfw.create_window(largura, altura, "Malhas e Texturas", None, None)
glfw.make_context_current(window)
vertex_code = """
        attribute vec3 position;
        attribute vec2 texture_coord;
        varying vec2 out_texture;

        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;

        void main(){
            gl_Position = projection * view * model * vec4(position,1.0);
            out_texture = vec2(texture_coord);
        }
        """
fragment_code = """
        uniform vec4 color;
        varying vec2 out_texture;
        uniform sampler2D samplerTexture;

        void main(){
            vec4 texture = texture2D(samplerTexture, out_texture);
            gl_FragColor = texture;
        }
        """
program  = glCreateProgram()
vertex   = glCreateShader(GL_VERTEX_SHADER)
fragment = glCreateShader(GL_FRAGMENT_SHADER)

glShaderSource(vertex, vertex_code)
glShaderSource(fragment, fragment_code)

glCompileShader(vertex)
if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(vertex).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Vertex Shader")

glCompileShader(fragment)
if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(fragment).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Fragment Shader")

glAttachShader(program, vertex)
glAttachShader(program, fragment)

glLinkProgram(program)
if not glGetProgramiv(program, GL_LINK_STATUS):
    print(glGetProgramInfoLog(program))
    raise RuntimeError('Linking error')

glUseProgram(program)

glEnable(GL_TEXTURE_2D)
qtd_texturas = 10
textures = glGenTextures(qtd_texturas)


caixa = obj.Object('caixa/caixa.obj', 'caixa/caixa2.jpg')
caixa.set_coordinates(0.0, 0.0, 0.0, -150.0, 10.0, 0.0, 15.0, 1.0, 1.0, 1.0)

terreno = obj.Object('terreno/terreno2.obj', 'terreno/pedra.jpg')
terreno.set_coordinates(0.0, 0.0, 0.0, 1.0, 0.0, -1.01, 0.0, 20.0, 20.0, 20.0)

casa = obj.Object('casa/casa.obj', 'casa/casa.jpg')
casa.set_coordinates(0.0, 0.0, 0.0, 1.0, 0.0, -1.0, 0.0, 5.0, 5.0, 5.0)

monstro = obj.Object('monstro/monstro.obj', 'monstro/monstro.jpg')
monstro.set_coordinates(0.0, 0.0, 1.0, 0.0, 0.0, -1.0, 0.0, 1.0, 1.0, 1.0)

cadeira = obj.Object('cadeira/cadeira.obj', 'cadeira/cadeira.jpg')
cadeira.set_coordinates(0.0, 0.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 1.0, 1.0)

bau = obj.Object('bau/bau.obj', 'bau/bau.png')
bau.set_coordinates(0.0, 0.0, 0.0, 1.0, -12.5, -1.0, 1.0, 2.5, 2.5, 2.5)

def rotacao_inc(self):
    self.angle += 0.1
    if(self.t_y < 10.0):
        self.t_y += 0.005

monstro.set_movement(rotacao_inc)


lista_objetos = obj.ObjList(
        [
            caixa,
            casa,
            terreno,
            monstro,
            cadeira,
            bau
            ]
        )
# Request a buffer slot from GPU
buffer = glGenBuffers(2)


# ###  Enviando coordenadas de vértices para a GPU

vertices = np.zeros(len(lista_objetos.vertices_list), [("position", np.float32, 3)])
vertices['position'] = lista_objetos.vertices_list


# Upload data
glBindBuffer(GL_ARRAY_BUFFER, buffer[0])
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
stride = vertices.strides[0]
offset = ctypes.c_void_p(0)
loc_vertices = glGetAttribLocation(program, "position")
glEnableVertexAttribArray(loc_vertices)
glVertexAttribPointer(loc_vertices, 3, GL_FLOAT, False, stride, offset)


# ###  Enviando coordenadas de textura para a GPU


textures = np.zeros(len(lista_objetos.tex_coord_list), [("position", np.float32, 2)]) # duas coordenadas
textures['position'] = lista_objetos.tex_coord_list


# Upload data
glBindBuffer(GL_ARRAY_BUFFER, buffer[1])
glBufferData(GL_ARRAY_BUFFER, textures.nbytes, textures, GL_STATIC_DRAW)
stride = textures.strides[0]
offset = ctypes.c_void_p(0)
loc_texture_coord = glGetAttribLocation(program, "texture_coord")
glEnableVertexAttribArray(loc_texture_coord)
glVertexAttribPointer(loc_texture_coord, 2, GL_FLOAT, False, stride, offset)


# ### Eventos para modificar a posição da câmera.
#
# * Usei as teclas A, S, D e W para movimentação no espaço tridimensional.
# * Usei a posição do mouse para "direcionar" a câmera.

# In[ ]:


cameraPos   = glm.vec3(0.0,  0.0,  1.0);
cameraFront = glm.vec3(0.0,  0.0, -1.0);
cameraUp    = glm.vec3(0.0,  1.0,  0.0);


polygonal_mode = False

def key_event(window,key,scancode,action,mods):
    global cameraPos, cameraFront, cameraUp, polygonal_mode

    cameraSpeed = 0.2
    if key == 87 and (action==1 or action==2): # tecla W
        cameraPos += cameraSpeed * cameraFront

    if key == 83 and (action==1 or action==2): # tecla S
        cameraPos -= cameraSpeed * cameraFront

    if key == 65 and (action==1 or action==2): # tecla A
        cameraPos -= glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed

    if key == 68 and (action==1 or action==2): # tecla D
        cameraPos += glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed

    if key == 80 and action==1 and polygonal_mode==True:
        polygonal_mode=False
    else:
        if key == 80 and action==1 and polygonal_mode==False:
            polygonal_mode=True



firstMouse = True
yaw = -90.0
pitch = 0.0
lastX =  largura/2
lastY =  altura/2

def mouse_event(window, xpos, ypos):
    global firstMouse, cameraFront, yaw, pitch, lastX, lastY
    if firstMouse:
        lastX = xpos
        lastY = ypos
        firstMouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos
    lastX = xpos
    lastY = ypos

    sensitivity = 0.3
    xoffset *= sensitivity
    yoffset *= sensitivity

    yaw += xoffset;
    pitch += yoffset;


    if pitch >= 90.0: pitch = 90.0
    if pitch <= -90.0: pitch = -90.0

    front = glm.vec3()
    front.x = math.cos(glm.radians(yaw)) * math.cos(glm.radians(pitch))
    front.y = math.sin(glm.radians(pitch))
    front.z = math.sin(glm.radians(yaw)) * math.cos(glm.radians(pitch))
    cameraFront = glm.normalize(front)



glfw.set_key_callback(window,key_event)
glfw.set_cursor_pos_callback(window, mouse_event)

def desenha_luz(t_x, t_y, t_z):
    

    # aplica a matriz model
    angle = 0.0
    
    r_x = 0.0; r_y = 0.0; r_z = 1.0;
    
    # translacao
    #t_x = 0.0; t_y = 0.0; t_z = 0.0;
    
    # escala
    s_x = 0.1; s_y = 0.1; s_z = 0.1;
    
    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)
    loc_model = glGetUniformLocation(program, "model")
    glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)
       
    
    #### define parametros de ilumincao do modelo
    ka = 1 # coeficiente de reflexao ambiente do modelo
    kd = 1 # coeficiente de reflexao difusa do modelo
    ks = 1 # coeficiente de reflexao especular do modelo
    ns = 1000.0 # expoente de reflexao especular
    
    loc_ka = glGetUniformLocation(program, "ka") # recuperando localizacao da variavel ka na GPU
    glUniform1f(loc_ka, ka) ### envia ka pra gpu
    
    loc_kd = glGetUniformLocation(program, "kd") # recuperando localizacao da variavel kd na GPU
    glUniform1f(loc_kd, kd) ### envia kd pra gpu    
    
    loc_ks = glGetUniformLocation(program, "ks") # recuperando localizacao da variavel ks na GPU
    glUniform1f(loc_ks, ks) ### envia ns pra gpu        
    
    loc_ns = glGetUniformLocation(program, "ns") # recuperando localizacao da variavel ns na GPU
    glUniform1f(loc_ns, ns) ### envia ns pra gpu            
    
    loc_light_pos = glGetUniformLocation(program, "lightPos") # recuperando localizacao da variavel lightPos na GPU
    glUniform3f(loc_light_pos, t_x, t_y, t_z) ### posicao da fonte de luz
        
    
    #define id da textura do modelo
    glBindTexture(GL_TEXTURE_2D, 1)
    
    
    # desenha o modelo
    glDrawArrays(GL_TRIANGLES, 36, 36) ## renderizando

def view():
    global cameraPos, cameraFront, cameraUp
    mat_view = glm.lookAt(cameraPos, cameraPos + cameraFront, cameraUp);
    mat_view = np.array(mat_view)
    return mat_view

def projection():
    global altura, largura
    # perspective parameters: fovy, aspect, near, far
    mat_projection = glm.perspective(glm.radians(45.0), largura/altura, 0.1, 1000.0)
    mat_projection = np.array(mat_projection)
    return mat_projection


# ### Nesse momento, exibimos a janela.

# In[ ]:


glfw.show_window(window)
glfw.set_cursor_pos(window, lastX, lastY)


# ### Loop principal da janela.
# Enquanto a janela não for fechada, esse laço será executado. É neste espaço que trabalhamos com algumas interações com a OpenGL.

# In[ ]:


glEnable(GL_DEPTH_TEST) ### importante para 3D

ang = 0.1
ns_inc = 32

while not glfw.window_should_close(window):

    glfw.poll_events()


    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glClearColor(1.0, 1.0, 1.0, 1.0)

    if polygonal_mode==True:
        glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
    if polygonal_mode==False:
        glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)



    lista_objetos.draw_objects(program)
    ang += 0.005
    desenha_luz(math.cos(ang)*0.5, math.sin(ang)*0.5, 3.0)   

    mat_view = view()
    loc_view = glGetUniformLocation(program, "view")
    glUniformMatrix4fv(loc_view, 1, GL_TRUE, mat_view)

    mat_projection = projection()
    loc_projection = glGetUniformLocation(program, "projection")
    glUniformMatrix4fv(loc_projection, 1, GL_TRUE, mat_projection)




    glfw.swap_buffers(window)

glfw.terminate()


# # Exercício
#
# * Adicione mais 2 modelos no cenário com suas respectivas texturas. Procure em repositórios abertos/gratuitos por modelos no formato Wavefront (extensão .obj). Verifique se o conteúdo das faces do modelo é baseado em triângulos. Verifique se o modelo acompanha alguma imagem (.jpg, png, etc) com a textura. Evite modelos compostos por múltiplos objetos/texturas.
#
# * Coloque um cubo para "encapsular" todo o seu cenário. A face inferior do cubo será seu terreno. A face superior será o céu. As faces laterais serão horizontes. Crie um único arquivo de textura (imagem png ou jpg) com todas as faces. No arquivo .obj do modelo, define as coordenadas de textura para cada triângulo.
