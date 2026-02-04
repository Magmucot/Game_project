import arcade
import random
import time

ROW_COUNT = 12
COLUMN_COUNT = 16
CELL_SIZE = 32
BOARD_LEFT = 40
BOARD_BOTTOM = 60
BOARD_WIDTH = COLUMN_COUNT * CELL_SIZE
BOARD_HEIGHT = ROW_COUNT * CELL_SIZE


class MinesGameView(arcade.View):
    def __init__(self, return_view_cls):
        super().__init__()
        self.return_view_cls = return_view_cls
        arcade.set_background_color(arcade.color.ASH_GREY)
        self.initialize_game()

    def initialize_game(self):
        self.row_count = ROW_COUNT
        self.column_count = COLUMN_COUNT
        self.total_mines = max(10, (self.row_count * self.column_count) // 8)
        self.mine_positions = set()
        self.revealed_cells = set()
        self.flagged_cells = set()
        self.is_first_click = True
        self.is_game_over = False
        self.is_win = False
        self.game_start_time = None
        self.elapsed_time = 0.0

    def place_mines_safely(self, safe_cell):
        possible_cells = [(row, col) for row in range(self.row_count) for col in range(self.column_count)]
        forbidden_cells = {safe_cell}
        safe_row, safe_col = safe_cell

        for row_offset in (-1, 0, 1):
            for col_offset in (-1, 0, 1):
                neighbor_row = safe_row + row_offset
                neighbor_col = safe_col + col_offset
                if 0 <= neighbor_row < self.row_count and 0 <= neighbor_col < self.column_count:
                    forbidden_cells.add((neighbor_row, neighbor_col))

        available_cells = [cell for cell in possible_cells if cell not in forbidden_cells]
        self.mine_positions = set(random.sample(available_cells, self.total_mines))

    def get_cell_neighbors(self, row, col):
        for row_offset in (-1, 0, 1):
            for col_offset in (-1, 0, 1):
                if row_offset == 0 and col_offset == 0:
                    continue
                neighbor_row = row + row_offset
                neighbor_col = col + col_offset
                if 0 <= neighbor_row < self.row_count and 0 <= neighbor_col < self.column_count:
                    yield (neighbor_row, neighbor_col)

    def count_adjacent_mines(self, row, col):
        mine_count = 0
        for neighbor in self.get_cell_neighbors(row, col):
            if neighbor in self.mine_positions:
                mine_count += 1
        return mine_count

    def reveal_empty_area(self, start_row, start_col):
        cells_to_check = [(start_row, start_col)]
        while cells_to_check:
            current_row, current_col = cells_to_check.pop()
            if (current_row, current_col) in self.revealed_cells:
                continue

            self.revealed_cells.add((current_row, current_col))

            if self.count_adjacent_mines(current_row, current_col) == 0:
                for neighbor in self.get_cell_neighbors(current_row, current_col):
                    if neighbor not in self.revealed_cells and neighbor not in self.mine_positions:
                        cells_to_check.append(neighbor)

    def check_for_win(self):
        total_cells = self.row_count * self.column_count
        if len(self.revealed_cells) + len(self.mine_positions) == total_cells:
            self.is_win = True
            self.is_game_over = True

    def on_draw(self):
        self.clear()

        arcade.draw_lbwh_rectangle_filled(BOARD_LEFT - 2, BOARD_BOTTOM - 2, BOARD_WIDTH + 4, BOARD_HEIGHT + 4,
                                          arcade.color.DARK_BROWN)

        for row in range(self.row_count):
            for col in range(self.column_count):
                cell_left = BOARD_LEFT + col * CELL_SIZE
                cell_bottom = BOARD_BOTTOM + row * CELL_SIZE
                is_revealed = (row, col) in self.revealed_cells

                cell_color = arcade.color.LIGHT_GRAY if is_revealed else arcade.color.GRAY
                arcade.draw_lbwh_rectangle_filled(cell_left, cell_bottom, CELL_SIZE, CELL_SIZE, cell_color)
                arcade.draw_lbwh_rectangle_outline(cell_left, cell_bottom, CELL_SIZE, CELL_SIZE, arcade.color.BLACK, 1)

                if is_revealed:
                    if (row, col) in self.mine_positions:
                        arcade.draw_circle_filled(cell_left + CELL_SIZE / 2, cell_bottom + CELL_SIZE / 2, CELL_SIZE / 4,
                                                  arcade.color.BLACK)
                    else:
                        adjacent_mines = self.count_adjacent_mines(row, col)
                        if adjacent_mines > 0:
                            arcade.draw_text(
                                str(adjacent_mines),
                                cell_left + CELL_SIZE / 2,
                                cell_bottom + CELL_SIZE / 2,
                                arcade.color.BLUE,
                                16,
                                anchor_x="center",
                                anchor_y="center",
                            )
                else:
                    if (row, col) in self.flagged_cells:
                        arcade.draw_text(
                            "F",
                            cell_left + CELL_SIZE / 2,
                            cell_bottom + CELL_SIZE / 2,
                            arcade.color.RED,
                            18,
                            anchor_x="center",
                            anchor_y="center",
                        )

        arcade.draw_text(f"Мин осталось: {self.total_mines}", BOARD_LEFT + BOARD_WIDTH + 20, BOARD_BOTTOM + BOARD_HEIGHT - 20,
                         arcade.color.WHITE, 16)

        if self.game_start_time:
            arcade.draw_text(
                f"Time: {int(self.elapsed_time)}s",
                BOARD_LEFT + BOARD_WIDTH + 20,
                BOARD_BOTTOM + BOARD_HEIGHT - 50,
                arcade.color.LIGHT_GRAY,
                14
            )

        arcade.draw_text(
            "Левый клик - открыть / Правый клик - флаг. R - перезапуск, ESC - выход",
            BOARD_LEFT,
            12,
            arcade.color.LIGHT_GRAY,
            12,
        )

        if self.is_game_over:
            result_text = "ВЫ ВЫИГРАЛИ!" if self.is_win else "BOOM! ТЫ ПРОИГРАЛ"
            arcade.draw_lbwh_rectangle_filled(BOARD_LEFT + BOARD_WIDTH / 2 - 200, BOARD_BOTTOM + BOARD_HEIGHT / 2 - 40,
                                              400, 80, (0, 0, 0, 200))
            arcade.draw_text(result_text, BOARD_LEFT + BOARD_WIDTH / 2, BOARD_BOTTOM + BOARD_HEIGHT / 2 + 8,
                             arcade.color.GOLD, 28, anchor_x="center")
            arcade.draw_text(
                "R - перезапуск, ESC - выход",
                BOARD_LEFT + BOARD_WIDTH / 2,
                BOARD_BOTTOM + BOARD_HEIGHT / 2 - 18,
                arcade.color.LIGHT_GRAY,
                12,
                anchor_x="center",
            )

    def on_update(self, delta_time):
        if self.game_start_time and not self.is_game_over:
            self.elapsed_time += delta_time

    def on_mouse_press(self, mouse_x, mouse_y, mouse_button, modifiers):
        if self.is_game_over:
            return

        if not (
                BOARD_LEFT <= mouse_x <= BOARD_LEFT + BOARD_WIDTH and BOARD_BOTTOM <= mouse_y <= BOARD_BOTTOM + BOARD_HEIGHT):
            return

        column_index = int((mouse_x - BOARD_LEFT) // CELL_SIZE)
        row_index = int((mouse_y - BOARD_BOTTOM) // CELL_SIZE)

        if mouse_button == arcade.MOUSE_BUTTON_RIGHT:
            if (row_index, column_index) not in self.revealed_cells:
                if (row_index, column_index) in self.flagged_cells:
                    self.flagged_cells.remove((row_index, column_index))
                else:
                    self.flagged_cells.add((row_index, column_index))
            return

        if self.is_first_click:
            self.place_mines_safely((row_index, column_index))
            self.is_first_click = False
            self.game_start_time = time.time()
            self.elapsed_time = 0.0

        if (row_index, column_index) in self.flagged_cells:
            return

        if (row_index, column_index) in self.mine_positions:
            self.is_game_over = True
            self.is_win = False
            self.revealed_cells.update(self.mine_positions)
            return

        if (row_index, column_index) not in self.revealed_cells:
            if self.count_adjacent_mines(row_index, column_index) == 0:
                self.reveal_empty_area(row_index, column_index)
            else:
                self.revealed_cells.add((row_index, column_index))

        self.check_for_win()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            self.initialize_game()
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.return_view_cls())
