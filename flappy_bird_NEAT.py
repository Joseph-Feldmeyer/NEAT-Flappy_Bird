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
import visualize
import pickle

# Initialize pygame and pygame fonts
pygame.init()

# Define global constants
WIN_WIDTH = 282
WIN_HEIGHT = 512
FLOOR = WIN_HEIGHT - 112
BG_VEL = 3
STAT_FONT = pygame.font.SysFont("comicsans", 25)
END_FONT = pygame.font.SysFont("comicsans", 35)
DRAW_LINES = True

# Restart generation counter
gen = 0 


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
def draw_window(win, birds, pipes, base, score, gen, pipe_ind):

    ### Initial gen setting
    if gen == 0:
        gen = 1
        
    ### Draw the background
    win.blit(bg_img, (0,0))
    ### Draw pipes
    for pipe in pipes:
        pipe.draw(win)
    ### Draw the base
    base.draw(win) 

    ### Draw the birds
    for bird in birds:
        # Draw the bird
        bird.draw(win)
        
        # draw lines from bird to pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win,
                                 (255,0,0),
                                 (bird.x + bird.img.get_width()//2,
                                   bird.y + bird.img.get_height()//2),
                                 (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()//2,
                                   pipes[pipe_ind].height),
                                 5)
                pygame.draw.line(win,
                                 (255,0,0),
                                 (bird.x + bird.img.get_width()//2,
                                   bird.y + bird.img.get_height()//2),
                                 (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()//2,
                                   pipes[pipe_ind].bottom),
                                 5)
            except:
                pass

            
    ### Score
    score_label = STAT_FONT.render("Score: " + str(score), 1,
                                   (255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width()-15, 10))

    ### generations
    score_label = STAT_FONT.render("Gens: " + str(gen-1), 1,
                                   (255,255,255))
    win.blit(score_label, (10,10))

    ### alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)), 1,
                                   (255,255,255))
    win.blit(score_label, (10,50))

    ### Update the display
    pygame.display.update()

    
## evaluate the genomes (previously main) 
def eval_genomes(genomes, config):
    global WIN, WIN_WIDTH, WIN_HEIGHT, gen
    gen += 1

    ### Create list holders for NNs, birds, genomes 
    nets = []
    birds = []
    ge = []

    for genome_id, genome in genomes:
        genome.fitness = 0      # Start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(WIN_WIDTH//4, WIN_HEIGHT//2))
        ge.append(genome) 

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
    while run and len(birds) > 0:
        clock.tick(30)
       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break 

        pipe_ind = 0
        if len(birds) > 0:
            # determine whether to use the first or second pipe
            # on screeen for the NN input
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width(): 
                pipe_ind = 1

        # increment bird fitness for every frame that it survives
        for x, bird in enumerate(birds):
            ge[x].fitness += 0.1
            bird.move()

            # Send the bird, top pipe, bottom pipe locations to the NN
            # determine whether to jump or not
            output = nets[birds.index(bird)].activate((bird.y,
                                                       abs(bird.y - pipes[pipe_ind].height),
                                                       abs(bird.y - pipes[pipe_ind].bottom) ))

            # Jump if over 0. 5
            if output[0] > 0.5:
                bird.jump()
            
        # Move the base
        base.move()

        
        # Move the pipes
        rem=[]
        add_pipe = False
        for pipe in pipes:
            pipe.move()

            # Check for collision
            for bird in birds:
                if pipe.collide(bird, WIN):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            # Check if pipe is off of screen 
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            # Check if pipe was passed
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            # Give more reward for passing through a pipe
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.y + bird.img.get_height()-10 >= FLOOR or bird.y < -10:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        # Draw the frame 
        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind) 

        # Break if score gets large enough
        if score > 100:
            pickle.dump(nets[0], open("best_pickle", "wb"))
            break

def run(config_file):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_file)

    # Create the population, which is top-level object for a NEAT run
    p = neat.Population(config)

    # Add a stdout reporter to show progress in terminal
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run for up to 50 generations
    winner = p.run(eval_genomes, 50)

    # Show final stats
    print('\nBest genome: \n{!s}'.format(winner))

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)

    

