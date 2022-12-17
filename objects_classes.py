from PIL import Image
from OpenGL.GL import *
import glm
import math
import numpy as np

class ObjList:
    def __init__(self, obj_list):

        self.vertices_list = []
        self.tex_coord_list = []
        self.objects = obj_list


        self.load_object(obj_list[0], 0)
        obj_list[0].set_limits((0, len(self.vertices_list)))

        for index in range(1, len(obj_list)):
            obj = obj_list[index]

            begin = len(self.vertices_list)

            self.load_object(obj, index)

            obj.set_limits((begin, len(self.vertices_list) - begin))



    def load_object(self, obj, index):
        for face in obj.model['faces']:
            for vertice_id in face[0]:
                self.vertices_list.append(obj.model['vertices'][vertice_id - 1])
            for texture_id in face[1]:
                self.tex_coord_list.append(obj.model['texture'][texture_id - 1])


        glBindTexture(GL_TEXTURE_2D, index)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, obj.img_width, obj.img_height, 0, GL_RGB, GL_UNSIGNED_BYTE, obj.image_data)

    def draw_objects(self, program):
        index = 0
        for obj in self.objects:
            mat_model = obj.draw()

            loc_model = glGetUniformLocation(program, "model")
            glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)

            #define id da textura do modelo
            glBindTexture(GL_TEXTURE_2D, index)


            # desenha o modelo
            glDrawArrays(GL_TRIANGLES, obj.limits[0], obj.limits[1]) ## renderizando

            index += 1


class Object:
    def __init__(self, obj_path, tex_path):
        self.load_obj(obj_path)
        self.load_tex(tex_path)
        self.movement = None

    def load_tex(self, tex_path):
        img = Image.open(tex_path)
        self.img_width = img.size[0]
        self.img_height = img.size[1]
        self.image_data = img.tobytes("raw", "RGB", 0, -1)


    def load_obj(self, obj_path):

        vertices = []
        texture_coords = []
        faces = []

        material = None

        for line in open(obj_path, "r"): ## para cada linha do arquivo .obj
            if line.startswith('#'): continue ## ignora comentarios
            values = line.split() # quebra a linha por espaço
            if not values: continue
            if values[0] == 'v':
                vertices.append(values[1:4])
            elif values[0] == 'vt':
                texture_coords.append(values[1:3])
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            elif values[0] == 'f':
                face = []
                face_texture = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        face_texture.append(int(w[1]))
                    else:
                        face_texture.append(0)
                faces.append((face, face_texture, material))
        self.model = {}
        self.model['vertices'] = vertices
        self.model['texture'] = texture_coords
        self.model['faces'] = faces

    def set_limits(self, limits):
        self.limits = limits

    def set_coordinates(self, angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z):
        self.angle = angle
        self.r_x = r_x
        self.r_y = r_y
        self.r_z = r_z

        self.t_x = t_x
        self.t_y = t_y
        self.t_z = t_z

        self.s_x = s_x
        self.s_y = s_y
        self.s_z = s_z

    #O atributo movement podera conter uma funcao que quando chamada altera
    #o valor das coordenadas do objeto de alguma forma especifica, permitindo
    #que o objeto seja personalizado
    def set_movement(self, movement):
        self.movement = movement

    def draw(self):
        if(self.movement != None):
            self.movement(self)

        angle = math.radians(self.angle)

        matrix_transform = glm.mat4(1.0) # instanciando uma matriz identidade


        # aplicando translacao
        matrix_transform = glm.translate(matrix_transform, glm.vec3(self.t_x, self.t_y, self.t_z))

        # aplicando rotacao
        matrix_transform = glm.rotate(matrix_transform, angle, glm.vec3(self.r_x, self.r_y, self.r_z))

        # aplicando escala
        matrix_transform = glm.scale(matrix_transform, glm.vec3(self.s_x, self.s_y, self.s_z))

        matrix_transform = np.array(matrix_transform)

        return matrix_transform

