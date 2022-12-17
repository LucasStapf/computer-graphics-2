from PIL import Image
from OpenGL.GL import *

class ObjList:
    def __init__(self, obj_list):
        self.vertices_list = []
        self.tex_coord_list = []
        index = 0
        for obj in obj_list:
            self.load_object(obj, index)
            index += 1

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


class Object:
    def __init__(self, obj_path, tex_path):
        self.load_obj(obj_path)
        self.load_tex(tex_path)

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
