#Game
import sys,pygame
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *

#Screenshot
from PIL import Image
import numpy as np

# IMPORT OBJECT LOADER
# from objloader import *

from DataAugmentation import OBJDataGenerator

import cv2

import argparse

class GameWindow:
    
    def __init__(self,width = 1280,height = 720,args = None):
       
        self.args = args

        if not pygame.init():
            raise Exception("pygame can't be initialized!")

        self.viewport = (width,height)
        #hx = self.viewport[0] / 2
        #hy = self.viewport[1] / 2

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
        self.obj_data_generator = OBJDataGenerator(args.bg_img_path,
                                                   args.obj_3d_path,
                                                   self.get_screenshot)
        # self.obj = OBJ(sys.argv[1], swapyz=True)
        # self.obj.generate()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
      
        gluPerspective(90.0, width/float(height), 1, 100.0)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)

        self.rx, self.ry = (0,0)
        self.tx, self.ty = (0,0)
        self.zpos = 5
        self.rotate = self.move = False
        

    def save_screenshot(self,filename = r'test.png'):
        
        #glReadBuffer(GL_FRONT)
        pixels = glReadPixels(0,0,*self.viewport,GL_RGB,GL_UNSIGNED_BYTE)
        
        image = Image.frombytes("RGB", self.viewport, pixels)
        image = image.transpose( Image.FLIP_TOP_BOTTOM)
        image.save(filename)

    def get_screenshot(self):
        #glReadBuffer(GL_FRONT)
        pixels = glReadPixels(0,0,*self.viewport,GL_RGB,GL_UNSIGNED_BYTE)

        img = Image.frombytes("RGB",self.viewport,pixels)
        
        return np.array(img)[:,:,::-1].astype(np.uint8)

 
    def display_BBOX(self):
       
        #print(self.get_screenshot().shape)
        if(self.args.show_2d_bbox):
            cv2.imshow("BBOX",self.obj_data_generator.draw_2D_BBOX(self.get_screenshot()))
        if(self.args.show_3d_bbox):
            cv2.imshow("BBOX",self.obj_data_generator.draw_3D_BBOX(self.get_screenshot()))
        cv2.waitKey(2)

    def update_screen(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()

        # RENDER OBJECT
        glTranslate(self.tx/20., self.ty/20., - self.zpos)
        glRotate(self.ry, 1, 0, 0)
        glRotate(self.rx, 0, 1, 0)
        self.obj_data_generator.obj.render()

        pygame.display.flip()
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

    parser = argparse.ArgumentParser()
    parser.add_argument('--bg_img_path',default='bg_1.jpg',help="Please enter background image's path.")
    parser.add_argument('--obj_3d_path',default='./3D_OBJ/LibertStatue.obj',help="Please enter 3D object file's path.")
    parser.add_argument('--show_3d_bbox',action='store_true',help='Display 3D BBOX')
    parser.add_argument('--show_2d_bbox',action='store_true',help='Display 2D BBOX')
    
    args = parser.parse_args()
    
    window = GameWindow(args=args)
    window.main_loop()
