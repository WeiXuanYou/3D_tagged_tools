from objloader import *
import cv2
import copy
from OpenGL.GLU import *

class OBJDataGenerator:
    def __init__(self,background_path,obj_path,get_screenshot_callback):
        
        self.get_screenshot_callback = get_screenshot_callback

        self.bg_img = cv2.imread(background_path)
        self.bg_img =  cv2.resize(self.bg_img,(1280,720))
               
        self.obj = OBJ(obj_path, swapyz=True)
        self.obj.generate()

    def paste_to_background(self,img):

        bg_img = copy.deepcopy(self.bg_img)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        mask = cv2.threshold(gray,10,255,cv2.THRESH_BINARY)[1]
        bg_img = cv2.bitwise_or(img,bg_img,mask=~mask)
        bg_img = cv2.bitwise_or(img,bg_img)

        return bg_img

    def get_2D_BBOX(self):
        bbox_3d_coordinates = self.get_3D_BBOX()

        x_min = min([i[0] for i in bbox_3d_coordinates])
        x_max = max([i[0] for i in bbox_3d_coordinates])
        y_min = min([i[1] for i in bbox_3d_coordinates])
        y_max = max([i[1] for i in bbox_3d_coordinates])
        
        bbox2D_coordinates = ((x_min,y_min),(x_max,y_max)) #,(x_max,y_min),(x_min,y_max),(x_max,y_max))
        #Convert 3D to 2D coordinates
        
        
        return bbox2D_coordinates

    def get_3D_BBOX(self):
        x_min,y_min,z_min,x_max,y_max,z_max = self.obj.get_min_max_pos()

        verticies = ((x_max, y_min, z_min),(x_max, y_max, z_min),
                     (x_min, y_max, z_min),(x_min, y_min, z_min),
                     (x_max, y_min, z_max),(x_max, y_max, z_max),
                     (x_min, y_min, z_max),(x_min, y_max, z_max))
        
        bbox3D_coordinates = []
        #Convert 3D to 2D coordinates
        for i in verticies:
            bbox3D_coordinates.append(tuple(map(int,gluProject(*i)))[:2])

        return bbox3D_coordinates

    def draw_2D_BBOX(self,img):
        bbox2D_coordinates = self.get_2D_BBOX()
        img = cv2.rectangle(img,*bbox2D_coordinates,(255,0,0),2)
        img = cv2.flip(img,0)
        
        #Add a background to an image
        img = self.paste_to_background(img)
        return img

    def draw_3D_BBOX(self,img):
        bbox3D_coordinates = self.get_3D_BBOX()

        edges = ((0,1),(0,3),(0,4),(2,1),
                 (2,3),(2,7),(6,3),(6,4),
                 (6,7),(5,1),(5,4),(5,7))


        for edge in edges:
            img = cv2.line(img,
                           bbox3D_coordinates[edge[0]],
                           bbox3D_coordinates[edge[1]],
                           (255,0,0),3)


        img = cv2.flip(img,0)
        
        
        #Add a background to an image
        img = self.paste_to_background(img)

        return img
    