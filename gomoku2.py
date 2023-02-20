import time
import pyautogui

import pygame
import numpy as np

import clipboard

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
        self.reward = 0
        self.before_opponent_action = None

        self.board_history = []

    def step(self, action):  # action: np.ndarray(y, x)
        if self.board[tuple(action)] != 0:
            raise ValueError('Invalid action')

        next_board = self.board.copy()
        next_board[tuple(action)] = self.turn

        # yixin 착수하는 부분
        yixin_margin = np.array([92, 109])
        yixin_gap = 41
        yixin_pos = yixin_margin + yixin_gap * action
        pyautogui.moveTo(tuple(yixin_pos))
        pyautogui.rightClick()

        self.board = next_board
        self.board_history.append(self.board)

        # self.reward = self.judge() * self.turn
        # reward = 0
        self.done = self.is_finished(action)  # True or False - (-self.turn)

        self.turn *= -1
        return self.done

    def opponent_step(self):
        zoom = 1.25
        log_pos = (int(607*zoom), int(472*zoom))

        pyautogui.moveTo(log_pos)
        pyautogui.rightClick()
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')

        log = clipboard.paste()
        opponent_action = log.split("BESTLINE: ")[-1].split(" ")[0].lstrip("[").rstrip("]")
        while opponent_action == self.before_opponent_action:
            time.sleep(1)
            pyautogui.rightClick()
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'c')

            log = clipboard.paste()
            opponent_action = log.split("BESTLINE: ")[-1].split(" ")[0].lstrip("[").rstrip("]")
        self.before_opponent_action = opponent_action
        opponent_action = np.array([15-int(opponent_action[1:]), ord(opponent_action[0])-ord('A')])

        self.board[tuple(opponent_action)] = -1
        self.turn *= -1

        self.reward = self.judge() * self.turn
        self.done = self.is_finished(opponent_action)

        return self.board, self.reward, self.done


    def judge(self):
        zoom = 1.25
        log_pos = (int(607*zoom), int(472*zoom))

        pyautogui.moveTo(log_pos)
        pyautogui.rightClick()
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')

        log = clipboard.paste()
        score = int(log.split("EVALUATION: ")[-1].split(" ")[0])

        return -score
        

    def check_five_in_a_row(self, stone, direction, count):
        if count == 5:
            return count, False

        next_stone = stone + direction

        # 보드 범위 밖의 좌표는 무시하기
        if not np.all((0 <= next_stone) & (next_stone < BOARD_SHAPE[0])):
            return count, True

        if self.board[tuple(next_stone)] == self.turn:  # 같은 색의 돌이면
            return self.check_five_in_a_row(next_stone, direction, count+1)
        elif self.board[tuple(next_stone)] == -self.turn: # 다른 색의 돌이면
            return count, True
        else:
            return count, False

    def is_finished(self, last_stone):
        last_stone = np.array(last_stone)
        directions = np.array([[1, 0], [0, 1], [1, 1], [1, -1]])

        # 8방향으로 5개 연속으로 놓여있는지 확인
        for direction in directions:
            # 5개 연속으로 놓여있는지 확인
            way1, _ = self.check_five_in_a_row(last_stone, direction, 1)
            way2, _ = self.check_five_in_a_row(last_stone, -direction, 1)
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

        # 점수 표시
        text = str(self.reward)
        # font = pygame.font.SysFont('comicsansms', FONT_SIZE)
        text = font.render(text, True, BLACK)
        self.screen.blit(text, TEXT_MARGIN + (0, 40))



        # 다른 클래스 상속받아서 사용할 때는 pygame.display.flip()을 호출하지 않음
        if type(self) == Gomoku:
            pygame.display.flip()

        # FPS
        clock = pygame.time.Clock()
        clock.tick(20)

    def reset(self):
        self.board = np.zeros(BOARD_SHAPE)
        self.turn = 1
        self.done = False
        self.board_history = []

        return self.board

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
