import arcade
import random

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
CELL_SIZE = 20
COLOR_LIGHT = (170, 215, 81)
COLOR_DARK = (162, 209, 73)


class SnakeGameView(arcade.View):
    def __init__(self, return_view_cls):
        super().__init__()
        self.return_view_cls = return_view_cls
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)
        self.apple = self.spawn_apple()
        self.game_over = False
        self.score = 0
        self.speed_timer = 0
        self.stats_recorded = False

    def on_show_view(self):
        arcade.set_background_color(arcade.color.ALMOND)

    def spawn_apple(self):
        while True:
            x = random.randint(0, SCREEN_WIDTH // CELL_SIZE - 1)
            y = random.randint(0, SCREEN_HEIGHT // CELL_SIZE - 1)
            if (x, y) not in self.snake:
                return (x, y)

    def on_draw(self):
        self.clear()

        # --- ШАХМАТНОЕ ПОЛЕ ---
        for row in range(SCREEN_HEIGHT // CELL_SIZE):
            for col in range(SCREEN_WIDTH // CELL_SIZE):
                if (row + col) % 2 == 0:
                    color = COLOR_LIGHT
                else:
                    color = COLOR_DARK

                arcade.draw_lbwh_rectangle_filled(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE, color)
        # -----------------------------

        # Отрисовка змейки
        for x, y in self.snake:
            arcade.draw_lbwh_rectangle_filled(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, arcade.color.GREEN)

        # Отрисовка яблока
        ax, ay = self.apple
        arcade.draw_lbwh_rectangle_filled(ax * CELL_SIZE, ay * CELL_SIZE, CELL_SIZE, CELL_SIZE, arcade.color.RED)

        high_score = self.window.data_manager.get_high_score("snake")
        arcade.draw_text(f"Счет: {self.score}", 10, SCREEN_HEIGHT - 30, arcade.color.BLACK, 18)
        arcade.draw_text(f"Лучший: {high_score}", 10, SCREEN_HEIGHT - 55, arcade.color.GRAY, 14)

        if self.game_over:
            arcade.draw_lbwh_rectangle_filled(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, (0, 0, 0, 150))
            arcade.draw_text(
                "ВЫ ПРОИГРАЛИ!", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20, arcade.color.WHITE, 32, anchor_x="center"
            )
            arcade.draw_text(
                f"Финальный результат: {self.score}",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 20,
                arcade.color.WHITE,
                24,
                anchor_x="center",
            )

    def on_update(self, delta_time):
        if self.game_over:
            # 3. Обращаемся к менеджеру в окне при окончании игры
            if not self.stats_recorded:
                self.window.data_manager.record_game("snake", self.score)
                self.stats_recorded = True
            return

        self.speed_timer += delta_time
        if self.speed_timer < 0.1:
            return
        self.speed_timer = 0

        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        if (
            new_head in self.snake
            or not (0 <= new_head[0] < SCREEN_WIDTH // CELL_SIZE)
            or not (0 <= new_head[1] < SCREEN_HEIGHT // CELL_SIZE)
        ):
            self.game_over = True
            return

        self.snake = [new_head] + self.snake

        if new_head == self.apple:
            self.apple = self.spawn_apple()
            self.score += 1
        else:
            self.snake.pop()

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.UP) and self.direction != (0, -1):
            self.direction = (0, 1)
        elif key in (arcade.key.S, arcade.key.DOWN) and self.direction != (0, 1):
            self.direction = (0, -1)
        elif key in (arcade.key.A, arcade.key.LEFT) and self.direction != (1, 0):
            self.direction = (-1, 0)
        elif key in (arcade.key.D, arcade.key.RIGHT) and self.direction != (-1, 0):
            self.direction = (1, 0)
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.return_view_cls())
