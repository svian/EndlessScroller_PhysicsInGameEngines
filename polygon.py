import numpy as np
import math
from pygame import *
from particle import Particle
import pygame

def intvec(v):
    return[round(v.x),round(v.y)]

class Polygon(Particle):
    def __init__(self, offsets=[], color=[0,0,0], width=0, normals_length=0, **kwargs):
        self.offsets = np.array(offsets, float)
        self.color = color
        self.width = width
        self.normals_length = normals_length

        #calculate self.normals
        offsets1 = np.roll(self.offsets, 1, axis=0)
        self.local_normals = np.cross([0,0,1], self.offsets - offsets1)[:,0:2]
        self.local_normals /= np.linalg.norm(self.local_normals, axis=1).reshape(-1,1)

        self.normals = self.local_normals.copy()

        super().__init__(**kwargs)
        
        self.points = self.offsets.copy()
        self.update_points()
        
        
    def update_points(self):
        for i in range(len(self.points)):
            #self.points[i] = self.pos + self.offsets[i]
            self.points[i] = self.world(self.offsets[i])
            
    
    def update(self, dt):
        super().update(dt)
        self.update_points()
    
    def set_pos(self, pos):
        super().set_pos(pos)
        self.update_points()
    
    def delta_pos(self, delta):
        super().delta_pos(delta)
        self.update_points()
    
    def draw(self, screen):
        points = np.array(self.points, int)

        draw.polygon(screen, self.color, points, self.width)

        if self.normals_length > 0:
            for p, n in zip(points, self.normals):
                pygame.draw.line(screen, self.color, p, np.array(p+n*self.normals_length, float))

class UniformPolygon(Polygon):
    def __init__(self,density=1,offsets=[],pos=[0,0],**kwargs):
        #calculate mass, inertia, and mass x center of mass for each triangle
        #calculate total mass, interia of new center, and displacement of pivot point
        #adjust center and inertia
        super().__init__(**kwargs)