
import pygame
from game.maze import CELL

SPEED = 2


class Player:
    def __init__(self, r, c):
        self.r, self.c = r, c

        cx = c * CELL + CELL // 2
        cy = r * CELL + CELL // 2

        self.rect = pygame.Rect(cx - 10, cy - 10, 20, 20)
        self.color = (60, 120, 220)

    def move(self, keys, walls, rows, cols):
        dx = dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = SPEED

        new_rect = self.rect.move(dx, 0)
        if self._valid(new_rect, walls, rows, cols):
            self.rect = new_rect

        new_rect = self.rect.move(0, dy)
        if self._valid(new_rect, walls, rows, cols):
            self.rect = new_rect

    def _valid(self, rect, walls, rows, cols):
        points = [
            (rect.left, rect.top),
            (rect.right - 1, rect.top),
            (rect.left, rect.bottom - 1),
            (rect.right - 1, rect.bottom - 1),
        ]

        for px, py in points:
            cr, cc = py // CELL, px // CELL

            if not (0 <= cr < rows and 0 <= cc < cols):
                return False

        return True

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)


class Enemy:
    def __init__(self, r, c):
        self.r, self.c = r, c

        cx = c * CELL + CELL // 2
        cy = r * CELL + CELL // 2

        self.rect = pygame.Rect(cx - 12, cy - 12, 24, 24)
        self.color = (220, 60, 60)

        self.timer = 0
        self.move_interval = 20

        # Power-pellet freeze state
        self.frozen = False
        self.freeze_timer = 0

    def update(self, walls, player, rows, cols):
        if self.frozen:
            self.freeze_timer -= 1

            if self.freeze_timer <= 0:
                self.freeze_timer = 0
                self.frozen = False

            return

        from game.maze import bfs

        self.timer += 1

        if self.timer >= self.move_interval:
            self.timer = 0

            pr = player.rect.centery // CELL
            pc = player.rect.centerx // CELL

            step = bfs(
                walls,
                (self.r, self.c),
                (pr, pc),
                rows,
                cols,
            )

            if step:
                dr, dc = step
                self.r += dr
                self.c += dc

                cx = self.c * CELL + CELL // 2
                cy = self.r * CELL + CELL // 2

                self.rect.center = (cx, cy)

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            self.color,
            self.rect,
            border_radius=5,
        )

        # Blue ring indicates that the enemy is frozen
        if self.frozen:
            pygame.draw.circle(
                screen,
                (100, 200, 255),
                self.rect.center,
                16,
                3,
            )

        # Eyes
        for ex in [self.rect.x + 4, self.rect.x + 14]:
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (ex, self.rect.y + 8),
                4,
            )
            pygame.draw.circle(
                screen,
                (0, 0, 0),
                (ex + 1, self.rect.y + 8),
                2,
            )
