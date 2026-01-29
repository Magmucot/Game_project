import arcade
import math
import random
from games import FighterGameView, TanksGameView, DicePokerView

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Оффлайн игры"


class Button:
    """Кнопка"""

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
        # Анимация масштаба
        target = 1.1 if self.hovered else 1.0
        self.hover_scale += (target - self.hover_scale) * delta_time * 10

    def draw(self):
        w = self.width * self.hover_scale
        h = self.height * self.hover_scale

        # Тень
        arcade.draw_lbwh_rectangle_filled(self.x - w / 2 + 4, self.y - h / 2 - 4, w, h, (0, 0, 0, 100))

        # Кнопка
        color = arcade.color.SLATE_BLUE if self.hovered else arcade.color.DARK_SLATE_BLUE
        arcade.draw_lbwh_rectangle_filled(self.x - w / 2, self.y - h / 2, w, h, color)

        # Рамка
        border_color = arcade.color.GOLD if self.hovered else arcade.color.WHITE
        arcade.draw_lbwh_rectangle_outline(self.x - w / 2, self.y - h / 2, w, h, border_color, 3)

        # Текст
        arcade.draw_text(
            self.text, self.x, self.y, arcade.color.WHITE, font_size=20, anchor_x="center", anchor_y="center", bold=True
        )

    def check_hover(self, mouse_x, mouse_y):
        self.hovered = (
            self.x - self.width / 2 < mouse_x < self.x + self.width / 2
            and self.y - self.height / 2 < mouse_y < self.y + self.height / 2
        )
        return self.hovered

    def check_click(self, mouse_x, mouse_y, button):
        if button == arcade.MOUSE_BUTTON_LEFT and self.check_hover(mouse_x, mouse_y):
            if self.action:
                self.action()
            return True
        return False


class BackgroundParticle:
    """Частица фона"""

    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(0, SCREEN_HEIGHT)
        self.speed = random.uniform(30, 80)
        self.size = random.uniform(2, 5)
        self.alpha = random.randint(50, 150)

    def update(self, delta_time):
        self.y -= self.speed * delta_time
        if self.y < 0:
            self.y = SCREEN_HEIGHT
            self.x = random.uniform(0, SCREEN_WIDTH)

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.size, (255, 255, 255, self.alpha))


class AnimatedBackground:
    """Анимированный фон"""

    def __init__(self, count=30):
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
        self.buttons = []
        self.background = AnimatedBackground()
        self.title_offset = 0.0
        self.time = 0.0
        self.setup_buttons()
        self.click_sound = arcade.load_sound("assets/click.wav")

    def setup_buttons(self):
        center_x = SCREEN_WIDTH // 2
        self.buttons = [
            Button(center_x, 320, 280, 70, "ИГРЫ", self.go_to_games),
            Button(center_x, 220, 280, 70, "НАСТРОЙКИ", self.go_to_settings),
        ]

    def go_to_games(self):
        self.window.show_view(GamesMenuView())

    def go_to_settings(self):
        self.window.show_view(SettingsView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_update(self, delta_time):
        self.background.update(delta_time)
        self.time += delta_time
        self.title_offset = math.sin(self.time * 2) * 5
        for btn in self.buttons:
            btn.update(delta_time)

    def on_draw(self):
        self.clear()
        self.background.draw()

        arcade.draw_text(
            "Оффлайн игры",
            SCREEN_WIDTH // 2,
            480 + self.title_offset,
            arcade.color.AQUA,
            48,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )

        arcade.draw_text(
            "Небольшая коллекция игр",
            SCREEN_WIDTH // 2,
            420,
            arcade.color.LIGHT_GRAY,
            18,
            anchor_x="center",
            anchor_y="center",
        )

        for btn in self.buttons:
            btn.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for btn in self.buttons:
            btn.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            btn.check_click(x, y, button)
            arcade.play_sound(self.click_sound)


class GamesMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.buttons = []
        self.background = AnimatedBackground()
        self.click_sound = arcade.load_sound("assets/click.wav")

        self.setup_buttons()

    def setup_buttons(self):
        games = [
            ("Игра 1", None),
            ("Игра 2", None),
            ("Игра 3", None),
            ("Файтинг", lambda: FighterGameView(GamesMenuView)),
            ("Танчики", lambda: TanksGameView(GamesMenuView)),
            ("Покер на костях", lambda: DicePokerView(GamesMenuView)),
        ]

        cols = 2
        start_x = SCREEN_WIDTH // 2 - 160
        start_y = 420
        gap_x = 320
        gap_y = 110

        for i, (name, game_class) in enumerate(games):
            col = i % cols
            row = i // cols
            x = start_x + col * gap_x
            y = start_y - row * gap_y

            if game_class:
                action = lambda gc=game_class: self.start_real_game(gc)
            else:
                action = lambda n=name: self.start_game(n)

            self.buttons.append(Button(x, y, 220, 65, name, action))

        self.buttons.append(Button(SCREEN_WIDTH // 2, 80, 200, 55, "НАЗАД", self.go_back))

    def start_real_game(self, game_view_factory):
        self.window.show_view(game_view_factory())

    def start_game(self, name):
        self.window.show_view(GamePlaceholderView(name))

    def go_back(self):
        self.window.show_view(MainMenuView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_update(self, delta_time):
        self.background.update(delta_time)
        for btn in self.buttons:
            btn.update(delta_time)

    def on_draw(self):
        self.clear()
        self.background.draw()

        arcade.draw_text(
            "ВЫБОР ИГРЫ",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 50,
            arcade.color.AQUA,
            40,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )

        for btn in self.buttons:
            btn.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for btn in self.buttons:
            btn.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            btn.check_click(x, y, button)
            arcade.play_sound(self.click_sound)


class SettingsView(arcade.View):
    def __init__(self):
        super().__init__()
        self.buttons = [Button(SCREEN_WIDTH // 2, 100, 200, 55, "НАЗАД", self.go_back)]
        self.background = AnimatedBackground()

    def go_back(self):
        self.window.show_view(MainMenuView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_update(self, delta_time):
        self.background.update(delta_time)
        for btn in self.buttons:
            btn.update(delta_time)

    def on_draw(self):
        self.clear()
        self.background.draw()

        arcade.draw_text(
            "НАСТРОЙКИ",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 50,
            arcade.color.AQUA,
            40,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )

        arcade.draw_text(
            "В разработке...", SCREEN_WIDTH // 2, 300, arcade.color.YELLOW, 28, anchor_x="center", anchor_y="center"
        )

        for btn in self.buttons:
            btn.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for btn in self.buttons:
            btn.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            btn.check_click(x, y, button)


class GamePlaceholderView(arcade.View):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.buttons = [Button(SCREEN_WIDTH // 2, 100, 200, 55, "НАЗАД", self.go_back)]

    def go_back(self):
        self.window.show_view(GamesMenuView())

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_update(self, delta_time):
        for btn in self.buttons:
            btn.update(delta_time)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            self.name, SCREEN_WIDTH // 2, 500, arcade.color.AQUA, 36, anchor_x="center", anchor_y="center", bold=True
        )
        arcade.draw_text(
            "Скоро здесь будет игра!",
            SCREEN_WIDTH // 2,
            300,
            arcade.color.YELLOW,
            24,
            anchor_x="center",
            anchor_y="center",
        )
        for btn in self.buttons:
            btn.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for btn in self.buttons:
            btn.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            btn.check_click(x, y, button)


class FinalResultsView(arcade.View):
    def __init__(self, return_view_class):
        super().__init__()
        self.return_view = return_view_class
        self.data_manager = GameDataManager()

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_BLUE)

        arcade.draw_text(
            "ИТОГОВАЯ СТАТИСТИКА", SCREEN_WIDTH // 2, 500, arcade.color.GOLD, 36, anchor_x="center", bold=True
        )

        data = self.data_manager.data
        y = 400
        # Отображение рекордов
        arcade.draw_text(
            f"Рекорд в танках: {data['high_scores']['tanks']} ур.",
            SCREEN_WIDTH // 2,
            y,
            arcade.color.WHITE,
            20,
            anchor_x="center",
        )
        y -= 50
        arcade.draw_text(
            f"Рекорд в покере: {data['high_scores']['dice_record']} очков",
            SCREEN_WIDTH // 2,
            y,
            arcade.color.WHITE,
            20,
            anchor_x="center",
        )
        y -= 50
        arcade.draw_text(
            f"Всего игр: {data['total_games']}", SCREEN_WIDTH // 2, y, arcade.color.GRAY, 18, anchor_x="center"
        )

        arcade.draw_text(
            "Нажмите ESC для выхода в меню", SCREEN_WIDTH // 2, 100, arcade.color.LIGHT_GRAY, 16, anchor_x="center"
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.return_view())


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(MainMenuView())
    arcade.run()


if __name__ == "__main__":
    main()
