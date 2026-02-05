import arcade

TILE = 80
PIECE_SIZE = 60
BOARD = 8
SCREEN = TILE * BOARD

WHITE = 1
BLACK = -1


class ChessPiece(arcade.Sprite):
    def __init__(self, kind, player, row, col):
        img = f"assets/pieces/{'w' if player == WHITE else 'b'}{kind}.png"
        super().__init__(img, scale=PIECE_SIZE / TILE)
        self.kind = kind
        self.player = player
        self.row = row
        self.col = col
        self.update_pos()
        self.first_move = True

    def update_pos(self):
        self.center_x = self.col * TILE + TILE // 2
        self.center_y = (BOARD - 1 - self.row) * TILE + TILE // 2


class ChessGameView(arcade.View):
    def __init__(self, return_view_cls=None):
        super().__init__()
        self.return_view_cls = return_view_cls

        self.turn = WHITE
        self.selected = None
        self.pieces = arcade.SpriteList()
        self.move_sound = arcade.load_sound("assets/audio_on_move.wav")
        self.game_over = False
        self.winner = None
        self.moves = []
        self.check_king = None
        self.checkers = []

        self.en_passant = None
        self.promoting = None
        self.promo_options = ["Q", "R", "B", "N"]
        self.promo_rects = []
        self.promo_sprites = arcade.SpriteList()

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

        for r, c in self.moves:
            target = self.piece_at(r, c)
            x = c * TILE
            y = (BOARD - 1 - r) * TILE

            if self.selected and self.selected.kind == "P":
                dr = r - self.selected.row
                dc = c - self.selected.col
                dir = -1 if self.selected.player == WHITE else 1

                if dc == 0 and (dr == dir or (dr == 2 * dir and self.selected.first_move)) and not target:
                    arcade.draw_lbwh_rectangle_filled(x, y, TILE, TILE, (100, 255, 100, 100))
                elif abs(dc) == 1 and dr == dir:
                    if target or (self.en_passant and (r, c) == self.en_passant):
                        arcade.draw_lbwh_rectangle_outline(x, y, TILE, TILE, (255, 50, 50, 200), 2)
            else:
                if not target:
                    arcade.draw_lbwh_rectangle_filled(x, y, TILE, TILE, (100, 255, 100, 100))
                else:
                    arcade.draw_lbwh_rectangle_outline(x, y, TILE, TILE, (255, 50, 50, 200), 2)

        if self.en_passant and (self.en_passant in self.moves):
            r, c = self.en_passant
            x = c * TILE
            y = (BOARD - 1 - r) * TILE

            dash = 6
            gap = 4
            pos = 0

            while pos < TILE:
                arcade.draw_line(x + pos, y, x + min(pos + dash, TILE), y, (255, 165, 0, 220), 3)
                arcade.draw_line(x + pos, y + TILE, x + min(pos + dash, TILE), y + TILE, (255, 165, 0, 220), 3)
                arcade.draw_line(x, y + pos, x, y + min(pos + dash, TILE), (255, 165, 0, 220), 3)
                arcade.draw_line(x + TILE, y + pos, x + TILE, y + min(pos + dash, TILE), (255, 165, 0, 220), 3)
                pos += dash + gap

        if self.selected:
            arcade.draw_lbwh_rectangle_outline(
                self.selected.col * TILE,
                (BOARD - 1 - self.selected.row) * TILE,
                TILE,
                TILE,
                arcade.color.YELLOW,
                3,
            )

        if self.check_king:
            arcade.draw_lbwh_rectangle_outline(
                self.check_king.col * TILE,
                (BOARD - 1 - self.check_king.row) * TILE,
                TILE,
                TILE,
                arcade.color.RED,
                4
            )

            for piece in self.checkers:
                arcade.draw_lbwh_rectangle_filled(
                    piece.col * TILE,
                    (BOARD - 1 - piece.row) * TILE,
                    TILE,
                    TILE,
                    (255, 100, 100, 100)
                )
                arcade.draw_lbwh_rectangle_outline(
                    piece.col * TILE,
                    (BOARD - 1 - piece.row) * TILE,
                    TILE,
                    TILE,
                    (255, 50, 50, 220),
                    2
                )

        self.pieces.draw()

        if self.promoting:
            self.draw_promo_menu()

        if self.game_over:
            arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN, SCREEN, (0, 0, 0, 180))
            arcade.draw_text(
                f"ШАХ И МАТ!",
                SCREEN // 2,
                SCREEN // 2 + 40,
                arcade.color.GOLD,
                48,
                anchor_x="center",
                anchor_y="center",
                align="center",
            )
            arcade.draw_text(
                f"Победили {'БЕЛЫЕ' if self.winner == WHITE else 'ЧЁРНЫЕ'}",
                SCREEN // 2,
                SCREEN // 2 - 40,
                arcade.color.WHITE,
                36,
                anchor_x="center",
                anchor_y="center",
                align="center",
            )

    def draw_promo_menu(self):
        menu_width = TILE * len(self.promo_options)
        menu_height = TILE
        menu_x = (SCREEN - menu_width) // 2
        menu_y = (SCREEN - menu_height) // 2

        arcade.draw_lbwh_rectangle_filled(menu_x, menu_y, menu_width, menu_height, arcade.color.DARK_SLATE_GRAY)
        arcade.draw_lbwh_rectangle_outline(menu_x, menu_y, menu_width, menu_height, arcade.color.GOLD, 3)

        self.promo_rects = []
        self.promo_sprites = arcade.SpriteList()

        for i, piece in enumerate(self.promo_options):
            rect_x = menu_x + i * TILE
            rect = (rect_x, menu_y, TILE, TILE)
            self.promo_rects.append(rect)

            if hasattr(self, 'promo_hover') and self.promo_hover == i:
                arcade.draw_lbwh_rectangle_filled(rect_x, menu_y, TILE, TILE, arcade.color.LIGHT_GRAY)

            sprite = arcade.Sprite(
                f"assets/pieces/{'w' if self.promoting.player == WHITE else 'b'}{piece}.png",
                scale=PIECE_SIZE / TILE
            )
            sprite.center_x = rect_x + TILE // 2
            sprite.center_y = menu_y + TILE // 2
            self.promo_sprites.append(sprite)

        self.promo_sprites.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if self.return_view_cls:
                self.window.show_view(self.return_view_cls())

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_over:
            return

        if self.promoting:
            self.handle_promo_click(x, y)
            return

        c = x // TILE
        r = BOARD - 1 - (y // TILE)
        piece = self.piece_at(r, c)

        if self.selected:
            if (r, c) in self.moves:
                self.make_move(r, c)
            else:
                if piece and piece.player == self.turn:
                    self.selected = piece
                    self.moves = self.get_moves(piece)
                else:
                    self.selected = None
                    self.moves = []
        else:
            if piece and piece.player == self.turn:
                self.selected = piece
                self.moves = self.get_moves(piece)

    def handle_promo_click(self, x, y):
        for i, rect in enumerate(self.promo_rects):
            rect_x, rect_y, width, height = rect
            if rect_x <= x <= rect_x + width and rect_y <= y <= rect_y + height:
                self.promoting.kind = self.promo_options[i]
                self.promoting.texture = arcade.load_texture(
                    f"assets/pieces/{'w' if self.promoting.player == WHITE else 'b'}{self.promo_options[i]}.png"
                )
                self.promoting.scale = PIECE_SIZE / TILE

                self.promo_sprites = arcade.SpriteList()

                self.turn *= -1
                self.promoting = None
                self.promo_rects = []

                self.check_king = None
                self.checkers = []
                if self.in_check(self.turn):
                    self.update_check()
                    if self.checkmate(self.turn):
                        self.game_over = True
                        self.winner = -self.turn
                break

    def make_move(self, r, c):
        target = self.piece_at(r, c)

        en_passant_cap = False
        if self.en_passant and (r, c) == self.en_passant and self.selected.kind == "P":
            cap_row = self.selected.row
            cap_col = c
            cap_pawn = self.piece_at(cap_row, cap_col)
            if cap_pawn:
                self.pieces.remove(cap_pawn)
                en_passant_cap = True

        old_r, old_c = self.selected.row, self.selected.col
        moving_pawn = (self.selected.kind == "P")

        if target and not en_passant_cap:
            self.pieces.remove(target)
            arcade.play_sound(self.move_sound)
        else:
            arcade.play_sound(self.move_sound)

        self.selected.row = r
        self.selected.col = c
        self.selected.update_pos()

        if self.selected.kind == "K" and abs(c - old_c) == 2:
            if c > old_c:
                rook_c = 7
                new_rook_c = c - 1
            else:
                rook_c = 0
                new_rook_c = c + 1

            rook = self.piece_at(r, rook_c)
            if rook:
                rook.col = new_rook_c
                rook.update_pos()
                rook.first_move = False

        new_en_passant = None
        if moving_pawn and abs(r - old_r) == 2:
            en_passant_r = (old_r + r) // 2
            new_en_passant = (en_passant_r, c)

        pawn_promo = False
        if self.selected.kind == "P":
            self.selected.first_move = False
            if (self.selected.player == WHITE and r == 0) or (self.selected.player == BLACK and r == 7):
                pawn_promo = True
                self.promoting = self.selected

        if self.selected.kind in ["K", "R"]:
            self.selected.first_move = False

        if self.in_check(self.selected.player):
            self.selected.row = old_r
            self.selected.col = old_c
            self.selected.update_pos()
            if target and not en_passant_cap:
                self.pieces.append(target)
            if en_passant_cap:
                cap_pawn = ChessPiece("P", -self.selected.player, old_r, c)
                cap_pawn.first_move = False
                self.pieces.append(cap_pawn)
            if self.selected.kind == "K" and abs(c - old_c) == 2:
                if c > old_c:
                    rook_c = 7
                    old_rook_c = c - 1
                else:
                    rook_c = 0
                    old_rook_c = c + 1

                rook = self.piece_at(r, old_rook_c)
                if rook:
                    rook.col = rook_c
                    rook.update_pos()
                    rook.first_move = True
            return

        if pawn_promo:
            self.en_passant = None
            return

        self.turn *= -1
        self.en_passant = new_en_passant
        self.check_king = None
        self.checkers = []

        if self.in_check(self.turn):
            self.update_check()
            if self.checkmate(self.turn):
                self.game_over = True
                self.winner = -self.turn

        self.selected = None
        self.moves = []

    def update_check(self):
        self.check_king = self.find_king(self.turn)
        self.checkers = []

        if self.check_king:
            for piece in self.pieces:
                if piece.player != self.turn and self.can_move(piece, self.check_king.row, self.check_king.col, False):
                    self.checkers.append(piece)

    def piece_at(self, r, c):
        for p in self.pieces:
            if p.row == r and p.col == c:
                return p
        return None

    def find_king(self, color):
        for p in self.pieces:
            if p.kind == "K" and p.player == color:
                return p
        return None

    def in_check(self, color):
        king = self.find_king(color)
        if not king:
            return True

        for piece in self.pieces:
            if piece.player != color and self.can_move(piece, king.row, king.col, False):
                return True
        return False

    def get_moves(self, piece):
        moves = []
        for r in range(BOARD):
            for c in range(BOARD):
                if self.can_move(piece, r, c):
                    old_r, old_c = piece.row, piece.col
                    target = self.piece_at(r, c)

                    en_passant_move = (piece.kind == "P" and self.en_passant and (r, c) == self.en_passant)

                    piece.row, piece.col = r, c
                    removed = None
                    if target and not en_passant_move:
                        self.pieces.remove(target)
                        removed = target

                    if en_passant_move:
                        cap_r = old_r
                        cap_c = c
                        cap_pawn = self.piece_at(cap_r, cap_c)
                        if cap_pawn:
                            self.pieces.remove(cap_pawn)
                            removed = cap_pawn

                    if piece.kind == "K" and abs(c - old_c) == 2:
                        if c > old_c:
                            rook_c = 7
                            new_rook_c = c - 1
                        else:
                            rook_c = 0
                            new_rook_c = c + 1

                        rook = self.piece_at(old_r, rook_c)
                        if rook:
                            rook.col = new_rook_c
                            temp_removed = None
                            if self.piece_at(old_r, new_rook_c) and self.piece_at(old_r, new_rook_c) != rook:
                                temp_removed = self.piece_at(old_r, new_rook_c)
                                self.pieces.remove(temp_removed)

                    if not self.in_check(piece.player):
                        moves.append((r, c))

                    piece.row, piece.col = old_r, old_c
                    if removed:
                        self.pieces.append(removed)

                    if piece.kind == "K" and abs(c - old_c) == 2:
                        if c > old_c:
                            rook_c = 7
                            new_rook_c = c - 1
                        else:
                            rook_c = 0
                            new_rook_c = c + 1

                        rook = self.piece_at(old_r, new_rook_c)
                        if rook and rook.kind == "R":
                            rook.col = rook_c
                            rook.update_pos()
                        if temp_removed:
                            self.pieces.append(temp_removed)

        return moves

    def can_move(self, piece, r, c, check=True):
        if not (0 <= r < BOARD and 0 <= c < BOARD):
            return False

        target = self.piece_at(r, c)
        if target and target.player == piece.player:
            return False

        dr = r - piece.row
        dc = c - piece.col

        if piece.kind == "P":
            dir = -1 if piece.player == WHITE else 1

            if dc == 0 and dr == dir and not target:
                return True

            if dc == 0 and dr == 2 * dir and piece.first_move:
                mid_r = piece.row + dir
                if not self.piece_at(mid_r, piece.col) and not target:
                    return True

            if abs(dc) == 1 and dr == dir and target:
                return True

            if abs(dc) == 1 and dr == dir and self.en_passant and (r, c) == self.en_passant:
                enemy_r = piece.row
                enemy_c = c
                enemy = self.piece_at(enemy_r, enemy_c)
                if enemy and enemy.kind == "P" and enemy.player != piece.player:
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
                if self.can_castle(piece, dc > 0):
                    if dc > 0:
                        if self.piece_at(piece.row, 5) or self.piece_at(piece.row, 6):
                            return False
                    else:
                        if self.piece_at(piece.row, 1) or self.piece_at(piece.row, 2) or self.piece_at(piece.row, 3):
                            return False

                    if self.in_check(piece.player):
                        return False

                    if dc > 0:
                        for col in range(piece.col + 1, 7):
                            temp_r = piece.row
                            temp_c = col
                            if self.square_attacked(temp_r, temp_c, piece.player):
                                return False
                    else:
                        for col in range(piece.col - 1, 0, -1):
                            temp_r = piece.row
                            temp_c = col
                            if self.square_attacked(temp_r, temp_c, piece.player):
                                return False

                    return True
            return False

        return False

    def square_attacked(self, row, col, color):
        for piece in self.pieces:
            if piece.player != color:
                if self.can_move(piece, row, col, False):
                    return True
        return False

    def clear_path(self, sr, sc, r, c):
        dr = r - sr
        dc = c - sc
        step_r = (dr > 0) - (dr < 0) if dr != 0 else 0
        step_c = (dc > 0) - (dc < 0) if dc != 0 else 0

        rr, cc = sr + step_r, sc + step_c
        while (rr, cc) != (r, c):
            if self.piece_at(rr, cc):
                return False
            rr += step_r
            cc += step_c
        return True

    def can_castle(self, king, kingside):
        row = king.row
        rook_col = 7 if kingside else 0

        rook = self.piece_at(row, rook_col)
        if not rook or rook.kind != "R" or not rook.first_move:
            return False

        start_col = min(king.col, rook_col) + 1
        end_col = max(king.col, rook_col)

        for col in range(start_col, end_col):
            if self.piece_at(row, col):
                return False

        return True

    def checkmate(self, color):
        if not self.in_check(color):
            return False

        for piece in self.pieces:
            if piece.player == color:
                if self.get_moves(piece):
                    return False

        return True
