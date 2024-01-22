from pygame import *
from circle import Circle
from wall import Wall
from polygon import Polygon
import numpy as np
import contact, random, math
from forces import Gravity

init()

fps = 60
dt = 1/fps
clock = time.Clock()
time=0

message_font = font.SysFont('ariel', size = 25, bold = False, italic = False)
 
frame_count = 0
frame_rate = 60
start_time = 90

screen = display.set_mode([800,600])

#Colors
GREEN=[124,252,0]
GREY=[200,200,200]
DARKGREY=[38,38,38]
WHITE=[255,255,255]
BLUE=[0,0,255]
LIGHTBLUE = [152,245,255]
PINK = [255,100,180]
PURPLE = [155,48,255]
ORANGE = [255,128,0]
YELLOW = [255,215,0]
RED=[255,0,0]
BLACK = [0,0,0]

walls = []
topWall = Wall([0,5],[800,5], GREY,5)
bottomWall = Wall([0,595],[800,595], GREY,5)
walls.append(topWall)
walls.append(bottomWall)

#grav_wall = Wall([800,0],[800,600], PURPLE, 100)
gravWalls = []

player = Circle(radius = 20,pos=[80,300], color = ORANGE, mass = 15, vel=[100,0])

forces=[]
shapes=[]
shapes.append(player)
forces.append(Gravity(objects = shapes, acc = [0,-980]))

def spawnGravWall(range):
    gravWalls.append(Wall([800,range[0]],[800,range[1]], PURPLE, 300))

def change_Grav(temp):
    forces.clear()
    grav = Gravity(objects=shapes, acc = [0,temp])
    forces.append(grav)

    return grav.acc[1]

wallObs=[]
#controls random generation of wall obstacles
def wallGenerate(range, playerXPos):
        #generate vertical wall
        x_val = random.randint(400,795)
        y_1 = random.randint(range[0],range[1]-50)
        
        wallObs.append(Circle(radius = 100,pos=[x_val,y_1], color = PINK, mass = 500, vel=[100,0]))

bits = []
#controls random generation of bits
def bitsGenerate(points, range):
    spawn =random.randint(1,1000)
    if spawn >= 1 and spawn <= 9:
        #spawn bonus life bit
        bits.append((Polygon(offsets=[[0,0], [20, 0], [10,-20]], pos = [805,random.randint(range[0],range[1])],avel=1, color=YELLOW, normals_length=0, vel=[random.randint(200+points, 250+points), 0])))
    elif spawn >= 10 and spawn <= 600:
        #spawn point bit
        bits.append((Polygon(offsets=[[0,0], [20, 0], [10,-20]], pos = [805,random.randint(range[0],range[1])],avel=5, color=LIGHTBLUE, normals_length=0, vel=[random.randint(40+points, 100+points), 0])))
    elif spawn >=601:
        #spawn damage bit
        bits.append((Polygon(offsets=[[0,0], [20, 0], [15,-20]], pos = [805,random.randint(range[0],range[1])],avel=3, color=RED, normals_length=0, vel=[random.randint(4+points, 100+points), 0])))

##EVENT LOOP##
points = 0
health = 100
lives = 3
spawnRateBits = 0
spawnGravZone = 0
spawnWall = 0
screenRange = [5,595]

grav_value = 0
tempGrav = 0

gameover = False
wallChanged = False
start = False
running = True

while running:
    for e in event.get():
        if e.type == QUIT:
            running = False

    if not start:
        #Starting screen with rules for game
        rules_title=message_font.render("HOW TO PLAY", True, RED)
        rules_controls=message_font.render("Move around with the arrow keys", True,WHITE)
        rules_obstacles=message_font.render("Watch out for obstacles", True,WHITE)
        rules_obsWall=message_font.render("Circles will spawn and block your path", True,WHITE)
        rules_obsGrav=message_font.render("Purple zones have a random gravity force while within them", True,WHITE)
        rules_bound=message_font.render("The more points you have the narrower the path will get!",True,WHITE)
        rules_offScreen=message_font.render("Stay on the screen, going out of bounds will damage your health",True,WHITE)
        rules_blueBits=message_font.render("Collect the blue bits for points",True,WHITE)
        rules_redBits=message_font.render("Hitting the red bits will damage your health",True,WHITE)
        rules_goldBits=message_font.render("Gold bits will give you an extra life",True,WHITE)
        start_message = message_font.render("PRESS SPACE TO START",True,RED)
        keys = key.get_pressed()
        if keys[K_SPACE]:
            start = True


    ##DRAW##
    screen.fill(BLACK)
    if not start:
        #display rules on start screen
        screen.blit(rules_title,[400 - (rules_title.get_width()/2), 100])
        screen.blit(rules_controls,[400 - (rules_controls.get_width()/2), 130])
        screen.blit(rules_obstacles,[400 - (rules_obstacles.get_width()/2), 160])
        screen.blit(rules_obsWall,[400 - (rules_obsWall.get_width()/2), 190])
        screen.blit(rules_obsGrav,[400 - (rules_obsGrav.get_width()/2), 220])
        screen.blit(rules_bound,[400 - (rules_bound.get_width()/2), 250])
        screen.blit(rules_offScreen,[400 - (rules_offScreen.get_width()/2), 280])
        screen.blit(rules_blueBits,[400 - (rules_blueBits.get_width()/2), 310])
        screen.blit(rules_redBits,[400 - (rules_redBits.get_width()/2), 340])
        screen.blit(rules_goldBits,[400 - (rules_goldBits.get_width()/2), 370])
        screen.blit(start_message, [400 - (start_message.get_width()/2), 500])

    if start and not gameover:
        for w in walls:
            w.draw(screen)

        for gw in gravWalls:
            gw.draw(screen)

        player.draw(screen)

        for b in bits:
            b.draw(screen)
        
        for w in wallObs:
            w.draw(screen)

        #TEXT#
        points_message = message_font.render(f"Lives: {lives}    Health: {health}    Points: {points}",True, BLUE)
        screen.blit(points_message, [790 - (points_message.get_width()), 10])  


        ##PHYSICS##
        #clear and apply gravity
        player.clear_force()

        for f in forces:
            f.apply()
        
        #player in test wall area
        for gw in gravWalls:
            if player.pos[0] >= gw.point1[0] - gw.width/2 and player.pos[0] <= gw.point1[0]+gw.width/2:
                grav_value = change_Grav(tempGrav)
            else:
                player.vel = [0,0]
                grav_value = change_Grav(0)

        #player hits bits
        for b in bits:
            c = contact.circle_polygon(player,b,restitution=1)
            if c.overlap >=0:
                if b.color == LIGHTBLUE:
                    points+=1
                    wallChanged = False
                elif b.color == RED:
                    health -= 5
                elif b.color == YELLOW:
                    lives +=1
                bits.remove(b)

        #player hits border walls
        c=contact.circle_wall(player,bottomWall,-player.radius-bottomWall.width, restitution=0.5)
        if c.overlap <= 0:
            c.resolveNeg()
        
        c=contact.circle_wall(player,topWall, player.radius+topWall.width, restitution=0.5)
        if c.overlap >= 0:
            c.resolvePos()
        
        #player hits circle obstacles
        for w in wallObs:
            c=contact.circle_circle(player, w, restitution=0.5)
            if c.overlap >= 0:
                c.resolvePos()

        #player velocity is affected by points they have
        player.vel[0] = 50 + (points/2)

        #UPDATE#
        player.update(dt)

        for gw in gravWalls:
            gw.update(dt)

        for b in bits:
            b.update(dt)
        
        for w in wallObs:
            w.update(dt)


        ##GAME MECHANICS##
        # Calculate total seconds
        total_seconds = frame_count // frame_rate
        # Divide by 60 to get total minutes
        minutes = total_seconds // 60
        # Use modulus to get seconds
        seconds = total_seconds % 60
        #ADJUST TO INCLUDE MILLISECONDS
        timer = message_font.render(f"{minutes}:{seconds}", True,BLUE)
        screen.blit(timer, [10, 10])

        if spawnRateBits > 0:
            spawnRateBits -= (1 + (points/8))

        #move gravity zone while not spawning new one
        if spawnGravZone > 0:
            for gw in gravWalls:
                gw.point1[0] -= 1
                gw.point2[0] -= 1

                gw.update_pos_normal()

            spawnGravZone -= 1
        
        #if not spawning new wall, move current walls
        if spawnWall > 0:
            spawnWall -= 1

        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
        frame_count += 1

        #spawn polgyons
        if spawnRateBits <= 0:
            spawnRateBits = 150
            bitsGenerate(points, screenRange)

        #despawn if offscreen
        for b in bits:
            if b.pos[0] < -10:
                bits.remove(b)

        #change thickness of top/bottom wall with point value
        if points % 5 == 0 and not wallChanged and topWall.width < 225:
            topWall.width += 5
            bottomWall.width += 5

            #adjust range of availible path space
            screenRange = [topWall.width, 600-bottomWall.width]
            #adjust wall pos so entire wall stays on screen
            topWall.point1[1] += 2
            topWall.point2[1] += 2

            bottomWall.point1[1] -= 2
            bottomWall.point2[1] -= 2

            wallChanged = True

        #change gravity value and spawn new wall
        if spawnGravZone <= 0:
            tempGrav =  random.randint(-980, 980)
            gravWalls.clear()
            spawnGravWall(screenRange)
            spawnGravZone = 900
        
        grav_mes = message_font.render(f"Gravity: {(grav_value*-1)/10}",True, BLUE)
        screen.blit(grav_mes, [790 - (grav_mes.get_width()), 100]) 

        #spawn wall object
        if spawnWall <= 0:
            wallGenerate(screenRange, player.pos[0])
            spawnWall = 400

            if len(wallObs) > 2:
                wallObs.pop(0)

        #player moves horizontally and vertically with arrow keys
        keys = key.get_pressed()
        if keys[K_LEFT]:
            player.pos[0] -= 5
        if keys[K_RIGHT]:
            player.pos[0] += 5
        if keys[K_UP]:
            player.pos[1] -= 7
        if keys[K_DOWN]:
            player.pos[1] += 7

        #if player goes off left side, health takes 30 damage, screen cleared, player respawned at start pos
        if player.pos[0] < -30:
            bits.clear()
            health -= 30
            player.pos = [80,300]
            forces.clear()
        
        #if health reaches 0, lose life, screen cleared, player respawned at start pos
        if health <= 0:
            lives -= 1
            health = 100
            player.pos = [80,300]
            bits.clear()
            forces.clear()
            wallObs.clear()

        #game over if all lives are lost
        if lives < 0:
            gameover = True

    if gameover:

        over_message = message_font.render(f"GAME OVER!   Score: {points}   Time: {minutes}:{seconds}", True, WHITE)
        screen.blit(over_message,[400 - (over_message.get_width()/2),195])

        restart_message = message_font.render("press SPACE to restart       press ESC to quit", True, WHITE)
        screen.blit(restart_message,[400 - (restart_message.get_width()/2),295])

        keys = key.get_pressed()
        if keys[K_SPACE]:
            #restart game
            points = 0
            health = 100
            lives = 3
            time = 0
            frame_count = 0
            frame_rate = 60
            start_time = 90
            spawnRateBits = 0
            spawnGravZone = 0
            topWall.width = 5
            topWall.point1[1]=5
            topWall.point2[1]=5
            bottomWall.width = 5
            bottomWall.point1[1]=595
            bottomWall.point2[1]=595

            gameover = False
            start = True
        if keys[K_ESCAPE]:
            running = False


    #update the screen
    display.update()
    #frame rate
    clock.tick(fps)