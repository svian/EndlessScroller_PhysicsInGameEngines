from particle import Particle
from pygame import *
import numpy as np

class Circle(Particle):
    def __init__(self, radius=10, color=[255,255,255], width=0, **kwargs):
        self.radius = radius
        self.color = color
        self.width = width
        super().__init__(**kwargs) #send the rest of the arguments to the superclass constructor

    def draw(self, screen):
        draw.circle(screen, self.color, np.array(self.pos, int), int(self.radius), self.width)