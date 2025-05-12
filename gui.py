import pygame
from board import Board
import pieces
import ai
from move import Move   

# Constants
WIDTH, HEIGHT = 640, 640
SQUARE_SIZE = WIDTH // 8
FPS = 60
IMAGES = {}


def load_images():
    types = ['p', 'r', 'n', 'b', 'q', 'k']
    colors = ['w', 'b']
    for color in colors:
        for t in types:
            name = f"{color}{t}"
            img = pygame.image.load(f"assets/{name}.png").convert_alpha()
            IMAGES[name] = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))


def draw_board(screen):
    colors = [pygame.Color(235, 235, 208), pygame.Color(119, 148, 85)]
    for y in range(8):
        for x in range(8):
            pygame.draw.rect(
                screen,
                colors[(x + y) % 2],
                pygame.Rect(x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            )


def draw_pieces(screen, board_state, exclude_piece=None, dragging_pos=None):
    for x in range(8):
        for y in range(8):
            piece = board_state.get_piece(x, y)
            if piece and piece is not exclude_piece:
                key = ('w' if piece.color == pieces.Piece.WHITE else 'b') + piece.piece_type.lower()
                screen.blit(IMAGES[key], (x * SQUARE_SIZE, y * SQUARE_SIZE))
    if exclude_piece and dragging_pos:
        mx, my = dragging_pos
        key = ('w' if exclude_piece.color == pieces.Piece.WHITE else 'b') + exclude_piece.piece_type.lower()
        screen.blit(IMAGES[key], (mx - SQUARE_SIZE // 2, my - SQUARE_SIZE // 2))


def animate_move(screen, clock, board_state, piece, from_pos, to_pos):
    sx, sy = from_pos[0] * SQUARE_SIZE, from_pos[1] * SQUARE_SIZE
    ex, ey = to_pos[0] * SQUARE_SIZE, to_pos[1] * SQUARE_SIZE
    start_time = pygame.time.get_ticks()
    duration = 200
    captured = board_state.get_piece(to_pos[0], to_pos[1])

    while True:
        now = pygame.time.get_ticks()
        t = min(1.0, (now - start_time) / duration)
        cx = sx + (ex - sx) * t
        cy = sy + (ey - sy) * t

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                return

        draw_board(screen)
        draw_pieces(screen, board_state, exclude_piece=piece)
        if captured:
            surf = IMAGES[('w' if captured.color == pieces.Piece.WHITE else 'b') + captured.piece_type.lower()].copy()
            surf.set_alpha(int(255 * (1 - t)))
            screen.blit(surf, (to_pos[0] * SQUARE_SIZE, to_pos[1] * SQUARE_SIZE))
        key = ('w' if piece.color == pieces.Piece.WHITE else 'b') + piece.piece_type.lower()
        screen.blit(IMAGES[key], (cx, cy))

        pygame.display.flip()
        clock.tick(FPS)
        if t >= 1.0:
            break


def get_square_under_mouse(pos):
    return pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE


def start_game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Engine")
    clock = pygame.time.Clock()
    load_images()

    game_board = Board.new()
    selected = None
    move_hints = []
    player_turn = True
    dragging = False
    drag_piece = None
    drag_from = None

    running = True
    while running:
        draw_board(screen)
        for hint in move_hints:
            pygame.draw.circle(
                screen, pygame.Color('green'),
                (hint.xto * SQUARE_SIZE + SQUARE_SIZE // 2,
                 hint.yto * SQUARE_SIZE + SQUARE_SIZE // 2),
                10
            )
        draw_pieces(
            screen, game_board,
            exclude_piece=drag_piece if dragging else None,
            dragging_pos=pygame.mouse.get_pos() if dragging else None
        )
        if selected:
            x, y = selected
            pygame.draw.rect(
                screen, pygame.Color('blue'),
                (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3
            )
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Click to select or deselect
            elif event.type == pygame.MOUSEBUTTONDOWN and player_turn:
                x, y = get_square_under_mouse(event.pos)
                if selected == (x, y):
                    # deselect on second click
                    selected = None
                    move_hints = []
                    drag_piece = None
                    dragging = False
                else:
                    piece = game_board.get_piece(x, y)
                    if piece and piece.color == pieces.Piece.WHITE:
                        selected = (x, y)
                        move_hints = [m for m in game_board.get_possible_moves(pieces.Piece.WHITE)
                                      if m.xfrom == x and m.yfrom == y]
                        drag_piece = piece
                        drag_from = (x, y)
                        dragging = False

            elif event.type == pygame.MOUSEMOTION and drag_piece and player_turn and selected:
                # start dragging only after move hints shown
                dragging = True

            elif event.type == pygame.MOUSEBUTTONUP and player_turn and drag_piece and selected:
                x_to, y_to = get_square_under_mouse(event.pos)
                move = Move(drag_from[0], drag_from[1], x_to, y_to)
                for m in game_board.get_possible_moves(pieces.Piece.WHITE):
                    if move.equals(m):
                        animate_move(screen, clock, game_board, drag_piece, drag_from, (x_to, y_to))
                        game_board.perform_move(m)
                        drag_piece = None
                        player_turn = False
                        break
                selected = None
                move_hints = []
                dragging = False
                if not player_turn:
                    if not game_board.get_possible_moves(pieces.Piece.BLACK):
                        if game_board.is_check(pieces.Piece.BLACK):
                            print("Trắng thắng (Chiếu bí)")
                        else:
                            print("Hòa (Stalemate)")
                        running = False

        # AI move
        if not player_turn and running:
            ai_move = ai.AI.get_ai_move(game_board, [], depth=3)
            if ai_move:
                animate_move(
                    screen, clock, game_board,
                    game_board.get_piece(ai_move.xfrom, ai_move.yfrom),
                    (ai_move.xfrom, ai_move.yfrom),
                    (ai_move.xto, ai_move.yto)
                )
                game_board.perform_move(ai_move)
            player_turn = True
            move_hints = []
            if not game_board.get_possible_moves(pieces.Piece.WHITE):
                if game_board.is_check(pieces.Piece.WHITE):
                    print("Black win")
                else:
                    print("Stalemate")
                running = False
        clock.tick(FPS)
    pygame.quit()