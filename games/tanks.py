import arcade
import math
import random

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600

BULLET_SPEED = 400  # пикселей/сек
TANK_SPEED = 120  # пикселей/сек
ROTATION_SPEED = 120  # градусов/сек


class Tank(arcade.Sprite):
    """Танк - наследуется от arcade.Sprite"""

    def __init__(self, x, y, color_name, start_angle=0):
        super().__init__()

        self.center_x = x
        self.center_y = y
        self.tank_angle = start_angle  # Переименовано чтобы не конфликтовать
        self.color_name = color_name

        if color_name == "blue":
            self.color_main = arcade.color.BLUE
            self.color_dark = arcade.color.DARK_BLUE
            self.color_light = arcade.color.LIGHT_BLUE
        else:
            self.color_main = arcade.color.RED
            self.color_dark = arcade.color.DARK_RED
            self.color_light = arcade.color.LIGHT_CORAL

        # Создаём текстуру
        self.texture = arcade.make_soft_square_texture(40, self.color_main, 255, 255)

        self.hp = 5
        self.max_hp = 5
        self.reload_timer = 0.0
        self.reload_time = 0.4
        self.alive = True

    def update_tank(self, delta_time: float):
        if self.reload_timer > 0:
            self.reload_timer -= delta_time

    def move_forward(self, delta_time: float):
        if not self.alive:
            return
        rad = math.radians(self.tank_angle)
        self.center_x += math.cos(rad) * TANK_SPEED * delta_time
        self.center_y += math.sin(rad) * TANK_SPEED * delta_time
        self._clamp_position()

    def move_backward(self, delta_time: float):
        if not self.alive:
            return
        rad = math.radians(self.tank_angle)
        self.center_x -= math.cos(rad) * TANK_SPEED * delta_time
        self.center_y -= math.sin(rad) * TANK_SPEED * delta_time
        self._clamp_position()

    def rotate_left(self, delta_time: float):
        if self.alive:
            self.tank_angle += ROTATION_SPEED * delta_time

    def rotate_right(self, delta_time: float):
        if self.alive:
            self.tank_angle -= ROTATION_SPEED * delta_time

    def _clamp_position(self):
        self.center_x = max(40, min(SCREEN_WIDTH - 40, self.center_x))
        self.center_y = max(40, min(SCREEN_HEIGHT - 100, self.center_y))

    def shoot(self) -> "Bullet":
        if self.reload_timer <= 0 and self.alive:
            self.reload_timer = self.reload_time
            rad = math.radians(self.tank_angle)
            return Bullet(
                self.center_x + math.cos(rad) * 35,
                self.center_y + math.sin(rad) * 35,
                self.tank_angle,
                self.color_main,
                self.color_name,
            )
        return None

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.alive = False

    def draw(self):
        if not self.alive:
            # Обломки
            arcade.draw_circle_filled(self.center_x, self.center_y, 20, arcade.color.DARK_GRAY)
            arcade.draw_circle_filled(self.center_x + 5, self.center_y - 5, 8, arcade.color.GRAY)
            return

        rad = math.radians(self.tank_angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        # Гусеницы
        for side in [-1, 1]:
            track_offset = 18
            tx = self.center_x - side * track_offset * sin_a
            ty = self.center_y + side * track_offset * cos_a

            points = []
            for dx, dy in [(-18, -6), (18, -6), (18, 6), (-18, 6)]:
                px = tx + dx * cos_a - dy * sin_a
                py = ty + dx * sin_a + dy * cos_a
                points.append((px, py))
            arcade.draw_polygon_filled(points, arcade.color.DARK_GRAY)

        # Корпус
        body_points = []
        for dx, dy in [(-20, -12), (20, -12), (20, 12), (-20, 12)]:
            px = self.center_x + dx * cos_a - dy * sin_a
            py = self.center_y + dx * sin_a + dy * cos_a
            body_points.append((px, py))
        arcade.draw_polygon_filled(body_points, self.color_main)
        arcade.draw_polygon_outline(body_points, self.color_dark, 2)

        # Башня
        arcade.draw_circle_filled(self.center_x, self.center_y, 12, self.color_dark)

        # Дуло
        end_x = self.center_x + cos_a * 28
        end_y = self.center_y + sin_a * 28
        arcade.draw_line(self.center_x, self.center_y, end_x, end_y, self.color_dark, 6)
        arcade.draw_line(self.center_x, self.center_y, end_x, end_y, self.color_light, 3)

    def draw_hp_bar(self):
        if not self.alive:
            return

        bar_width = 50
        bar_height = 8
        hp_ratio = max(0, self.hp / self.max_hp)

        x = self.center_x - bar_width // 2
        y = self.center_y + 35

        arcade.draw_lbwh_rectangle_filled(x, y, bar_width, bar_height, arcade.color.DARK_RED)
        arcade.draw_lbwh_rectangle_filled(x, y, bar_width * hp_ratio, bar_height, arcade.color.LIME_GREEN)
        arcade.draw_lbwh_rectangle_outline(x, y, bar_width, bar_height, arcade.color.WHITE, 1)


class Bullet:
    """Снаряд - обычный класс без наследования"""

    def __init__(self, x, y, angle, color, owner):
        self.x = x
        self.y = y
        self.bullet_angle = angle
        self.bullet_color = color
        self.owner = owner
        self.active = True

        # Скорость в направлении
        rad = math.radians(angle)
        self.velocity_x = math.cos(rad) * BULLET_SPEED
        self.velocity_y = math.sin(rad) * BULLET_SPEED

    def update(self, delta_time: float):
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time

        if self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT:
            self.active = False

    def draw(self):
        if not self.active:
            return
        arcade.draw_circle_filled(self.x, self.y, 6, self.bullet_color)
        arcade.draw_circle_filled(self.x, self.y, 4, arcade.color.YELLOW)
        arcade.draw_circle_filled(self.x, self.y, 2, arcade.color.WHITE)

    def check_hit_tank(self, tank: Tank) -> bool:
        if not tank.alive:
            return False
        dist = math.sqrt((self.x - tank.center_x) ** 2 + (self.y - tank.center_y) ** 2)
        return dist < 25

    def check_hit_wall(self, wall: "Wall") -> bool:
        if wall.hp <= 0:
            return False
        return abs(self.x - wall.x) < wall.wall_size // 2 + 5 and abs(self.y - wall.y) < wall.wall_size // 2 + 5


class Wall:
    """Стена - обычный класс без наследования"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 3
        self.wall_size = 40  # Переименовано!

    def draw(self):
        if self.hp <= 0:
            return

        arcade.draw_lbwh_rectangle_filled(
            self.x - self.wall_size // 2,
            self.y - self.wall_size // 2,
            self.wall_size,
            self.wall_size,
            arcade.color.SADDLE_BROWN,
        )

        # Кирпичный узор
        for row in range(4):
            for col in range(2):
                bx = self.x - self.wall_size // 2 + col * 20 + (row % 2) * 10
                by = self.y - self.wall_size // 2 + row * 10
                if bx < self.x + self.wall_size // 2 - 5:
                    arcade.draw_lbwh_rectangle_outline(bx, by, 18, 9, arcade.color.BROWN, 1)

        arcade.draw_lbwh_rectangle_outline(
            self.x - self.wall_size // 2,
            self.y - self.wall_size // 2,
            self.wall_size,
            self.wall_size,
            arcade.color.DARK_BROWN,
            2,
        )

        # Трещины
        if self.hp < 3:
            arcade.draw_line(self.x - 12, self.y - 12, self.x + 8, self.y + 8, arcade.color.BLACK, 2)
        if self.hp < 2:
            arcade.draw_line(self.x + 10, self.y - 8, self.x - 5, self.y + 12, arcade.color.BLACK, 2)

    def hit(self):
        self.hp -= 1


class Explosion:
    """Анимация взрыва"""

    def __init__(self, x, y, big=False):
        self.x = x
        self.y = y
        self.time = 0.0
        self.max_time = 0.5 if big else 0.3
        self.big = big

    def update(self, delta_time: float):
        self.time += delta_time

    def draw(self):
        if self.time >= self.max_time:
            return

        progress = self.time / self.max_time
        alpha = int(255 * (1 - progress))
        size_mult = 2 if self.big else 1

        radius = progress * 40 * size_mult
        arcade.draw_circle_filled(self.x, self.y, radius, (255, 100, 0, alpha // 2))
        arcade.draw_circle_filled(self.x, self.y, radius * 0.7, (255, 200, 0, alpha))
        arcade.draw_circle_filled(self.x, self.y, radius * 0.4, (255, 255, 200, alpha))

        # Искры
        if progress < 0.5:
            for i in range(8):
                angle = i * 45 + progress * 200
                dist = progress * 50 * size_mult
                sx = self.x + math.cos(math.radians(angle)) * dist
                sy = self.y + math.sin(math.radians(angle)) * dist
                arcade.draw_circle_filled(sx, sy, 3, (255, 255, 0, alpha))

    @property
    def finished(self):
        return self.time >= self.max_time


class TanksGameView(arcade.View):
    def __init__(self, return_view_class):
        super().__init__()
        self.return_view_class = return_view_class

        self.tank1: Tank = None
        self.tank2: Tank = None
        self.bullets: list = None
        self.walls: list = None
        self.explosions: list = None

        self.game_over = False
        self.winner = None
        self.keys_pressed = set()

        self.setup()

    def setup(self):
        self.tank1 = Tank(100, 300, "blue", 0)
        self.tank2 = Tank(800, 300, "red", 180)

        self.bullets = []
        self.walls = []
        self.explosions = []

        self.game_over = False
        self.winner = None

        # Стены
        wall_positions = [
            (450, 150),
            (450, 200),
            (450, 400),
            (450, 450),
            (200, 150),
            (250, 150),
            (650, 450),
            (700, 450),
            (300, 300),
            (600, 300),
        ]
        for wx, wy in wall_positions:
            self.walls.append(Wall(wx, wy))

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_TAN)

    def on_draw(self):
        self.clear()

        # Пол
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - 60, arcade.color.DARK_TAN)

        # Стены
        for wall in self.walls:
            wall.draw()

        # Взрывы
        for exp in self.explosions:
            exp.draw()

        # Танки
        self.tank1.draw()
        self.tank2.draw()
        self.tank1.draw_hp_bar()
        self.tank2.draw_hp_bar()

        # Пули
        for bullet in self.bullets:
            bullet.draw()

        # UI
        arcade.draw_lbwh_rectangle_filled(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60, (30, 30, 30, 230))

        self.draw_top_bar(180, SCREEN_HEIGHT - 30, self.tank1.hp, self.tank1.max_hp, arcade.color.BLUE, "ИГРОК 1")
        self.draw_top_bar(
            SCREEN_WIDTH - 180, SCREEN_HEIGHT - 30, self.tank2.hp, self.tank2.max_hp, arcade.color.RED, "ИГРОК 2"
        )

        arcade.draw_text("WASD + SPACE", 180, SCREEN_HEIGHT - 55, arcade.color.CYAN, 10, anchor_x="center")
        arcade.draw_text(
            "Стрелки + ENTER", SCREEN_WIDTH - 180, SCREEN_HEIGHT - 55, arcade.color.ORANGE, 10, anchor_x="center"
        )
        arcade.draw_text("ESC - выход", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 35, arcade.color.WHITE, 12, anchor_x="center")

        if self.game_over:
            arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 180))
            arcade.draw_lbwh_rectangle_filled(
                SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 80, 440, 160, arcade.color.DARK_SLATE_GRAY
            )
            arcade.draw_lbwh_rectangle_outline(
                SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 80, 440, 160, arcade.color.GOLD, 5
            )

            winner_color = arcade.color.CYAN if self.winner == "ИГРОК 1" else arcade.color.ORANGE
            arcade.draw_text(
                f"{self.winner} ПОБЕДИЛ!",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 30,
                winner_color,
                36,
                anchor_x="center",
                anchor_y="center",
                bold=True,
            )
            arcade.draw_text(
                "R - реванш | ESC - выход",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 40,
                arcade.color.WHITE,
                20,
                anchor_x="center",
                anchor_y="center",
            )

    def draw_top_bar(self, x, y, hp, max_hp, color, label):
        bar_width = 180
        bar_height = 22
        hp_ratio = max(0, hp / max_hp)

        arcade.draw_lbwh_rectangle_filled(
            x - bar_width // 2, y - bar_height // 2, bar_width, bar_height, arcade.color.DARK_RED
        )
        arcade.draw_lbwh_rectangle_filled(
            x - bar_width // 2, y - bar_height // 2, bar_width * hp_ratio, bar_height, color
        )
        arcade.draw_lbwh_rectangle_outline(
            x - bar_width // 2, y - bar_height // 2, bar_width, bar_height, arcade.color.WHITE, 2
        )
        arcade.draw_text(
            f"{label}: {hp}/{max_hp}", x, y, arcade.color.WHITE, 12, anchor_x="center", anchor_y="center", bold=True
        )

    def on_update(self, delta_time):
        # Ограничиваем delta_time
        delta_time = min(delta_time, 0.05)

        if self.game_over:
            for exp in self.explosions:
                exp.update(delta_time)
            self.explosions = [e for e in self.explosions if not e.finished]
            return

        # Управление танком 1
        if arcade.key.W in self.keys_pressed:
            self.tank1.move_forward(delta_time)
        if arcade.key.S in self.keys_pressed:
            self.tank1.move_backward(delta_time)
        if arcade.key.A in self.keys_pressed:
            self.tank1.rotate_left(delta_time)
        if arcade.key.D in self.keys_pressed:
            self.tank1.rotate_right(delta_time)

        # Управление танком 2
        if arcade.key.UP in self.keys_pressed:
            self.tank2.move_forward(delta_time)
        if arcade.key.DOWN in self.keys_pressed:
            self.tank2.move_backward(delta_time)
        if arcade.key.LEFT in self.keys_pressed:
            self.tank2.rotate_left(delta_time)
        if arcade.key.RIGHT in self.keys_pressed:
            self.tank2.rotate_right(delta_time)

        self.tank1.update_tank(delta_time)
        self.tank2.update_tank(delta_time)

        # Пули
        bullets_to_remove = []
        for bullet in self.bullets:
            bullet.update(delta_time)

            if not bullet.active:
                bullets_to_remove.append(bullet)
                continue

            # Стены
            for wall in self.walls:
                if bullet.check_hit_wall(wall):
                    wall.hit()
                    bullets_to_remove.append(bullet)
                    self.explosions.append(Explosion(bullet.x, bullet.y))
                    break

            # Танки
            if bullet not in bullets_to_remove:
                if bullet.owner != "blue" and bullet.check_hit_tank(self.tank1):
                    self.tank1.hit()
                    bullets_to_remove.append(bullet)
                    self.explosions.append(Explosion(bullet.x, bullet.y, big=True))
                elif bullet.owner != "red" and bullet.check_hit_tank(self.tank2):
                    self.tank2.hit()
                    bullets_to_remove.append(bullet)
                    self.explosions.append(Explosion(bullet.x, bullet.y, big=True))

        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)

        # Взрывы
        for exp in self.explosions:
            exp.update(delta_time)
        self.explosions = [e for e in self.explosions if not e.finished]

        # Победа
        if not self.tank1.alive:
            self.game_over = True
            self.winner = "ИГРОК 2"
            self.explosions.append(Explosion(self.tank1.center_x, self.tank1.center_y, big=True))
        elif not self.tank2.alive:
            self.game_over = True
            self.winner = "ИГРОК 1"
            self.explosions.append(Explosion(self.tank2.center_x, self.tank2.center_y, big=True))

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

        if key == arcade.key.SPACE:
            bullet = self.tank1.shoot()
            if bullet:
                self.bullets.append(bullet)

        if key == arcade.key.ENTER:
            bullet = self.tank2.shoot()
            if bullet:
                self.bullets.append(bullet)

        if key == arcade.key.ESCAPE:
            self.window.show_view(self.return_view_class())

        if key == arcade.key.R and self.game_over:
            self.setup()

    def on_key_release(self, key, modifiers):
        self.keys_pressed.discard(key)
