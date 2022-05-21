import pygame
from pygame.locals import *
from sudoku import Sudoku
from resources import load_sudokus, load_sudoku, store_sudokus
import random
import jsonpickle
from menu import Button

class SudokuViewer:

    MODES = ["digit", "corner", "center", "color"]
    KEY_DIGIT_MAPPER = {K_0: 0, K_1: 1, K_2: 2, K_3: 3, K_4: 4, K_5: 5, K_6: 6, K_7: 7, K_8: 8, K_9: 9}
    KEY_MODE_MAPPER = {K_z: 0, K_x: 1, K_c: 2, K_v: 3}
    SQUARE_SIZE = 70
    COLORS: list[tuple[int, int, int]] = list([tuple((random.randint(0, 255) for _ in range(3))) for _ in range(9)])
    BUTTON_SIZE = 100

    def __init__(self, sudoku, screen):
        self.sudoku: Sudoku = sudoku
        self.i = 0
        self.screen = screen
        self.mode = 0
        self.marked: set[tuple[int, int]] = set()
        self.background = pygame.Surface((self.sudoku.width * self.SQUARE_SIZE + 2,
                                          self.sudoku.height * self.SQUARE_SIZE + 2))
        self.digit_surface = pygame.Surface((self.sudoku.width * self.SQUARE_SIZE + 2,
                                             self.sudoku.height * self.SQUARE_SIZE + 2))
        self.marking_surface = pygame.Surface((self.sudoku.width * self.SQUARE_SIZE + 2,
                                               self.sudoku.height * self.SQUARE_SIZE + 2))
        self.num_pad_surface = pygame.Surface((3 * self.BUTTON_SIZE, 4 * self.BUTTON_SIZE))
        self.key_buttons = [Button((i % 3) * self.BUTTON_SIZE,
                                   (i // 3) * self.BUTTON_SIZE, str(i + 1), self.BUTTON_SIZE, self.BUTTON_SIZE) for i in range(9)]
        self.set_up_num_pad()
        self.draw_background()
        self.func_mapper = \
            {(K_TAB, False): self.swap_mode, (K_z, True): self.sudoku.undo, (K_x, True): self.sudoku.redo,
             (K_r, True): self.sudoku.clear, (K_BACKSPACE, False): self.delete_squares,
             (K_f, False): self.sudoku.validate, (K_a, True): self.mark_all}
        self.last_pressed = pygame.time.get_ticks()

    def draw_background(self):
        size = self.SQUARE_SIZE
        self.background.fill((255, 255, 255))
        self.background.set_colorkey((255, 255, 255))
        for region in self.sudoku.regions:
            self.draw_outline_for_area(self.background, region, (0, 0, 0), 4)
        for x in range(self.sudoku.width + 1):
            pygame.draw.line(self.background, (0, 0, 0), (x * size, 0), (x * size, self.sudoku.height * size), 2)
        for y in range(self.sudoku.width + 1):
            pygame.draw.line(self.background, (0, 0, 0), (0, y * size), (self.sudoku.width * size, y * size), 2)

    def set_up_num_pad(self):
        self.num_pad_surface.fill((255, 255, 255))
        for button in self.key_buttons:
            button.draw(self.num_pad_surface, self.BUTTON_SIZE, (12, 123, 78))

    def game_loop(self):

        while True:
            #print(pygame.time.get_ticks())
            self.update_screen()
            if pygame.mouse.get_pressed()[0]:
                self.mark_square(False)
            for event in pygame.event.get():
                if event.type == QUIT: return
                if event.type == KEYDOWN:
                    match event.key:
                        case key if key in self.KEY_DIGIT_MAPPER:
                            self.sudoku.change_squares(self.MODES[self.mode], self.KEY_DIGIT_MAPPER[event.key], self.marked)
                        case key if key in self.KEY_MODE_MAPPER and not pygame.key.get_pressed()[K_LCTRL]:
                            self.mode = self.KEY_MODE_MAPPER[event.key]
                        case key if (key, pygame.key.get_pressed()[K_LCTRL]) in self.func_mapper:
                            self.func_mapper[(key, pygame.key.get_pressed()[K_LCTRL])]()
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    reset = True
                    for i, button in enumerate(self.key_buttons):
                        if button.is_hovered(800, 300):
                            reset = False
                            self.sudoku.change_squares(self.MODES[self.mode], i + 1, self.marked)
                    if not pygame.key.get_pressed()[K_LCTRL] and reset:
                        self.marked = set()
                    self.mark_square(pygame.time.get_ticks() < self.last_pressed + 300)

    def swap_mode(self):
        self.mode = (self.mode + 1) % 4
        self.i += 1

    def delete_squares(self):
        self.sudoku.delete_squares(self.marked)

    def mark_all(self):
        self.marked = {(x, y) for x in range(self.sudoku.width) for y in range(self.sudoku.height)}

    def mark_square(self, double_click):
        x, y = pygame.mouse.get_pos()
        x, y = (x - 100) // self.SQUARE_SIZE, (y - 100) // self.SQUARE_SIZE
        if 0 <= x < self.sudoku.width and 0 <= y < self.sudoku.height:
            if double_click:
                self.marked |= self.sudoku.get_all_digits_of_type(x, y, self.mode)
            self.marked.add((x, y))
            self.last_pressed = pygame.time.get_ticks()

    def update_screen(self):
        self.screen.fill((255, 255, 255))
        self.digit_surface.fill((123, 123, 123))
        self.digit_surface.set_colorkey((123, 123, 123))
        self.marking_surface.fill((123, 123, 123))
        self.marking_surface.set_colorkey((123, 123, 123))
        self.sudoku.draw(self.digit_surface, self.SQUARE_SIZE, self.COLORS, self.i)
        self.draw_outline_for_area(self.marking_surface, self.marked, (70, 13, 180), 5)
        self.screen.blit(self.digit_surface, (100, 100))
        self.screen.blit(self.background, (100, 100))
        self.screen.blit(self.marking_surface, (100, 100))
        self.screen.blit(self.num_pad_surface, (800, 300))

        pygame.display.flip()

    def draw_outline_for_area(self, surface, area, color, width):
        for x, y in area:
            for (xd, yd), (xs, ys, xe, ye) in zip([(0, 1), (1, 0), (0, -1), (-1, 0)],
                                                  [(0, 1, 1, 1), (1, 0, 1, 1), (0, 0, 1, 0), (0, 0, 0, 1)]):
                if (x + xd, y + yd) not in area:
                    pygame.draw.line(surface, color,
                                     ((x + xs) * self.SQUARE_SIZE, ((y + ys) * self.SQUARE_SIZE)),
                                     ((x + xe) * self.SQUARE_SIZE, ((y + ye) * self.SQUARE_SIZE)), width)


class SudokuSetter(SudokuViewer):

    def __init__(self, screen):
        super().__init__(Sudoku(9, 9), screen)

    def game_loop(self):
        super().game_loop()
        for y in range(self.sudoku.width):
            for x, square in enumerate(self.sudoku.squares[y]):
                if square.digit is not None:
                    square.frozen = True
        try:
            sudokus = load_sudokus()
            sudokus.append(jsonpickle.encode(self.sudoku))
        except FileNotFoundError:
            super().game_loop()

        print(sudokus)
        store_sudokus(sudokus)

