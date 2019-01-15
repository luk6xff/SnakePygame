import pygame
import random
import os
from collections import namedtuple, defaultdict
from collections import deque
from operator import add,mul

# resources taken from:
#  http://www.biryuk.com/2015/05/free-snake-sprites.html
#  https://openclipart.org/detail/265429/brick-wall
#  http://texturelib.com/texture/?path=/Textures/grass/grass/grass_grass_0121
#  https://all-free-download.com/free-photos/download/snake_skin_texture_02_hd_pictures_169872_download.html

screen_width = 900
screen_height = 600
sprite_size = namedtuple('sprite_size', ['x', 'y'])(30, 30)
screen_texture_size = (sprite_size.x, sprite_size.y, screen_width - sprite_size.x, screen_height - sprite_size.y)



class Game:

    DIRECTIONS = {'right':(1,0), 'left':(-1,0), 'up':(0,-1), 'down':(0,1)}
    FPS = 4

    def __init__(self):
        #os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        self.ctx = {
                    'screen': pygame.display.set_mode((screen_width, screen_height)),
                    'res_holder': defaultdict()
                   }

        pygame.display.set_caption('retro snake game')
        self.clock = pygame.time.Clock() 
        self.load_resources('resources')

        # Game states dictionary

        self.states = {'menu':self.menu, 'init':self.init, 'play':self.play, 'pause':self.pause, 'over':self.game_over, 'exit':self.exit}
        self._current_state = 'menu'

    def _set_state(self, state):
        if state in self.states.keys():
            self._current_state = state
        else:
            raise ValueError("Invalid state: {} cannot be set! Available game states are: {}".format(state).format(''.join(self.states)))
        

    
    def _create_entities(self):
        """
        Creates game objects (Snake, apples, stones)
        """
        self.wall = []
        self.draw_wall()
        self.snake = Snake(((screen_width//2),(screen_height//2)))
        self.stones = Stone()
        self.apples = Apple()
        self.stones.create(self) # Create one stone
        self.apples.create(self) # Create one apple


    def draw_wall(self):
        '''
        Creates wall around the map (TODO - reading map from file - specific to level)
        '''
        self.wall.clear()
        for x in range(0, screen_width, sprite_size.x):
            a = (x, 0)
            b = (x, screen_height-sprite_size.y)
            self.ctx['screen'].blit(self.ctx['res_holder']['sprite'].WALL, a)
            self.ctx['screen'].blit(self.ctx['res_holder']['sprite'].WALL, b)
            self.wall.append(a)
            self.wall.append(b)
        for y in range(0, screen_height, sprite_size.y):
            a = (0, y)
            b = (screen_width-sprite_size.x, y)
            self.ctx['screen'].blit(self.ctx['res_holder']['sprite'].WALL, a)
            self.ctx['screen'].blit(self.ctx['res_holder']['sprite'].WALL, b)
            self.wall.append(a)
            self.wall.append(b)

    def load_resources(self, res_path):
        """
        Loads all the game resources from the given path
        """

        def get_path(entity_path):
            return os.path.join(res_path, entity_path)

        Colors = namedtuple('Color', ['white', 'black', 'red', 'light_red', 'dark_green'])
        self.ctx['res_holder']['color'] = Colors((255,255,255), (0,0,0), (255,0,0), (155,0,0), (0,120,0))


        Sprites = namedtuple('Sprite', ['HEAD', 'TAIL', 'BODY', 'TURN', 'APPLE', 'STONE', 'DIAMOND', 'WALL', 'game_background', 'game_texture'])
        self.ctx['res_holder']['sprite'] = Sprites(pygame.transform.scale(pygame.image.load(get_path('snake_head.png')), sprite_size),
                                                   pygame.transform.scale(pygame.image.load(get_path('snake_tail.png')), sprite_size),
                                                   pygame.transform.scale(pygame.image.load(get_path('snake_body.png')), sprite_size),
                                                   pygame.transform.scale(pygame.image.load(get_path('snake_turn.png')), sprite_size),
                                                   pygame.transform.scale(pygame.image.load(get_path('apple.png')), sprite_size),
                                                   pygame.transform.scale(pygame.image.load(get_path('stone.png')), sprite_size),
                                                   pygame.transform.scale(pygame.image.load(get_path('diamond.png')), sprite_size),
                                                   pygame.transform.scale(pygame.image.load(get_path('wall.png')), sprite_size),
                                                   pygame.image.load(get_path('game_background.jpg')),
                                                   pygame.image.load(get_path('game_texture.jpg')))
                                                   
        Music = namedtuple('Music', ['POINT', 'HIT'])
        self.ctx['res_holder']['music'] = Music(pygame.mixer.Sound(get_path("point.wav")),
                                                pygame.mixer.Sound(get_path("hit.wav")))
    
        Font = namedtuple('Font', ['font'])
        self.ctx['res_holder']['font'] = Font(get_path('font.ttf'))

        pygame.mixer.music.load(get_path('music.mp3'))
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(loops=-1)

    def draw_text(self, text, color, size, x, y):
        """
        Draws a text on a screen area
        """  
        font = pygame.font.Font(self.ctx['res_holder']['font'].font, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.ctx['screen'].blit(text_surface, text_rect)


    def generate_random_location(self):
        """
        Returns a random location of the sprite in the area
        """  
        snake = self.snake.get_locations()
        stones = self.stones.get_locations()
        apples = self.apples.get_locations()
        already_taken_space = snake + stones + apples + self.wall
        xy = (0,0)
        while True:
            xy = (random.randrange(0, screen_width, sprite_size.x), random.randrange(0, screen_height, sprite_size.y))
            if xy not in already_taken_space:
                break
        return xy

    def check_collision(self):
        """
        Checks if collision between snake and other entities occured
        """   
        snake = self.snake.get_locations()
        stones = self.stones.get_locations()
        apples = self.apples.get_locations()

        if not(snake[0][0] > screen_texture_size[0] and snake[0][0] < screen_texture_size[2] \
           and snake[0][1] > screen_texture_size[1] and snake[0][1] < screen_texture_size[3]):
            self.ctx['res_holder']['music'].HIT.play()
            self._set_state('over') 
        # check if collision with stone occured
        if snake[0] in stones:
            self.ctx['res_holder']['music'].HIT.play()
            self._set_state('over') 
        # check collision with apples
        try:
            i = apples.index(snake[0])
            self.snake.grow()
            self.ctx['res_holder']['music'].POINT.play()
            self.points += 10  # TODO different for other entities
            self.apples.destroy(i)
            self.apples.create(self)
        except ValueError:
            pass

    def score(self, score):
        """
        Updates the score value on the screen
        """       
        font = pygame.font.Font(self.ctx['res_holder']['font'].font, 30)
        text = font.render('SCORE: {}'.format(score), True, self.ctx['res_holder']['color'].black)
        self.ctx['screen'].blit(text, [30,30])

    #### STATES callbacks ####
    def init(self):        
        self.points = 0
        self.speed = Game.FPS
        self._create_entities()
        self._set_state('play')

    def play(self):
        self.handle_event()
        self.update()
        # Do not draw next step if state changed already
        if self._current_state is not 'play':
            return
        self.draw()
        self.clock.tick(self.speed) 

    def pause(self):        
        self.draw_text("PAUSE", self.ctx['res_holder']['color'].black, 60, screen_width/2, screen_height/2 -130)
        self.draw_text("Press P to continue", self.ctx['res_holder']['color'].black, 30, screen_width/2, screen_height/2)
        pygame.display.update()
        
        while self._current_state == 'pause':      
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self._set_state('play')

    def menu(self):
        buttons = [Button(self.ctx['screen'], "PLAY", (screen_width//2, screen_height//2 - 50), lambda: self._set_state('init')),
                   Button(self.ctx['screen'], "QUIT", (screen_width//2, screen_height//2 + 50), lambda: self._set_state('exit'))]
        
        while self._current_state == 'menu':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._set_state('exit')
                elif event.type == pygame.MOUSEBUTTONDOWN:              
                    for b in buttons:
                        b.mouse_button_down()
            
            self.ctx['screen'].blit(self.ctx['res_holder']['sprite'].game_texture, (0,0))
            self.draw_text("RETRO SNAKE GAME", self.ctx['res_holder']['color'].black, 50, screen_width//2, 10)
            self.draw_text("by luk6xff (2019)", self.ctx['res_holder']['color'].black, 20, screen_width-150, screen_height-40)
            for b in buttons:
                b.draw()                       
            pygame.display.update()
            self.clock.tick(50)
    
    def game_over(self):
        buttons = [Button(self.ctx['screen'], "MENU", (screen_width//2, screen_height//2 - 100), lambda: self._set_state('menu')),
                   Button(self.ctx['screen'], "PLAY AGAIN", (screen_width//2, screen_height//2), lambda: self._set_state('init')),
                   Button(self.ctx['screen'], "QUIT", (screen_width//2, screen_height//2 + 100), lambda: self._set_state('exit')) ]
        
        while self._current_state == 'over': 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._set_state('exit')
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self._set_state('exit')
                    if event.key == pygame.K_c:
                        self._set_state('init')
                elif event.type == pygame.MOUSEBUTTONDOWN:              
                    for b in buttons:
                        b.mouse_button_down()
           
            self.ctx['screen'].blit(self.ctx['res_holder']['sprite'].game_texture, (0,0))
            self.draw_text("SCORE: " + str(self.points), self.ctx['res_holder']['color'].black, 50, screen_width//2, 0)
                    
            for b in buttons:
                b.draw()  
            pygame.display.update()         
            self.clock.tick(50)

    def exit(self):
        pygame.quit()
        pygame.font.quit()
        quit()
    #### STATES callbacks end ####


    ### Gameplay state main methods ###
    def handle_event(self):
        """
        Responsible handling all the external events during the play state
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                self._set_state('exit')
                break
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT):
                    self.snake.update_direction(self.DIRECTIONS['left'])
                    break
                elif (event.key == pygame.K_RIGHT):
                    self.snake.update_direction(self.DIRECTIONS['right'])
                    break
                elif (event.key == pygame.K_UP):
                    self.snake.update_direction(self.DIRECTIONS['up'])
                    break 
                elif (event.key == pygame.K_DOWN):
                    self.snake.update_direction(self.DIRECTIONS['down'])
                    break
                if event.key == pygame.K_p:
                    self._set_state('pause')
                    break
                

    def update(self):
        """
        Responsible for updating game status 
        """
        self.snake.update()
        self.check_collision()


    def draw(self):
        """
        Responsible for redrawing all the whole screen during the play state
        """
        self.ctx['screen'].blit(self.ctx['res_holder']['sprite'].game_background, (0,0))
        self.draw_wall() 
        self.apples.draw(self.ctx)
        self.stones.draw(self.ctx)
        self.snake.draw(self.ctx)
        self.score(self.points)    
        pygame.display.update()


    def run(self):
        """
        Main run method of the game 
        """
        try: 
            while True:
                self.states[self._current_state]()
        except Exception as e:
            print(str(e))
            self.exit()



class Button():
    '''
    Utility Button class
    '''

    # colors taken from here https://www.webucator.com/blog/2015/03/python-color-constants-module/
    CYAN3 = (0, 205, 205)
    CADETBLUE3= (122, 197, 205)
    BLACK = (0, 0, 0)
    
    def __init__(self, screen, txt, location, action, bg=CYAN3, fg=BLACK, size=(270, 90), font_name="Segoe Print", font_size=30):
        self.color = bg  # the static (normal) color
        self.bg = bg  # actual game_background color, can change on mouseover
        self.fg = fg  # text color
        self.size = size
        self.screen = screen
        self.font = pygame.font.SysFont(font_name, font_size)
        self.txt = txt
        self.txt_surf = self.font.render(self.txt, 1, self.fg)
        self.txt_rect = self.txt_surf.get_rect(center=[s//2 for s in self.size])

        self.surface = pygame.surface.Surface(size)
        self.rect = self.surface.get_rect(center=location)

        self.call_back_ = action

    def draw(self):
        self.mouse_over()

        self.surface.fill(self.bg)
        self.surface.blit(self.txt_surf, self.txt_rect)
        self.screen.blit(self.surface, self.rect)

    def mouse_over(self):
        self.bg = self.color
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.bg = Button.CADETBLUE3 # mouseover color

    def mouse_button_down(self):
        pos = pygame.mouse.get_pos()    
        if self.rect.collidepoint(pos):
            self.call_back()

    def call_back(self):
        self.call_back_()



class Stone:
    
    def __init__(self):
        self.stones = []

    def create(self, game):
        new_stone = game.generate_random_location()
        self.stones.append(new_stone)

    def destroy(self, idx):
        del self.stones[idx]

    def get_locations(self):
        return self.stones
        
    def draw(self, ctx):
        for st in self.stones:
            ctx['screen'].blit(ctx['res_holder']['sprite'].STONE, (st[0], st[1]))
    

            
class Apple:
    
    def __init__(self):
        self.apples = []

    def create(self, game):
        new_apple = game.generate_random_location()
        self.apples.append(new_apple)
    
    def destroy(self, idx):
        del self.apples[idx]

    def get_locations(self):
        return self.apples
  
    def draw(self, ctx):
        for ap in self.apples:
            ctx['screen'].blit(ctx['res_holder']['sprite'].APPLE, (ap[0], ap[1]))



class Snake():
    
    Segment = namedtuple('Segment', ['direction', 'location'])

    def __init__(self, location):
        self.direction = Game.DIRECTIONS['right']
        self.last_direction = self.direction
        self.turns = deque()

        # Apply first 3 segments of the snake
        self.snake = [
                        Snake.Segment(self.direction, (location[0], location[1])),
                        Snake.Segment(self.direction, (location[0]-sprite_size.x, location[1])),
                        Snake.Segment(self.direction, (location[0]-sprite_size.x*2, location[1])),
                        Snake.Segment(self.direction, (location[0]-sprite_size.x*3, location[1]))
                     ]

    def _calc_next_position(self, segment_index, new_direction):
        new_location  = tuple(map(add, self.snake[segment_index].location, tuple(map(mul, new_direction, sprite_size))))
        self.snake[segment_index] = Snake.Segment(new_direction, new_location)

    def get_locations(self):
        return [seg.location for seg in self.snake]
    
    def update(self):

        # Did a snake direction changed before ?
        if self.last_direction != self.direction:
            # Add turn location to the turns queue
            self.turns.append(Snake.Segment(self.direction, self.snake[0].location))
            # Update direction of the head
            self.snake[0] = Snake.Segment(self.direction, self.snake[0].location)

        # Update snake's body position
        for i,seg in enumerate(self.snake):
            self._calc_next_position(i, seg.direction)
     
        # Check if there is any segment which should turn
        for i,seg in enumerate(self.snake):
            for j,turn in enumerate(self.turns):
                if seg.location == turn.location:
                    self.snake[i] = turn
                    # if this was tail, remove the first(left) turn from the turns queue
                    if (i == len(self.snake)-1 and j == 0):
                        self.turns.popleft()
                        #print(self.turns)
                        return

        self.last_direction = self.direction

    def grow(self):
        # TODO
        pass

    def update_direction(self, direction):
        if direction == Game.DIRECTIONS['right'] and self.direction == Game.DIRECTIONS['left']:
            return
        if direction == Game.DIRECTIONS['left'] and self.direction == Game.DIRECTIONS['right']:       
            return
        if direction == Game.DIRECTIONS['up'] and self.direction == Game.DIRECTIONS['down']:
            return
        if direction == Game.DIRECTIONS['down'] and self.direction == Game.DIRECTIONS['up']:       
            return
        self.direction = direction

    def draw(self, ctx):
        for i, seg in enumerate(self.snake):
            sprite = Snake.rotate_segment(seg, ctx['res_holder']['sprite'].BODY)
            #if seg in self.turns:
            #    sprite = Snake.rotate_segment(seg, ctx['res_holder']['sprite'].TURN)    # TODO for now let's use body for turns
            if i == 0:
                sprite = Snake.rotate_segment(seg, ctx['res_holder']['sprite'].HEAD)
            elif i == len(self.snake)-1:
                sprite = Snake.rotate_segment(seg, ctx['res_holder']['sprite'].TAIL)
            ctx['screen'].blit(sprite, seg.location)       

    @staticmethod
    def rotate_segment(segment, sprite):
        if segment.direction == Game.DIRECTIONS['right']:
            rotated_sprite = pygame.transform.rotate(sprite, 0)
        elif segment.direction == Game.DIRECTIONS['left']:
            rotated_sprite = pygame.transform.rotate(sprite, 180)
        elif segment.direction == Game.DIRECTIONS['up']:
            rotated_sprite = pygame.transform.rotate(sprite, 90)    
        elif segment.direction == Game.DIRECTIONS['down']:
            rotated_sprite = pygame.transform.rotate(sprite, 270)       
        return rotated_sprite

                    

    
if __name__ == "__main__":
    game = Game()
    game.run()


