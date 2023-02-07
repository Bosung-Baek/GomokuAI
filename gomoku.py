import time

import pygame
import numpy as np

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

WINDOW_X = 1200
WINDOW_Y = 800

BOARD_SIZE = 600
BOARD_MARGIN = np.array([100, 100])

BOARD_NUM = 15
BOARD_SHAPE = (BOARD_NUM, BOARD_NUM)

LINE_GAP = int(BOARD_SIZE / BOARD_NUM)  # pygame 그릴 때, 격자 간격 (pixel)
DOT_SIZE = 4

class Gomoku:
    def __init__(self):
        self.board = np.zeros(BOARD_SHAPE)
        self.pygame_init()
        self.turn = 1  # 1: black, -1: white

    def step(self, action):
        if self.board[action] != 0:
            raise ValueError('Invalid action')

        self.board[action] = self.turn
        self.turn *= -1
        return self.board, self.reward(), self.done()

    def reward(self):
        pass

    def done(self):
        pass
    
    def pygame_init(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_X, WINDOW_Y))
        self.screen.fill(WHITE)
        pygame.display.set_caption('Gomoku')
        pygame.display.flip()


    def render(self):
        # draw line
        for i in range(15):
            pygame.draw.line(self.screen, BLACK, (0, i*LINE_GAP) + BOARD_MARGIN, (BOARD_SIZE-LINE_GAP, i*LINE_GAP) + BOARD_MARGIN)
            pygame.draw.line(self.screen, BLACK, (i*LINE_GAP, 0) + BOARD_MARGIN, (i*LINE_GAP, BOARD_SIZE-LINE_GAP) + BOARD_MARGIN)
        
        # draw dot
        for i in range(3):
            for j in range(3):
                pygame.draw.circle(self.screen, BLACK, (i*7*LINE_GAP, j*7*LINE_GAP) + BOARD_MARGIN, DOT_SIZE)

        # draw stone
        for i in range(15):
            for j in range(15):
                if self.board[i][j] == 1:
                    pygame.draw.circle(self.screen, BLACK, (i*LINE_GAP, j*LINE_GAP) + BOARD_MARGIN, int(LINE_GAP/2))

                elif self.board[i][j] == -1:
                    pygame.draw.circle(self.screen, WHITE, (i*LINE_GAP, j*LINE_GAP) + BOARD_MARGIN, int(LINE_GAP/2))
                    pygame.draw.circle(self.screen, BLACK, (i*LINE_GAP, j*LINE_GAP) + BOARD_MARGIN, int(LINE_GAP/2), 1)

        pygame.display.flip()
        

if __name__ == '__main__':
    gomoku = Gomoku()
    gomoku.render()
    gomoku.step((1, 1))
    time.sleep(1)

    gomoku.render()
    gomoku.step((2, 2))
    time.sleep(1)

    gomoku.render()
    gomoku.step((3, 3))
    time.sleep(1)

    gomoku.render()
    gomoku.step((4, 4))
    time.sleep(1)
