import arcade

TILE = 80
PIECE_SIZE = 60
BOARD = 8
SCREEN = TILE * BOARD

WHITE = 1
BLACK = -1


class ChessGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.board = self.create_board()
        self.turn = WHITE
        self.selected = None
        self.textures = self.load_textures()
        self.move_sound = arcade.load_sound("assets/audio_on_move.wav")
        self.game_over = False
        self.winner = None

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def create_board(self):
        b = [[None] * BOARD for _ in range(BOARD)]
        for i in range(BOARD):
            b[1][i] = ("P", BLACK)
            b[6][i] = ("P", WHITE)
        order = ["R", "N", "B", "Q", "K", "B", "N", "R"]
        for i, p in enumerate(order):
            b[0][i] = (p, BLACK)
            b[7][i] = (p, WHITE)
        return b

    def load_textures(self):
        tex = {}
        for c in ["w", "b"]:
            for p in ["P", "R", "N", "B", "Q", "K"]:
                tex[(p, WHITE if c == "w" else BLACK)] = arcade.load_texture(f"assets/pieces/{c}{p}.png")
        return tex

    def on_draw(self):
        self.clear()

        # доска
        for r in range(BOARD):
            for c in range(BOARD):
                color = arcade.color.BEIGE if (r + c) % 2 == 0 else arcade.color.BROWN
                arcade.draw_lbwh_rectangle_filled(c * TILE, (BOARD - 1 - r) * TILE, TILE, TILE, color)

        # фигуры
        for r in range(BOARD):
            for c in range(BOARD):
                piece = self.board[r][c]
                if piece:
                    tex = self.textures[piece]
                    arcade.draw_texture_rectangle(
                        c * TILE + TILE // 2,
                        (BOARD - 1 - r) * TILE + TILE // 2,
                        PIECE_SIZE, PIECE_SIZE,
                        tex
                    )

        # выделение выбранной клетки
        if self.selected:
            r, c = self.selected
            arcade.draw_lbwh_rectangle_outline(c * TILE, (BOARD - 1 - r) * TILE, TILE, TILE, arcade.color.RED, 3)

        # сообщение о конце игры
        if self.game_over:
            arcade.draw_text(
                f"МАТ! Победили {'белые' if self.winner == WHITE else 'чёрные'}",
                SCREEN // 2, SCREEN // 2,
                arcade.color.WHITE, 32,
                anchor_x="center"
            )

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_over:
            return

        c = x // TILE
        r = BOARD - 1 - (y // TILE)
        if not (0 <= r < BOARD and 0 <= c < BOARD):
            return

        piece = self.board[r][c]

        if self.selected:
            sr, sc = self.selected
            if self.is_legal_move(sr, sc, r, c):
                self.board[r][c] = self.board[sr][sc]
                self.board[sr][sc] = None
                arcade.play_sound(self.move_sound)
                self.turn *= -1
                if self.is_checkmate(self.turn):
                    self.game_over = True
                    self.winner = -self.turn
            self.selected = None
        else:
            if piece and piece[1] == self.turn:
                self.selected = (r, c)

    def is_legal_move(self, sr, sc, r, c):
        piece, color = self.board[sr][sc]
        target = self.board[r][c]
        if target and target[1] == color:
            return False

        dr = r - sr
        dc = c - sc

        if piece == "P":
            dir = -1 if color == WHITE else 1
            if dc == 0 and dr == dir and not target:
                return True
            if abs(dc) == 1 and dr == dir and target:
                return True

        if piece == "R":
            if dr == 0 or dc == 0:
                return self.clear_path(sr, sc, r, c)

        if piece == "B":
            if abs(dr) == abs(dc):
                return self.clear_path(sr, sc, r, c)

        if piece == "Q":
            if dr == 0 or dc == 0 or abs(dr) == abs(dc):
                return self.clear_path(sr, sc, r, c)

        if piece == "N":
            return (abs(dr), abs(dc)) in [(1, 2), (2, 1)]

        if piece == "K":
            return max(abs(dr), abs(dc)) == 1

        return False

    def clear_path(self, sr, sc, r, c):
        dr = (r - sr)
        dc = (c - sc)
        step_r = (dr > 0) - (dr < 0)
        step_c = (dc > 0) - (dc < 0)
        rr, cc = sr + step_r, sc + step_c
        while (rr, cc) != (r, c):
            if self.board[rr][cc]:
                return False
            rr += step_r
            cc += step_c
        return True

    def is_checkmate(self, color):
        king = None
        for r in range(BOARD):
            for c in range(BOARD):
                if self.board[r][c] == ("K", color):
                    king = (r, c)
        if not king:
            return True

        for r in range(BOARD):
            for c in range(BOARD):
                p = self.board[r][c]
                if p and p[1] == -color:
                    if self.is_legal_move(r, c, *king):
                        return True
        return False
