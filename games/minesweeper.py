import arcade
import random
import time

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
TITLE = "Сапёр"

ROWS = 12
COLS = 16
CELL = 32
LEFT = 40
BOTTOM = 60
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL


class MinesweeperGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
        arcade.set_background_color(arcade.color.ASH_GREY)
        self.setup()

    def setup(self):
        self.rows = ROWS
        self.cols = COLS
        self.mines_total = max(10, (self.rows * self.cols) // 8)
        self.mines = set()
        self.revealed = set()
        self.flags = set()
        self.first_click = True
        self.game_over = False
        self.win = False
        self.start_time = None
        self.elapsed = 0.0

    def place_mines_avoiding(self, avoid):
        poss = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        forbidden = {avoid}
        ar, ac = avoid
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                rr, cc = ar + dr, ac + dc
                if 0 <= rr < self.rows and 0 <= cc < self.cols:
                    forbidden.add((rr, cc))
        choices = [p for p in poss if p not in forbidden]
        self.mines = set(random.sample(choices, self.mines_total))

    def neighbors(self, r, c):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield (nr, nc)

    def count_mines(self, r, c):
        return sum(1 for n in self.neighbors(r, c) if n in self.mines)

    def flood_reveal(self, r, c):
        stack = [(r, c)]
        while stack:
            rr, cc = stack.pop()
            if (rr, cc) in self.revealed:
                continue
            self.revealed.add((rr, cc))
            if self.count_mines(rr, cc) == 0:
                for n in self.neighbors(rr, cc):
                    if n not in self.revealed and n not in self.mines:
                        stack.append(n)

    def check_win(self):
        total = self.rows * self.cols
        if len(self.revealed) + len(self.mines) == total:
            self.win = True
            self.game_over = True

    def on_draw(self):
        self.clear()
        arcade.draw_lbwh_rectangle_filled(LEFT - 2, BOTTOM - 2, WIDTH + 4, HEIGHT + 4, arcade.color.DARK_BROWN)
        for r in range(self.rows):
            for c in range(self.cols):
                left = LEFT + c * CELL
                bottom = BOTTOM + r * CELL
                revealed = (r, c) in self.revealed
                color = arcade.color.LIGHT_GRAY if revealed else arcade.color.GRAY
                arcade.draw_lbwh_rectangle_filled(left, bottom, CELL, CELL, color)
                arcade.draw_lbwh_rectangle_outline(left, bottom, CELL, CELL, arcade.color.BLACK, 1)
                if revealed:
                    if (r, c) in self.mines:
                        arcade.draw_circle_filled(left + CELL / 2, bottom + CELL / 2, CELL / 4, arcade.color.BLACK)
                    else:
                        cnt = self.count_mines(r, c)
                        if cnt > 0:
                            arcade.draw_text(str(cnt), left + CELL / 2, bottom + CELL / 2, arcade.color.BLUE, 16,
                                             anchor_x="center", anchor_y="center")
                else:
                    if (r, c) in self.flags:
                        arcade.draw_text("F", left + CELL / 2, bottom + CELL / 2, arcade.color.RED, 18,
                                         anchor_x="center", anchor_y="center")
        arcade.draw_text(f"Mines: {self.mines_total}", LEFT + WIDTH + 20, BOTTOM + HEIGHT - 20, arcade.color.WHITE, 16)
        if self.start_time:
            arcade.draw_text(f"Time: {int(self.elapsed)}s", LEFT + WIDTH + 20, BOTTOM + HEIGHT - 50,
                             arcade.color.LIGHT_GRAY, 14)
        arcade.draw_text("Left click open / Right click flag. R - restart", LEFT, 12,
                         arcade.color.LIGHT_GRAY, 12)
        if self.game_over:
            txt = "YOU WIN!" if self.win else "BOOM! YOU LOST"
            arcade.draw_lbwh_rectangle_filled(LEFT + WIDTH / 2 - 200, BOTTOM + HEIGHT / 2 - 40, 400, 80, (0, 0, 0, 200))
            arcade.draw_text(txt, LEFT + WIDTH / 2, BOTTOM + HEIGHT / 2 + 8, arcade.color.GOLD, 28, anchor_x="center")
            arcade.draw_text("R - restart", LEFT + WIDTH / 2, BOTTOM + HEIGHT / 2 - 18,
                             arcade.color.LIGHT_GRAY, 12, anchor_x="center")

    def on_update(self, dt):
        if self.start_time and not self.game_over:
            self.elapsed += dt

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_over:
            return
        if not (LEFT <= x <= LEFT + WIDTH and BOTTOM <= y <= BOTTOM + HEIGHT):
            return
        c = int((x - LEFT) // CELL)
        r = int((y - BOTTOM) // CELL)
        if button == arcade.MOUSE_BUTTON_RIGHT:
            if (r, c) not in self.revealed:
                if (r, c) in self.flags:
                    self.flags.remove((r, c))
                else:
                    self.flags.add((r, c))
            return
        if self.first_click:
            self.place_mines_avoiding((r, c))
            self.first_click = False
            self.start_time = time.time()
            self.elapsed = 0.0
        if (r, c) in self.flags:
            return
        if (r, c) in self.mines:
            self.game_over = True
            self.win = False
            self.revealed.update(self.mines)
            return
        if (r, c) not in self.revealed:
            if self.count_mines(r, c) == 0:
                self.flood_reveal(r, c)
            else:
                self.revealed.add((r, c))
        self.check_win()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            self.setup()
