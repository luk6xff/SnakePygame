import pygame
import random
import os
from collections import namedtuple, defaultdict


# resources taken from:
#  http://www.biryuk.com/2015/05/free-snake-sprites.html
#  https://openclipart.org/detail/265429/brick-wall
#  http://texturelib.com/texture/?path=/Textures/grass/grass/grass_grass_0121
#  https://all-free-download.com/free-photos/download/snake_skin_texture_02_hd_pictures_169872_download.html

screen_width = 900
screen_height = 600
sprite_size = namedtuple('sprite_size', ['x', 'y'])(30, 30) 
FPS = 10

class Game:

    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
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

        # Game variables
        self.states = ['intro', 'init', 'run', 'pause', 'over', 'exit']
        self.current_state = 'intro'
      
        self.game_exit = False
        self.game_over = False
        
        self.points = 0
        self.speed = FPS

        self.lead_x = screen_width/2 
        self.lead_y = screen_height/2 
        self.lead_x_change = sprite_size 
        self.lead_y_change = 0 
        
        self.snake = Snake(self.lead_x, self.lead_y)
        self.stones = Stone()
        self.apple = Apple(self.stones, self.snake)


    def load_resources(self, res_path):

        def get_path(entity_path):
            return os.path.join(res_path, entity_path)

        snake_colors = ['red', 'blue', 'purple']
        snake_color = snake_colors[0]

        Colors = namedtuple('Color', ['white', 'black', 'red', 'light_red', 'dark_green'])
        self.ctx['res_holder']['color'] = Colors((255,255,255), (0,0,0), (255,0,0), (155,0,0), (0,120,0))


        Sprites = namedtuple('Sprite', ['HEAD', 'TAIL', 'BODY', 'TURN', 'APPLE', 'STONE', 'DIAMOND', 'WALL', 'game_background', 'game_texture'])
        self.ctx['res_holder']['sprite'] = Sprites(pygame.transform.scale(pygame.image.load(get_path('snake_head_{}.png'.format(snake_color))), sprite_size),
                                                   pygame.transform.scale(pygame.image.load(get_path('snake_tail_{}.png'.format(snake_color))), sprite_size),
                                                   pygame.transform.scale(pygame.image.load(get_path('snake_body_{}.png'.format(snake_color))), sprite_size),
                                                   pygame.transform.scale(pygame.image.load(get_path('snake_turn_{}.png'.format(snake_color))), sprite_size),
                                                   pygame.transform.scale(pygame.image.load(get_path('apple.png')), sprite_size),
                                                   pygame.transform.scale(pygame.image.load(get_path('stone.png')), sprite_size),
                                                   pygame.transform.scale(pygame.image.load(get_path('diamond.png')), sprite_size),
                                                   pygame.transform.scale(pygame.image.load(get_path('wall.png')), sprite_size),
                                                   pygame.image.load(get_path('game_background.jpg')),
                                                   pygame.image.load(get_path('game_texture.jpg')))
                                                   
        Music = namedtuple('Music', ['POINT', 'HIT', 'EVOLUTION'])
        self.ctx['res_holder']['music'] = Music(pygame.mixer.Sound(get_path("sfx_point.wav")),
                                                pygame.mixer.Sound(get_path("sfx_hit.wav")),
                                                pygame.mixer.Sound(get_path("Star_Wars_-_Imperial_march.wav")))
    
        Font = namedtuple('Font', ['flup'])
        self.ctx['res_holder']['font'] = Font(get_path('flup.ttf'))

        pygame.mixer.music.load(get_path('music.mp3'))
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(loops=-1)

    def draw_text(self, text, color, size, x, y):
        font = pygame.font.Font(self.ctx['res_holder']['font'].flup, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.ctx['screen'].blit(text_surface, text_rect)


    def draw_wall(self):
        '''
        Creates wall around the map (TODO - reading map from file - specific to level)
        '''
        for x in range(screen_width):
            self.ctx['screen'].blit(self.ctx['res_holder']['sprite'].WALL, (x*sprite_size.x, 0))
            self.ctx['screen'].blit(self.ctx['res_holder']['sprite'].WALL, (x*sprite_size.x, screen_height-sprite_size.y))
        for y in range(screen_height):
            self.ctx['screen'].blit(self.ctx['res_holder']['sprite'].WALL, (0, y*sprite_size.y))
            self.ctx['screen'].blit(self.ctx['res_holder']['sprite'].WALL, (screen_width-sprite_size.x, y*sprite_size.y))


    # def button(text, x, y, width, height, inactive, active, text_color = self.black, action = None):
    #     cursor = pygame.mouse.get_pos()
    #     click = pygame.mouse.get_pressed()
        
    #     if (x + width > cursor[0] > x and y + height > cursor[1] > y):
    #         self.ctx.blit(ACTIVE_B, (x,y))
            
    #         if click[0] == 1 and action != None:
    #             if action == 'play' or action == 'again':
    #                 gameLoop()
    #             elif action == 'controls' or action == 'previous':
    #                 draw_controls()
    #             elif action == 'quit':
    #                 pygame.quit()
    #                 pygame.font.quit()
    #                 quit()
    #             elif action == 'menu':
    #                 draw_game_intro()
    #             elif action == 'next':
    #                 draw_controls_next()  
    #     else:
    #         ctx['screen'].blit(INACTIVE_B, (x,y))
    #     draw_text(text, text_color, int(round(height/2)), x + width/2, y + height/4)


    def score(self, score):
        font = pygame.font.Font(self.ctx['res_holder']['font'].flup, 25)
        text = font.render('SCORE: {}'.format(score), True, self.ctx['res_holder']['color'].black)
        self.ctx['screen'].blit(text, [20,20])

    def pause(self):
        
        self.draw_text("PAUSE", self.ctx['res_holder']['color'].black, 60, screen_width/2, screen_height/2 -130)
        self.draw_text("Press P to continue", self.ctx['res_holder']['color'].black, 30, screen_width/2, screen_height/2)
        pygame.display.update()
        
        while True:      
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        return

    def intro(self):

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    pygame.font.quit()
                    quit()                
                        
            self.ctx['screen'].blit(self.ctx['res_holder']['sprite'].START, (0,0))

            # button("PLAY", 350, 250, 200, 70, self.ctx['res_holder']['color'].red, self.ctx['res_holder']['color'].light_red, action = 'play')
            # button("CONTROLS", 350, 350, 200, 70, self.ctx['res_holder']['color'].red, self.ctx['res_holder']['color'].light_red, action = 'controls')
            # button("QUIT", 350, 450, 200, 70, self.ctx['res_holder']['color'].red, self.ctx['res_holder']['color'].light_red, action = 'quit')
            
            pygame.display.update()

            self.clock.tick(15)
    
    def draw(self):
        self.apple.draw(self.ctx)
        self.stones.draw(self.ctx)
        self.snake.draw(self.ctx)
        self.score(self.points)    
        pygame.display.update()       

    def update(self):
        if self.snake.direction == "left":
            self.lead_x_change = -sprite_size.x
            self.lead_y_change = 0
        elif self.snake.direction == "right":
            self.lead_x_change = sprite_size.x
            self.lead_y_change = 0
        elif self.snake.direction == "up":
            self.lead_y_change = -sprite_size.y
            self.lead_x_change = 0
        elif self.snake.direction == "down":
            self.lead_y_change = sprite_size.y
            self.lead_x_change = 0
            
        self.lead_x += self.lead_x_change
        self.lead_y += self.lead_y_change
                    
        if (self.lead_x == self.apple.x and self.lead_y == self.apple.y):
            
            self.apple.renew(self.stones, self.snake)
            self.snake.length += 1
            self.points += 10
            self.ctx['res_holder']['music'].POINT.play()
            
            if (self.points)%40 == 0:
                self.stones.add(self.snake)
                
            if (self.points)%70 == 0:
                self.speed += 1
                print(self.speed)
                        
            if self.lead_x >= screen_width-sprite_size.x:
                self.lead_x = sprite_size.x
            elif self.lead_x < sprite_size.x:
                self.lead_x = screen_width-2*sprite_size.x
            elif self.lead_y >= screen_height-sprite_size.y:
                self.lead_y = sprite_size.y
            elif self.lead_y < sprite_size.y:
                self.lead_y = screen_height-2*sprite_size.y

        self.snake.update(self.lead_x, self.lead_y)
        self.game_over = self.snake.isDead(self.stones, self.ctx)

    def handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                self.game_exit= True
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT) and self.snake.direction != "right":
                    self.snake.direction = "left"
                elif (event.key == pygame.K_RIGHT) and self.snake.direction != "left":
                    self.snake.direction = "right"
                elif (event.key == pygame.K_UP) and self.snake.direction != "down":
                    self.snake.direction = "up"    
                elif (event.key == pygame.K_DOWN) and self.snake.direction != "up":
                    self.snake.direction = "down"

                if event.key == pygame.K_p:
                    self.pause()


    def run(self):

        #game_states

        self.ctx['screen'].blit(self.ctx['res_holder']['sprite'].game_background, (0,0))
        self.draw_wall()  
        while not self.game_exit:
            self.handle_event()
            self.update()
            self.draw() 
            self.clock.tick(self.speed)                                    
            while self.game_over == True: 
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.game_exit = True
                        self.game_exit = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            self.game_over = True
                            self.game_over = False 
                        #if event.key == pygame.K_c:
                            #init_game()  #TODO
                            
                self.ctx['screen'].blit(self.ctx['res_holder']['sprite'].game_texture, (0,0))
                self.draw_text("SCORE: " + str(self.points), self.ctx['res_holder']['color'].black, 50, screen_width/2, screen_height/2-25)
                            
                # self.button("MENU", 100, 450, 200, 70, self.red, self.light_red, action = 'menu')
                # self.button("PLAY AGAIN", 350, 450, 200, 70, self.red, self.light_red, action = 'again')
                # self.button("QUIT", 600, 450, 200, 70, self.red, self.light_red, action = 'quit')
         
                pygame.display.update()         
                self.clock.tick(15)
                
        pygame.quit()
        pygame.font.quit()
        quit()

class Button():
    WHITE = (255, 255, 255)
    GREY = (200, 200, 200)
    BLACK = (0, 0, 0)
    
    def __init__(self, screen, txt, location, action, bg=WHITE, fg=BLACK, size=(80, 30), font_name="Segoe Print", font_size=16):
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
        self.mouseover()

        self.surface.fill(self.bg)
        self.surface.blit(self.txt_surf, self.txt_rect)
        self.screen.sscreen.blit(self.surface, self.rect)

    def mouseover(self):
        self.bg = self.color
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.bg = GREY  # mouseover color

    def call_back(self):
        self.call_back_()


class Stone:
    
    def __init__(self):
        self.list = []

    def add(self, other):
    
        newStoneX, newStoneY = randLocationGen(self.list, other.list)
        newStone = [newStoneX, newStoneY]
        self.list.append(newStone)
        
    def draw(self, ctx):
        for i in range(len(self.list)):
            ctx['screen'].blit(ctx['res_holder']['sprite'].STONE, (self.list[i][0],self.list[i][1]))
            
    def destroy(self, stone):
        self.list.remove(stone)
            
class Apple:
    
    def __init__(self, stones, snake):
        self.renew(stones, snake)
    
    def renew(self, stones, snake):
        self.x, self.y = randLocationGen(stones.list, snake.list)
        
    def draw(self, ctx):
        ctx['screen'].blit(ctx['res_holder']['sprite'].APPLE, (self.x, self.y))

                   
class Snake:
    
    def __init__(self, lead_x, lead_y):
        self.direction = "right"
        
        self.list = [["right", lead_x-2*sprite_size.x, lead_y],
                     ["right", lead_x-sprite_size.x, lead_y],
                     ["right", lead_x, lead_y]]
                          
        self.head = ["right", lead_x, lead_y]
        self.length = 3
        self.superTimer = 0
        
    def superSnake(self, FPS):
        self.superTimer = 10*FPS
        
    def update(self, lead_x, lead_y):
        self.head = []
        self.head.append(self.direction)
            
        self.head.append(lead_x)
        self.head.append(lead_y)
        
        self.list.append(self.head)
        
        if len(self.list) > self.length:
            del self.list[0]

        if self.superTimer > 0:
            self.superTimer -= 1

    def draw(self, ctx):
        self.view(ctx['res_holder']['sprite'].HEAD, ctx['res_holder']['sprite'].TAIL,
                  ctx['res_holder']['sprite'].BODY, ctx['res_holder']['sprite'].TURN, ctx)
               
    def view(self, head, tail, body, turn, ctx):
        
        ctx['screen'].blit(rotate(self.list[-1],head), (self.list[-1][1],self.list[-1][2]))       
        ctx['screen'].blit(rotate(self.list[1],tail), (self.list[0][1],self.list[0][2]))
            
        for i in range(1, self.length-1):
            
            if self.list[i][0] == self.list[i+1][0]:
                ctx['screen'].blit(rotate(self.list[i],body), (self.list[i][1],self.list[i][2]))
            
            elif (self.list[i][0] == "down" and self.list[i+1][0] == "right") or (self.list[i][0] == "right" and self.list[i+1][0] == "up") or (self.list[i][0] == "up" and self.list[i+1][0] == "left") or (self.list[i][0] == "left" and self.list[i+1][0] == "down"):       
                ctx['screen'].blit(rotate(self.list[i+1],turn), (self.list[i][1],self.list[i][2]))
            
            elif (self.list[i][0] == "right" and self.list[i+1][0] == "down") or (self.list[i][0] == "down" and self.list[i+1][0] == "left") or (self.list[i][0] == "left" and self.list[i+1][0] == "up") or (self.list[i][0] == "up" and self.list[i+1][0] == "right"):        
                ctx['screen'].blit(rotate(self.list[i+1],turn), (self.list[i][1],self.list[i][2]))
        
    def isDead(self, other, ctx):
        
        for eachSegment in self.list[:-1]:
            if eachSegment[1] == self.head[1] and eachSegment[2] == self.head[2]:
                ctx['res_holder']['music'].HIT.play()
                pygame.mixer.music.set_volume(0.2)
                return True
                
        if self.superTimer <= 0:
            
            for eachStone in other.list:
                if eachStone[0] == self.head[1] and eachStone[1] == self.head[2]:
                    ctx['res_holder']['music'].HIT.play()
                    return  True
                    
            if self.head[1] >= screen_width-sprite_size.y or self.head[1] < sprite_size.y or self.head[2] >= screen_height-sprite_size.x or self.head[2] < sprite_size.x:
                ctx['res_holder']['music'].HIT.play()
                return True
                
        return False
        
    def trim(self):
        if len(self.list) > 13:
            self.list = self.list[10:]
            self.length -= 10

def rotate(segment, image):
    if segment[0] == "right":
        rotatedImage = pygame.transform.rotate(image, 0)
    elif segment[0] == "left":
        rotatedImage = pygame.transform.rotate(image, 180)
    elif segment[0] == "up":
        rotatedImage = pygame.transform.rotate(image, 90)    
    elif segment[0] == "down":
        rotatedImage = pygame.transform.rotate(image, 270)       
    return rotatedImage        
    
    
def randLocationGen (stonesList, snakeList):
    randX = round((random.randrange(sprite_size.x, screen_width - 2*sprite_size.x))/sprite_size.x)*sprite_size.x
    randY = round((random.randrange(sprite_size.y, screen_height - 2*sprite_size.y))/sprite_size.y)*sprite_size.y
    

    for stone in stonesList:
        for element in snakeList:
            if(randX == stone[0] and randY == stone[1]) or (randX == element[1] and randY == element[2]):
                print("!TEXT!" + str(randX)+str(element[1]) + str(randY)+str(element[2]))
                return randLocationGen(stonesList, snakeList)
    
    return randX, randY

                    


# def draw_game_intro():
    

        
                    
    
if __name__ == "__main__":
    game = Game()
    game.run()


