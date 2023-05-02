from src.search import alpha_beta_fail_hard, alpha_beta_fail_soft
import chess
from chess import Move
import chess.engine
import chess.svg
import numpy as np
import openai
import re, time, os


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
        # Pause for 5 seconds
        time.sleep(5)

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
    def __init__(self, path, color = True):
        """
        Initialize player.

        Parameters
        ----------
        path : str
            Path to the Stockfish engine.
        color : bool, default=True
            True if playing as white, False if playing as black.
        """
        self.color = color
        # AI tutor
        self.tutor = StockfishPlayer(path, color = color)

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

            if move == "resign":
                # Player resigns
                return None

            elif move == "display":
                # Generate SVG of board
                boardsvg = chess.svg.board(board, size=600, coordinates=True)
                with open('board.svg', 'w') as outputfile:
                    outputfile.write(boardsvg)
                print('-----\nBoard written to board.svg')
                time.sleep(0.1)
                os.startfile('board.svg')

            elif move == "tutor":
                # Get tutor move suggestion and commentary
                move = self.tutor.get_move(board)
                print(f"-----\nThe tutor's suggested move is {move}")
                get_ChatGPT_response(move, board.turn, str(board))

            elif move[0:2] == move[2:4]:
                # Player did not move, passed turn
                print([move[0:2], move[2:4]])
                return chess.Move.null()

            else:
                # Play move entered by player
                move = Move.from_uci(move)
                if move in list(board.legal_moves):
                    break
                else:
                    print(f"-----\n{move} is not a legal move.")

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
    if board == None:
        # Generate new board to play on
        board = chess.Board()
    game_moves = []

    resign = False

    print("=================================== START GAME ===================================")

    while not board.is_game_over(claim_draw=True):

        print("--------------------------------")
        if isinstance(black_player, HumanPlayer):
            print_board(board, False)
        else:
            print_board(board, True)

        if board.turn == white_player.color:
            move = white_player.get_move(board)
            if move == None:
                print("Game ended.")
                resign = True
                break
            if not isinstance(white_player, HumanPlayer):
                print("White move: {}".format(move.uci()))
        else:
            move = black_player.get_move(board)
            if move == None:
                print("Game ended.")
                resign = True
                break
            if not isinstance(black_player, HumanPlayer):
                print("Black move: {}".format(move.uci()))
        game_moves.append(move.uci())
        board.push(move)

    # Close all instances of Stockfish engine
    if isinstance(white_player, HumanPlayer):
        white_player.tutor.close_engine()
    if isinstance(black_player, HumanPlayer):
        black_player.tutor.close_engine()
    if isinstance(white_player, StockfishPlayer):
        white_player.close_engine()
    if isinstance(black_player, StockfishPlayer):
        black_player.close_engine()

    # Print outcome and save game data to file
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
        next_moves = game_moves[(i * 2):(i * 2 + 2)]
        if len(next_moves) == 1:
            print(f"{i + 1:>6}  {next_moves[0]}\n")
            f.write(f"{next_moves[0]}")
        else:
            print(f"{i + 1:>6}  {next_moves[0]}\t{next_moves[1]}")
            f.write(f"{next_moves[0]},{next_moves[1]}\n")

    f.close()

    print("================================== GAME ENDED ==================================")
    print("Game data available at game_data.csv")
