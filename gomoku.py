import time

import pygame
import numpy as np

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

WINDOW_SIZE = (1200, 800)  # pygame 창 크기 (pixel)

BOARD_SIZE = 600  # pygame 보드 크기 (pixel)
BOARD_MARGIN = np.array([100, 100])  # pygame 보드 위치 조정 (pixel)
# board를 기준으로 pygame 텍스트 위치 조정 (pixel)
TEXT_MARGIN = BOARD_MARGIN + np.array([BOARD_SIZE + 50, 0])

BOARD_SHAPE = (15, 15)
LINE_GAP = int(BOARD_SIZE / BOARD_SHAPE[0])  # pygame 그릴 때, 격자 간격 (pixel)

DOT_SIZE = 4
FONT_SIZE = 30

CIRCLE_RADIUS = int(LINE_GAP / 2.5)  # pygame 돌 그릴 때, 반지름 (pixel)

class Gomoku:
    def __init__(self):
        # 0: empty, 1: black, -1: white
        self.board = np.zeros(BOARD_SHAPE, dtype=np.int8)
        self.pygame_init()
        self.turn = 1  # 1: black, -1: white
        self.done = False

        self.board_history = []

    def step(self, action):  # action: np.ndarray(x, y)
        if self.board[tuple(action)] != 0:
            raise ValueError('Invalid action')

        next_board = self.board.copy()
        next_board[tuple(action)] = self.turn

        self.board = next_board
        self.board_history.append(self.board)

        # reward = self.judge() * self.turn
        reward = 0
        self.done = self.is_finished(action)

        self.turn *= -1
        return self.board, reward, self.done

    def judge(self):

        #5개 연속으로 놓여있는지 확인
        #가로
        for i in range(BOARD_SHAPE[0]):
            pass
            #3개 연속으로 놓여있는지 확인
            #가로
        for i in range(BOARD_SHAPE[0]):
            for j in range(BOARD_SHAPE[0]-4):
                if np.all(self.board[i:i+4][j]) == self.turn:
                    return self.turn
        #세로
        for i in range(BOARD_SHAPE[0]-4):
            for j in range(BOARD_SHAPE[0]):
                if np.all(self.board[i][j:j+4]) == self.turn:
                    return self.turn
        #대각선
        for i in range(BOARD_SHAPE[0]-4):
            for j in range(BOARD_SHAPE[0]-4):
                if self.board[i][j] == self.board[i+1][j+1] == self.board[i+2][j+2] == self.board[i+3][j+3] == self.board[i+4][j+4] == self.turn:
                    return self.turn
        for i in range(BOARD_SHAPE[0]-4):
            for j in range(4, BOARD_SHAPE[0]):
                if self.board[i][j] == self.board[i+1][j-1] == self.board[i+2][j-2] == self.board[i+3][j-3] == self.board[i+4][j-4] == self.turn:
                    return self.turn

    def check_five_in_a_row(self, stone, direction, count):
        if count == 5:
            return count

        next_stone = stone + direction

        # 보드 범위 밖의 좌표는 무시하기
        if not np.all((0 <= next_stone) & (next_stone < BOARD_SHAPE[0])):
            return count

        if self.board[tuple(next_stone)] == self.turn:  # 같은 색의 돌이면
            return self.check_five_in_a_row(next_stone, direction, count+1)
        else:
            return count

    def is_finished(self, last_stone):
        last_stone = np.array(last_stone)
        directions = np.array([[1, 0], [0, 1], [1, 1], [1, -1]])

        # 8방향으로 5개 연속으로 놓여있는지 확인
        for direction in directions:
            # 5개 연속으로 놓여있는지 확인
            way1 = self.check_five_in_a_row(last_stone, direction, 1)
            way2 = self.check_five_in_a_row(last_stone, -direction, 1)
            if way1 + way2 - 1 >= 5:
                return True
        else:
            return False

    # pygame 초기화
    def pygame_init(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption('Gomoku')
        pygame.display.flip()

    # pygame 렌더
    def render(self):
        self.screen.fill(WHITE)

        # draw line
        for i in range(15):
            pygame.draw.line(self.screen, BLACK, (0, i*LINE_GAP) + BOARD_MARGIN,
                             (BOARD_SIZE-LINE_GAP, i*LINE_GAP) + BOARD_MARGIN)
            pygame.draw.line(self.screen, BLACK, (i*LINE_GAP, 0) + BOARD_MARGIN,
                             (i*LINE_GAP, BOARD_SIZE-LINE_GAP) + BOARD_MARGIN)

        # draw dot
        for i in range(3):
            for j in range(3):
                pygame.draw.circle(self.screen, BLACK, (i*4*LINE_GAP, j*4*LINE_GAP) +
                                   BOARD_MARGIN + (LINE_GAP*3, LINE_GAP*3), DOT_SIZE)

        # draw stone
        for i in range(15):
            for j in range(15):
                if self.board[i][j] == 1:
                    pygame.draw.circle(
                        self.screen, BLACK, (i*LINE_GAP, j*LINE_GAP) + BOARD_MARGIN, CIRCLE_RADIUS)

                elif self.board[i][j] == -1:
                    pygame.draw.circle(
                        self.screen, WHITE, (i*LINE_GAP, j*LINE_GAP) + BOARD_MARGIN, CIRCLE_RADIUS)
                    pygame.draw.circle(
                        self.screen, BLACK, (i*LINE_GAP, j*LINE_GAP) + BOARD_MARGIN, CIRCLE_RADIUS, 1)

        # turn 표시
        if self.done * self.turn == -1:
            text = 'Black win'
        elif self.done * self.turn == 1:
            text = 'White win'
        elif self.turn == 1:
            text = 'Black turn'
        else:
            text = 'White turn'

        font = pygame.font.SysFont('comicsansms', FONT_SIZE)
        text = font.render(text, True, BLACK)
        self.screen.blit(text, TEXT_MARGIN)

        # 다른 클래스 상속받아서 사용할 때는 pygame.display.flip()을 호출하지 않음
        if type(self) == Gomoku:
            pygame.display.flip()

    def reset(self):
        self.board = np.zeros(BOARD_SHAPE)
        self.turn = 1
        self.done = False
        self.board_history = []

    def undo(self):
        if len(self.board_history) > 0:
            self.board_history.pop()
            self.board = self.board_history[-1]
            self.turn *= -1
            self.done = False


# 자동으로 돌을 두는 예제 실행
if __name__ == '__main__':
    gomoku = Gomoku()
    gomoku.render()
    time.sleep(1)

    gomoku.step((1, 1))
    gomoku.render()
    time.sleep(1)

    gomoku.step((2, 2))
    gomoku.render()
    time.sleep(1)

    gomoku.step((3, 3))
    gomoku.render()
    time.sleep(1)

    gomoku.step((4, 4))
    gomoku.render()
    time.sleep(1)
