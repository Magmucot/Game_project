import arcade
import random

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
CELL_SIZE = 20


class SnakeGameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)
        self.apple = self.spawn_apple()
        self.game_over = False
        self.score = 0
        self.speed_timer = 0

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

        for x, y in self.snake:
            arcade.draw_lbwh_rectangle_filled(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, arcade.color.GREEN)

        ax, ay = self.apple
        arcade.draw_lbwh_rectangle_filled(ax * CELL_SIZE, ay * CELL_SIZE, CELL_SIZE, CELL_SIZE, arcade.color.RED)

        arcade.draw_text(f"Score: {self.score}", 10, SCREEN_HEIGHT - 30, arcade.color.BLACK, 18)

        if self.game_over:
            arcade.draw_text("GAME OVER", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20, arcade.color.RED, 32,
                             anchor_x="center")
            arcade.draw_text(f"Final Score: {self.score}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 20, arcade.color.BLACK,
                             24,
                             anchor_x="center")

    def on_update(self, delta_time):
        if self.game_over:
            return

        self.speed_timer += delta_time
        if self.speed_timer < 0.1:
            return
        self.speed_timer = 0

        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        if (new_head in self.snake or
                not (0 <= new_head[0] < SCREEN_WIDTH // CELL_SIZE) or
                not (0 <= new_head[1] < SCREEN_HEIGHT // CELL_SIZE)):
            self.game_over = True
            return

        self.snake = [new_head] + self.snake

        if new_head == self.apple:
            self.apple = self.spawn_apple()
            self.score += 1
        else:
            self.snake.pop()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W and self.direction != (0, -1):
            self.direction = (0, 1)
        elif key == arcade.key.S and self.direction != (0, 1):
            self.direction = (0, -1)
        elif key == arcade.key.A and self.direction != (1, 0):
            self.direction = (-1, 0)
        elif key == arcade.key.D and self.direction != (-1, 0):
            self.direction = (1, 0)
