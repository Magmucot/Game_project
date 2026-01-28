import arcade

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Супер проект"

COLOR_BG = arcade.color.DARK_BLUE_GRAY
COLOR_BUTTON = arcade.color.DARK_SLATE_BLUE
COLOR_BUTTON_HOVER = arcade.color.SLATE_BLUE
COLOR_TEXT = arcade.color.WHITE
COLOR_TITLE = arcade.color.AQUA


# ===================== КНОПКА =====================
class Button:
    """Простая кнопка для меню."""

    def __init__(self, x, y, width, height, text, action=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.action = action
        self.hovered = False

    def draw(self):
        color = COLOR_BUTTON_HOVER if self.hovered else COLOR_BUTTON
        arcade.draw_lbwh_rectangle_filled(self.x - self.width / 2, self.y - self.height / 2,
                                          self.width, self.height, color)
        arcade.draw_text(self.text, self.x, self.y, COLOR_TEXT, font_size=20,
                         anchor_x="center", anchor_y="center")

    def check_hover(self, mouse_x, mouse_y):
        self.hovered = (self.x - self.width / 2 < mouse_x < self.x + self.width / 2 and
                        self.y - self.height / 2 < mouse_y < self.y + self.height / 2)
        return self.hovered

    def check_click(self, mouse_x, mouse_y, button):
        if button == arcade.MOUSE_BUTTON_LEFT and self.check_hover(mouse_x, mouse_y):
            if self.action:
                self.action()
            return True
        return False


# ===================== ГЛАВНОЕ МЕНЮ =====================
class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.buttons = []
        self.setup_buttons()

    def setup_buttons(self):
        center_x = SCREEN_WIDTH // 2
        start_y = 350
        step = 100
        self.buttons = [
            Button(center_x, start_y, 250, 60, "ИГРЫ", self.go_to_games),
            Button(center_x, start_y - step, 250, 60, "НАСТРОЙКИ", self.go_to_settings)
        ]

    def go_to_games(self):
        self.window.show_view(GamesMenuView())

    def go_to_settings(self):
        self.window.show_view(SettingsView())

    def on_show_view(self):
        arcade.set_background_color(COLOR_BG)

    def on_draw(self):
        self.clear()
        arcade.draw_text("СУПЕР ПРОЕКТ", SCREEN_WIDTH // 2, 500, COLOR_TITLE, 40,
                         anchor_x="center", anchor_y="center", bold=True)
        for btn in self.buttons:
            btn.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for btn in self.buttons:
            btn.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            btn.check_click(x, y, button)


# ===================== МЕНЮ ИГР =====================
class GamesMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.buttons = []
        self.setup_buttons()

    def setup_buttons(self):
        games = [f"Игра {i}" for i in range(1, 7)]
        cols = 2
        start_x = SCREEN_WIDTH // 2 - 150
        start_y = 400
        gap_x = 300
        gap_y = 120

        for i, name in enumerate(games):
            col = i % cols
            row = i // cols
            x = start_x + col * gap_x
            y = start_y - row * gap_y
            self.buttons.append(Button(x, y, 200, 60, name, lambda n=name: self.start_game(n)))

        self.buttons.append(Button(SCREEN_WIDTH // 2, 100, 200, 50, "НАЗАД", self.go_back))

    def start_game(self, name):
        self.window.show_view(GamePlaceholderView(name))

    def go_back(self):
        self.window.show_view(MainMenuView())

    def on_show_view(self):
        arcade.set_background_color(COLOR_BG)

    def on_draw(self):
        self.clear()
        arcade.draw_text("ВЫБОР ИГРЫ", SCREEN_WIDTH // 2, 500, COLOR_TITLE, 36,
                         anchor_x="center", anchor_y="center", bold=True)
        for btn in self.buttons:
            btn.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for btn in self.buttons:
            btn.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            btn.check_click(x, y, button)


# ===================== НАСТРОЙКИ =====================
class SettingsView(arcade.View):
    def __init__(self):
        super().__init__()
        self.buttons = [Button(SCREEN_WIDTH // 2, 100, 200, 50, "НАЗАД", self.go_back)]

    def go_back(self):
        self.window.show_view(MainMenuView())

    def on_show_view(self):
        arcade.set_background_color(COLOR_BG)

    def on_draw(self):
        self.clear()
        arcade.draw_text("НАСТРОЙКИ", SCREEN_WIDTH // 2, 500, COLOR_TITLE, 36,
                         anchor_x="center", anchor_y="center", bold=True)
        arcade.draw_text("Здесь пока пусто...", SCREEN_WIDTH // 2, 300, COLOR_TEXT, 24,
                         anchor_x="center", anchor_y="center")
        for btn in self.buttons:
            btn.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for btn in self.buttons:
            btn.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            btn.check_click(x, y, button)


# ===================== ЗАГЛУШКА ИГРЫ =====================
class GamePlaceholderView(arcade.View):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.buttons = [Button(SCREEN_WIDTH // 2, 100, 200, 50, "НАЗАД", self.go_back)]

    def go_back(self):
        self.window.show_view(GamesMenuView())

    def on_show_view(self):
        arcade.set_background_color(COLOR_BG)

    def on_draw(self):
        self.clear()
        arcade.draw_text(self.name, SCREEN_WIDTH // 2, 500, COLOR_TITLE, 36,
                         anchor_x="center", anchor_y="center", bold=True)
        arcade.draw_text("Здесь будет игра!", SCREEN_WIDTH // 2, 300, COLOR_TEXT, 24,
                         anchor_x="center", anchor_y="center")
        for btn in self.buttons:
            btn.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for btn in self.buttons:
            btn.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for btn in self.buttons:
            btn.check_click(x, y, button)


# ===================== ЗАПУСК =====================
def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(MainMenuView())
    arcade.run()


if __name__ == "__main__":
    main()
