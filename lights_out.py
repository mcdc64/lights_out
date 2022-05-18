import random
import numpy as np
import pygame
import time
from enum import Enum



class State(Enum): # two possible states for a square
    OFF = 0
    ON = 1

class Square(pygame.sprite.Sprite):
    def __init__(self,x,y,square_length):
        self.x = x # x index of the square
        self.y = y # y index of the square
        self.state = State.OFF
        self.square_length = square_length #physical size of the square on the screen (for pygame to draw it)
        self.rect = pygame.Rect(0,0,0,0)

    def change_state(self,state):
        self.state = state

    def toggle_state(self): # swaps the state of the square
        if(self.state == State.OFF):
            self.state = State.ON
        else:
            self.state = State.OFF

    def get_coords_from_index(x, y, grid_width, grid_height, top_bottom_margin, between_margin, left_margin): # given x,y indices of a square, shows where it should be placed on the screen
        x_coord = left_margin + x * (square_length + between_margin)
        y_coord = top_bottom_margin + y * (square_length + between_margin)
        return (x_coord, y_coord)

    def initialise_rect(self, grid_width, grid_height, top_bottom_margin, between_margin, left_margin):
        rect_pos = get_coords_from_index(self.x,self.y, grid_width, grid_height, top_bottom_margin, between_margin, left_margin)
        self.rect = pygame.Rect(rect_pos[0],rect_pos[1],square_length,square_length)
    def update(self): # updates the sprite of the square if its state changes
        if(self.state == State.OFF):
            self.image = pygame.transform.scale(pygame.image.load("images/light_off.png"),(self.square_length, self.square_length))
        else:
            self.image = pygame.transform.scale(pygame.image.load("images/light_on.png"),
                                                (self.square_length, self.square_length))
    def draw(self,screen):
        screen.blit(self.image, self.rect)



def von_neumann(x,y,width,height,toroidal): #get Von Neumann nbhd of a point with invalid coords removed (or modulo in the toroidal case)
    points = [(x+1,y),(x,y+1),(x-1,y),(x,y-1)]
    output = [(x+1,y),(x,y+1),(x-1,y),(x,y-1)]
    if(toroidal):
        output = [[x + 1, y], [x, y + 1], [x - 1, y], [x, y - 1]]
        for point in output:
            point[0] = point[0]%width
            point[1] = point[1]%height
        return output
    for i in range(len(points)):
        point = points[i]
        if(point[0]<0 or point[0]>=width):
            output.remove(point)
            continue
        if(point[1]<0 or point[1]>=height):
            output.remove(point)
            continue
    return output

def move(grid,move_x,move_y,toroidal): # make a move by changing the chosen square and its neighbours
    neighbours = von_neumann(move_x,move_y,grid_width,grid_height,toroidal)
    grid[move_x][move_y].toggle_state()
    for point in neighbours:
        grid[point[0]][point[1]].toggle_state()



pygame.init()
pygame.display.set_caption("Lights Out")

def get_coords_from_index(x,y,grid_width,grid_height,top_bottom_margin,between_margin,left_margin):
    x_coord = left_margin+x*(square_length+between_margin)
    y_coord = top_bottom_margin+y*(square_length+between_margin)
    return (x_coord,y_coord)

screen_width = 1000

aspect_ratio = 1.5 #around 1.5 is best
screen_height = int(screen_width/aspect_ratio)
top_bottom_margin = screen_width//14
between_margin = 4

screen = pygame.display.set_mode([screen_width, screen_height])
pygame.display.set_icon(pygame.image.load("images/window_icon.png"))


running = True
has_won = False
all_off = True
on_menu = True
game_started = False
fontsize = 48#*int(screen_width/1400)
font = pygame.font.SysFont(None, fontsize)
moves = 0
toroidal = False
difficulty = "Easy"

while running:
    on_count = 0
    all_off = True
    if on_menu: # start on the main menu where the player can select their difficulty and toroidal conditions
        screen.fill((127,127,127))
        button_size = (screen_width//6,screen_width//8)
        checkbox_size = (64,64)
        logo_size = (screen_width//2,screen_width//4)
        logo_img = pygame.transform.scale(pygame.image.load("images/logo.png"),logo_size)
        easy_img = pygame.transform.scale(pygame.image.load("images/easy_button.png"),button_size)
        hard_img = pygame.transform.scale(pygame.image.load("images/hard_button.png"),button_size)
        torus_check_img = None
        if(not toroidal):
            torus_check_img = pygame.transform.scale(pygame.image.load("images/checkbox_off.png"), checkbox_size)
        elif(toroidal):
            torus_check_img = pygame.transform.scale(pygame.image.load("images/checkbox_on.png"), checkbox_size)

        logo_rect = pygame.Rect((screen_width - logo_size[0])//2,top_bottom_margin,logo_size[0],logo_size[1])
        easy_rect = pygame.Rect((screen_width - button_size[0])//2,top_bottom_margin+logo_size[1]+0.25*button_size[1],button_size[0],button_size[1])
        hard_rect = pygame.Rect((screen_width - button_size[0]) // 2, screen_height//2+ 1.5*button_size[1], button_size[0], button_size[1])

        torus_rect = pygame.Rect((screen_width + 2*button_size[0]) // 2, screen_height//2+ 0.75*button_size[1], checkbox_size[0], checkbox_size[1])

        torus_text = "Toroidal?" # add a checkbox to let the player choose toroidal boundary (and corresponding text)
        torus_text_img = font.render(torus_text, True, (200, 200, 200))
        torus_text_img_dims = torus_text_img.get_rect().size
        screen.blit(torus_text_img,((screen_width + 2.25*button_size[0]) // 2 + checkbox_size[0],(screen_height+0.6*checkbox_size[1])//2+ 0.75*button_size[1]))
        screen.blit(logo_img,logo_rect)
        screen.blit(easy_img,easy_rect)
        screen.blit(hard_img,hard_rect)
        screen.blit(torus_check_img,torus_rect)
        for event in pygame.event.get(): # handle all the events that can occur on the main menu
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP and not has_won:
                pos = pygame.mouse.get_pos()
                if(easy_rect.collidepoint(pos)):
                    difficulty = "Easy"
                    on_menu = False
                elif(hard_rect.collidepoint(pos)):
                    difficulty = "Hard"
                    on_menu = False
                elif (torus_rect.collidepoint(pos)):
                    if(toroidal):
                        toroidal = False
                    elif(not toroidal):
                        toroidal = True

        pygame.display.flip()
        continue

    if(not on_menu and not game_started): # do everything that only needs to be done once at the start
        # we need to do this inside the main loop as the player must first choose the difficulty
        game_started = True
        grid_width = 4
        grid_height = 4

        if(difficulty=="Hard"):
            grid_width = 5
            grid_height = 5

        square_length = int((screen_height - 2 * top_bottom_margin - (grid_height - 1) * between_margin) / grid_height)
        left_margin = (screen_width - (grid_width * square_length) - ((grid_width - 1) * between_margin)) / 2



        grid = [[None for _ in range(grid_height)] for _ in range(grid_width)] #initialise the grid (will fill it with squares)

        for i in range(0, grid_width): #place the rectangles corresponding to each square
            for j in range(0, grid_height):
                grid[i][j] = Square(i, j, square_length)
                grid[i][j].initialise_rect(grid_width, grid_height, top_bottom_margin, between_margin, left_margin)

        for i in range(0, 6):  # make 6 random moves to mess up the grid while guaranteeing the existence of a solution
            rand_point = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
            move(grid, rand_point[0], rand_point[1],toroidal)


    for event in pygame.event.get(): # handle events during the actual game (i.e. when the player clicks squares)
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP and not has_won:
            pos = pygame.mouse.get_pos()
            for i in range(grid_width):
                for j in range(grid_height):
                    rect = grid[i][j].rect
                    if rect.collidepoint(pos):
                        move(grid,grid[i][j].x,grid[i][j].y,toroidal)
                        moves+=1
    screen.fill((127,127,127))

    for i in range(grid_width): # update and draw each of the rects
        for j in range(grid_height):
            grid[i][j].update()
            grid[i][j].draw(screen)
            if (grid[i][j].state == State.ON):
                on_count += 1
                all_off = False
    if all_off: # if all the lights are off, we win
        has_won = True

    count_text = "Lights On: "+str(on_count) # display the counters for lights left, and moves made
    move_text = "Moves: "+str(moves)
    count_text_img = font.render(count_text,True,(0,200,103))
    move_text_img = font.render(move_text,True,(0,200,103))
    screen.blit(count_text_img,(left_margin//6,top_bottom_margin//2))
    screen.blit(move_text_img, (left_margin //6, (top_bottom_margin // 2)+fontsize))

    if(has_won):
        win_text = "All lights off! A winner is you!"
        win_img = font.render(win_text, True, (0, 200, 103))
        img_dims = win_img.get_rect().size
        screen.blit(win_img,((screen_width - img_dims[0])//2,(screen_height- img_dims[1])//2-(3*between_margin)))

    pygame.display.flip()
pygame.quit() # quit once the main loop is complete