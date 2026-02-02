import arcade

TILE = 80
PIECE_SIZE = 60
BOARD = 8
SCREEN = TILE * BOARD

WHITE = 1
BLACK = -1


class ChessGameView(arcade.Sprite):
    def __init__(self, kind, player, row, col):
        img = f"assets/pieces/{'w' if player == WHITE else 'b'}{kind}.png"
        super().__init__(img, scale=PIECE_SIZE / TILE)
        self.kind = kind
        self.player = player
        self.row = row
        self.col = col
        self.update_position()
        self.first_move = True

    def update_position(self):
        self.center_x = self.col * TILE + TILE // 2
        self.center_y = (BOARD - 1 - self.row) * TILE + TILE // 2


class ChessGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.turn = WHITE
        self.selected_piece = None
        self.pieces = arcade.SpriteList()
        self.move_sound = arcade.load_sound("assets/audio_on_move.wav")
        self.game_over = False
        self.winner = None
        self.valid_moves = []
        self.check_king = None
        self.setup_board()

    def setup_board(self):
        self.pieces = arcade.SpriteList()
        for i in range(BOARD):
            self.pieces.append(ChessPiece("P", BLACK, 1, i))
            self.pieces.append(ChessPiece("P", WHITE, 6, i))
        order = ["R", "N", "B", "Q", "K", "B", "N", "R"]
        for i, kind in enumerate(order):
            self.pieces.append(ChessPiece(kind, BLACK, 0, i))
            self.pieces.append(ChessPiece(kind, WHITE, 7, i))

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()

        for r in range(BOARD):
            for c in range(BOARD):
                color = arcade.color.BEIGE if (r + c) % 2 == 0 else arcade.color.BROWN
                arcade.draw_lbwh_rectangle_filled(c * TILE, (BOARD - 1 - r) * TILE, TILE, TILE, color)

        for r, c in self.valid_moves:
            target = self.get_piece_at(r, c)
            color = arcade.color.LIGHT_GREEN if not target else arcade.color.RED
            arcade.draw_lbwh_rectangle_filled(c * TILE, (BOARD - 1 - r) * TILE, TILE, TILE, color)

        if self.selected_piece:
            arcade.draw_lbwh_rectangle_outline(
                self.selected_piece.col * TILE,
                (BOARD - 1 - self.selected_piece.row) * TILE,
                TILE, TILE,
                arcade.color.YELLOW, 3
            )

        if self.check_king:
            arcade.draw_lbwh_rectangle_outline(
                self.check_king.col * TILE,
                (BOARD - 1 - self.check_king.row) * TILE,
                TILE, TILE,
                arcade.color.RED, 4
            )

        self.pieces.draw()

        if self.game_over:
            arcade.draw_lbwh_rectangle_filled(
                0, 0,
                SCREEN, SCREEN,
                (0, 0, 0, 180)
            )
            arcade.draw_text(
                f"ШАХ И МАТ!",
                SCREEN // 2, SCREEN // 2 + 40,
                arcade.color.GOLD, 48,
                anchor_x="center", anchor_y="center", align="center"
            )
            arcade.draw_text(
                f"Победили {'БЕЛЫЕ' if self.winner == WHITE else 'ЧЁРНЫЕ'}",
                SCREEN // 2, SCREEN // 2 - 40,
                arcade.color.WHITE, 36,
                anchor_x="center", anchor_y="center", align="center"
            )
            arcade.draw_text(
                "Нажмите ESC для выхода",
                SCREEN // 2, 50,
                arcade.color.LIGHT_GRAY, 24,
                anchor_x="center", anchor_y="center", align="center"
            )

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            if self.game_over:
                arcade.close_window()
            else:
                self.selected_piece = None
                self.valid_moves = []

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_over:
            return

        c = x // TILE
        r = BOARD - 1 - (y // TILE)
        piece = self.get_piece_at(r, c)

        if self.selected_piece:
            if (r, c) in self.valid_moves:
                self.make_move(r, c)
            else:
                if piece and piece.player == self.turn:
                    self.selected_piece = piece
                    self.valid_moves = self.get_valid_moves(piece)
                else:
                    self.selected_piece = None
                    self.valid_moves = []
        else:
            if piece and piece.player == self.turn:
                self.selected_piece = piece
                self.valid_moves = self.get_valid_moves(piece)

    def make_move(self, r, c):
        target = self.get_piece_at(r, c)

        old_row, old_col = self.selected_piece.row, self.selected_piece.col

        if target:
            self.pieces.remove(target)
            arcade.play_sound(self.move_sound)
        else:
            arcade.play_sound(self.move_sound)

        self.selected_piece.row = r
        self.selected_piece.col = c
        self.selected_piece.update_position()

        if self.selected_piece.kind == "P":
            self.selected_piece.first_move = False
            if (self.selected_piece.player == WHITE and r == 0) or \
                    (self.selected_piece.player == BLACK and r == 7):
                self.selected_piece.kind = "Q"
                self.selected_piece.texture = arcade.load_texture(
                    f"assets/pieces/{'w' if self.selected_piece.player == WHITE else 'b'}Q.png"
                )
                self.selected_piece.scale = PIECE_SIZE / TILE

        if self.is_in_check(self.selected_piece.player):
            self.selected_piece.row = old_row
            self.selected_piece.col = old_col
            self.selected_piece.update_position()
            if target:
                self.pieces.append(target)
            return

        self.turn *= -1
        self.check_king = None

        if self.is_in_check(self.turn):
            self.check_king = self.find_king(self.turn)
            if self.is_checkmate(self.turn):
                self.game_over = True
                self.winner = -self.turn

        self.selected_piece = None
        self.valid_moves = []

    def get_piece_at(self, r, c):
        for p in self.pieces:
            if p.row == r and p.col == c:
                return p
        return None

    def find_king(self, color):
        for p in self.pieces:
            if p.kind == "K" and p.player == color:
                return p
        return None

    def is_in_check(self, color):
        king = self.find_king(color)
        if not king:
            return True

        for piece in self.pieces:
            if piece.player != color and self.is_legal_move(piece, king.row, king.col, check_check=False):
                return True
        return False

    def get_valid_moves(self, piece):
        moves = []
        for r in range(BOARD):
            for c in range(BOARD):
                if self.is_legal_move(piece, r, c):
                    old_row, old_col = piece.row, piece.col
                    target = self.get_piece_at(r, c)

                    piece.row, piece.col = r, c
                    removed_piece = None
                    if target:
                        self.pieces.remove(target)
                        removed_piece = target

                    if not self.is_in_check(piece.player):
                        moves.append((r, c))

                    piece.row, piece.col = old_row, old_col
                    if removed_piece:
                        self.pieces.append(removed_piece)

        return moves

    def is_legal_move(self, piece, r, c, check_check=True):
        if not (0 <= r < BOARD and 0 <= c < BOARD):
            return False

        target = self.get_piece_at(r, c)
        if target and target.player == piece.player:
            return False

        dr = r - piece.row
        dc = c - piece.col

        if piece.kind == "P":
            direction = -1 if piece.player == WHITE else 1

            if dc == 0 and dr == direction and not target:
                return True

            if dc == 0 and dr == 2 * direction and piece.first_move:
                mid_r = piece.row + direction
                if not self.get_piece_at(mid_r, piece.col) and not target:
                    return True

            if abs(dc) == 1 and dr == direction and target:
                return True

            return False

        if piece.kind == "R":
            if dr == 0 or dc == 0:
                return self.clear_path(piece.row, piece.col, r, c)
            return False

        if piece.kind == "B":
            if abs(dr) == abs(dc):
                return self.clear_path(piece.row, piece.col, r, c)
            return False

        if piece.kind == "Q":
            if dr == 0 or dc == 0 or abs(dr) == abs(dc):
                return self.clear_path(piece.row, piece.col, r, c)
            return False

        if piece.kind == "N":
            return (abs(dr), abs(dc)) in [(1, 2), (2, 1)]

        if piece.kind == "K":
            if max(abs(dr), abs(dc)) == 1:
                return True
            if piece.first_move and dr == 0 and abs(dc) == 2:
                return self.can_castle(piece, dc > 0)
            return False

        return False

    def clear_path(self, sr, sc, r, c):
        dr = (r - sr)
        dc = (c - sc)
        step_r = (dr > 0) - (dr < 0) if dr != 0 else 0
        step_c = (dc > 0) - (dc < 0) if dc != 0 else 0

        rr, cc = sr + step_r, sc + step_c
        while (rr, cc) != (r, c):
            if self.get_piece_at(rr, cc):
                return False
            rr += step_r
            cc += step_c
        return True

    def can_castle(self, king, kingside):
        row = king.row
        rook_col = 7 if kingside else 0

        rook = self.get_piece_at(row, rook_col)
        if not rook or rook.kind != "R" or not rook.first_move:
            return False

        start_col = min(king.col, rook_col) + 1
        end_col = max(king.col, rook_col)

        for col in range(start_col, end_col):
            if self.get_piece_at(row, col):
                return False

        return True

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False

        for piece in self.pieces:
            if piece.player == color:
                if self.get_valid_moves(piece):
                    return False

        return True
