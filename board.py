import pieces
from move import Move

class Board:

    WIDTH = 8
    HEIGHT = 8

    def __init__(self, chesspieces, white_king_moved, black_king_moved):
        self.chesspieces = chesspieces
        self.white_king_moved = white_king_moved
        self.black_king_moved = black_king_moved
        self.en_passant_target = None  # To support en passant

    @classmethod
    def clone(cls, chessboard):
        chesspieces = [[0 for x in range(Board.WIDTH)] for y in range(Board.HEIGHT)]
        for x in range(Board.WIDTH):
            for y in range(Board.HEIGHT):
                piece = chessboard.chesspieces[x][y]
                if piece != 0:
                    chesspieces[x][y] = piece.clone()
        new_board = cls(chesspieces, chessboard.white_king_moved, chessboard.black_king_moved)
        new_board.en_passant_target = chessboard.en_passant_target
        return new_board

    @classmethod
    def new(cls):
        chess_pieces = [[0 for x in range(Board.WIDTH)] for y in range(Board.HEIGHT)]
        for x in range(Board.WIDTH):
            chess_pieces[x][Board.HEIGHT-2] = pieces.Pawn(x, Board.HEIGHT-2, pieces.Piece.WHITE)
            chess_pieces[x][1] = pieces.Pawn(x, 1, pieces.Piece.BLACK)

        chess_pieces[0][Board.HEIGHT-1] = pieces.Rook(0, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[Board.WIDTH-1][Board.HEIGHT-1] = pieces.Rook(Board.WIDTH-1, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[0][0] = pieces.Rook(0, 0, pieces.Piece.BLACK)
        chess_pieces[Board.WIDTH-1][0] = pieces.Rook(Board.WIDTH-1, 0, pieces.Piece.BLACK)

        chess_pieces[1][Board.HEIGHT-1] = pieces.Knight(1, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[Board.WIDTH-2][Board.HEIGHT-1] = pieces.Knight(Board.WIDTH-2, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[1][0] = pieces.Knight(1, 0, pieces.Piece.BLACK)
        chess_pieces[Board.WIDTH-2][0] = pieces.Knight(Board.WIDTH-2, 0, pieces.Piece.BLACK)

        chess_pieces[2][Board.HEIGHT-1] = pieces.Bishop(2, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[Board.WIDTH-3][Board.HEIGHT-1] = pieces.Bishop(Board.WIDTH-3, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[2][0] = pieces.Bishop(2, 0, pieces.Piece.BLACK)
        chess_pieces[Board.WIDTH-3][0] = pieces.Bishop(Board.WIDTH-3, 0, pieces.Piece.BLACK)

        chess_pieces[4][Board.HEIGHT-1] = pieces.King(4, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[3][Board.HEIGHT-1] = pieces.Queen(3, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[4][0] = pieces.King(4, 0, pieces.Piece.BLACK)
        chess_pieces[3][0] = pieces.Queen(3, 0, pieces.Piece.BLACK)

        return cls(chess_pieces, False, False)

    def get_possible_moves(self, color):
        moves = []
        for x in range(Board.WIDTH):
            for y in range(Board.HEIGHT):
                piece = self.chesspieces[x][y]
                if piece != 0 and piece.color == color:
                    for move in piece.get_possible_moves(self):
                        copy = Board.clone(self)
                        copy.perform_move(move)
                        if not copy.is_check(color):
                            moves.append(move)
        return moves

    def perform_move(self, move: Move):
        piece = self.chesspieces[move.xfrom][move.yfrom]

        # En passant capture
        if isinstance(piece, pieces.Pawn) and self.en_passant_target == (move.xto, move.yto):
            self.chesspieces[move.xto][move.yfrom] = 0

        # Move piece
        self.move_piece(piece, move.xto, move.yto)

        # Pawn promotion
        if isinstance(piece, pieces.Pawn) and (piece.y == 0 or piece.y == Board.HEIGHT-1):
            self.chesspieces[piece.x][piece.y] = pieces.Queen(piece.x, piece.y, piece.color)

        # Set en passant target
        if isinstance(piece, pieces.Pawn) and abs(move.yto - move.yfrom) == 2:
            self.en_passant_target = (piece.x, (move.yto + move.yfrom)//2)
        else:
            self.en_passant_target = None

        # Castling: handle rook
        if isinstance(piece, pieces.King):
            # mark king moved
            if piece.color == pieces.Piece.WHITE:
                self.white_king_moved = True
            else:
                self.black_king_moved = True

            dx = move.xto - move.xfrom
            if dx == 2:  # kingside
                rook = self.chesspieces[move.xto+1][move.yto]
                self.move_piece(rook, move.xto-1, move.yto)
            elif dx == -2:  # queenside
                rook = self.chesspieces[move.xto-2][move.yto]
                self.move_piece(rook, move.xto+1, move.yto)

    def move_piece(self, piece, xto, yto):
        self.chesspieces[piece.x][piece.y] = 0
        piece.x = xto
        piece.y = yto
        self.chesspieces[xto][yto] = piece

    def is_check(self, color):
        other_color = pieces.Piece.BLACK if color == pieces.Piece.WHITE else pieces.Piece.WHITE

        for x in range(Board.WIDTH):
            for y in range(Board.HEIGHT):
                attacker = self.chesspieces[x][y]
                if attacker != 0 and attacker.color == other_color:
                    for move in attacker.get_possible_moves(self):
                        if self.get_piece(move.xto, move.yto) != 0 and self.get_piece(move.xto, move.yto).piece_type == pieces.King.PIECE_TYPE:
                            if self.get_piece(move.xto, move.yto).color == color:
                                return True
        return False

    def get_piece(self, x, y):
        if not self.in_bounds(x, y):
            return 0
        return self.chesspieces[x][y]

    def in_bounds(self, x, y):
        return 0 <= x < Board.WIDTH and 0 <= y < Board.HEIGHT

    def to_string(self):
        string = "    A  B  C  D  E  F  G  H\n"
        string += "    -----------------------\n"
        for y in range(Board.HEIGHT):
            string += str(8 - y) + " | "
            for x in range(Board.WIDTH):
                piece = self.chesspieces[x][y]
                if piece != 0:
                    string += piece.to_string()
                else:
                    string += ".. "
            string += "\n"
        return string + "\n"
