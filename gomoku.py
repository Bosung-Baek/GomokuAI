import time

import pygame
import numpy as np

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

WINDOW_SIZE = (1200, 800)  # pygame 창 크기 (pixel)

BOARD_SIZE = 600  # pygame 보드 크기 (pixel)
BOARD_MARGIN = np.array([100, 100])  # pygame 보드 위치 조정 (pixel)

STONE_NUM = 15
BOARD_SHAPE = (STONE_NUM, STONE_NUM)

LINE_GAP = int(BOARD_SIZE / STONE_NUM)  # pygame 그릴 때, 격자 간격 (pixel)
DOT_SIZE = 4

class Gomoku:
    def __init__(self):
        self.board = np.zeros(BOARD_SHAPE)
        self.pygame_init()
        self.turn = 1  # 1: black, -1: white
        self.done = False

        self.board_history = []

    def step(self, action):  # action: (x, y)
        if self.board[action] != 0:
            raise ValueError('Invalid action')
        
        new_board = self.board.copy()
        new_board[action] = self.turn
        self.board_history.append(new_board)

        reward = self.judge(action)*self.turn

        self.turn *= -1
        self.board = new_board
        return self.board, reward

    def judge(self):
        
        #5개 연속으로 놓여있는지 확인
        #가로
        for i in range(STONE_NUM):

        #3개 연속으로 놓여있는지 확인
        #가로
        for i in range(STONE_NUM):
            for j in range(STONE_NUM-4):
                if np.all(self.board[i:i+4][j]) == self.turn:
                    return self.turn
        #세로
        for i in range(STONE_NUM-4):
            for j in range(STONE_NUM):
                if np.all(self.board[i][j:j+4]) == self.turn:
                    return self.turn
        #대각선
        for i in range(STONE_NUM-4):
            for j in range(STONE_NUM-4):
                if self.board[i][j] == self.board[i+1][j+1] == self.board[i+2][j+2] == self.board[i+3][j+3] == self.board[i+4][j+4] == self.turn:
                    return self.turn
        for i in range(STONE_NUM-4):
            for j in range(4, STONE_NUM):
                if self.board[i][j] == self.board[i+1][j-1] == self.board[i+2][j-2] == self.board[i+3][j-3] == self.board[i+4][j-4] == self.turn:
                    return self.turn
        
            
    def pygame_init(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption('Gomoku')
        pygame.display.flip()


    def render(self):
        self.screen.fill(WHITE)

        # draw line
        for i in range(15):
            pygame.draw.line(self.screen, BLACK, (0, i*LINE_GAP) + BOARD_MARGIN, (BOARD_SIZE-LINE_GAP, i*LINE_GAP) + BOARD_MARGIN)
            pygame.draw.line(self.screen, BLACK, (i*LINE_GAP, 0) + BOARD_MARGIN, (i*LINE_GAP, BOARD_SIZE-LINE_GAP) + BOARD_MARGIN)
        
        # draw dot
        for i in range(3):
            for j in range(3):
                pygame.draw.circle(self.screen, BLACK, (i*4*LINE_GAP, j*4*LINE_GAP) + BOARD_MARGIN + (LINE_GAP*3, LINE_GAP*3), DOT_SIZE)

        # draw stone
        for i in range(15):
            for j in range(15):
                if self.board[i][j] == 1:
                    pygame.draw.circle(self.screen, BLACK, (i*LINE_GAP, j*LINE_GAP) + BOARD_MARGIN, int(LINE_GAP/2))

                elif self.board[i][j] == -1:
                    pygame.draw.circle(self.screen, WHITE, (i*LINE_GAP, j*LINE_GAP) + BOARD_MARGIN, int(LINE_GAP/2))
                    pygame.draw.circle(self.screen, BLACK, (i*LINE_GAP, j*LINE_GAP) + BOARD_MARGIN, int(LINE_GAP/2), 1)

        # say turn
        if self.turn == 1:
            text = 'Black turn'
        else:
            text = 'White turn'
        font = pygame.font.SysFont('comicsansms', 30)
        text = font.render(text, True, BLACK)
        self.screen.blit(text, (BOARD_SIZE + BOARD_MARGIN[0] + 50, BOARD_MARGIN[1]))

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
