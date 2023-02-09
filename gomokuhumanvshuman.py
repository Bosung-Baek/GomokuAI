from gomoku import *

import sys
import pygame

FPS = 10


class GomokuHumanVsHuman(Gomoku):
    def render(self):
        super().render()

        # 마우스 커서 위치에 힌트 표시
        mouse_pos = np.array(pygame.mouse.get_pos())
        stone_pos = (mouse_pos+LINE_GAP/2 - BOARD_MARGIN) / LINE_GAP
        stone_pos = np.array(stone_pos, dtype=int)

        # 마우스 커서 위치가 보드 안에 있을 때만 힌트 표시
        if np.all((stone_pos >= 0) & (stone_pos < STONE_NUM)):
            if self.board[tuple(stone_pos)] == 0:
                pygame.draw.circle(self.screen, (0, 0, 0),
                                   stone_pos * LINE_GAP + BOARD_MARGIN, CIRCLE_RADIUS, 1)
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
            mouse_pos = np.array(pygame.mouse.get_pos())
            stone_pos = (mouse_pos+LINE_GAP/2 - BOARD_MARGIN) / LINE_GAP
            stone_pos = np.array(stone_pos, dtype=int)
            if np.all((stone_pos >= 0) & (stone_pos < STONE_NUM)):
                if gomoku.board[tuple(stone_pos)] == 0:
                    gomoku.step(stone_pos)

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
