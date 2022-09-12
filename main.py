#Game
import sys,pygame
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *

#Screenshot and bbox
import copy
from PIL import Image
import cv2
import numpy as np

# IMPORT OBJECT LOADER
from objloader import *


class GameWindow:
    
    def __init__(self,width = 1280,height = 720):
       
        if not pygame.init():
            raise Exception("pygame can't be initialized!")

        self.viewport = (width,height)
        hx = self.viewport[0] / 2
        hy = self.viewport[1] / 2

        window = pygame.display.set_mode(self.viewport, OPENGL | DOUBLEBUF)

        if not window:
            raise Exception("pygame window can't be created!")

        glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)           # most obj files expect to be smooth-shaded

        # LOAD OBJECT AFTER PYGAME INIT
        self.obj = OBJ(sys.argv[1], swapyz=True)
        self.obj.generate()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
      
        gluPerspective(90.0, width/float(height), 1, 100.0)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)

        self.rx, self.ry = (0,0)
        self.tx, self.ty = (0,0)
        self.zpos = 5
        self.rotate = self.move = False

        self.bg_img = cv2.imread(r"bg_1.jpg")
        self.bg_img = cv2.resize(self.bg_img,self.viewport)

        self.img = np.zeros((self.viewport[1],self.viewport[0],3),dtype=np.uint8)

        self.img_bbox_coordinates = [(0, 0),(0, 0),
                                     (0, 0),(0, 0),
                                     (0, 0),(0, 0),
                                     (0, 0),(0, 0)]
       

    def save_screenshot(self,filename = r'test.png'):
        
        glReadBuffer(GL_FRONT)
        pixels = glReadPixels(0,0,*self.viewport,GL_RGB,GL_UNSIGNED_BYTE)
        
        image = Image.frombytes("RGB", self.viewport, pixels)
        image = image.transpose( Image.FLIP_TOP_BOTTOM)
        image.save(filename)

    def get_screenshot(self):
        glReadBuffer(GL_FRONT)
        pixels = glReadPixels(0,0,*self.viewport,GL_RGB,GL_UNSIGNED_BYTE)

        img = Image.frombytes("RGB",self.viewport,pixels)
        
        return np.array(img)[:,:,::-1].astype(np.uint8)


    def get_BBOX(self):
        x_min,y_min,z_min,x_max,y_max,z_max = self.obj.get_min_max()

        verticies = ((x_max, y_min, z_min),(x_max, y_max, z_min),
                     (x_min, y_max, z_min),(x_min, y_min, z_min),
                     (x_max, y_min, z_max),(x_max, y_max, z_max),
                     (x_min, y_min, z_max),(x_min, y_max, z_max))

        img_bbox_coordinates = []

        #Convert 3D to 2D coordinates
        for i in verticies:
            img_bbox_coordinates.append(tuple(map(int,gluProject(*i)))[:2])
            #print(f"{tuple(map(int,gluProject(*i)))[:2]}",end ='')
        #print()

        return img_bbox_coordinates

    #@staticmethod
    def paste_to_background(self):

        bg_img = copy.deepcopy(self.bg_img)
        gray = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
        mask = cv2.threshold(gray,10,255,cv2.THRESH_BINARY)[1]
        bg_img = cv2.bitwise_or(self.img,bg_img,mask=~mask)
        bg_img = cv2.bitwise_or(self.img,bg_img)
        return bg_img
#
 
    def display_BBOX(self):
       
        
        edges = ((0,1),(0,3),(0,4),(2,1),
                 (2,3),(2,7),(6,3),(6,4),
                 (6,7),(5,1),(5,4),(5,7))

        #Draw bbox
        for edge in edges:
            #print(self.img_bbox_coordinates[edge[0]])
            #print(self.img_bbox_coordinates[edge[1]])
        #    point1 = tuple(map(int,gluProject(*verticies[edge[0]])[:2]))
        #    point2 = tuple(map(int,gluProject(*verticies[edge[1]])[:2]))
            self.img = cv2.line(self.img,
                            self.img_bbox_coordinates[edge[0]],
                            self.img_bbox_coordinates[edge[1]],
                            (255,0,0),3)

        self.img = cv2.flip(self.img,0)
        
        #Add a background to an image
        bg_img = self.paste_to_background()
        cv2.imshow("BBOX",bg_img)
        cv2.waitKey(2)

    def update_screen(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()

        # RENDER OBJECT
        glTranslate(self.tx/20., self.ty/20., - self.zpos)
        glRotate(self.ry, 1, 0, 0)
        glRotate(self.rx, 0, 1, 0)
        self.obj.render()

        pygame.display.flip()
        self.img_bbox_coordinates = self.get_BBOX()
        self.img = self.get_screenshot() 
        self.display_BBOX()
        

    def main_loop(self):
        clock = pygame.time.Clock()
   
        while(True):
            clock.tick(30)
            for e in pygame.event.get():
                if e.type == QUIT:
                    #ScreenShot('t1.jpg')
                    #break
                    #print(obj.get_min_max())
                    sys.exit()

                elif e.type == KEYDOWN and e.key == K_ESCAPE:
                    #ScreenShot('t1.jpg')
                    #break
                    #print(obj.get_min_max())
                    sys.exit()

                elif e.type == MOUSEBUTTONDOWN:
                    if e.button == 4: self.zpos = max(1, self.zpos-1)
                    elif e.button == 5: self.zpos += 1
                    elif e.button == 1: self.rotate = True
                    elif e.button == 3: self.move = True

                elif e.type == MOUSEBUTTONUP:
                    if e.button == 1: self.rotate = False
                    elif e.button == 3: self.move = False

                elif e.type == MOUSEMOTION:
                    i, j = e.rel
                    if self.rotate:
                        self.rx += i
                        self.ry += j
                    if self.move:
                        self.tx += i
                        self.ty -= j

            self.update_screen()
            
            #self.display_BBOX()

if __name__ == '__main__':
    window = GameWindow()
    window.main_loop()
