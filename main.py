import numpy
import pygame
from sudoku import Sudoku, solveSudoku, Square
from sudokuViewer import SudokuViewer, SudokuSetter
from resources import load_sudoku
import numpy as np
from menu import Menu


def _main():
    pass
    pygame.init()

    screen = pygame.display.set_mode((1400, 800))
    #menu = Menu(screen)
    #soduku = menu.main_menu()
    #sudoku = Sudoku(9, 9)
    #s_viewer = SudokuSetter(screen)
    #s_viewer.game_loop()


    #
    sudoku = solveSudoku(load_sudoku(-1).squares, None)
    s = Sudoku(9, 9)
    print(sudoku)
    s.squares = [[Square(list(digit)[0]) for digit in row] for row in sudoku]
    s_viewer = SudokuViewer(s, screen)
    s_viewer.game_loop()
    pygame.quit()


if __name__ == "__main__":
    _main()
