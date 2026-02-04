import arcade
import math
import random
from games import FighterGameView, TanksGameView, DicePokerView, MinesGameView, SnakeGameView, ChessGameView
from data_manager import GameDataManager

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Оффлайн игры — 6 в 1"


class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.action = action
        self.hovered = False
        self.hover_scale = 1.0

    def update(self, delta_time):
        target = 1.1 if self.hovered else 1.0
        self.hover_scale += (target - self.hover_scale) * delta_time * 10

    def draw(self):
        w, h = self.width * self.hover_scale, self.height * self.hover_scale
        arcade.draw_lbwh_rectangle_filled(self.x - w / 2 + 4, self.y - h / 2 - 4, w, h, (0, 0, 0, 100))
        color = arcade.color.SLATE_BLUE if self.hovered else arcade.color.DARK_SLATE_BLUE
        arcade.draw_lbwh_rectangle_filled(self.x - w / 2, self.y - h / 2, w, h, color)
        border = arcade.color.GOLD if self.hovered else arcade.color.WHITE
        arcade.draw_lbwh_rectangle_outline(self.x - w / 2, self.y - h / 2, w, h, border, 3)
        arcade.draw_text(
            self.text, self.x, self.y, arcade.color.WHITE, 18, anchor_x="center", anchor_y="center", bold=True
        )

    def check_hover(self, mouse_x, mouse_y):
        self.hovered = abs(mouse_x - self.x) < self.width / 2 and abs(mouse_y - self.y) < self.height / 2
        return self.hovered

    def check_click(self, mouse_x, mouse_y, button):
        if button == arcade.MOUSE_BUTTON_LEFT and self.check_hover(mouse_x, mouse_y):
            if self.action:
                self.action()
            return True
        return False


class BackgroundParticle:
    def __init__(self):
        self.reset(random.randint(0, SCREEN_HEIGHT))

    def reset(self, start_y=SCREEN_HEIGHT):
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = start_y
        self.speed = random.uniform(20, 60)
        self.size = random.uniform(1, 3)
        self.alpha = random.randint(50, 180)

    def update(self, delta_time):
        self.y -= self.speed * delta_time
        if self.y < 0:
            self.reset()

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.size, (255, 255, 255, self.alpha))


class StableBackground:
    def __init__(self, count=50):
        self.particles = [BackgroundParticle() for _ in range(count)]

    def update(self, delta_time):
        for p in self.particles:
            p.update(delta_time)

    def draw(self):
        for p in self.particles:
            p.draw()


class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = StableBackground()
        self.time = 0.0
        self.buttons = [
            Button(SCREEN_WIDTH // 2, 320, 280, 70, "К ИГРАМ", self.go_to_games),
            Button(SCREEN_WIDTH // 2, 220, 280, 70, "СТАТИСТИКА", self.go_to_settings),
        ]
        try:
            self.click_sound = arcade.load_sound("assets/click.wav")
        except Exception:
            self.click_sound = None

    def go_to_games(self):
        self.window.show_view(GamesMenuView())

    def go_to_settings(self):
        self.window.show_view(SettingsView())

    def on_update(self, delta_time):
        self.background.update(delta_time)
        self.time += delta_time
        for btn in self.buttons:
            btn.update(delta_time)

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        self.background.draw()
        title_y = 480 + math.sin(self.time * 2) * 8
        arcade.draw_text("ИГРОВОЙ ХАБ", SCREEN_WIDTH // 2, title_y, arcade.color.AQUA, 48, anchor_x="center", bold=True)
        for btn in self.buttons:
            btn.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for btn in self.buttons:
            btn.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            if btn.check_click(x, y, button) and self.click_sound:
                arcade.play_sound(self.click_sound)


class GamesMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = StableBackground()
        self.setup_buttons()

    def setup_buttons(self):
        self.buttons = []
        game_list = [
            ("Файтинг", lambda: FighterGameView(GamesMenuView)),
            ("Танчики", lambda: TanksGameView(GamesMenuView)),
            ("Кости", lambda: DicePokerView(GamesMenuView)),
            ("Минер", lambda: MinesGameView(GamesMenuView)),
            ("Змейка", lambda: SnakeGameView(GamesMenuView)),
            ("Шахматы", lambda: ChessGameView(GamesMenuView)),
        ]

        # Отрисовка сетки
        for i, (name, view_factory) in enumerate(game_list):
            column = i % 2
            row = i // 2
            x = SCREEN_WIDTH // 2 - 150 + (column * 300)
            y = 450 - (row * 100)
            self.buttons.append(Button(x, y, 240, 60, name, lambda v=view_factory: self.window.show_view(v())))

        self.buttons.append(
            Button(SCREEN_WIDTH // 2, 100, 200, 55, "НАЗАД", lambda: self.window.show_view(MainMenuView()))
        )

    def on_update(self, delta_time):
        self.background.update(delta_time)
        for btn in self.buttons:
            btn.update(delta_time)

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        self.background.draw()
        arcade.draw_text("ВЫБОР ИГРЫ", SCREEN_WIDTH // 2, 540, arcade.color.AQUA, 36, anchor_x="center", bold=True)
        for btn in self.buttons:
            btn.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for btn in self.buttons:
            btn.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            btn.check_click(x, y, button)


class SettingsView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = StableBackground()
        self.buttons = [Button(SCREEN_WIDTH // 2, 100, 200, 55, "НАЗАД", lambda: self.window.show_view(MainMenuView()))]

    def on_update(self, delta_time):
        self.background.update(delta_time)
        for btn in self.buttons:
            btn.update(delta_time)

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        self.background.draw()
        arcade.draw_text("СТАТИСТИКА", SCREEN_WIDTH // 2, 520, arcade.color.GOLD, 40, anchor_x="center", bold=True)

        stats = self.window.data_manager.data
        lines = [
            f"Кости (рекорд): {self.window.data_manager.get_high_score('dice')}",
            f"Змейка(рекорд): {self.window.data_manager.get_high_score('snake')}",
            f"Игр в шахматах: {self.window.data_manager.get_high_score('chess_cnt')}",
            f"Игр в файтинге: {self.window.data_manager.get_high_score('fighter_cnt')}",
            f"Первый победил в файтинге: {stats['player_stats']['first_won']}",
            f"Второй победил в файтинге: {stats['player_stats']['second_won']}",
            f"Всего запусков: {stats['total_games']}",
        ]
        for i, text in enumerate(lines):
            arcade.draw_text(text, SCREEN_WIDTH // 2, 460 - i * 50, arcade.color.WHITE, 20, anchor_x="center")
        for btn in self.buttons:
            btn.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for btn in self.buttons:
            btn.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            btn.check_click(x, y, button)


class GamePlaceholderView(arcade.View):
    def __init__(self, game_name):
        super().__init__()
        self.game_name = game_name
        self.buttons = [Button(SCREEN_WIDTH // 2, 150, 200, 55, "МЕНЮ", lambda: self.window.show_view(GamesMenuView()))]

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        arcade.draw_text(self.game_name, SCREEN_WIDTH // 2, 400, arcade.color.WHITE, 40, anchor_x="center")
        arcade.draw_text(
            "Эта игра находится в разработке", SCREEN_WIDTH // 2, 330, arcade.color.GRAY, 20, anchor_x="center"
        )
        for btn in self.buttons:
            btn.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for btn in self.buttons:
            btn.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            btn.check_click(x, y, button)


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.data_manager = GameDataManager()
    window.show_view(MainMenuView())
    arcade.run()


if __name__ == "__main__":
    main()
