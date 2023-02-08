from gomoku import *

import sys
import pygame

FPS = 10


class GomokuHumanVsHuman(Gomoku):
    def render(self):
        super().render()

        # 마우스 커서 위치에 힌트 표시
        x, y = pygame.mouse.get_pos()
        x = int(((x+LINE_GAP/2) - BOARD_MARGIN[0]) / LINE_GAP)
        y = int(((y+LINE_GAP/2) - BOARD_MARGIN[1]) / LINE_GAP)

        # 마우스 커서 위치가 보드 안에 있을 때만 힌트 표시
        if 0 <= x < STONE_NUM and 0 <= y < STONE_NUM:
            if self.board[x, y] == 0:
                pygame.draw.circle(self.screen, (0, 0, 0), (x * LINE_GAP +
                                   BOARD_MARGIN[0], y * LINE_GAP + BOARD_MARGIN[1]), CIRCLE_RADIUS, 1)

        pygame.display.flip()


gomoku = GomokuHumanVsHuman()

while True:

    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # 마우스 클릭 시 돌 놓기
        if event.type == pygame.MOUSEBUTTONDOWN and not gomoku.done:
            x, y = event.pos
            x = int(((x+LINE_GAP/2) - BOARD_MARGIN[0]) / LINE_GAP)
            y = int(((y+LINE_GAP/2) - BOARD_MARGIN[1]) / LINE_GAP)
            if 0 <= x < STONE_NUM and 0 <= y < STONE_NUM:
                if gomoku.board[x, y] == 0:
                    gomoku.step((x, y))

        # 스페이스바 누르면 게임 리셋, 왼쪽 화살표 누르면 한 수 뒤로
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                gomoku.reset()
            elif event.key == pygame.K_LEFT:
                gomoku.undo()

    gomoku.render()

    # 프레임 속도 조절
    clock = pygame.time.Clock()
    clock.tick(FPS)
