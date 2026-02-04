import arcade
import random

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
CELL_SIZE = 20
LIGHT_COLOR = (170, 215, 81)
DARK_COLOR = (162, 209, 73)


class SnakeGameView(arcade.View):
    def __init__(self, return_view_cls):
        super().__init__()
        self.return_view_cls = return_view_cls
        self.snake_body = [(10, 10), (9, 10), (8, 10)]
        self.snake_direction = (1, 0)
        self.apple_position = self.generate_apple()
        self.is_game_over = False
        self.score = 0
        self.move_timer = 0
        self.is_score_recorded = False

    def on_show_view(self):
        arcade.set_background_color(arcade.color.ALMOND)

    def generate_apple(self):
        grid_width = SCREEN_WIDTH // CELL_SIZE
        grid_height = SCREEN_HEIGHT // CELL_SIZE

        while True:
            apple_x = random.randint(0, grid_width - 1)
            apple_y = random.randint(0, grid_height - 1)
            if (apple_x, apple_y) not in self.snake_body:
                return (apple_x, apple_y)

    def on_draw(self):
        self.clear()

        grid_width = SCREEN_WIDTH // CELL_SIZE
        grid_height = SCREEN_HEIGHT // CELL_SIZE

        for row in range(grid_height):
            for column in range(grid_width):
                if (row + column) % 2 == 0:
                    cell_color = LIGHT_COLOR
                else:
                    cell_color = DARK_COLOR

                arcade.draw_lbwh_rectangle_filled(column * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE, cell_color)

        for segment_x, segment_y in self.snake_body:
            arcade.draw_lbwh_rectangle_filled(
                segment_x * CELL_SIZE, segment_y * CELL_SIZE, CELL_SIZE, CELL_SIZE, arcade.color.GREEN
            )

        apple_x, apple_y = self.apple_position
        arcade.draw_lbwh_rectangle_filled(
            apple_x * CELL_SIZE, apple_y * CELL_SIZE, CELL_SIZE, CELL_SIZE, arcade.color.RED
        )

        high_score = self.window.data_manager.get_stats("snake")
        arcade.draw_text(f"Счет: {self.score}", 10, SCREEN_HEIGHT - 30, arcade.color.BLACK, 18)
        arcade.draw_text(f"Лучший: {high_score}", 10, SCREEN_HEIGHT - 55, arcade.color.GRAY, 14)

        if self.is_game_over:
            arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 150))
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
        if self.is_game_over:
            if not self.is_score_recorded:
                self.window.data_manager.record_game("snake", self.score)
                self.is_score_recorded = True
            return

        self.move_timer += delta_time
        if self.move_timer < 0.1:
            return

        self.move_timer = 0

        head_x, head_y = self.snake_body[0]
        new_head_x = head_x + self.snake_direction[0]
        new_head_y = head_y + self.snake_direction[1]
        new_head = (new_head_x, new_head_y)

        grid_width = SCREEN_WIDTH // CELL_SIZE
        grid_height = SCREEN_HEIGHT // CELL_SIZE

        is_collision = (
            new_head in self.snake_body or not (0 <= new_head_x < grid_width) or not (0 <= new_head_y < grid_height)
        )

        if is_collision:
            self.is_game_over = True
            return

        self.snake_body = [new_head] + self.snake_body

        if new_head == self.apple_position:
            self.apple_position = self.generate_apple()
            self.score += 1
        else:
            self.snake_body.pop()

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.UP) and self.snake_direction != (0, -1):
            self.snake_direction = (0, 1)
        elif key in (arcade.key.S, arcade.key.DOWN) and self.snake_direction != (0, 1):
            self.snake_direction = (0, -1)
        elif key in (arcade.key.A, arcade.key.LEFT) and self.snake_direction != (1, 0):
            self.snake_direction = (-1, 0)
        elif key in (arcade.key.D, arcade.key.RIGHT) and self.snake_direction != (-1, 0):
            self.snake_direction = (1, 0)

        if key == arcade.key.ESCAPE:
            self.window.show_view(self.return_view_cls())
