import arcade
import enum
import random

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600

GROUND_Y = 120
# Параметры для физического движка (в пикселях/кадр)
GRAVITY = 0.8
JUMP_SPEED = 14
MOVE_SPEED = 5
ATTACK_RANGE = 90
ATTACK_DAMAGE = 10
ATTACK_COOLDOWN = 0.4


class FaceDirection(enum.Enum):
    LEFT = 0
    RIGHT = 1


class Fighter(arcade.Sprite):
    """Боец - наследуется от arcade.Sprite"""

    def __init__(self, x, y, player_num):
        super().__init__()

        self.player_num = player_num
        self.center_x = x
        self.center_y = y

        # Цвета для игроков
        if player_num == 1:
            self.color_main = arcade.color.BLUE
            self.color_dark = arcade.color.DARK_BLUE
            self.color_light = arcade.color.LIGHT_BLUE
        else:
            self.color_main = arcade.color.RED
            self.color_dark = arcade.color.DARK_RED
            self.color_light = arcade.color.LIGHT_CORAL

        # Создаём текстуру
        self._create_texture()

        # Характеристики
        self.hp = 100
        self.max_hp = 100
        self.face_direction = FaceDirection.RIGHT if player_num == 1 else FaceDirection.LEFT

        # Состояния
        self.is_walking = False
        self.is_attacking = False
        self.attack_timer = 0.0
        self.attack_cooldown_timer = 0.0
        self.hit_stun_timer = 0.0

        # Анимация ходьбы
        self.walk_animation_timer = 0.0
        self.walk_frame = 0

        # Флаг нахождения на земле
        self.on_ground = False

    def _create_texture(self):
        """Создаём текстуру для хитбокса спрайта"""
        self.texture = arcade.make_soft_square_texture(80, self.color_main, 255, 255)

    def update_fighter(self, delta_time: float):
        """Обновление состояния бойца (таймеры и анимации, БЕЗ физики)"""
        # Обновляем таймеры
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= delta_time
        if self.hit_stun_timer > 0:
            self.hit_stun_timer -= delta_time

        # Атака
        if self.is_attacking:
            self.attack_timer += delta_time
            if self.attack_timer >= 0.25:
                self.is_attacking = False
                self.attack_timer = 0

        # Границы экрана
        if self.center_x < 50:
            self.center_x = 50
            self.change_x = 0
        elif self.center_x > SCREEN_WIDTH - 50:
            self.center_x = SCREEN_WIDTH - 50
            self.change_x = 0

        # Анимация ходьбы
        if self.is_walking and self.on_ground:
            self.walk_animation_timer += delta_time
            if self.walk_animation_timer >= 0.15:
                self.walk_animation_timer = 0
                self.walk_frame = (self.walk_frame + 1) % 4
        else:
            self.walk_frame = 0

    def move(self, direction: int):
        """Движение: -1 влево, 1 вправо, 0 стоп"""
        self.change_x = direction * MOVE_SPEED
        self.is_walking = direction != 0
        if direction < 0:
            self.face_direction = FaceDirection.LEFT
        elif direction > 0:
            self.face_direction = FaceDirection.RIGHT

    def jump(self):
        """Прыжок"""
        if self.on_ground:
            # Используем change_y для физического движка
            self.change_y = JUMP_SPEED

    def attack(self):
        """Атака"""
        if self.attack_cooldown_timer <= 0 and not self.is_attacking:
            self.is_attacking = True
            self.attack_timer = 0
            self.attack_cooldown_timer = ATTACK_COOLDOWN
            return True
        return False

    def can_hit(self, other: "Fighter") -> bool:
        """Проверка, может ли ударить другого бойца"""
        if self.is_attacking and 0.08 < self.attack_timer < 0.15:
            dist = abs(self.center_x - other.center_x)
            if dist < ATTACK_RANGE:
                if self.face_direction == FaceDirection.RIGHT and other.center_x > self.center_x:
                    return True
                elif self.face_direction == FaceDirection.LEFT and other.center_x < self.center_x:
                    return True
        return False

    def take_damage(self, damage: int) -> bool:
        """Получение урона"""
        if self.hit_stun_timer <= 0:
            self.hp -= damage
            self.hit_stun_timer = 0.3
            return True
        return False

    def draw_fighter(self):
        """Кастомная отрисовка бойца (не вызывает draw() спрайта)"""
        body_offset = 5 if not self.on_ground else 0

        # Тень
        arcade.draw_ellipse_filled(self.center_x, GROUND_Y - 5, 40, 15, (0, 0, 0, 80))

        # Смещение ног для анимации ходьбы
        leg_offset = 0
        if self.is_walking and self.on_ground:
            leg_offset = [0, 5, 0, -5][self.walk_frame]

        # Ноги
        arcade.draw_lbwh_rectangle_filled(
            self.center_x - 18, self.center_y - 40 + body_offset - leg_offset, 12, 30, self.color_dark
        )
        arcade.draw_lbwh_rectangle_filled(
            self.center_x + 6, self.center_y - 40 + body_offset + leg_offset, 12, 30, self.color_dark
        )

        # Туловище
        arcade.draw_lbwh_rectangle_filled(self.center_x - 18, self.center_y - 10 + body_offset, 36, 45, self.color_main)

        # Пояс
        arcade.draw_lbwh_rectangle_filled(self.center_x - 18, self.center_y - 10 + body_offset, 36, 8, self.color_dark)

        # Руки
        facing_right = self.face_direction == FaceDirection.RIGHT
        arm_dir = 1 if facing_right else -1

        if self.is_attacking and self.attack_timer < 0.15:
            # Атакующая рука
            arcade.draw_lbwh_rectangle_filled(
                self.center_x + arm_dir * 15, self.center_y + 10 + body_offset, arm_dir * 45, 12, self.color_light
            )
            arcade.draw_circle_filled(
                self.center_x + arm_dir * 60, self.center_y + 16 + body_offset, 10, self.color_light
            )
        else:
            # Обычные руки
            arcade.draw_lbwh_rectangle_filled(
                self.center_x - 28, self.center_y + 5 + body_offset, 10, 25, self.color_light
            )
            arcade.draw_lbwh_rectangle_filled(
                self.center_x + 18, self.center_y + 5 + body_offset, 10, 25, self.color_light
            )

        # Голова
        arcade.draw_circle_filled(self.center_x, self.center_y + 45 + body_offset, 18, self.color_light)

        # Глаза
        eye_offset = 6 if facing_right else -6
        arcade.draw_circle_filled(
            self.center_x + eye_offset - 4, self.center_y + 48 + body_offset, 4, arcade.color.WHITE
        )
        arcade.draw_circle_filled(
            self.center_x + eye_offset + 4, self.center_y + 48 + body_offset, 4, arcade.color.WHITE
        )

        pupil_offset = 2 if facing_right else -2
        arcade.draw_circle_filled(
            self.center_x + eye_offset - 4 + pupil_offset, self.center_y + 48 + body_offset, 2, arcade.color.BLACK
        )
        arcade.draw_circle_filled(
            self.center_x + eye_offset + 4 + pupil_offset, self.center_y + 48 + body_offset, 2, arcade.color.BLACK
        )

        # Индикатор игрока
        label = "P1" if self.player_num == 1 else "P2"
        arcade.draw_text(label, self.center_x, self.center_y + 75, arcade.color.WHITE, 12, anchor_x="center", bold=True)

    def draw_hp_bar(self):
        """HP бар над персонажем"""
        bar_width = 70
        bar_height = 10
        hp_ratio = max(0, self.hp / self.max_hp)

        x = self.center_x - bar_width // 2
        y = self.center_y + 85

        arcade.draw_lbwh_rectangle_filled(x, y, bar_width, bar_height, arcade.color.DARK_RED)
        arcade.draw_lbwh_rectangle_filled(x, y, bar_width * hp_ratio, bar_height, arcade.color.LIME_GREEN)
        arcade.draw_lbwh_rectangle_outline(x, y, bar_width, bar_height, arcade.color.WHITE, 2)


class HitParticle:
    """Частица при ударе"""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.velocity_x = random.uniform(-150, 150)
        self.velocity_y = random.uniform(100, 300)
        self.lifetime = random.uniform(0.3, 0.6)
        self.max_lifetime = self.lifetime
        self.particle_color = color
        self.particle_size = random.uniform(4, 10)
        self.active = True

    def update(self, delta_time: float):
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        self.velocity_y -= 400 * delta_time
        self.lifetime -= delta_time
        if self.lifetime <= 0:
            self.active = False

    def draw(self):
        if not self.active:
            return
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color = (*self.particle_color[:3], alpha)
        arcade.draw_circle_filled(self.x, self.y, self.particle_size, color)


class FighterGameView(arcade.View):
    def __init__(self, return_view_cls):
        super().__init__()
        self.return_view_cls = return_view_cls

        self.player1: Fighter = None
        self.player2: Fighter = None
        self.particles: list = None

        # Списки спрайтов для физического движка
        self.walls_list: arcade.SpriteList = None

        # Физические движки
        self.physics_engine_1 = None
        self.physics_engine_2 = None

        self.game_over = False
        self.winner = None
        self.keys_pressed = set()

        try:
            self.hit_sound = arcade.load_sound(":resources:sounds/hit1.wav")
        except Exception:
            self.hit_sound = None

        self.setup()

    def setup(self):
        """Инициализация/перезапуск игры"""
        # Создаём список платформ
        self.walls_list = arcade.SpriteList(use_spatial_hash=True)

        # Создаём землю
        ground = arcade.SpriteSolidColor(SCREEN_WIDTH * 2, 40, arcade.color.DARK_BROWN)
        ground.center_x = SCREEN_WIDTH // 2
        ground.center_y = GROUND_Y - 20
        self.walls_list.append(ground)

        # Создаём бойцов
        self.player1 = Fighter(200, GROUND_Y + 80, 1)
        self.player2 = Fighter(700, GROUND_Y + 80, 2)

        # Создаём физические движки
        self.physics_engine_1 = arcade.PhysicsEnginePlatformer(
            self.player1, gravity_constant=GRAVITY, walls=self.walls_list
        )

        self.physics_engine_2 = arcade.PhysicsEnginePlatformer(
            self.player2, gravity_constant=GRAVITY, walls=self.walls_list
        )

        self.particles = []
        self.game_over = False
        self.winner = None
        self.keys_pressed.clear()

    def spawn_particles(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(HitParticle(x, y, color))

    def on_show_view(self):
        arcade.set_background_color(arcade.color.SKY_BLUE)

    def draw_background(self):
        # Небо
        arcade.draw_lbwh_rectangle_filled(0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2, arcade.color.SKY_BLUE)
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 2, arcade.color.LIGHT_SKY_BLUE)

        # Солнце
        arcade.draw_circle_filled(100, SCREEN_HEIGHT - 80, 45, arcade.color.YELLOW)

        # Облака
        for cx, cy in [(200, 520), (450, 480), (700, 530)]:
            arcade.draw_ellipse_filled(cx, cy, 100, 50, arcade.color.WHITE)
            arcade.draw_ellipse_filled(cx + 40, cy + 15, 80, 45, arcade.color.WHITE)
            arcade.draw_ellipse_filled(cx - 35, cy + 10, 70, 40, arcade.color.WHITE)

        # Горы
        points = [
            (0, GROUND_Y + 80),
            (150, GROUND_Y + 180),
            (300, GROUND_Y + 100),
            (450, GROUND_Y + 160),
            (600, GROUND_Y + 90),
            (750, GROUND_Y + 140),
            (900, GROUND_Y + 110),
            (900, GROUND_Y),
            (0, GROUND_Y),
        ]
        arcade.draw_polygon_filled(points, arcade.color.DIM_GRAY)

        # Земля
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, GROUND_Y, arcade.color.DARK_BROWN)
        arcade.draw_lbwh_rectangle_filled(0, GROUND_Y - 15, SCREEN_WIDTH, 20, arcade.color.DARK_GREEN)

    def on_draw(self):
        self.clear()
        self.draw_background()

        # Частицы
        for particle in self.particles:
            particle.draw()

        # Игроки
        self.player1.draw_fighter()
        self.player2.draw_fighter()
        self.player1.draw_hp_bar()
        self.player2.draw_hp_bar()

        # UI
        arcade.draw_lbwh_rectangle_filled(0, SCREEN_HEIGHT - 70, SCREEN_WIDTH, 70, (0, 0, 0, 200))

        self.draw_top_hp_bar(180, SCREEN_HEIGHT - 35, self.player1.hp, self.player1.max_hp, arcade.color.BLUE, "ИГРОК 1")
        self.draw_top_hp_bar(
            SCREEN_WIDTH - 180, SCREEN_HEIGHT - 35, self.player2.hp, self.player2.max_hp, arcade.color.RED, "ИГРОК 2"
        )

        arcade.draw_text(
            "VS",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 35,
            arcade.color.GOLD,
            24,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
        arcade.draw_text("WASD + Space", 180, SCREEN_HEIGHT - 60, arcade.color.CYAN, 11, anchor_x="center")
        arcade.draw_text(
            "Стрелки + Enter", SCREEN_WIDTH - 180, SCREEN_HEIGHT - 60, arcade.color.ORANGE, 11, anchor_x="center"
        )

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
                34,
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

    def draw_top_hp_bar(self, x, y, hp, max_hp, color, label):
        bar_width = 200
        bar_height = 28
        hp_ratio = max(0, hp / max_hp)

        arcade.draw_lbwh_rectangle_filled(
            x - bar_width // 2, y - bar_height // 2, bar_width, bar_height, arcade.color.DARK_RED
        )
        arcade.draw_lbwh_rectangle_filled(
            x - bar_width // 2, y - bar_height // 2, bar_width * hp_ratio, bar_height, color
        )
        arcade.draw_lbwh_rectangle_outline(
            x - bar_width // 2, y - bar_height // 2, bar_width, bar_height, arcade.color.WHITE, 3
        )
        arcade.draw_text(f"{label}: {hp}", x, y, arcade.color.WHITE, 14, anchor_x="center", anchor_y="center", bold=True)

    def on_update(self, delta_time):
        delta_time = min(delta_time, 0.05)

        if self.game_over:
            return

        # Управление P1
        direct1 = 0
        if arcade.key.A in self.keys_pressed:
            direct1 -= 1
        if arcade.key.D in self.keys_pressed:
            direct1 += 1
        self.player1.move(direct1)

        # Управление P2
        direct2 = 0
        if arcade.key.LEFT in self.keys_pressed:
            direct2 -= 1
        if arcade.key.RIGHT in self.keys_pressed:
            direct2 += 1
        self.player2.move(direct2)

        # === ОБНОВЛЕНИЕ ФИЗИЧЕСКИХ ДВИЖКОВ ===
        self.physics_engine_1.update()
        self.physics_engine_2.update()

        # Проверка нахождения на земле через физ. движок
        self.player1.on_ground = self.physics_engine_1.can_jump()
        self.player2.on_ground = self.physics_engine_2.can_jump()

        # Обновление таймеров и анимаций
        self.player1.update_fighter(delta_time)
        self.player2.update_fighter(delta_time)

        # Частицы
        for particle in self.particles:
            particle.update(delta_time)
        self.particles = [p for p in self.particles if p.active]

        # Проверка ударов
        if self.player1.can_hit(self.player2) and self.player2.take_damage(ATTACK_DAMAGE):
            if self.hit_sound:
                arcade.play_sound(self.hit_sound)
            self.spawn_particles(self.player2.center_x, self.player2.center_y + 20, arcade.color.RED)

        if self.player2.can_hit(self.player1) and self.player1.take_damage(ATTACK_DAMAGE):
            if self.hit_sound:
                arcade.play_sound(self.hit_sound)
            self.spawn_particles(self.player1.center_x, self.player1.center_y + 20, arcade.color.BLUE)

        # Победа
        if self.player1.hp <= 0:
            self.game_over = True
            self.window.data_manager.record_game("fighter", 0, won=False)
            self.winner = "ИГРОК 2"
        elif self.player2.hp <= 0:
            self.game_over = True
            self.window.data_manager.record_game("fighter", 0, won=True)
            self.winner = "ИГРОК 1"

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

        if key == arcade.key.W:
            self.player1.jump()
        elif key == arcade.key.UP:
            self.player2.jump()
        elif key == arcade.key.SPACE:
            self.player1.attack()
        elif key == arcade.key.ENTER:
            self.player2.attack()
        elif key == arcade.key.ESCAPE:
            self.window.show_view(self.return_view_cls())
        elif key == arcade.key.R and self.game_over:
            self.setup()

    def on_key_release(self, key, modifiers):
        self.keys_pressed.discard(key)
