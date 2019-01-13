import pygame
import random
import os
from collections import namedtuple, defaultdict


# resources taken from:
#  http://www.biryuk.com/2015/05/free-snake-sprites.html
#  https://openclipart.org/detail/265429/brick-wall
#  http://texturelib.com/texture/?path=/Textures/grass/grass/grass_grass_0121

screen_width = 900
screen_height = 600
sprite_size = 30 
FPS = 10

class Game:

    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        self.ctx = {
                    'window': pygame.display.set_mode((screen_width, screen_height)),
                    'res_holder': defaultdict()
                   }

        pygame.display.set_caption('retro snake game')
        self.clock = pygame.time.Clock() 
        self.load_resources('resources')


    def load_resources(self, res_path):

        def get_path(entity_path):
            return os.path.join(res_path, entity_path)
        
        Colors = namedtuple('Color', ['white', 'black', 'red', 'light_red', 'dark_green'])
        self.ctx['res_holder']['color'] = Colors((255,255,255), (0,0,0), (255,0,0), (155,0,0), (0,120,0))


        Sprites = namedtuple('Sprite', ['HEAD', 'TAIL', 'BODY', 'TURN', 'APPLE', 'STONE', 'START', 'WHITE_DIAMOND', 'WALL', 'background'])
        self.ctx['res_holder']['sprite'] = Sprites(pygame.transform.scale(pygame.image.load(get_path('snake_head.png')), (30, 30)),
                                                   pygame.transform.scale(pygame.image.load(get_path('snake_tail.png')), (30, 30)),
                                                   pygame.transform.scale(pygame.image.load(get_path('snake_body.png')), (30, 30)),
                                                   pygame.transform.scale(pygame.image.load(get_path('snake_turn.png')), (30, 30)),
                                                   pygame.image.load(get_path('apple.png')),
                                                   pygame.image.load(get_path('stone.gif')),
                                                   pygame.image.load(get_path('background.jpg')),
                                                   pygame.image.load(get_path('WHITE_DIAMOND.png')),
                                                   pygame.transform.scale(pygame.image.load(get_path('wall.png')), (30, 30)),
                                                   pygame.image.load(get_path('background.jpg')) )
                                                   
        Music = namedtuple('Music', ['POINT', 'HIT', 'EVOLUTION', 'STONEDDESTROY'])
        self.ctx['res_holder']['music'] = Music(pygame.mixer.Sound(get_path("sfx_point.wav")),
                                                pygame.mixer.Sound(get_path("sfx_hit.wav")),
                                                pygame.mixer.Sound(get_path("Star_Wars_-_Imperial_march.wav")),
                                                pygame.mixer.Sound(get_path("STONEDESTROY.wav")))
    
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
        self.ctx['window'].blit(text_surface, text_rect)


    def draw_wall(self):
        '''
        Creates wall around the map (TODO - reading map from file - specific to level)
        '''
        for x in range(screen_width):
            self.ctx['window'].blit(self.ctx['res_holder']['sprite'].WALL, (x*sprite_size, 0))
            self.ctx['window'].blit(self.ctx['res_holder']['sprite'].WALL, (x*sprite_size, screen_height-sprite_size))
        for y in range(screen_height):
            self.ctx['window'].blit(self.ctx['res_holder']['sprite'].WALL, (0, y*sprite_size))
            self.ctx['window'].blit(self.ctx['res_holder']['sprite'].WALL, (screen_width-sprite_size, y*sprite_size))


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
    #         ctx['window'].blit(INACTIVE_B, (x,y))
    #     draw_text(text, text_color, int(round(height/2)), x + width/2, y + height/4)
     
    def score(self, score):
        font = pygame.font.Font(self.ctx['res_holder']['font'].flup, 25)
        text = font.render(str(score), True, self.ctx['res_holder']['color'].black)
        self.ctx['window'].blit(text, [14,14])

    def pause(self):
        
        self.draw_text("PAUSE", self.ctx['res_holder']['color'].black, 60, screen_width/2, screen_height/2 -130)
        self.draw_text("Press P to continue", self.ctx['res_holder']['color'].black, 30, screen_width/2, screen_height/2)
        pygame.display.update()
        
        while True:      
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        return
    
    def draw(self):
        gameExit = False
        gameOver = False
        
        points = 0
        speed = FPS

        lead_x = screen_width/2 
        lead_y = screen_height/2 
        lead_x_change = sprite_size 
        lead_y_change = 0 
        
        Snake = snake(lead_x, lead_y)
        Stones = stones()
        Apple = apple(Stones, Snake)

        while not gameExit:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    gameExit = True
                
                
                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_LEFT) and Snake.direction != "right":
                        Snake.direction = "left"
                    elif (event.key == pygame.K_RIGHT) and Snake.direction != "left":
                        Snake.direction = "right"
                    elif (event.key == pygame.K_UP) and Snake.direction != "down":
                        Snake.direction = "up"    
                    elif (event.key == pygame.K_DOWN) and Snake.direction != "up":
                        Snake.direction = "down"

                    if event.key == pygame.K_p:
                        self.pause()
                        
            if Snake.direction == "left":
                lead_x_change = -sprite_size
                lead_y_change = 0
            elif Snake.direction == "right":
                lead_x_change = sprite_size
                lead_y_change = 0
            elif Snake.direction == "up":
                lead_y_change = -sprite_size
                lead_x_change = 0
            elif Snake.direction == "down":
                lead_y_change = sprite_size
                lead_x_change = 0
                
            lead_x += lead_x_change
            lead_y += lead_y_change
                        
            if (lead_x == Apple.x and lead_y == Apple.y):
                
                Apple.renew(Stones, Snake)
                Snake.length += 1
                points += 10
                self.ctx['res_holder']['music'].POINT.play()
                
                if (points)%40 == 0:
                    Stones.add(Snake)
                    
                if (points)%70 == 0:
                    speed += 1
                    print(speed)
                          
                if lead_x >= screen_width-sprite_size:
                    lead_x = sprite_size
                elif lead_x < sprite_size:
                    lead_x = screen_width-2*sprite_size
                elif lead_y >= screen_height-sprite_size:
                    lead_y = sprite_size
                elif lead_y < sprite_size:
                    lead_y = screen_height-2*sprite_size

            Snake.update(lead_x, lead_y)
            gameOver = Snake.isDead(Stones, self.ctx)
                    
            self.ctx['window'].blit(self.ctx['res_holder']['sprite'].background, (0,0))
            self.draw_wall() 
            Apple.draw(self.ctx)
            Stones.draw(self.ctx)
            Snake.draw(self.ctx)
            #self.ctx.blit(self.wall, (0,0)) create wall
            self.score(points) 
            
            pygame.display.update()   
            self.clock.tick(speed)
            
            while gameOver == True:

                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameExit = True
                        gameOver = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            gameExit = True
                            gameOver = False 
                        #if event.key == pygame.K_c:
                            #gameLoop()  #TODO
                            
                # #self.ctx.blit(self.GAMEOVER, (0,0))
                # self.draw_text("SCORE: " + str(points), self.black, 50, screen_width/2, screen_height/2-25)
                            
                # self.button("MENU", 100, 450, 200, 70, self.red, self.light_red, action = 'menu')
                # self.button("PLAY AGAIN", 350, 450, 200, 70, self.red, self.light_red, action = 'again')
                # self.button("QUIT", 600, 450, 200, 70, self.red, self.light_red, action = 'quit')
            
                pygame.display.update()
            
                self.clock.tick(15)
                
        pygame.quit()
        pygame.font.quit()
        quit()
        pass

    def update(self):
        pass

    def handle_event(self):
        pass



class stones:
    
    def __init__(self):
        self.list = []

    def add(self, other):
    
        newStoneX, newStoneY = randLocationGen(self.list, other.list)
        newStone = [newStoneX, newStoneY]
        self.list.append(newStone)
        
    def draw(self, ctx):
        for i in range(len(self.list)):
            ctx['window'].blit(ctx['res_holder']['sprite'].STONE, (self.list[i][0],self.list[i][1]))
            
    def destroy(self, stone):
        self.list.remove(stone)
            
class apple:
    
    def __init__(self, stones, snake):
        self.renew(stones, snake)
    
    def renew(self, stones, snake):
        self.x, self.y = randLocationGen(stones.list, snake.list)
        
    def draw(self, ctx):
        ctx['window'].blit(ctx['res_holder']['sprite'].APPLE, (self.x, self.y))

                   
class snake:
    
    def __init__(self, lead_x, lead_y):
        self.direction = "right"
        
        self.list = [["right", lead_x-2*sprite_size, lead_y],
                     ["right", lead_x-sprite_size, lead_y],
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
        
        ctx['window'].blit(rotate(self.list[-1],head), (self.list[-1][1],self.list[-1][2]))       
        ctx['window'].blit(rotate(self.list[1],tail), (self.list[0][1],self.list[0][2]))
            
        for i in range(1, self.length-1):
            
            if self.list[i][0] == self.list[i+1][0]:
                ctx['window'].blit(rotate(self.list[i],body), (self.list[i][1],self.list[i][2]))
            
            elif (self.list[i][0] == "down" and self.list[i+1][0] == "right") or (self.list[i][0] == "right" and self.list[i+1][0] == "up") or (self.list[i][0] == "up" and self.list[i+1][0] == "left") or (self.list[i][0] == "left" and self.list[i+1][0] == "down"):       
                ctx['window'].blit(rotate(self.list[i+1],turn), (self.list[i][1],self.list[i][2]))
            
            elif (self.list[i][0] == "right" and self.list[i+1][0] == "down") or (self.list[i][0] == "down" and self.list[i+1][0] == "left") or (self.list[i][0] == "left" and self.list[i+1][0] == "up") or (self.list[i][0] == "up" and self.list[i+1][0] == "right"):        
                ctx['window'].blit(rotate(self.list[i+1],turn), (self.list[i][1],self.list[i][2]))
        
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
                    
            if self.head[1] >= screen_width-sprite_size or self.head[1] < sprite_size or self.head[2] >= screen_height-sprite_size or self.head[2] < sprite_size:
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
    randX = round((random.randrange(sprite_size, screen_width - 2*sprite_size))/sprite_size)*sprite_size
    randY = round((random.randrange(sprite_size, screen_height - 2*sprite_size))/sprite_size)*sprite_size
    

    for stone in stonesList:
        for element in snakeList:
            if(randX == stone[0] and randY == stone[1]) or (randX == element[1] and randY == element[2]):
                print("!TEXT!" + str(randX)+str(element[1]) + str(randY)+str(element[2]))
                return randLocationGen(stonesList, snakeList)
    
    return randX, randY

                    


# def draw_game_intro():
    
#     while True:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 pygame.font.quit()
#                 quit()                
                    
#         ctx['window'].blit(START, (0,0))

#         button("PLAY", 350, 250, 200, 70, self.red, self.light_red, action = 'play')
#         button("CONTROLS", 350, 350, 200, 70, self.red, self.light_red, action = 'controls')
#         button("QUIT", 350, 450, 200, 70, self.red, self.light_red, action = 'quit')
        
#         pygame.display.update()
        
#         clock.tick(15)
        
                    
    
if __name__ == "__main__":
    game = Game()
    game.draw()


