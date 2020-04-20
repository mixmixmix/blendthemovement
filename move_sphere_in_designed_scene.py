
import numpy as np #remember to add to sys.path proper python libs
import bpy
from mathutils import Vector

"""
Updates position of all Zwierzaks.
They generally like to cluster, if they are suitably far away
"""
def updatePosition(zwk,zwks,x_home,y_home):
    zwk.x_prev = zwk.x_pos
    zwk.y_prev = zwk.y_pos
    fardist=30.
    dhome_x=zwk.x_prev - x_home
    dhome_y=zwk.x_prev - x_home
    homing_x = 0.01*dhome_x
    homing_y = 0.01*dhome_y
    pl_x=max(0.33+homing_x,0)
    pl_y=max(0.33+homing_y,0)
    dx = np.random.choice([-1,0,1], p=[pl_x, 0.34, 0.66-pl_x])
    dy = np.random.choice([-1,0,1], p=[pl_y, 0.34, 0.66-pl_y])
    # dx, dy = np.round(2*np.random.rand(2,)-1).astype(int)
    zwk.x_pos = zwk.x_prev+dx
    zwk.y_pos = zwk.y_prev+dy
    return zwk

"""
Handle colisions:
 - boundry conditions? Let's make it reflective, but simulate so that animals keep off the long grass.
 - collisions with other animals: This is going to be async, so if animal wants to move to other position, it will not make this movement. I need occupancy grid for that.
"""
def handleColisions(zwk, borders, zwks_list):
    rside = borders.x_max
    lside = borders.x_min # ASSUME IT IS SQUARE
    zwk.x_pos = max(min(zwk.x_pos,rside-1),lside)
    zwk.y_pos = max(min(zwk.y_pos,rside-1),lside)

    for other_zwk in zwks_list:
        if other_zwk.id == zwk.id:
            continue
        if zwk.x_pos == other_zwk.x_pos and zwk.y_pos == other_zwk.y_pos:
            zwk.x_pos = zwk.x_prev
            zwk.y_pos = zwk.y_prev
    return zwk


class Zwierzak:
    def __init__(self, zwkid, x_init,y_init, hue=0, sat=1):
        self.id = zwkid
        self.x_init=x_init
        self.y_init=y_init
        self.x_pos=x_init
        self.y_pos=y_init
        self.x_prev=x_init
        self.y_prev=y_init
        self.hsv=(hue,sat,0) # initialise as a dim value

"""
This class shows any natural and unnatural boundaries for the environment
"""
class Borders:
    x_min=0
    y_min=0
    x_max=100
    y_max=100
    def __init__(self, xmi,ymi,xma,yma): #isn't that a dumb constructor syntax, heh?
        self.x_min=xmi
        self.y_min=ymi
        self.x_max=xma
        self.y_max=yma

# useful shortcut
scene = bpy.context.scene

side = 10
borders = Borders(0,0,side,side)
ani = bpy.data.objects['Sphere']
x_init, y_init = [side//2,side//2]
home = [x_init, y_init]
alf0 = Zwierzak('alf0',x_init,y_init, hue=0,sat=1)
alfs = [alf0]

number_of_frame = 0

for it in range(250):
    for alf in alfs:
        alf = updatePosition(alf,alfs,home[0],home[1])
        alf = handleColisions(alf,borders,alfs)
        ani.location = (alf.x_pos,alf.y_pos,0)
        ani.keyframe_insert(data_path="location", index=-1)
            # print(plane[alf.x_pos,alf.y_pos])
        number_of_frame += 1
