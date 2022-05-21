import pygame
from pygame.locals import *


class Button:

    def __init__(self, x, y, text, width, height):
        self.x = x
        self.y = y
        self.text = text
        self.rect = pygame.Rect(self.x, self.y, width, height)

    def draw(self, surface, size, color):
        font = pygame.font.SysFont(None, size)
        text = font.render(self.text, False, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = self.rect.center
        pygame.draw.rect(surface,  color, self.rect)
        surface.blit(text, text_rect)

    def is_hovered(self, x, y):
        return self.rect.collidepoint(pygame.mouse.get_pos()[0] - x, pygame.mouse.get_pos()[1] - y)


class Menu:

    BUTTON_HEIGHT = 150
    BUTTON_WIDTH = 400

    def __init__(self, screen):
        self.screen = screen 
        self.buttons = []

    def main_menu(self):
        self.screen.fill((255, 255, 255))
        button_x = self.screen.get_width() // 2 - self.BUTTON_WIDTH // 2
        self.buttons = [Button(button_x, 300, "Regular sudoku", self.BUTTON_WIDTH, self.BUTTON_HEIGHT),
                        Button(button_x, 500, "Custom sudoku", self.BUTTON_WIDTH, self.BUTTON_HEIGHT)]
        self.draw_screen()
        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_ESCAPE or event == QUIT: return
                if event == MOUSEBUTTONDOWN and event.button == 1:
                    for button in self.buttons:
                        if button.is_hovered(0, 0):
                            print("asdasd")

    def draw_screen(self):
        self.screen.fill((255, 255, 255))
        for button in self.buttons:
            button.draw(self.screen, 50, (255, 0, 0))
        pygame.display.flip()



