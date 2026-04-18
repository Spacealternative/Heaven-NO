import math
import random
import sys
from pathlib import Path

import pygame

pygame.init()
pygame.display.set_caption("WW2 Anti-Air Defense")

WIDTH, HEIGHT = 960, 640
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
FPS = 60

SKY = (40, 40, 50)
GROUND = (28, 28, 34)
WHITE = (255, 255, 255)
RED = (220, 60, 60)
YELLOW = (245, 210, 80)
GRAY = (120, 120, 120)
DARK_GRAY = (70, 70, 80)
BLACK = (18, 18, 24)
LIGHT = (210, 210, 210)
BEAM = (255, 255, 210)

FONT_BIG = pygame.font.SysFont("arial", 44, bold=True)
FONT_MED = pygame.font.SysFont("arial", 28, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 20)

GAME_TIME = 60
MAX_MISSES = 7

CANNON_BASE = (WIDTH // 2, HEIGHT - 60)
ANGLE_OPTIONS = [80, 60, 40, 20, 10]
ANGLE_LABELS = ["80", "60", "40", "20", "10"]
BULLET_SPEED = 12
BULLET_RADIUS = 4

BUTTON_W, BUTTON_H = 180, 60
AIM_RECT = pygame.Rect(40, HEIGHT - 90, BUTTON_W, BUTTON_H)
SHOOT_RECT = pygame.Rect(WIDTH - 220, HEIGHT - 90, BUTTON_W, BUTTON_H)
RESTART_RECT = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 60, 240, 54)

PLANE_SPAWN_MIN = 0.8
PLANE_SPAWN_MAX = 1.8
PLANE_PATHS = {
    "B17": Path(r"D:\Hamster\Material\B17.png"),
    "B29": Path(r"D:\Hamster\Material\B29.png"),
    "B36": Path(r"D:\Hamster\Material\B36.png"),
}
FIRE_PATH = Path(r"D:\Hamster\Material\FIRE.png")


def draw_text(surface, text, font, color, x, y, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(img, rect)


def clamp(value, low, high):
    return max(low, min(high, value))


def load_image(path, size, fallback_color=(220, 220, 220)):
    if path.exists():
        img = pygame.image.load(str(path)).convert_alpha()
    else:
        img = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(img, fallback_color, (0, 0, size[0], size[1]))
    return pygame.transform.smoothscale(img, size)


def tint_image(img, tint):
    out = img.copy()
    out.fill((*tint, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return out


B17_IMG = load_image(PLANE_PATHS["B17"], (92, 46))
B29_IMG = load_image(PLANE_PATHS["B29"], (118, 52))
B36_IMG = load_image(PLANE_PATHS["B36"], (156, 60))
FIRE_IMG = load_image(FIRE_PATH, (42, 42), (255, 150, 60))


class Button:
    def __init__(self, rect, text, color, text_color=WHITE):
        self.rect = rect
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=12)
        pygame.draw.rect(surface, WHITE, self.rect, 3, border_radius=12)
        draw_text(surface, self.text, FONT_MED, self.text_color, self.rect.centerx, self.rect.centery, center=True)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


class Bullet:
    def __init__(self, x, y, angle_deg):
        rad = math.radians(angle_deg)
        self.x = x
        self.y = y
        self.vx = math.cos(rad) * BULLET_SPEED
        self.vy = -math.sin(rad) * BULLET_SPEED
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < -30 or self.x > WIDTH + 30 or self.y < -30 or self.y > HEIGHT + 30:
            self.alive = False

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), BULLET_RADIUS)

    def rect(self):
        return pygame.Rect(int(self.x - BULLET_RADIUS), int(self.y - BULLET_RADIUS), BULLET_RADIUS * 2, BULLET_RADIUS * 2)


class Plane:
    def __init__(self):
        self.kind = random.choice(["B17", "B29", "B36"])
        self.from_left = random.choice([True, False])
        self.falling = False
        self.alive = True
        self.dead = False
        self.counted = False
        self.vy = 0.0
        self.spin = 0.0

        if self.kind == "B17":
            self.base_img = B17_IMG
            self.night_img = tint_image(self.base_img, (110, 110, 120))
            self.y = random.randint(220, 300)
            self.speed = random.uniform(1.4, 2.0)
        elif self.kind == "B29":
            self.base_img = B29_IMG
            self.night_img = tint_image(self.base_img, (100, 100, 112))
            self.y = random.randint(140, 200)
            self.speed = random.uniform(1.2, 1.8)
        else:
            self.base_img = B36_IMG
            self.night_img = tint_image(self.base_img, (95, 95, 108))
            self.y = random.randint(70, 130)
            self.speed = random.uniform(3.0, 4.2)

        self.img = self.base_img if self.from_left else pygame.transform.flip(self.base_img, True, False)
        self.night_img = self.night_img if self.from_left else pygame.transform.flip(self.night_img, True, False)
        self.x = -self.img.get_width() if self.from_left else WIDTH + self.img.get_width()
        self.vx = self.speed if self.from_left else -self.speed
        self.w = self.img.get_width()
        self.h = self.img.get_height()

    def center(self):
        return self.x + self.w * 0.5, self.y + self.h * 0.5

    def hit(self):
        self.falling = True
        self.vy = 0
        self.spin = random.choice([-4.0, -2.5, 2.5, 4.0])

    def update(self):
        if self.falling:
            self.vy += 0.22
            self.y += self.vy
            self.x += self.vx
            self.vx *= 0.995
            self.spin += 0.35
            if self.y > HEIGHT + 120:
                self.dead = True
        else:
            self.x += self.vx
            if self.x < -180 or self.x > WIDTH + 180:
                self.dead = True

    def draw(self, surface, lit):
        img = self.img if lit else self.night_img
        if self.falling:
            rotated = pygame.transform.rotozoom(img, self.spin, 1.0)
            r = rotated.get_rect(center=(int(self.x + self.w * 0.5), int(self.y + self.h * 0.5)))
            surface.blit(rotated, r.topleft)
            fx = FIRE_IMG
            if self.spin < 0:
                fx = pygame.transform.rotate(FIRE_IMG, -15)
            surface.blit(fx, (int(self.x + self.w * 0.35), int(self.y + self.h * 0.45)))
        else:
            surface.blit(img, (int(self.x), int(self.y)))

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)


class SearchLight:
    def __init__(self, origin, side):
        self.origin = origin
        self.side = side
        self.angle = -55 if side == "left" else -125
        self.sweep_dir = 1 if side == "left" else -1
        self.sweep_min = -88 if side == "left" else -92
        self.sweep_max = -12 if side == "left" else -168
        self.sweep_speed = 0.45
        self.spread = 16
        self.range = 470
        self.locked_plane = None

    def angle_to_plane(self, plane):
        px, py = plane.center()
        dx = px - self.origin[0]
        dy = py - self.origin[1]
        return math.degrees(math.atan2(dy, dx))

    def dist_to_plane(self, plane):
        px, py = plane.center()
        dx = px - self.origin[0]
        dy = py - self.origin[1]
        return math.hypot(dx, dy)

    def cone_match(self, plane):
        if not plane.alive:
            return False
        dist = self.dist_to_plane(plane)
        if dist > self.range:
            return False
        ang = self.angle_to_plane(plane)
        diff = abs((ang - self.angle + 180) % 360 - 180)
        return diff <= self.spread

    def update(self, planes):
        if self.locked_plane is not None:
            if (not self.locked_plane.alive
                or self.locked_plane.falling
                or self.dist_to_plane(self.locked_plane) > self.range):
                self.locked_plane = None

        if self.locked_plane is None:
            self.angle += self.sweep_speed * self.sweep_dir
            if self.side == "left":
                if self.angle > self.sweep_max:
                    self.sweep_dir = -1
                elif self.angle < self.sweep_min:
                    self.sweep_dir = 1
            else:
                if self.angle < self.sweep_max:
                    self.sweep_dir = 1
                elif self.angle > self.sweep_min:
                    self.sweep_dir = -1

            candidates = [p for p in planes if self.cone_match(p) and not p.falling]
            if candidates:
                candidates.sort(key=self.dist_to_plane)
                self.locked_plane = candidates[0]

        if self.locked_plane is not None:
            self.angle = self.angle_to_plane(self.locked_plane)

    def points(self):
        ox, oy = self.origin
        left = self.angle - self.spread
        right = self.angle + self.spread
        p1 = (ox, oy)
        p2 = (ox + math.cos(math.radians(left)) * self.range, oy + math.sin(math.radians(left)) * self.range)
        p3 = (ox + math.cos(math.radians(right)) * self.range, oy + math.sin(math.radians(right)) * self.range)
        return [p1, p2, p3]

    def contains(self, plane):
        return self.locked_plane is plane or self.cone_match(plane)

    def draw(self, surface):
        beam = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(beam, (255, 255, 210, 44), self.points())
        pygame.draw.polygon(beam, (255, 255, 210, 92), self.points(), 2)
        surface.blit(beam, (0, 0))
        ox, oy = self.origin
        ex = ox + math.cos(math.radians(self.angle)) * self.range
        ey = oy + math.sin(math.radians(self.angle)) * self.range
        pygame.draw.line(surface, BEAM, self.origin, (ex, ey), 2)


class Game:
    def __init__(self):
        self.aim_button = Button(AIM_RECT, "AIM", DARK_GRAY)
        self.shoot_button = Button(SHOOT_RECT, "SHOOT", RED)
        self.restart_button = Button(RESTART_RECT, "RESTART", DARK_GRAY)
        self.reset()

    def reset(self):
        self.angle_index = 2
        self.bullets = []
        self.planes = []
        self.searchlights = [
            SearchLight((65, HEIGHT - 20), "left"),
            SearchLight((WIDTH - 65, HEIGHT - 20), "right"),
        ]
        self.score = 0
        self.misses = 0
        self.start_ticks = pygame.time.get_ticks()
        self.last_spawn_time = pygame.time.get_ticks()
        self.next_spawn_delay = random.randint(int(PLANE_SPAWN_MIN * 1000), int(PLANE_SPAWN_MAX * 1000))
        self.game_over = False
        self.win = False

    def current_time_left(self):
        elapsed = (pygame.time.get_ticks() - self.start_ticks) / 1000
        return max(0, GAME_TIME - elapsed)

    def current_angle(self):
        return ANGLE_OPTIONS[self.angle_index]

    def cycle_aim(self):
        self.angle_index = (self.angle_index + 1) % len(ANGLE_OPTIONS)

    def shoot(self):
        angle = self.current_angle()
        ang = math.radians(angle)
        muzzle_x = CANNON_BASE[0] + math.cos(ang) * 60
        muzzle_y = CANNON_BASE[1] - math.sin(ang) * 60
        self.bullets.append(Bullet(muzzle_x, muzzle_y, angle))

    def spawn_plane(self):
        self.planes.append(Plane())

    def handle_click(self, pos):
        if self.game_over:
            if self.restart_button.clicked(pos):
                self.reset()
            else:
                self.reset()
            return
        if self.aim_button.clicked(pos):
            self.cycle_aim()
        elif self.shoot_button.clicked(pos):
            self.shoot()

    def update(self):
        if self.game_over:
            return

        now = pygame.time.get_ticks()
        if now - self.last_spawn_time >= self.next_spawn_delay:
            self.spawn_plane()
            self.last_spawn_time = now
            self.next_spawn_delay = random.randint(int(PLANE_SPAWN_MIN * 1000), int(PLANE_SPAWN_MAX * 1000))

        for light in self.searchlights:
            light.update(self.planes)

        for bullet in self.bullets:
            bullet.update()

        for plane in self.planes:
            plane.update()

        for bullet in self.bullets:
            if not bullet.alive:
                continue
            for plane in self.planes:
                if plane.alive and not plane.falling and bullet.rect().colliderect(plane.rect()):
                    plane.hit()
                    bullet.alive = False
                    self.score += 1
                    break

        for plane in self.planes:
            if plane.dead and not plane.falling and not plane.counted:
                self.misses += 1
                plane.counted = True
        self.bullets = [b for b in self.bullets if b.alive]
        self.planes = [p for p in self.planes if not p.dead]

        if self.current_time_left() <= 0:
            self.game_over = True
            self.win = True
        if self.misses >= MAX_MISSES:
            self.game_over = True
            self.win = False

    def draw_background(self, surface):
        surface.fill(SKY)
        for x, y, r in [(140, 90, 24), (330, 60, 18), (560, 95, 26), (800, 70, 20)]:
            pygame.draw.circle(surface, (55, 55, 65), (x, y), r)
            pygame.draw.circle(surface, (50, 50, 60), (x + 26, y + 7), r + 6)
            pygame.draw.circle(surface, (58, 58, 68), (x + 50, y), r - 2)
        pygame.draw.rect(surface, GROUND, (0, HEIGHT - 80, WIDTH, 80))
        pygame.draw.rect(surface, BLACK, (0, HEIGHT - 80, WIDTH, 10))

    def draw_cannon(self, surface):
        x, y = CANNON_BASE
        pygame.draw.rect(surface, (85, 85, 92), (x - 44, y + 18, 88, 22), border_radius=8)
        pygame.draw.circle(surface, (60, 60, 66), (x, y + 10), 24)
        pygame.draw.circle(surface, (120, 120, 130), (x, y + 10), 18)
        angle = self.current_angle()
        rad = math.radians(angle)
        barrel_len = 72
        end_x = x + math.cos(rad) * barrel_len
        end_y = y + 10 - math.sin(rad) * barrel_len
        pygame.draw.line(surface, BLACK, (x, y + 10), (end_x, end_y), 13)
        pygame.draw.line(surface, LIGHT, (x, y + 10), (end_x, end_y), 8)
        pygame.draw.polygon(surface, (70, 70, 76), [(x - 70, y + 36), (x - 50, y + 2), (x - 30, y + 36)])
        pygame.draw.polygon(surface, (70, 70, 76), [(x + 70, y + 36), (x + 50, y + 2), (x + 30, y + 36)])
        pygame.draw.line(surface, (55, 55, 60), (x - 100, y + 40), (x + 100, y + 40), 8)
        draw_text(surface, f"ANGLE: {ANGLE_LABELS[self.angle_index]}", FONT_SMALL, WHITE, 20, HEIGHT - 125)

    def draw_hud(self, surface):
        draw_text(surface, f"SCORE: {self.score}", FONT_MED, WHITE, 20, 16)
        draw_text(surface, f"MISSES: {self.misses}/{MAX_MISSES}", FONT_MED, WHITE, 20, 48)
        draw_text(surface, f"TIME: {int(self.current_time_left())}", FONT_MED, WHITE, WIDTH - 140, 16)
        self.aim_button.draw(surface)
        self.shoot_button.draw(surface)
        draw_text(surface, "Aim changes angle. Shoot fires one shell.", FONT_SMALL, WHITE, WIDTH // 2, HEIGHT - 22, center=True)

    def draw_planes(self, surface):
        for plane in self.planes:
            lit = any(light.contains(plane) for light in self.searchlights)
            plane.draw(surface, lit)

    def draw_game_over(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))
        msg = "MISSION COMPLETE" if self.win else "BASE LOST"
        sub = f"FINAL SCORE: {self.score}"
        hint = "Click restart or press R"
        draw_text(surface, msg, FONT_BIG, WHITE, WIDTH // 2, HEIGHT // 2 - 60, center=True)
        draw_text(surface, sub, FONT_MED, WHITE, WIDTH // 2, HEIGHT // 2 - 5, center=True)
        self.restart_button.draw(surface)
        draw_text(surface, hint, FONT_SMALL, WHITE, WIDTH // 2, HEIGHT // 2 + 104, center=True)

    def draw(self, surface):
        self.draw_background(surface)
        for light in self.searchlights:
            light.draw(surface)
        self.draw_planes(surface)
        for bullet in self.bullets:
            bullet.draw(surface)
        self.draw_cannon(surface)
        self.draw_hud(surface)
        if self.game_over:
            self.draw_game_over(surface)


def main():
    game = Game()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                game.handle_click(event.pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a and not game.game_over:
                    game.cycle_aim()
                elif event.key == pygame.K_SPACE and not game.game_over:
                    game.shoot()
                elif event.key == pygame.K_r and game.game_over:
                    game.reset()

        game.update()
        game.draw(SCREEN)
        pygame.display.flip()
        CLOCK.tick(FPS)


if __name__ == "__main__":
    main()