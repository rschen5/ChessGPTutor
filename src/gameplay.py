from src.search import alpha_beta_fail_hard, alpha_beta_fail_soft
import chess
from chess import Move
import chess.engine
import chess.svg
import numpy as np
import openai, pygame
import re, json, time, os, sys, math


# Reference for GUI: https://blog.devgenius.io/simple-interactive-chess-gui-in-python-c6d6569f7b6c

# Initialize display
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
scrn = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
pygame.init()

# Board size specifications for display
SQUARE_SIZE = 100
BOARD_OFFSET = 50
BORDER_OFFSET = 6

# Colors
WHITE = (255, 255, 255)
BLUE = (50, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND = (232, 181, 132)
BOARD_OUTLINE = (79, 40, 3)
DARK_SQUARE = (216, 140, 68)
LIGHT_SQUARE = (255, 204, 156)
LATEST_MOVE = (120, 148, 84)

# Initialize chess board
b = chess.Board()
print("Setting up the board")

# Load piece images
IMAGE_PATH = "./images/"

og_pieces = {
    'p': pygame.image.load(IMAGE_PATH + 'bP.png').convert_alpha(),
    'n': pygame.image.load(IMAGE_PATH + 'bN.png').convert_alpha(),
    'b': pygame.image.load(IMAGE_PATH + 'bB.png').convert_alpha(),
    'r': pygame.image.load(IMAGE_PATH + 'bR.png').convert_alpha(),
    'q': pygame.image.load(IMAGE_PATH + 'bQ.png').convert_alpha(),
    'k': pygame.image.load(IMAGE_PATH + 'bK.png').convert_alpha(),
    'P': pygame.image.load(IMAGE_PATH + 'wP.png').convert_alpha(),
    'N': pygame.image.load(IMAGE_PATH + 'wN.png').convert_alpha(),
    'B': pygame.image.load(IMAGE_PATH + 'wB.png').convert_alpha(),
    'R': pygame.image.load(IMAGE_PATH + 'wR.png').convert_alpha(),
    'Q': pygame.image.load(IMAGE_PATH + 'wQ.png').convert_alpha(),
    'K': pygame.image.load(IMAGE_PATH + 'wK.png').convert_alpha()
}

# Resized piece images
pieces = {k: pygame.transform.scale(v, (SQUARE_SIZE, SQUARE_SIZE)) for k, v in og_pieces.items()}


# Board

def drawText(surface, text, color, rect, font, aa, bkg):
    """
    Draw some text into an area of a surface.
    Automatically wraps words and returns any text that didn't get blitted.
    Reference: https://www.pygame.org/wiki/TextWrap.
    """
    rect = pygame.Rect(rect)
    y = rect.top
    lineSpacing = -2

    # Get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # Determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # Determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # If we've wrapped the text, then adjust the wrap to the last word
        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1

        # Render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], True, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # Remove the text we just blitted
        text = text[i:]

    return text

def update(scrn, board, suggested_move, chatGPT_text, human_black, highlight_squares = None, latest_move = False):
    '''
    Updates the game window display.

    Parameters
    ----------
    scrn : pygame.Surface
        The screen displayed in the game window.
    board : chess.Board
        Chess board representing the current board state.
    suggested_move : str
        The suggested move from Stockfish for the human player.
    chatGPT_text : str
        ChatGPT's commentary on the suggested move.
    human_black : bool
        True if the human player is playing as black, False if they are playing as white.
    highlight_squares : list of int, default=None
        List if squares (0-63) to draw a box around on the chess board.
    latest_move : bool, default=False
        True if highlight_squares reflects the latest move that a player has made.
        False if highlight_squares reflects the possible squares a human player-selected piece can move to.
    '''
    # Set screen background color
    scrn.fill(BACKGROUND)

    # Create a font object
    font = pygame.font.Font('freesansbold.ttf', math.floor(32 * SCREEN_HEIGHT / 900))

    # Letters and numbers to mark the sides of the board to denote squares
    CHARACTER_LIST = ['A','B','C','D','E','F','G','H']
    NUMBER_LIST = ['8','7','6','5','4','3','2','1']

    # Draw border
    pygame.draw.rect(scrn, BOARD_OUTLINE, pygame.Rect(BOARD_OFFSET - (SQUARE_SIZE / 100 * BORDER_OFFSET),
                                                      BOARD_OFFSET - (SQUARE_SIZE / 100 * BORDER_OFFSET),
                                                      8 * SQUARE_SIZE + (2 * SQUARE_SIZE / 100) * BORDER_OFFSET,
                                                      8 * SQUARE_SIZE + (2 * SQUARE_SIZE / 100) * BORDER_OFFSET), 5)

    # Flip board if human is playing as black
    if human_black:
        board = board.transform(chess.flip_vertical).transform(chess.flip_horizontal)

    # Start by drawing dark-colored square for the board, alternating
    dark_square = True

    for i in range(64):
        # Draw board squares
        if dark_square:
            pygame.draw.rect(scrn, DARK_SQUARE, pygame.Rect(BOARD_OFFSET + (i % 8) * SQUARE_SIZE,
                                                            BOARD_OFFSET + (7 * SQUARE_SIZE) - (i // 8) * SQUARE_SIZE,
                                                            SQUARE_SIZE, SQUARE_SIZE))
        else:
            pygame.draw.rect(scrn, LIGHT_SQUARE, pygame.Rect(BOARD_OFFSET + (i % 8) * SQUARE_SIZE,
                                                             BOARD_OFFSET + (7 * SQUARE_SIZE) - (i // 8) * SQUARE_SIZE,
                                                             SQUARE_SIZE, SQUARE_SIZE))
        if i % 8 != 7:
            dark_square = not dark_square

        # Draw pieces
        piece = board.piece_at(i)
        if piece == None:
            pass
        else:
            scrn.blit(pieces[str(piece)], (BOARD_OFFSET + (i % 8) * SQUARE_SIZE,
                                           BOARD_OFFSET + (7 * SQUARE_SIZE) - (i // 8) * SQUARE_SIZE))
    
    # Draw letters and numbers
    for i in range(8):

        # Text surface object for letters
        if human_black:
            text_letter = font.render(CHARACTER_LIST[7 - i], True, BLACK, BACKGROUND)
        else:
            text_letter = font.render(CHARACTER_LIST[i], True, BLACK, BACKGROUND)

        # Rectangular object for the text surface object
        textLetterRect = text_letter.get_rect()

        # Set the center of the rectangular object
        textLetterRect.center = (2 * BOARD_OFFSET + i * SQUARE_SIZE, int(BOARD_OFFSET / 2))

        scrn.blit(text_letter, textLetterRect)

        # Text surface object for numbers
        if human_black:
            text_number = font.render(NUMBER_LIST[7 - i], True, BLACK, BACKGROUND)
        else:
            text_number = font.render(NUMBER_LIST[i], True, BLACK, BACKGROUND)

        # Rectangular object for the text surface object
        textNumberRect = text_number.get_rect()

        # Set the center of the rectangular object
        textNumberRect.center = (int(BOARD_OFFSET / 2), 2 * BOARD_OFFSET + i * SQUARE_SIZE)

        scrn.blit(text_number, textNumberRect)

    # Draw lines
    for i in range(7):
        i = i + 1
        pygame.draw.line(scrn, WHITE, (BOARD_OFFSET + 0, BOARD_OFFSET + i * SQUARE_SIZE),
                         (BOARD_OFFSET + 8 * SQUARE_SIZE, BOARD_OFFSET + i * SQUARE_SIZE))
        pygame.draw.line(scrn, WHITE, (BOARD_OFFSET + i * SQUARE_SIZE, BOARD_OFFSET),
                         (BOARD_OFFSET + i * SQUARE_SIZE, BOARD_OFFSET + 8 * SQUARE_SIZE))

    # Draw boxes around squares to highlight
    if highlight_squares != None:
        if latest_move:
            # Highlighted square reflects the latest move a player made
            for square in highlight_squares:
                x = BOARD_OFFSET + SQUARE_SIZE * chess.square_file(square)
                y = BOARD_OFFSET + SQUARE_SIZE * (7 - chess.square_rank(square))
                pygame.draw.rect(scrn, LATEST_MOVE, pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE), 5)
        else:
            # Highlighted squares reflect the possible squares a human player-selected piece can move to
            for square in highlight_squares:
                x = BOARD_OFFSET + SQUARE_SIZE * chess.square_file(square)
                y = BOARD_OFFSET + SQUARE_SIZE * (7 - chess.square_rank(square))
                pygame.draw.rect(scrn, BLUE, pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE), 5)

    # Text object for the current turn
    current_turn = who(board.turn).title()
    turn_text = "Current turn: {}".format(current_turn)
    text_letter = font.render(turn_text, True, BLACK, WHITE)

    textLetterRect = text_letter.get_rect()

    textLetterRect.center = (2*BOARD_OFFSET+ 10*SQUARE_SIZE, int(BOARD_OFFSET/2))

    text = drawText(scrn, turn_text, BLACK,
                    pygame.Rect(2 * BOARD_OFFSET + 8 * SQUARE_SIZE, int(BOARD_OFFSET / 2),
                                math.floor(SCREEN_WIDTH * 5 / 14), math.floor(SCREEN_HEIGHT / 9)),
                    font, True, None)
    print(text)

    if suggested_move != None and chatGPT_text != None:
        # Human player's turn
        # Text object for the move suggestion
        stockfish_text = "Stockfish suggestion: {}".format(suggested_move)

        text = drawText(scrn, stockfish_text, BLACK,
                        pygame.Rect(2 * BOARD_OFFSET + 8 * SQUARE_SIZE, int(BOARD_OFFSET / 2) + BOARD_OFFSET,
                                    math.floor(SCREEN_WIDTH * 5 / 14), math.floor(SCREEN_HEIGHT / 9)),
                        font, True, None)
        print(text)

        # Text object for the move commentary
        intro_text = "ChatGPT's commentary:"

        text = drawText(scrn, intro_text, BLACK,
                        pygame.Rect(2 * BOARD_OFFSET + 8 * SQUARE_SIZE, int(BOARD_OFFSET / 2) + BOARD_OFFSET * 2,
                                    math.floor(SCREEN_WIDTH * 5 / 14), math.floor(SCREEN_HEIGHT / 9)),
                        font, True, None)
        print(text)

        chatGPT_text = "{}".format(chatGPT_text)

        text = drawText(scrn, chatGPT_text, BLACK,
                        pygame.Rect(2 * BOARD_OFFSET + 8 * SQUARE_SIZE, int(BOARD_OFFSET / 2) + BOARD_OFFSET * 3,
                                    math.floor(SCREEN_WIDTH * 5 / 14), math.floor(SCREEN_HEIGHT / 9 * 6)),
                        font, True, None)
        print(text)

    else:
        # Opponent's turn
        sleep_text = "Opponent is thinking..."

        text = drawText(scrn, sleep_text, BLACK,
                        pygame.Rect(2 * BOARD_OFFSET + 8 * SQUARE_SIZE, int(BOARD_OFFSET / 2) + BOARD_OFFSET,
                                    math.floor(SCREEN_WIDTH * 5 / 14), math.floor(SCREEN_HEIGHT / 18)),
                        font, True, None)
        print(text)

    pygame.display.flip()


# Players

class StockfishPlayer():
    """
    Player using the Stockfish engine for move generation.
    Used for the medium opponent, hard opponent, and AI tutor.
    """
    def __init__(self, path, color = True, time_limit = 1.0, depth = 16):
        """
        Initialize player.

        Parameters
        ----------
        path : str
            Path to the Stockfish engine.
        color : bool, default=True
            True if playing as white, False if playing as black.
        time_limit : float, default=1.0
            Time limit for Stockfish to search for a move suggestion.
        depth : int, default=16
            The maximum search depth for Stockfish.
        """
        self.color = color
        self.engine = chess.engine.SimpleEngine.popen_uci(path)
        self.limit = chess.engine.Limit(time = time_limit, depth = depth)

    def get_move(self, board, sleep = True):
        """
        Get the best move for a board state.

        Parameters
        ----------
        board : chess.Board
            Chess board representing the current board state.
        sleep : bool, default=True
            True if the player is an opponent - makes the player pause before generating a move.
            False if the player is not an opponent and is the tutor for the human player.

        Returns
        -------
        chess.Move
            Best move for a board state.
        """
        if sleep:
            # Pause for 10 seconds
            time.sleep(10)
        result = self.engine.play(board, self.limit)
        return result.move

    def close_engine(self):
        """
        Closes the Stockfish engine. Necessary for a clean exit from the game window.
        """
        self.engine.quit()

class ABPlayer():
    """
    Player using alpha-beta pruning for move generation.
    Used for the easy opponent.
    """
    def __init__(self, color = True, fail_hard = True, depth = 3):
        """
        Initialize player.

        Parameters
        ----------
        color : bool, default=True
            True if playing as white, False if playing as black.
        fail_hard : bool, default=True
            True to use the fail-hard version of alpha-beta pruning, False to use the fail-soft version.
        depth : int, default=3
            The maximum search depth for alpha-beta pruning.
        """
        self.color = color
        self.fail_hard = fail_hard
        self.depth = depth

    def get_move(self, board):
        """
        Get the suggested move for a board state.

        Parameters
        ----------
        board : chess.Board
            Chess board representing the current board state.

        Returns
        -------
        chess.Move
            Suggested move for a board state.
        """
        if self.fail_hard:
            moves, _ = alpha_beta_fail_hard(board, self.depth, board.turn)
        else:
            moves, _ = alpha_beta_fail_soft(board, self.depth, board.turn)

        # Make sure move is legal
        current_move = ""
        for move in moves:
            if (chess.Move.from_uci(str(move)) in board.legal_moves):
                current_move = move
                break
        if current_move == "":
            current_move = moves[0]

        return Move.from_uci(current_move)

class HumanPlayer():
    """
    Human player.
    """
    def __init__(self, color = True):
        """
        Initialize player.

        Parameters
        ----------
        color : bool, default=True
            True if playing as white, False if playing as black.
        """
        self.color = color
        # AI tutor
        self.tutor = StockfishPlayer(path = self.__get_path(), color = color)

    def __get_path(self):
        """
        Returns the path to the Stockfish engine for the tutor.

        Returns
        -------
        str
            Path to the Stockfish engine.
        """
        f = open("./config.json")
        data = json.load(f)
        f.close()
        return data['STOCKFISH_PATH']

    def get_move(self, board):
        """
        Get the human player's choice move for a board state using a command-line interface.

        Parameters
        ----------
        board : chess.Board
            Chess board representing the current board state.

        Returns
        -------
        chess.Move
            Suggested move for a board state.
        """
        if len(list(board.legal_moves)) == 0:
            print("No more possible moves.")
            return None

        while (True):
            # Print menu
            print('Note: Please limit tutor requests to 3 per minute')
            print('Enter one of the following:')
            print(' - move (ex. d2d4)')
            print(' - "tutor" to get a hint')
            print(' - "display" to get an image of the board')
            print(' - "resign" to end game')
            # Get menu choice
            print('Enter choice: ', end="")
            move = input().strip()

            # Player did not move, passed turn
            if move[0:2] == move[2:4]:
                print([move[0:2], move[2:4]])
                return chess.Move.null()

            print('-----')
            if move == "resign":
                # Player resigns
                return None

            elif move == "display":
                # Generate SVG of board
                boardsvg = chess.svg.board(board, size=600, coordinates=True)
                with open('board.svg', 'w') as outputfile:
                    outputfile.write(boardsvg)
                print('Board written to board.svg')
                time.sleep(0.1)
                os.startfile('board.svg')

            elif move == "tutor":
                # Get tutor move suggestion and commentary
                move = self.tutor.get_move(board)
                print(f"The tutor's suggested move is {move}")
                get_ChatGPT_response(move, board.turn, str(board))

            else:
                # Play move entered by player
                move = Move.from_uci(move)
                if move in list(board.legal_moves):
                    break
                else:
                    print(f"{move} is not a legal move.")

            print('---------------')

        return move


# Gameplay

def who(player):
    """
    Determine if a player is the white or black player.
    Return the color in a string.

    Parameters
    ----------
    player : chess.Color
        The player's color.

    Returns
    -------
    str
        "WHITE" if the player is the white player or "BLACK" if the player is the black player.
    """
    if player == chess.WHITE:
        return "WHITE"
    elif player == chess.BLACK:
        return "BLACK"
    return None

def __convert(c):
    """
    Get the formatted string of a board piece for printing to the command line.

    Parameters
    ----------
    c : str
        The piece or an empty space in ASCII format on a chess board.

    Returns
    -------
    str
        Formatted representation of the given piece or empty space for printing.
    """
    if c == '.':
        # Empty space
        return '..'
    elif c.islower():
        # Black piece
        return f'B{c.upper()}'
    else:
        # White piece
        return f'W{c}'

def print_board(board, is_white):
    """
    Print formatted chess board.

    Parameters
    ----------
    board : chess.Board
        Chess board representing the current board state.
    is_white : bool
        True if the human player is playing as white, False if playing as black.
    """
    fen_str = board.board_fen()

    # Replace numbers in empty spaces with corresponding number of '.' characters
    for i in range(1, 9):
        if str(i) in fen_str:
            fen_str = re.sub(f"{i}", "." * i, fen_str)

    pieces = [list(s) for s in fen_str.split('/')]
    pieces = [list(map(__convert, l)) for l in pieces]

    print("Current board:\n")

    if is_white:
        # Print board from the white player's point of view
        for i in range(8):
            print(f"{8 - i} | {' '.join(pieces[i])}")
        print(f"  -------------------------")
        print("    a  b  c  d  e  f  g  h\n")
    else:
        # Print board from the black player's point of view
        for i in range(8):
            print(f"{i + 1} | {' '.join(pieces[7 - i][::-1])}")
        print(f"  -------------------------")
        print("    h  g  f  e  d  c  b  a\n")

def get_ChatGPT_response(current_move, is_white, current_board_string):
    """
    Get move commentary from ChatGPT.

    Parameters
    ----------
    current_move : str
        The move suggested by Stockfish for the human player.
    is_white : bool
        True if the human player is playing as white, False if playing as black.
    current_board_string : str
        ASCII representation of the board state.

    Returns
    -------
    str
        Commentary on the given move.
    """
    system_message = "You will comment on the current state of this chess game described in an ASCII format. Answer as concisely as possible."
    board_state_message = "This is the current chess board state in ASCII format:"

    current_color = who(is_white).lower()
    comment_message = "Please comment on the quality of move {} for {}".format(current_move, current_color)

    # Prompt ChatGPT
    response = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo',
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": board_state_message},
            {"role": "user", "content": current_board_string},
            {"role": "user", "content": comment_message},
        ],
        max_tokens = 100
    )
    # Get ChatGPT response
    message = response.choices[0]['message']
    response_string = "{}".format(message['content'])

    # Filter for invalid explanation
    if "not possible" in response_string or "illegal" in response_string or "not legal" in response_string or "not valid" in response_string or "invalid" in response_string:
        response_string = "Sorry, I'm having a hard time understanding this move and board."

    print(response_string)

    return response_string

def play_game(white_player, black_player, human_black, board = None):
    """
    Play full chess game.

    Parameters
    ----------
    white_player : StockfishPlayer, ABPlayer, or HumanPlayer
        The white player.
    black_player : StockfishPlayer, ABPlayer, or HumanPlayer
        The black player.
    human_black : bool
        True if the human player is playing as black, False if playing as white.
    board : chess.Board, default=None
        Chess board representing the board state to start playing from.
        If None, start from the opening board state.
    """
    global SCREEN_WIDTH, SCREEN_HEIGHT, SQUARE_SIZE, BOARD_OFFSET, scrn, pieces

    if board == None:
        # Generate new board to play on
        board = chess.Board()
    game_moves = []

    resign = False

    print("=================================== START GAME ===================================")

    # Name the game window
    pygame.display.set_caption('Chess')

    # Variables for updating display
    index_moves = []
    if human_black:
        suggested_move = None
        chatGPT_text = None
    else:
        suggested_move = ""
        chatGPT_text = ""
    highlight_squares = []
    update(scrn, board, suggested_move, chatGPT_text, human_black)

    while not board.is_game_over(claim_draw=True):

        print("--------------------------------")
        if isinstance(black_player, HumanPlayer):
            print_board(board, False)
        else:
            print_board(board, True)

        if board.turn == white_player.color:
            current_player = white_player
        else:
            current_player = black_player

        if isinstance(current_player, HumanPlayer):
            # Human player's turn, get tutor move suggestion and commentary
            move = current_player.tutor.get_move(board, sleep = False)
            try:
                chatGPT_text = get_ChatGPT_response(move, board.turn, str(board))
            except:
                chatGPT_text = "ChatGPT has received too many requests. Commentary will resume in a couple moves."
            suggested_move = "{}".format(move)

            update(scrn, board, suggested_move, chatGPT_text, human_black, highlight_squares, latest_move=True)

            move = None

            while move is None:
                # Get human player's choice move from the game window
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        # Quit the program and pygame
                        pygame.quit()
                        if isinstance(white_player, HumanPlayer):
                            white_player.tutor.close_engine()
                        if isinstance(black_player, HumanPlayer):
                            black_player.tutor.close_engine()
                        if isinstance(white_player, StockfishPlayer):
                            white_player.close_engine()
                        if isinstance(black_player, StockfishPlayer):
                            black_player.close_engine()
                        sys.exit(0)

                    elif event.type == pygame.VIDEORESIZE:
                        # Resize window
                        # Adjust screen and board display variables accordingly
                        SQUARE_SIZE = SQUARE_SIZE * event.dict['size'][1] / SCREEN_HEIGHT
                        BOARD_OFFSET = SQUARE_SIZE / 2
                        SCREEN_WIDTH, SCREEN_HEIGHT = event.dict['size']
                        pieces = {k: pygame.transform.scale(v, (SQUARE_SIZE, SQUARE_SIZE)) for k, v in og_pieces.items()}
                        scrn = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
                        update(scrn, board, suggested_move, chatGPT_text, human_black, highlight_squares, latest_move=True)

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Mouse clicked
                        # Get position of mouse
                        pos = pygame.mouse.get_pos()

                        # Find which square was clicked and its index
                        if human_black:
                            square = (7 - math.floor((pos[0] - BOARD_OFFSET) / SQUARE_SIZE), 7 - math.floor((pos[1] - BOARD_OFFSET) / SQUARE_SIZE))
                        else:
                            square = (math.floor((pos[0] - BOARD_OFFSET) / SQUARE_SIZE), math.floor((pos[1] - BOARD_OFFSET) / SQUARE_SIZE))
                        if square[0] < 0 or square[0] > 7 or square[1] < 0 or square[1] > 7:
                            continue

                        index = (7 - square[1]) * 8 + square[0]
                        print(index)

                        if index in index_moves: 
                            # Moving a piece
                            move = moves[index_moves.index(index)]

                            print(move)

                            #reset index and moves
                            index = None
                            index_moves = []

                        # Show possible moves
                        else:
                            # Check the square that is clicked
                            piece = board.piece_at(index)
                            # If empty, pass
                            if piece == None:
                                pass
                            else:
                                # Figure out what moves this piece can make
                                all_moves = list(board.legal_moves)
                                moves = []
                                highlight_squares = []
                                for m in all_moves:
                                    if m.from_square == index:

                                        moves.append(m)

                                        t = m.to_square
                                        if human_black:
                                            t = 63 - t

                                        # Highlight squares it can move to
                                        highlight_squares.append(t)

                                update(scrn, board, suggested_move, chatGPT_text, human_black, highlight_squares)

                                index_moves = [a.to_square for a in moves]

            suggested_move = None
            chatGPT_text = None

            if move == None:
                print("Game ended.")
                resign = True
                break
        else:
            move = current_player.get_move(board)
            if move == None:
                print("Game ended.")
                resign = True
                break
            print(f"{who(current_player.color)} move: {move.uci()}")

            suggested_move = ""
            chatGPT_text = ""

        game_moves.append(move.uci())
        board.push(move)

        square_num = move.to_square
        if human_black:
            square_num = 63 - square_num
        highlight_squares = [square_num]

        update(scrn, board, suggested_move, chatGPT_text, human_black, highlight_squares, latest_move = True)

        if board.outcome() != None:
            print(board.outcome())
            print(board)

    # Deactivate the pygame library
    pygame.quit()
    # Close all instances of Stockfish engine
    if isinstance(white_player, HumanPlayer):
        white_player.tutor.close_engine()
    if isinstance(black_player, HumanPlayer):
        black_player.tutor.close_engine()
    if isinstance(white_player, StockfishPlayer):
        white_player.close_engine()
    if isinstance(black_player, StockfishPlayer):
        black_player.close_engine()

    outcome = board.outcome()
    if outcome == None:
        if resign:
            t = "RESIGN"
        else:
            t = "DRAW"
        w = None
    else:
        t = str(outcome.termination).split('.')[1]
        w = who(outcome.winner)

    f = open("game_data.csv", "w")
    f.write(f"{t},{w},{len(game_moves)}\n")

    print("================================================================")
    print(f"Outcome: {t}\nWinner: {w}\nNumber of moves: {len(game_moves)}")
    print("================================================================")
    print("Moves:\tWHITE\tBLACK\n        -------------")
    for i in range(int(np.ceil(len(game_moves) / 2))):
        next_moves = game_moves[(i*2):(i*2 + 2)]
        if len(next_moves) == 1:
            print(f"{i+1:>6}  {next_moves[0]}\n")
            f.write(f"{next_moves[0]}")
        else:
            print(f"{i+1:>6}  {next_moves[0]}\t{next_moves[1]}")
            f.write(f"{next_moves[0]},{next_moves[1]}\n")

    f.close()

    print("================================== GAME ENDED ==================================")
    print("Game data available at game_data.csv")
