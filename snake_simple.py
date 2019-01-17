import sys
import pygame
import random
import os
from collections import namedtuple


# -----OBJECTS-----
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
pygame.font.init()
pygame.mixer.init()
 
fps = 60
fpsClock = pygame.time.Clock()
speed = 10

score = 0
 
screen_width = 640
screen_height = 480
grid_size = (20, 20)
screen = pygame.display.set_mode((screen_width, screen_height))

DIRECTIONS = {'right':(1,0), 'left':(-1,0), 'up':(0,-1), 'down':(0,1)}
direction = DIRECTIONS['right']

Colors = namedtuple('Color', ['white', 'black', 'red', 'light_red', 'dark_green'])
colors = Colors((255,255,255), (0,0,0), (255,0,0), (155,0,0), (0,120,0))

Sprites = namedtuple('Sprite', ['HEAD', 'TAIL', 'BODY', 'TURN_RIGHT', 'TURN_LEFT', 'APPLE', 'STONE', 'DIAMOND', 'WALL', 'game_background', 'game_texture'])
sprites = Sprites(pygame.transform.scale(pygame.image.load('resources/snake_head.png'), grid_size),
                  pygame.transform.scale(pygame.image.load('resources/snake_tail.png'), grid_size),
                  pygame.transform.scale(pygame.image.load('resources/snake_body_straight.png'), grid_size),
                  pygame.transform.scale(pygame.image.load('resources/snake_body_right.png'), grid_size),
                  pygame.transform.scale(pygame.image.load('resources/snake_body_left.png'), grid_size),
                  pygame.transform.scale(pygame.image.load('resources/apple.png'), grid_size),
                  pygame.transform.scale(pygame.image.load('resources/stone.png'), grid_size),
                  pygame.transform.scale(pygame.image.load('resources/diamond.png'), grid_size),
                  pygame.transform.scale(pygame.image.load('resources/wall.png'), grid_size),
                  pygame.image.load('resources/game_background.jpg'),
                  pygame.image.load('resources/game_texture.jpg'))

Music = namedtuple('Music', ['POINT', 'HIT'])
music = Music(pygame.mixer.Sound("resources/point.wav"),
              pygame.mixer.Sound("resources/hit.wav"))

Font = namedtuple('Font', ['font'])
fonts = Font('resources/font.ttf')

# Setup music
pygame.mixer.music.load('resources/music.mp3')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(loops=-1)

exit_game = False

wall = []

# -----FUNCTIONS-----
def draw_wall():
    wall.clear()
    for x in range(0, screen_width, grid_size[0]):
        a = (x, 0)
        b = (x, screen_height-grid_size[1])
        screen.blit(sprites.WALL, a)
        screen.blit(sprites.WALL, b)
        wall.append(a)
        wall.append(b)
    for y in range(0, screen_height, grid_size[1]):
        a = (0, y)
        b = (screen_width-grid_size[0], y)
        screen.blit(sprites.WALL, a)
        screen.blit(sprites.WALL, b)
        wall.append(a)
        wall.append(b)

def draw_text(text, color, size, x, y):
    font = pygame.font.Font(fonts.font, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)

def generate_random_location():
    """
    Returns a random location of the sprite in the area
    """  
    snake_location = [d[1] for d in snake]
    already_taken_area = snake_location + stones + apples + wall
    xy = (0,0)
    while True:
        xy = (random.randrange(0, screen_width, grid_size[0]), random.randrange(0, screen_height, grid_size[1]))
        if xy not in already_taken_area:
            break
    return xy

def update_direction(direct):
    if direct == DIRECTIONS['right'] and direction == DIRECTIONS['left']:
        return
    if direct == DIRECTIONS['left'] and direction == DIRECTIONS['right']:       
        return
    if direct == DIRECTIONS['up'] and direction == DIRECTIONS['down']:
        return
    if direct == DIRECTIONS['down'] and direction == DIRECTIONS['up']:       
        return
    direction = direct

def rotate_segment(direct, sprite):
    rotated_sprite = None
    if direct == DIRECTIONS['right']:
        rotated_sprite = pygame.transform.rotate(sprite, 0)
    elif direct == DIRECTIONS['left']:
        rotated_sprite = pygame.transform.rotate(sprite, 180)
    elif direct == DIRECTIONS['up']:
        rotated_sprite = pygame.transform.rotate(sprite, 90)    
    elif direct == DIRECTIONS['down']:
        rotated_sprite = pygame.transform.rotate(sprite, 270)       
    return rotated_sprite

# States
def pause():        
    draw_text("PAUSE", colors.black, 60, screen_width/2, screen_height/2 -130)
    draw_text("Press P to continue", colors.black, 30, screen_width/2, screen_height/2)
    pygame.display.update()
    
    while True:      
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return

def game_over():
    while True: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game = True
                return  
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    exit_game = True
                    return    
                if event.key == pygame.K_RETURN:
                    return
        
        screen.blit(sprites.game_texture, (0,0))
        draw_text("SCORE: " + str(score), colors.black, 50, screen_width//2, 0)
        draw_text("Press ENTER to play again or Q to exit the game", colors.black, 20, screen_width//2, screen_height//2)
        pygame.display.update()         
        fpsClock.tick(fps)

# -----MAIN-----
while exit_game == False:

    # init game
    draw_wall()
    direction = DIRECTIONS['right']
    snake = [
                (direction, (screen_width//2,                screen_height//2)),
                (direction, (screen_width//2-grid_size[0],   screen_height//2)),
                (direction, (screen_width//2-2*grid_size[0], screen_height//2)),
                (direction, (screen_width//2-3*grid_size[0], screen_height//2)),
            ]
    stones = []
    apples = []
    frame = 0
    score = 0

    # generate some stones and apples
    for s in range(5):
        stones.append(generate_random_location())
    apples.append(generate_random_location())

    while True:
        screen.blit(sprites.game_background, (0, 0))
        d = direction
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game = True
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT):
                    d = DIRECTIONS['left']
                elif (event.key == pygame.K_RIGHT):
                    d = DIRECTIONS['right']
                elif (event.key == pygame.K_UP):
                    d = DIRECTIONS['up']
                elif (event.key == pygame.K_DOWN):
                    d = DIRECTIONS['down']
                if event.key == pygame.K_p:
                    pause()
        if d == DIRECTIONS['right'] and direction == DIRECTIONS['left']:
            pass
        elif d == DIRECTIONS['left'] and direction == DIRECTIONS['right']:       
            pass
        elif d == DIRECTIONS['up'] and direction == DIRECTIONS['down']:
            pass
        elif d == DIRECTIONS['down'] and direction == DIRECTIONS['up']:       
            pass
        else:
            direction = d        
    
        #### Update 
        # update per speed parameter
        if frame % speed == 0:
            
                        # update second segment with 
            snake[0] = (snake[0][0], snake[0][1])
            # add new head
            snake.insert(0, (direction, (snake[0][1][0]+direction[0]*grid_size[0],
                                        snake[0][1][1]+direction[1]*grid_size[1])))
            # Check colissions
            snake_location = [d[1] for d in snake[1:]]
            dead_area = set(snake_location + stones + wall)
            if snake[0][1] in dead_area:
                music.HIT.play()
                break  

            # Check if we ate the apple
            grow = False
            if snake[0][1] in apples:
                idx = apples.index(snake[0][1])
                del apples[idx]
                apples.append(generate_random_location())
                grow = True
                music.POINT.play()
                score += 10
            # remove last segment if snake didn't eat an apple 
            if not grow:
                snake.pop()

        #### Draw
        draw_wall()
        # apples
        for ap in apples:
            screen.blit(sprites.APPLE, (ap[0], ap[1]))
        for st in stones:
            screen.blit(sprites.STONE, (st[0], st[1]))
        # snake
        for i, seg in enumerate(snake):
            sprite = rotate_segment(seg[0], sprites.BODY)
            #sprite = rotate_segment(seg, ctx['res_holder']['sprite'].TURN)    # TODO use TURN sprite for turns
            if i == 0:
                sprite = rotate_segment(seg[0], sprites.HEAD)
            elif i == len(snake)-1:
                sprite = rotate_segment(seg[0], sprites.TAIL)
            screen.blit(sprite, seg[1])

        # update the score value on the screen 
        font = pygame.font.Font(fonts.font, 30)
        text = font.render('SCORE: {}'.format(score), True, colors.black)
        screen.blit(text, grid_size) 

        # Update display  
        pygame.display.update()
        pygame.display.flip()
        fpsClock.tick(fps)
        frame += 1

    if exit_game is not True:
        game_over()

# Close game
pygame.quit()
pygame.font.quit()
pygame.quit()
sys.exit()