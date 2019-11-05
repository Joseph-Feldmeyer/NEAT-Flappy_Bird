'''
flappy_bird.py 
~~~
Create the flappy bird game. 
Create a NN using NEAT for the game. 

https://github.com/techwithtim/NEAT-Flappy-Bird
'''


# Import libraries
import pygame
import random
import os
import time
import neat

# Initialize pygame and pygame fonts
pygame.init()

# Define global constants
WIN_WIDTH = 282
WIN_HEIGHT = 512
FLOOR = WIN_HEIGHT - 112
BG_VEL = 3
STAT_FONT = pygame.font.SysFont("comicsans", 25)
END_FONT = pygame.font.SysFont("comicsans", 35)


# Load main window
WIN = pygame.display.set_mode( (WIN_WIDTH, WIN_HEIGHT) )
pygame.display.set_caption("Flappy Bird")

# Load images
pipe_img = pygame.image.load(os.path.join("imgs", "pipe.png"))
bg_img = pygame.image.load(os.path.join("imgs", "bg.png"))
bird_images = [
    pygame.image.load(os.path.join("imgs", "bird" + str(x) + ".png"))
    for x in range(1,4) ]
base_img = pygame.image.load(os.path.join("imgs", "base.png"))


# Create classes

## Bird
class Bird:

    ### Variables
    MAX_ROTATION = 25
    IMGS = bird_images
    ROT_VEL = 20
    ANIMATION_TIME = BG_VEL

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0           # degrees to tilt the image
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -7.2
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        ### For downward acceleration
        displacement = self.vel * (self.tick_count) + \
            0.5 * (2.5) * (self.tick_count)**2  # Calculate displacement

        ### Terminal velocity
        if displacement >= 8:
            displacement = 8

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:                   # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        ### For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        else:
            self.img = self.IMGS[0]
            self.img_count = 0

        # Stop flapping when nose diving
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        # tilt the bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        # Find the actual pixels fo the bird image
        return pygame.mask.from_surface(self.img)


## Pipe
class Pipe():
    GAP = 100

    def __init__(self, x):
        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        # Index function for if bird passed the pipe 
        self.passed = False

        # Set the height of the pipe 
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, FLOOR-self.GAP-50)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= BG_VEL

    def draw(self, win):
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom)) 

    def collide(self, bird, win):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
        
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if b_point or t_point:
            return True

        return False


## Base
class Base():

    ### Define variables
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= BG_VEL
        self.x2 -= BG_VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y)) 



    
# Define functions

## Rotate and draw bird image
def blitRotateCenter(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    surf.blit(rotated_image, new_rect.topleft)

    
## Draw Window
def draw_window(win, bird, pipes, base, score):

    ### Draw the background
    win.blit(bg_img, (0,0))
    ### Draw pipes
    for pipe in pipes:
        pipe.draw(win)
    ### Draw the base
    base.draw(win) 

    ### Draw the bird 
    bird.draw(win)

    ### Score
    score_label = STAT_FONT.render("Score: " + str(score), 1,
                                   (255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width()-15, 10))

    pygame.display.update()

    
## Main
def main():
    global WIN, WIN_WIDTH, WIN_HEIGHT
    
    ### Create bird 
    bird = Bird(WIN_WIDTH//4, WIN_HEIGHT//2)

    ### Create base
    base = Base(FLOOR)
    ### Create pipes
    pipes = [Pipe(WIN_WIDTH)]
    ### Create score
    score = 0
    
    ### Create clock
    clock = pygame.time.Clock()

    ### Main loop
    run = True
    while run:
        clock.tick(30)

        # --- # Move the bird # --- #
        bird.move()
        # --- # Move the bird # --- #

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

            # --- # Jump the bird # --- #
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                bird.jump()
            # --- # Jump the bird # --- #

        # Move the base
        base.move()

        
        # Move the pipes
        rem=[]
        add_pipe = False
        for pipe in pipes:
            pipe.move()

        # Check for collision
        if pipe.collide(bird, WIN):
            print("Your score is: ", score)
            run = False
            pygame.quit()
            quit()
            

        # Check if pipe is off of screen 
        if pipe.x + pipe.PIPE_TOP.get_width() < 0:
            rem.append(pipe)

        # Check if pipe was passed
        if not pipe.passed and pipe.x < bird.x:
            pipe.passed = True
            add_pipe = True

        if add_pipe:
            score += 1
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        # Check if bird still on screen
        if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -10:
            print("Your score is: ", score)
            run = False
            pygame.quit()
            quit()
        

        # Draw the frame 
        draw_window(WIN, bird, pipes, base, score) 


main()

