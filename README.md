
# Augmented 3D BBOX data through virtual 3D object
This tool mainly augments the 3D object detection dataset by loading 3D objects (eg .obj, .fbx) and projecting them into 3D space using pygame and openGL, and manipulating and replacing different objects and scenes by rotating or translating .


## Get Started 
step 1 download repository

    git clone https://github.com/WeiXuanYou/3D_tagged_tools.git

step 2 Install related libraries

    pip install -r requirements

##  Demo

Run
    
    python main.py your_object_file

Example

    python main.py .\3D_OBJ\LibertyStatue\LibertStatue.obj
    
![](https://i.imgur.com/kswMlbi.png)

## Reference
[1] https://www.pygame.org/wiki/OBJFileLoader
