from dataclasses import dataclass, field, replace
import pygame
from pygame.locals import *
import random
from collections import deque
import jsonpickle
import json
import numpy as np
from bitstring import BitArray
import copy


@dataclass()
class Square:
    digit: int = None
    corner: set[int] = field(default_factory=set)
    center: set[int] = field(default_factory=set)
    color: int = None
    frozen: bool = False

    def change_square(self, attr, value):
        if attr != "color" and self.frozen: return self
        if attr is None: return Square()
        elif isinstance(digits := getattr(self, attr), set):
            if value in digits:
                return replace(self, **{attr: (digits - {value})})
            return replace(self, **{attr: (digits | {value})})
        elif getattr(self, attr) == value:
            return replace(self, **{attr: None})
        return replace(self, **{attr: value})

    def draw(self, screen, size, x, y, font, font2, colors):
        if self.color is not None:
            rect = pygame.Rect(x * size, y * size, size, size)
            pygame.draw.rect(screen, colors[self.color], rect)
        if self.digit is not None:
            bold = self.frozen
            text = font.render(str(self.digit), bold, (0, 0, 0) if self.frozen else (0, 0, 255))
            text_rect = text.get_rect()
            text_rect.center = ((x + 0.5) * size, (y + 0.5) * size)
            screen.blit(text, text_rect)
        else:
            text = font2.render("".join([str(x) for x in sorted(self.center)]), False, (0, 0, 0))
            text_rect = text.get_rect()
            text_rect.center = ((x + 0.5) * size, (y + 0.5) * size)
            screen.blit(text, text_rect)
            text = font2.render("".join([str(x) for x in sorted(self.corner)]), False, (0, 0, 0))
            text_rect = text.get_rect()
            text_rect.midleft = ((x + 0.05) * size, (y + 0.14) * size)
            screen.blit(text, text_rect)


class Sudoku:

    def __init__(self, width: int, height: int, regions: list[set[tuple[int, int]]] = None, arrows=None, cages=None):
        self.width = width
        self.height = width
        self.regions = regions if regions is not None else \
            [{(i + x, j + y) for x in range(3) for y in range(3)} for i in range(0, 9, 3) for j in range(0, 9, 3)]
        self.squares = np.array([[Square() for _ in range(width)] for _ in range(height)])
        self.arrows = arrows
        self.cages = cages
        self.action_stack = deque()
        self.redo_stack = deque()

    def change_squares(self, attr: str | None, value, squares: set[tuple[int, int]]) -> None:
        self.action_stack.append([(self.squares[y][x], x, y) for x, y in squares])
        for x, y in squares:
            self.squares[y][x] = self.squares[y][x].change_square(attr, value)

    def delete_squares(self, squares: set[tuple[int, int]]):
        self.change_squares(None, None, squares)

    def undo(self):
        self.undo_redo(self.action_stack, self.redo_stack)

    def redo(self):
        self.undo_redo(self.redo_stack, self.action_stack)

    def undo_redo(self, stack, other):
        if not stack: return
        top = stack.pop()
        other.append([(self.squares[y][x], x, y) for square, x, y in top])
        for square, x, y in top:
            self.squares[y][x] = square

    def clear(self):
        self.change_squares(None, None, {(x, y) for x in range(self.width) for y in range(self.width)})

    def draw(self, screen: pygame.Surface, size: int, colors: list[tuple[int, int, int]], i):
        font = pygame.font.SysFont("microsoftsansserif", size)
        small_font = pygame.font.SysFont("microsoftsansserif", size // 3)
        for y, row in enumerate(self.squares):
            for x, square in enumerate(row):
                self.squares[y][x].draw(screen, size, x, y, font, small_font, colors)

    def validate(self):
        for row in self.squares:
            digits = set()
            for square in row:
                if square.digit in digits and square.digit is not None: return False
                digits.add(square.digit)
        for x in range(self.width):
            digits = set()
            for y in range(self.height):
                square = self.squares[y][x]
                if square.digit in digits and square.digit is not None: return False
                digits.add(square.digit)

    def json(self):
        return {"width": self.width, "height": self.height,
                "squares": [[self.squares[y][x].digit for x in range(self.width)] for y in range(self.height)]}

    def get_all_digits_of_type(self, x, y, mode):
        digit = self.squares[y][x].digit
        if digit is None: return
        return {(x, y) for y in range(self.height) for x in range(self.width) if self.squares[y][x].digit == digit}


def solveSudoku(squares, screen):
    digits = [(x, y) for x in range(squares.shape[1]) for y in range(squares.shape[0]) if squares[y, x].digit is not None]
    sudoku = np.array([[{square.digit} if square.digit is not None else
                        set(range(1, 10)) for x, square in enumerate(row)] for y, row in enumerate(squares)])
    #print(sudoku)
    #print(digits)
    for x, y in digits:
        update_candidates(sudoku, x, y)

    return recursive_solve(sudoku, screen)



def recursive_solve(sudoku, screen, x=None, y=None):
    sudoku = copy.deepcopy(sudoku)
    print(sudoku)
    if x is not None:
        if len(sudoku[y][x]) == 1:
            update_candidates(sudoku, x, y)
    #print(sudoku)
    for y, row in enumerate(sudoku):
        for x, square in enumerate(row):
            if len(square) == 0:
                print("asdasdsad")
                return
            if len(square) > 1:
                for digit in list(sudoku[y, x]):
                    sudoku[y][x] = {digit}
                    if (solve := recursive_solve(sudoku, screen, x, y)) is not None:
                        return solve
                print(8)
                return
    for y, row in enumerate(sudoku):
        for x, square in enumerate(row):
            update_candidates(sudoku, x, y)
    for y, row in enumerate(sudoku):
        for x, square in enumerate(row):
            if not square: return
    return sudoku
"""
    min = None
    min_val = None
    for y, row in enumerate(sudoku):
        for x, square in enumerate(row):
            if (length := len(square)) == 0: return
            if length == 2:
                first, second = list(square)
                square.remove(first)
                if (solve := recursive_solve(sudoku, screen, x, y)) is not None:
                    return solve
                square.append(first)
                square.remove(second)
                return recursive_solve(sudoku)
            if 1 < length  and (min_val is None or length < min_val):
                min = x, y
                min_val = length
    if min is None: return sudoku
    x, y = min
    for digit in list(sudoku[y, x]):
        sudoku[y][x] = {digit}
        if solve := recursive_solve(sudoku, screen, x, y):
            return solve
"""

def update_candidates(sudoku, x, y):
    for x_, y_ in [(x2, y) for x2 in range(9)] + [(x, y2) for y2 in range(9)] + \
                  [(x2, y2) for x2 in range((x // 3) * 3, (x // 3) * 3 + 3) for y2 in range((y // 3) * 3, (y // 3) * 3 + 3)]:

        if (x, y) != (x_, y_):
            length = len(sudoku[y][x])
            sudoku[y_, x_] = sudoku[y_, x_] - sudoku[y, x]
            if len(sudoku[y_, x_]) == 1 < length:
                update_candidates(sudoku, x_, y_)





