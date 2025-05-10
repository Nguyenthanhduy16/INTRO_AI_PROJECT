import pygame
import board, pieces, ai
from move import Move

WIDTH, HEIGHT = 640, 640
SQUARE_SIZE = WIDTH // 8

IMAGES = {}

def load_images():
    types = ['p', 'r', 'n', 'b', 'q', 'k']
    colors = ['w', 'b']
    for color in colors:
        for t in types:
            name = f"{color}{t}"
            IMAGES[name] = pygame.transform.scale(
                pygame.image.load(f"assets/{name}.png"),
                (SQUARE_SIZE, SQUARE_SIZE)
            )

def draw_board(screen):
    colors = [pygame.Color(235, 235, 208), pygame.Color(119, 148, 85)]
    for y in range(8):
        for x in range(8):
            color = colors[(x + y) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(x*SQUARE_SIZE, y*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(screen, board_state, dragging_piece=None, dragging_pos=None):
    for x in range(8):
        for y in range(8):
            piece = board_state.chesspieces[x][y]
            if piece != 0:
                if dragging_piece and piece == dragging_piece:
                    continue  # tạm thời không vẽ quân đang kéo
                key = ('w' if piece.color == pieces.Piece.WHITE else 'b') + piece.piece_type.lower()
                screen.blit(IMAGES[key], pygame.Rect(x*SQUARE_SIZE, y*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # Vẽ quân đang kéo nếu có
    if dragging_piece and dragging_pos:
        key = ('w' if dragging_piece.color == pieces.Piece.WHITE else 'b') + dragging_piece.piece_type.lower()
        mx, my = dragging_pos
        screen.blit(IMAGES[key], (mx - SQUARE_SIZE//2, my - SQUARE_SIZE//2))

def get_square_under_mouse(pos):
    x, y = pos
    return x // SQUARE_SIZE, y // SQUARE_SIZE

def animate_move(screen, piece, from_pos, to_pos):
    start_time = pygame.time.get_ticks()
    duration = 200  # milliseconds
    start_x = from_pos[0] * SQUARE_SIZE
    start_y = from_pos[1] * SQUARE_SIZE
    end_x = to_pos[0] * SQUARE_SIZE
    end_y = to_pos[1] * SQUARE_SIZE
    clock = pygame.time.Clock()

    while True:
        now = pygame.time.get_ticks()
        t = min(1.0, (now - start_time) / duration)
        current_x = start_x + (end_x - start_x) * t
        current_y = start_y + (end_y - start_y) * t

        draw_board(screen)
        draw_pieces(screen, game_board, piece, (current_x + SQUARE_SIZE//2, current_y + SQUARE_SIZE//2))
        pygame.display.flip()
        clock.tick(60)

        if t >= 1.0:
            break

def start_game():
    global game_board  # Needed for animate_move
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess GUI")
    clock = pygame.time.Clock()

    load_images()
    game_board = board.Board.new()
    selected = None
    player_turn = True
    move_hints = []

    dragging = False
    dragging_piece = None
    dragging_from = None

    running = True
    while running:
        draw_board(screen)
        for move in move_hints:
            pygame.draw.circle(
                screen, pygame.Color('green'),
                (move.xto * SQUARE_SIZE + SQUARE_SIZE // 2, move.yto * SQUARE_SIZE + SQUARE_SIZE // 2), 10
            )
        draw_pieces(screen, game_board, dragging_piece, pygame.mouse.get_pos() if dragging else None)

        if selected:
            x, y = selected
            pygame.draw.rect(screen, pygame.Color('blue'), (x*SQUARE_SIZE, y*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and player_turn:
                x, y = get_square_under_mouse(pygame.mouse.get_pos())
                piece = game_board.get_piece(x, y)
                if piece and piece.color == pieces.Piece.WHITE:
                    selected = (x, y)
                    move_hints = [m for m in game_board.get_possible_moves(pieces.Piece.WHITE) if m.xfrom == x and m.yfrom == y]
                    dragging = True
                    dragging_piece = piece
                    dragging_from = (x, y)

            elif event.type == pygame.MOUSEBUTTONUP and player_turn and dragging:
                dragging = False
                dragging_piece = None
                to_x, to_y = get_square_under_mouse(pygame.mouse.get_pos())
                if dragging_from:
                    move = Move(dragging_from[0], dragging_from[1], to_x, to_y)
                    possible = game_board.get_possible_moves(pieces.Piece.WHITE)
                    valid = False
                    for m in possible:
                        if move.equals(m):
                            animate_move(screen, game_board.get_piece(m.xfrom, m.yfrom), (m.xfrom, m.yfrom), (m.xto, m.yto))
                            game_board.perform_move(m)
                            player_turn = False
                            valid = True
                            break
                    selected = None if valid else (to_x, to_y)
                    move_hints = []

                    if not player_turn:
                        if not game_board.get_possible_moves(pieces.Piece.BLACK):
                            if game_board.is_check(pieces.Piece.BLACK):
                                print("Trắng thắng (Chiếu bí)")
                            else:
                                print("Hòa (Stalemate)")
                            running = False

        if not player_turn and running:
            ai_move = ai.AI.get_ai_move(game_board, [])
            if ai_move:
                animate_move(screen, game_board.get_piece(ai_move.xfrom, ai_move.yfrom), (ai_move.xfrom, ai_move.yfrom), (ai_move.xto, ai_move.yto))
                game_board.perform_move(ai_move)
            player_turn = True
            move_hints = []

            if not game_board.get_possible_moves(pieces.Piece.WHITE):
                if game_board.is_check(pieces.Piece.WHITE):
                    print("Đen thắng (Chiếu bí)")
                else:
                    print("Hòa (Stalemate)")
                running = False

        clock.tick(60)

    pygame.quit()
