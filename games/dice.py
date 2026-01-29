import arcade
import random
import math
from data_manager import GameDataManager

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600

COMBINATIONS = [
    ("Покер (5 одинаковых)", "50"),
    ("Каре (4 одинаковых)", "40"),
    ("Фулл Хаус (3+2)", "35"),
    ("Большой стрит (2-6)", "30"),
    ("Малый стрит (1-5)", "30"),
    ("Тройка (3 одинаковых)", "25"),
    ("Две пары", "20"),
    ("Пара", "10"),
    ("Ничего", "сумма"),
]


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
        self.click_sound = arcade.load_sound(":resources:sounds/hit1.wav")

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


class AnimatedDie:
    """Анимированный кубик - обычный класс"""

    def __init__(self, x, y, die_size=70):
        self.x = x
        self.y = y
        self.die_size = die_size  # Переименовано!
        self.value = random.randint(1, 6)
        self.locked = False

        # Анимация
        self.rolling = False
        self.roll_time = 0.0
        self.roll_duration = 0.8
        self.bounce_offset = 0.0
        self.shake_x = 0.0
        self.shake_y = 0.0

    def start_roll(self):
        if not self.locked:
            self.rolling = True
            self.roll_time = 0.0

    def update(self, delta_time: float):
        if self.rolling:
            self.roll_time += delta_time
            progress = self.roll_time / self.roll_duration

            if progress >= 1.0:
                # Конец анимации
                self.rolling = False
                self.roll_time = 0.0
                self.shake_x = 0.0
                self.shake_y = 0.0
                self.bounce_offset = 0.0
                self.value = random.randint(1, 6)
            else:
                # Анимация
                shake_amount = 8 * (1 - progress)
                self.shake_x = random.uniform(-shake_amount, shake_amount)
                self.shake_y = random.uniform(-shake_amount, shake_amount)

                # Подпрыгивание
                self.bounce_offset = math.sin(progress * math.pi * 5) * 25 * (1 - progress)

                # Смена значения с замедлением
                change_interval = 0.05 + progress * 0.15
                if int(self.roll_time / change_interval) != int((self.roll_time - delta_time) / change_interval):
                    self.value = random.randint(1, 6)

    def draw(self):
        draw_x = self.x + self.shake_x
        draw_y = self.y + self.shake_y + self.bounce_offset

        # Тень
        shadow_scale = 1.0 - self.bounce_offset * 0.01
        arcade.draw_ellipse_filled(
            self.x, self.y - self.die_size // 2 - 8, self.die_size * 0.6 * shadow_scale, 10 * shadow_scale, (0, 0, 0, 60)
        )

        half = self.die_size // 2

        # Цвет кубика
        if self.locked:
            main_color = arcade.color.DARK_GREEN
            top_color = arcade.color.GREEN
            border_color = arcade.color.LIME_GREEN
        else:
            main_color = arcade.color.GHOST_WHITE
            top_color = arcade.color.WHITE
            border_color = arcade.color.GRAY

        # Основа
        arcade.draw_lbwh_rectangle_filled(
            draw_x - half + 2, draw_y - half, self.die_size - 4, self.die_size - 4, main_color
        )

        # Верхняя половина светлее
        arcade.draw_lbwh_rectangle_filled(draw_x - half + 2, draw_y, self.die_size - 4, half - 2, top_color)

        # Рамка
        arcade.draw_lbwh_rectangle_outline(
            draw_x - half, draw_y - half, self.die_size, self.die_size, border_color, 3 if self.locked else 2
        )

        # Точки
        self.draw_dots(draw_x, draw_y)

        # Метка заблокированного
        if self.locked:
            arcade.draw_text(
                "HOLD", draw_x, draw_y + half + 12, arcade.color.LIME_GREEN, 11, anchor_x="center", bold=True
            )

    def draw_dots(self, cx, cy):
        dot_color = arcade.color.BLACK
        dot_size = 7
        offset = self.die_size // 4

        patterns = {
            1: [(0, 0)],
            2: [(-1, -1), (1, 1)],
            3: [(-1, -1), (0, 0), (1, 1)],
            4: [(-1, -1), (-1, 1), (1, -1), (1, 1)],
            5: [(-1, -1), (-1, 1), (0, 0), (1, -1), (1, 1)],
            6: [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1)],
        }

        for dx, dy in patterns.get(self.value, []):
            px = cx + dx * offset
            py = cy + dy * offset
            arcade.draw_circle_filled(px + 1, py - 1, dot_size, (0, 0, 0, 80))
            arcade.draw_circle_filled(px, py, dot_size, dot_color)
            arcade.draw_circle_filled(px - 2, py + 2, 2, (100, 100, 100))

    def check_click(self, mx, my):
        return abs(mx - self.x) < self.die_size // 2 and abs(my - self.y) < self.die_size // 2


class BotPlayer:
    def __init__(self, difficulty="Medium"):
        """Сложность:
        Easy - Легко
        Medium - Средне
        Hard - Сложно"""
        self.difficulty = difficulty

    def decision(self, dice_vals, rolls_left):
        """Возвращает список индексов кубиков, которые нужно оставить"""
        counts = {x: dice_vals.count(x) for x in set(dice_vals)}

        if self.difficulty == "Easy":
            return self._logic_easy()
        elif self.difficulty == "Medium":
            return self._logic_medium(dice_vals, counts, rolls_left)
        else:
            return self._logic_hard(dice_vals, counts, rolls_left)

    def _logic_easy(self):
        # Случайный выбор
        return random.sample(range(5), random.randint(0, 4))

    def _logic_medium(self, values, counts, rolls_left):
        # Жадный алг: держим пары и сеты, игнорируем стриты
        for val, count in counts.items():
            if count >= 2:
                return [i for i, v in enumerate(values) if v == val]

        threshold = 4 if rolls_left == 1 else 5
        return [i for i, v in enumerate(values) if v >= threshold]

    def _logic_hard(self, values, counts, rolls_left):
        """
        Продвинутая логика:
        1. Проверяет готовые сильные комбинации.
        2. Взвешивает шансы (стрит vs пары).
        3. Учитывает оставшиеся броски.
        """
        unique_vals = sorted(list(set(values)))

        # --- 1. готовые комбинации---
        # Покер (5 одинаковых)
        if 5 in counts.values():
            return [0, 1, 2, 3, 4]

        # Стриты (5 подряд)
        if len(unique_vals) == 5 and (unique_vals[-1] - unique_vals[0] == 4):
            return [0, 1, 2, 3, 4]

        # Фулл Хаус (3 + 2)
        if 3 in counts.values() and 2 in counts.values():
            return [0, 1, 2, 3, 4]

        # --- 2. Отличные позиции ---
        # Каре (4 одинаковых)
        for val, count in counts.items():
            if count == 4:
                return self._get_indices(values, [val])

        # "Почти стрит" (4 подряд) - высокий приоритет
        # Ищем последовательность из 4 чисел (например 2,3,4,5)
        streak_4 = self._find_longest_streak(unique_vals, min_len=4)
        if streak_4:
            return self._get_indices(values, streak_4)

        # --- 3. Хорошие позиции ---
        # Тройка (3 одинаковых)
        for val, count in counts.items():
            if count == 3:
                return self._get_indices(values, [val])

        # Две пары
        pairs = [k for k, v in counts.items() if v == 2]
        if len(pairs) == 2:
            return self._get_indices(values, pairs)

        # --- 4. Рискованные позиции (Только если есть броски) ---
        # "Почти стрит" (3 подряд) - только если rolls_left > 0
        if rolls_left > 0:
            streak_3 = self._find_longest_streak(unique_vals, min_len=3)
            # Если у нас стрит 3 подряд (напр. 3,4,5), это лучше чем просто пара 2-2
            if streak_3:
                # Но если есть пара высоких (5 или 6), лучше оставить пару
                if not (pairs and max(pairs) >= 5):
                    return self._get_indices(values, streak_3)

        # Обычная пара
        if pairs:
            return self._get_indices(values, [max(pairs)])

        # --- 5. Ничего нет ---
        # Оставляем 5 или 6
        high_dice = [v for v in values if v >= 5]
        if high_dice:
            return [i for i, v in enumerate(values) if v >= 5]

        # Если всё плохо, оставляем самую большую
        max_val = max(values)
        return [values.index(max_val)]

    def _get_indices(self, all_values, target_values):
        """Возвращает индексы кубиков, значения которых есть в target_values"""

        found_map = {v: 0 for v in target_values}

        res = []
        for i, v in enumerate(all_values):
            if v in target_values:
                # Эвристика: если target_values - это последовательность (стрит), берем по 1 шт каждого
                is_sequence = len(target_values) > 1 and (
                    max(target_values) - min(target_values) == len(target_values) - 1
                )

                if is_sequence:
                    if found_map[v] == 0:
                        res.append(i)
                        found_map[v] += 1
                else:
                    # Если пары/тройки - берем все
                    res.append(i)
        return res

    def _find_longest_streak(self, unique_sorted_vals, min_len):
        """Ищет самую длинную последовательность"""
        best_streak = []
        curr_streak = [unique_sorted_vals[0]]

        for i in range(1, len(unique_sorted_vals)):
            if unique_sorted_vals[i] == unique_sorted_vals[i - 1] + 1:
                curr_streak.append(unique_sorted_vals[i])
            else:
                if len(curr_streak) >= len(best_streak):
                    best_streak = curr_streak
                curr_streak = [unique_sorted_vals[i]]

        if len(curr_streak) >= len(best_streak):
            best_streak = curr_streak

        if len(best_streak) >= min_len:
            return best_streak
        return None

    def should_stop(self, score):
        if self.difficulty == "Easy":
            return score >= 40
        if self.difficulty == "Medium":
            return score >= 35
        return score >= 32


class DicePokerView(arcade.View):
    def __init__(self, return_view_class):
        super().__init__()
        self.return_view_class = return_view_class
        self.dice = []
        self.curr_player = 1
        self.rolls_left = 3
        self.scores = {1: 0, 2: 0}
        self.round = 1
        self.max_rounds = 5
        self.game_over = False
        self.round_scored = False
        self.data_manager = GameDataManager()

        self.sounds = {}
        self.load_sounds()

        # Bot
        self.vs_bot = False
        self.difficulty = "Medium"
        self.bot = None
        self.bot_timer = 0

        self.setup()

    def load_sounds(self):
        try:
            self.sounds["roll"] = arcade.load_sound("assets/roll.wav")
            self.sounds["click"] = arcade.load_sound("assets/click.wav")
            self.sounds["win"] = arcade.load_sound("assets/win.wav")
        except Exception:
            pass

    def setup(self):
        self.dice = []
        start_x = 180
        for i in range(5):
            die = AnimatedDie(start_x + i * 95, 280, 65)
            self.dice.append(die)

        self.curr_player = 1
        self.rolls_left = 3
        self.round = 1
        self.game_over = False
        self.scores = {1: 0, 2: 0}
        self.round_scored = False

        self.game_started = False
        self.bot_timer = 0
        self.setup_buttons()

    def setup_buttons(self):
        self.game_buttons = []

        # Кнопки основного игрового процесса
        self.btn_roll = Button(140, 90, 140, 40, "БРОСИТЬ", self.roll_all_dice)
        self.btn_score = Button(340, 90, 140, 40, "ЗАПИСАТЬ", self.score_hand)
        self.btn_exit = Button(540, 90, 140, 40, "ВЫХОД", self.go_back)

        self.game_buttons = [self.btn_roll, self.btn_score, self.btn_exit]

        # Кнопки меню выбора (создаются динамически или заранее)
        self.menu_buttons = []
        # Сложность
        self.btn_easy = Button(
            SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2 + 40, 140, 40, "ЛЕГКИЙ", lambda: self.set_diff("Easy")
        )
        self.btn_medium = Button(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40, 140, 40, "СРЕДНИЙ", lambda: self.set_diff("Medium")
        )
        self.btn_hard = Button(
            SCREEN_WIDTH // 2 + 160, SCREEN_HEIGHT // 2 + 40, 140, 40, "СЛОЖНЫЙ", lambda: self.set_diff("Hard")
        )

        # Режим
        self.btn_pvp = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 100, 180, 50, "С ДРУГОМ", self.start_pvp)
        self.btn_pve = Button(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2 - 100, 180, 50, "С БОТОМ", self.start_pve)

        self.menu_buttons = [self.btn_easy, self.btn_medium, self.btn_hard, self.btn_pvp, self.btn_pve]

    def on_draw(self):
        self.clear()
        if not self.game_started:
            self.draw_menu()
        else:
            self.draw_game()

    def roll_all_dice(self):
        if self.rolls_left > 0 and not self.game_over:
            if "roll" in self.sounds:
                arcade.play_sound(self.sounds["roll"])

            any_rolled = False
            for die in self.dice:
                if not die.locked:
                    die.start_roll()
                    any_rolled = True
            if any_rolled:
                self.rolls_left -= 1

    def score_hand(self):
        if any(d.rolling for d in self.dice):
            return

        if self.rolls_left < 3 and not self.round_scored:
            score = self.calculate_score()
            self.scores[self.curr_player] += score
            self.round_scored = True

            if self.curr_player == 1:
                self.curr_player = 2
                self.reset_for_next_turn()
            else:
                self.curr_player = 1
                self.round += 1
                if self.round > self.max_rounds:
                    self.game_over = True
                else:
                    self.reset_for_next_turn()

        if self.game_over:
            is_record = self.data_manager.record_game("dice", self.scores[1], self.scores[1] > self.scores[2])
            if is_record and "win" in self.sounds:
                arcade.play_sound(self.sounds["win"])

    def reset_for_next_turn(self):
        self.rolls_left = 3
        self.round_scored = False
        for die in self.dice:
            die.locked = False

    def calculate_score(self):
        values = [d.value for d in self.dice]
        counts = {}
        for v in values:
            counts[v] = counts.get(v, 0) + 1

        max_count = max(counts.values())
        unique = len(counts)

        if max_count == 5:
            return 50
        if max_count == 4:
            return 40
        if max_count == 3 and unique == 2:
            return 35

        sorted_vals = sorted(set(values))
        if sorted_vals == [1, 2, 3, 4, 5] or sorted_vals == [2, 3, 4, 5, 6]:
            return 30

        if max_count == 3:
            return 25

        pairs = sum(1 for c in counts.values() if c == 2)
        if pairs == 2:
            return 20
        if max_count == 2:
            return 10

        return sum(values)

    def get_hand_info(self):
        values = [d.value for d in self.dice]
        counts = {}
        for v in values:
            counts[v] = counts.get(v, 0) + 1

        max_count = max(counts.values()) if counts else 0
        unique = len(counts)

        if max_count == 5:
            return "ПОКЕР!", 50, arcade.color.GOLD
        if max_count == 4:
            return "Каре", 40, arcade.color.ORANGE
        if max_count == 3 and unique == 2:
            return "Фулл Хаус", 35, arcade.color.PURPLE

        sorted_vals = sorted(set(values))
        if sorted_vals == [2, 3, 4, 5, 6]:
            return "Большой стрит", 30, arcade.color.GREEN
        if sorted_vals == [1, 2, 3, 4, 5]:
            return "Малый стрит", 30, arcade.color.GREEN

        if max_count == 3:
            return "Тройка", 25, arcade.color.CYAN

        pairs = sum(1 for c in counts.values() if c == 2)
        if pairs == 2:
            return "Две пары", 20, arcade.color.BLUE
        if max_count == 2:
            return "Пара", 10, arcade.color.LIGHT_BLUE

        return f"Сумма: {sum(values)}", sum(values), arcade.color.GRAY

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_update(self, delta_time):
        delta_time = min(delta_time, 0.05)
        for die in self.dice:
            die.update(delta_time)

        # Анимация кнопок
        active_buttons = self.menu_buttons if not self.game_started else self.game_buttons
        for btn in active_buttons:
            btn.update(delta_time)

        # Если играем с ботом и сейчас его очередь
        if self.game_started and self.vs_bot and self.curr_player == 2:
            if not any(d.rolling for d in self.dice):
                self.bot_timer += delta_time

                # Имитация задержки перед действием
                if self.rolls_left == 3 and self.bot_timer > 1.0:
                    self.roll_all_dice()
                    self.bot_timer = 0
                elif 0 < self.rolls_left < 3 and self.bot_timer > 1.5:
                    curr_vals = [d.value for d in self.dice]
                    _, score, _ = self.get_hand_info()

                    if self.bot.should_stop(score):
                        self.score_hand()
                    else:
                        keep_indices = self.bot.decision(curr_vals, self.rolls_left)
                        for i in range(5):
                            self.dice[i].locked = i in keep_indices
                        self.roll_all_dice()
                    self.bot_timer = 0
                elif self.rolls_left == 0 and self.bot_timer > 1.0:
                    self.score_hand()
                    self.bot_timer = 0

    def draw_menu(self):
        arcade.draw_text(
            "ВЫБОР РЕЖИМА",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 150,
            arcade.color.GOLD,
            34,
            anchor_x="center",
            bold=True,
        )

        # Рисуем анимированные кнопки вместо обычных прямоугольников
        for btn in self.menu_buttons:
            # Подсветка выбранной сложности
            if btn.text in ["ЛЕГКИЙ", "СРЕДНИЙ", "СЛОЖНЫЙ"]:
                btn.hovered = (
                    (self.difficulty == "Easy" and btn.text == "ЛЕГКИЙ")
                    or (self.difficulty == "Medium" and btn.text == "СРЕДНИЙ")
                    or (self.difficulty == "Hard" and btn.text == "СЛОЖНЫЙ")
                    or btn.hovered
                )  # Сохраняем эффект наведения
            btn.draw()

    def draw_game(self):
        self.clear()

        # Игровой стол
        arcade.draw_lbwh_rectangle_filled(20, 160, 650, 200, arcade.color.DARK_GREEN)
        arcade.draw_lbwh_rectangle_outline(20, 160, 650, 200, arcade.color.SADDLE_BROWN, 8)

        # Заголовок
        arcade.draw_text("ПОКЕР НА КОСТЯХ", 350, SCREEN_HEIGHT - 45, arcade.color.GOLD, 32, anchor_x="center", bold=True)

        # Панель информации
        arcade.draw_lbwh_rectangle_filled(20, 400, 180, 140, (0, 0, 0, 180))
        arcade.draw_lbwh_rectangle_outline(20, 400, 180, 140, arcade.color.GOLD, 2)

        player_color = arcade.color.CYAN if self.curr_player == 1 else arcade.color.ORANGE
        arcade.draw_text(f"Ход: Игрок {self.curr_player}", 110, 520, player_color, 15, anchor_x="center", bold=True)
        arcade.draw_text(f"Раунд: {self.round}/{self.max_rounds}", 110, 490, arcade.color.WHITE, 13, anchor_x="center")
        arcade.draw_text(f"Бросков: {self.rolls_left}", 110, 460, arcade.color.WHITE, 13, anchor_x="center")

        # Индикаторы бросков
        for i in range(3):
            color = arcade.color.GREEN if i < self.rolls_left else arcade.color.DARK_RED
            arcade.draw_circle_filled(70 + i * 30, 425, 10, color)

        # Панель счета
        arcade.draw_lbwh_rectangle_filled(220, 400, 200, 140, (0, 0, 0, 180))
        arcade.draw_lbwh_rectangle_outline(220, 400, 200, 140, arcade.color.GOLD, 2)

        arcade.draw_text("СЧЁТ", 320, 520, arcade.color.GOLD, 17, anchor_x="center", bold=True)
        arcade.draw_text(f"Игрок 1: {self.scores[1]}", 320, 480, arcade.color.CYAN, 16, anchor_x="center")
        arcade.draw_text(f"Игрок 2: {self.scores[2]}", 320, 445, arcade.color.ORANGE, 16, anchor_x="center")

        # Кости
        for die in self.dice:
            die.draw()

        # Текущая комбинация
        if self.rolls_left < 3 and not any(d.rolling for d in self.dice):
            name, score, color = self.get_hand_info()
            arcade.draw_lbwh_rectangle_filled(180, 380, 320, 30, (0, 0, 0, 150))
            arcade.draw_text(f"{name}: +{score}", 340, 395, color, 18, anchor_x="center", anchor_y="center", bold=True)

        # Подсказка
        arcade.draw_text(
            "Клик = заблокировать | SPACE = бросить | ENTER = записать",
            340,
            140,
            arcade.color.LIGHT_GRAY,
            11,
            anchor_x="center",
        )

        # Кнопки
        self.btn_roll.draw()
        self.btn_score.draw()
        self.btn_exit.draw()

        # Панель комбинаций
        self.draw_combinations_panel()

        if self.game_over:
            self.draw_game_over()

    def draw_combinations_panel(self):
        panel_x = SCREEN_WIDTH - 210
        panel_y = 90
        panel_width = 190
        panel_height = 460

        arcade.draw_lbwh_rectangle_filled(panel_x, panel_y, panel_width, panel_height, (0, 0, 0, 200))
        arcade.draw_lbwh_rectangle_outline(panel_x, panel_y, panel_width, panel_height, arcade.color.DARK_GOLDENROD, 2)

        arcade.draw_text(
            "КОМБИНАЦИИ",
            panel_x + panel_width // 2,
            panel_y + panel_height - 25,
            arcade.color.GOLD,
            13,
            anchor_x="center",
            bold=True,
        )

        y = panel_y + panel_height - 55
        for name, score in COMBINATIONS:
            arcade.draw_text(name, panel_x + 10, y, arcade.color.WHITE, 10)
            arcade.draw_text(score, panel_x + panel_width - 10, y, arcade.color.YELLOW, 10, anchor_x="right")
            y -= 45

    def draw_button(self, x, y, width, height, text, enabled):
        color = arcade.color.DARK_SLATE_BLUE if enabled else arcade.color.DIM_GRAY
        text_color = arcade.color.WHITE if enabled else arcade.color.GRAY

        arcade.draw_lbwh_rectangle_filled(x - width // 2, y - height // 2, width, height, color)
        arcade.draw_lbwh_rectangle_outline(x - width // 2, y - height // 2, width, height, arcade.color.WHITE, 2)
        arcade.draw_text(text, x, y, text_color, 13, anchor_x="center", anchor_y="center", bold=True)

    def draw_game_over(self):
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 200))

        arcade.draw_lbwh_rectangle_filled(
            SCREEN_WIDTH // 2 - 230, SCREEN_HEIGHT // 2 - 100, 460, 200, arcade.color.DARK_SLATE_GRAY
        )
        arcade.draw_lbwh_rectangle_outline(
            SCREEN_WIDTH // 2 - 230, SCREEN_HEIGHT // 2 - 100, 460, 200, arcade.color.GOLD, 5
        )

        arcade.draw_text(
            "ИГРА ОКОНЧЕНА!",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 55,
            arcade.color.GOLD,
            28,
            anchor_x="center",
            bold=True,
        )

        if self.scores[1] > self.scores[2]:
            winner, winner_color = "ИГРОК 1", arcade.color.CYAN
        elif self.scores[2] > self.scores[1]:
            winner, winner_color = "ИГРОК 2", arcade.color.ORANGE
        else:
            winner, winner_color = "НИЧЬЯ", arcade.color.WHITE

        arcade.draw_text(
            f"Победитель: {winner}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 10,
            winner_color,
            24,
            anchor_x="center",
            bold=True,
        )
        arcade.draw_text(
            f"Счёт: {self.scores[1]} - {self.scores[2]}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 25,
            arcade.color.WHITE,
            20,
            anchor_x="center",
        )
        arcade.draw_text(
            "R - новая игра | ESC - выход",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 65,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center",
        )

    def on_mouse_motion(self, x, y, dx, dy):
        """Анимации на кнопках"""
        active_btns = self.menu_buttons if not self.game_started else self.game_buttons
        for btn in active_btns:
            btn.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        active_btns = self.menu_buttons if not self.game_started else self.game_buttons

        # 1. Проверяем клик
        for btn in active_btns:
            if btn.check_click(x, y, button):
                return

        # 2. Логика игры
        if self.game_started and not (self.vs_bot and self.curr_player == 2):
            if self.rolls_left < 3 and self.rolls_left > 0:
                if not any(d.rolling for d in self.dice):
                    for die in self.dice:
                        if die.check_click(x, y):
                            die.locked = not die.locked

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.return_view_class())
        if key == arcade.key.R and self.game_over:
            self.setup()
        if key == arcade.key.SPACE:
            self.roll_all_dice()
        if key == arcade.key.ENTER:
            self.score_hand()

    def set_diff(self, diff):
        self.difficulty = diff

    def start_pvp(self):
        self.vs_bot = False
        self.game_started = True

    def start_pve(self):
        self.vs_bot = True
        self.bot = BotPlayer(self.difficulty)
        self.game_started = True

    def go_back(self):
        self.window.show_view(self.return_view_class())
