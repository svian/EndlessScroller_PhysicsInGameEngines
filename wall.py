from particle import Particle
import math
import numpy as np
import pygame

def intvec(v):
    return [round(v.x), round(v.y)]

def mag(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1])

class Wall(Particle):
    def __init__(self, point1=[0,0], point2=[0,0], color=[0,0,0],width=0):
        self.color = color
        self.point1 = np.array(point1, float)
        self.point2 = np.array(point2, float)
        self.width = width
        self.update_pos_normal()
        super().__init__(pos=self.pos)
    
    def update_pos_normal(self):
        self.pos = (self.point1 + self.point2)/2
        self.normal = np.cross([0,0,1], self.point2 - self.point1)[0:2]
        self.normal /= mag(self.normal)
    
    def draw(self, screen):
        pygame.draw.line(screen, self.color, np.array(self.point1, int), np.array(self.point2, int),self.width)
