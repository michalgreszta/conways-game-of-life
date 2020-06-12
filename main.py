
import pygame as pg
import sys
from settings import *

''' POJEDYNCZY KWADRACIK '''
class Square(pg.sprite.Sprite):
    # x, y to parametry piksela w lewym, górnym rogu
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, game):
        # Argumenty: powierzchnia do rysowania, kolor wypełnienia, obiekt przechowujący współrzędne prostokąta)
        pg.draw.rect(game.screen, YELLOW, pg.Rect(self.x, self.y, TILESIZE, TILESIZE)) 

''' STRUKTURA '''
class Structure:
    def __init__(self, d=[]):
        # Przechowuje dane o strukturze; 
        self.data = d

    # x, y są numerami indeksów w siatce
    def load(self, grid, x, y):
        # Dla każdej kolumny
        for i in range(0,len(self.data)):
            for j in  range(0, len(self.data[i])):
                # wkleja w cześć kolumny siatki dane o kolumnie struktury
                grid.tiles[x+i][y+j] = Square((x+i)*TILESIZE, (y+j)*TILESIZE) if self.data[i][j]==1 else None
        return grid

STR_GLIDER = Structure( [ [0,0,1], [1,0,1], [0,1,1] ] )
STR_SMALLEXPLODER = Structure( [ [0,1,1,0], [1,1,0,1], [0,1,1,0] ] )
STR_EXPLODER = Structure( [ [1,1,1,1,1], [0,0,0,0,0], [1,0,0,0,1], [0,0,0,0,0], [1,1,1,1,1] ] )
STR_10CELLROW = Structure( [ [1], [1], [1], [1], [1], [1], [1], [1], [1], [1] ] )
STR_10CELLCOLUMN = Structure ( [ [1,1,1,1,1,1,1,1,1,1] ] )
STR_LIGHTWEIGHTSPACESHIP = Structure ( [ [0,1,0,1], [1,0,0,0], [1,0,0,0], [1,0,0,1], [1,1,1,0] ] )
STR_TUMBLER = Structure ( [ [0,0,0,1,1,1], [1,1,0,0,0,1], [1,1,1,1,1,0], [0,0,0,0,0,0], [1,1,1,1,1,0], [1,1,0,0,0,1], [0,0,0,1,1,1] ] )
STR_RPENTOMINO = Structure( [ [0,1,0], [1,1,1], [1,0,0] ] )
STR_ACORN = Structure( [ [0,0,1], [1,0,1], [0,0,0], [0,1,0], [0,0,1], [0,0,1], [0,0,1] ] )

''' OBSŁUGA SIATKI '''
class Grid:
    def __init__(self, screensize):
        self.size = screensize
        self.clear()

    def clear(self):
        # dwuwymiarowa lista wypełniona 'nonami' || tiles[x][y], gdzie x, y są numerami kafelków liczonymi od 0
        self.tiles = [ [None for y in range(0, self.size[1]//TILESIZE)] for x in range(0, self.size[0]//TILESIZE)]
    
    def step(self):
        newborn = []
        dead = []
        
        for x in range(0, len(self.tiles)):
            for y in range(0, len(self.tiles[x])):
                neighbours = self.getNeighbours(x,y)

                if neighbours == 3:
                    newborn.append((x, y))
                elif neighbours <= 1 or neighbours >= 4:
                    dead.append((x, y))

        for k in newborn:
            self.tiles[k[0]][k[1]] = Square(k[0]*TILESIZE, k[1]*TILESIZE)
        for k in dead:
            self.tiles[k[0]][k[1]] = None

    def getNeighbours(self, x, y):
       tmp = [(x-1, y-1), (x, y-1), (x+1, y-1),
              (x-1, y),             (x+1, y),
              (x-1, y+1), (x, y+1), (x+1, y+1)]
       
       counter = 0
       for k in tmp:
           x = k[0]%len(self.tiles)
           if self.tiles[x][k[1]%len(self.tiles[x])] != None:
               counter += 1
       return counter

    # Zwraca pozycję kafelka w siatce (parametry lewego górnego rogu(w pikselach))
    def get_grid_pos(self, pos):
        tmp = self.get_grid_index(pos)
        return (tmp[0]*TILESIZE, tmp[1]*TILESIZE)

    # "Obcina" część po przecinku - podaje numer klocka, który wybraliśmy
    def get_grid_index(self, pos):
        return (pos[0]//TILESIZE, pos[1]//TILESIZE)

    def draw(self, game):
        # Dla każdego elementu listy - jeśli nie jest nonem, to rysuje kwadracik
        for col in self.tiles:
            for s in col:
                if s!=None: s.draw(game)
        
        # Rysuje pionowe linie
        for x in range(0, self.size[0], TILESIZE):
            pg.draw.line(game.screen, LIGHTGREY, (x, 0), (x, self.size[1]))
        # Rysuje poziome linie
        for y in range(0, self.size[1], TILESIZE):
            pg.draw.line(game.screen, LIGHTGREY, (0, y), (self.size[0], y))

''' SYSTEM GRY '''
class Game:
    def __init__(self):
        pg.init()
        # flaga wklej strukture
        self.paste = None
        # Tworzenie zmiennej kursor
        self.cursor = (0,0)
        # Automatycznie przewija klatki
        self.autoplay = False
        # Szybkość gry, ustalana przez użytkownika
        self.tempo = 2
        # Inicjalizowanie siatki
        self.grid = Grid((WIDTH-MENU_W, HEIGHT))
        # Ustaw rozmiary okna
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))   
        # Ustaw tytuł okna           
        pg.display.set_caption(TITLE)
        # Tworzy obiekt do śledzenia czasu
        self.clock = pg.time.Clock()
        # Wczytuje tło do menu
        self.bg = pg.transform.scale(pg.image.load('menu_bg.jpg'), (MENU_W, HEIGHT))
        # Steruje reakcją na klawisze (delay przy przytrzymaniu, interval - przy każdym przejściu)
        pg.key.set_repeat(100, 200)


    def changeSquare(self):
        if self.grid.size[0] <= self.cursor[0]:
            return
        
        gp = self.grid.get_grid_pos(self.cursor)                        # pozycja lewego górnego rogu klocka (w pikselach)
        index = self.grid.get_grid_index(self.cursor)                   # numer klocka (po indeksach num. od zera)
        # do konkretnej komórki w tablicy jest wpisywany obiekt o parametrach rogu 'gp'
        if self.grid.tiles[index[0]][index[1]] == None:
            self.grid.tiles[index[0]][index[1]] = Square(gp[0], gp[1])
        # Jeśli istnieje obiekt, to ustawia go na None
        else:
            self.grid.tiles[index[0]][index[1]] = None

    def placeStruct(self):
        self.grid = self.paste.load(self.grid, *self.grid.get_grid_index(self.cursor))
        #funkcja(a, b, c)
        #dane = [1,2,3]
        #funckja(*dane)

    def draw(self):
        # Wypełnia ekran wybranym kolorem
        self.screen.fill(BGCOLOR)
        self.screen.blit(self.bg, (WIDTH-MENU_W, 0))
        # Rysuje siatkę
        self.grid.draw(self)
        self.write(24, "Game Of Life", WHITE, WIDTH-MENU_W//2, 50)
        
        i = 0
        for s in ["S - next step", "A - auto", "C - clear screen", "E - exit", "+/- change speed"]:
            self.write(16, s, YELLOW, WIDTH-MENU_W + 20, 80+i*25, False)
            i+=1

        i = 0
        for s in ["1 - GLIDER", "2 - SMALL EXPLODER", "3 - EXPLODER", "4 - 10 CELL ROW", "5 - 10 CELL COLUMN", "6 - LITE SPACESHIP", "7 - TUMBLER", "8 - RPENTOMINO", "9 - ACORN"]: 
            self.write(16, s, YELLOW, WIDTH-MENU_W + 20, 240+i*25, False)
            i+=1       

        pg.display.flip()

    def write(self, size, text, clr, left, top, center=True):
        font = pg.font.SysFont("Consolas", size)
        tmp = font.render(text, True, clr)
        # Parametry: obrazek z tekstem, położenie obrazka względem lewej strony i wysokości)
        if center:
            self.screen.blit(tmp, (left - tmp.get_width()//2, top - tmp.get_height()//2))
        else:
            self.screen.blit(tmp, (left, top))

    def events(self):
        # catch all events here
        for event in pg.event.get(): 
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key in [pg.K_ESCAPE, pg.K_e]:       
                    self.quit()
                if event.key == pg.K_c:
                    self.grid.clear()
                    self.autoplay = False
                if event.key == pg.K_s:
                    self.grid.step()
                if event.key == pg.K_a:
                    self.autoplay = not self.autoplay
                if event.key == pg.K_EQUALS:
                    if self.tempo < 60:
                        self.tempo += 1
                if event.key == pg.K_MINUS:
                    if self.tempo > 1:
                        self.tempo -= 1
                
                # predefiniowane struktury
                if event.key == pg.K_1:
                    self.paste = STR_GLIDER
                if event.key == pg.K_2:
                    self.paste = STR_SMALLEXPLODER
                if event.key == pg.K_3:
                    self.paste = STR_EXPLODER
                if event.key == pg.K_4:
                    self.paste = STR_10CELLROW
                if event.key == pg.K_5:
                    self.paste = STR_10CELLCOLUMN
                if event.key == pg.K_6:
                    self.paste = STR_LIGHTWEIGHTSPACESHIP
                if event.key == pg.K_7:
                    self.paste = STR_TUMBLER
                if event.key == pg.K_8:
                    self.paste = STR_RPENTOMINO
                if event.key == pg.K_9:
                    self.paste = STR_ACORN
            if event.type == pg.MOUSEBUTTONUP:
                # Po kliknięciu, pobiera pozycję myszy (w pikselach)...
                self.cursor = pg.mouse.get_pos()
                if self.paste!=None:
                    self.placeStruct()
                    self.paste = None
                else:
                    # i wywołuje metodę 'addSquare',
                    self.changeSquare()

    def run(self):
        self.playing = True
        while self.playing:
            if self.autoplay:
                self.clock.tick(self.tempo)
            else:
                self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    # wyłącza program
    def quit(self):                                           
        pg.quit()
        sys.exit()

    def update(self):
        if self.autoplay:
            self.grid.step()
    
    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass

# create the game object
g = Game()
g.show_start_screen()
while True:
    g.run()
    g.show_go_screen()