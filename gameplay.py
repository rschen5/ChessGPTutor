import chess
from chess import Move
import random
import openai
import numpy as np
from search import minimax, alpha_beta_fail_hard, alpha_beta_fail_soft
import re
import json
import chess.svg
import time, os

# from PyQt5.QtSvg import QSvgWidget
# from PyQt5.QtWidgets import QApplication, QWidget
# class MainWindow(QWidget):
#     def __init__(self):
#         super().__init__()

#         self.setGeometry(100, 100, 800, 800)

#         self.widgetSvg = QSvgWidget(parent=self)
#         self.widgetSvg.setGeometry(10, 10, 720, 720)

#         self.chessboard = chess.Board()

#         self.chessboardSvg = chess.svg.board(self.chessboard).encode("UTF-8")
#         self.widgetSvg.load(self.chessboardSvg)


class RandomPlayer():
    def __init__(self, color = True):
        self.color = color

    def get_move(self, board):
        return random.choice(list(board.legal_moves))


class StockfishPlayer():
    def __init__(self, path, color = True, time_limit = 1.0, depth=16):
        self.color = color
        self.engine = chess.engine.SimpleEngine.popen_uci(path)
        self.limit = chess.engine.Limit(time=time_limit, depth=depth)
    
    def get_move(self, board):
        result = self.engine.play(board, self.limit)
        return result.move
    
    def close_engine(self):
        self.engine.quit()


class AIPlayer():
    def __init__(self, color = True, algo = "minimax", depth = 1):
        self.color = color
        self.algo = algo
        self.depth = depth

    def get_move(self, board):
        if self.algo == "AB_hard":
            moves, _ = alpha_beta_fail_hard(board, self.depth, board.turn)
        elif self.algo == "AB_soft":
            moves, _ = alpha_beta_fail_soft(board, self.depth, board.turn)
        else:
            moves, _ = minimax(board, self.depth, board.turn)
        current_move = ""
        for move in moves:
            if (chess.Move.from_uci(str(move)) in board.legal_moves):
                current_move = move
                break
        if current_move == "":
            current_move = moves[0]

        return Move.from_uci(current_move)


# could also add human player for testing later
class HumanPlayer():
    def __init__(self, color = True):
        self.color = color
        self.tutor = StockfishPlayer(path = self.__get_path(), color = color)
    
    def __get_path(self):
        f = open("./config.json")
        data = json.load(f)
        f.close()
        return data['STOCKFISH_PATH']

    def get_move(self, board):
        if len(list(board.legal_moves)) == 0:
            print("No more possible moves.")
            return None
        while (True):
            print('Note: Please limit tutor requests to 3 per minute')
            print('Enter one of the following:')
            print(' - move (ex. d2d4)')
            print(' - "tutor" to get a hint')
            print(' - "display" to get an image of the board')
            print(' - "resign" to end game')
            print('Enter choice: ', end="")
            move = input().strip()
            if move == "resign":
                return None
            elif move == "display":
                # https://stackoverflow.com/questions/61439815/how-to-display-an-svg-image-in-python
                print('-----')
                boardsvg = chess.svg.board(board, size=600, coordinates=True)
                with open('board.svg', 'w') as outputfile:
                    outputfile.write(boardsvg)
                print('Board written to board.svg')
                time.sleep(0.1)
                os.startfile('board.svg')
                # app = QApplication([])
                # window = MainWindow()
                # window.show()
                # app.exec()
                # app.setQuitOnLastWindowClosed(app.exec())

            elif move == "tutor":
                print('-----')
                move = self.tutor.get_move(board)
                print(f"The tutor's suggested move is {move}")
                get_ChatGPT_response(move, board.turn, str(board))

            else:
                move = Move.from_uci(move)
                if move in list(board.legal_moves):
                    break
                else:
                    print(f"{move} is not a legal move.")
            print('---------------')
        return move


def who(player):
    if player == chess.WHITE:
        return "WHITE"
    elif player == chess.BLACK:
        return "BLACK"
    return None


def __convert(c):
    if c == '.':
        return '..'
    elif c.islower():
        return f'B{c.upper()}'
    else:
        return f'W{c}'

def print_board(board, is_white):
    fen_str = board.board_fen()

    for i in range(1, 9):
        if str(i) in fen_str:
            fen_str = re.sub(f"{i}", "." * i, fen_str)
    
    pieces = [list(s) for s in fen_str.split('/')]
    pieces = [list(map(__convert, l)) for l in pieces]

    print("Current board:\n")

    if is_white:
        for i in range(8):
            print(f"{8-i} | {' '.join(pieces[i])}")
        print(f"  -------------------------")
        print("    a  b  c  d  e  f  g  h\n")
    else:
        for i in range(8):
            print(f"{i+1} | {' '.join(pieces[7-i][::-1])}")
        print(f"  -------------------------")
        print("    h  g  f  e  d  c  b  a\n")


def get_ChatGPT_response(current_move, is_white, current_board_string):
    system_message = "You will comment on the current state of this chess game described in an ASCII format. Answer as concisely as possible."
    board_state_message = "This is the current chess board state in ASCII format:"

    current_color = "black"
    if is_white:
        current_color = "white"

    comment_message = "Please comment on the quality of move {} for {}".format(current_move, current_color)    
#     comment_message = "Please comment on the quality on this move {} that was just performed by {}".format(current_move, current_color)    
#     comment_message = "Please comment on how the board state is favorable or not for {}".format(current_color)    

    try_again_message = "Are you sure the move {} is invalid for the current board state? Please make sure your output contains the correct assignment of pieces".format(current_move)

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": board_state_message},
            {"role": "user", "content": current_board_string},
            {"role": "user", "content": comment_message},
        ],
        max_tokens=100
    )

    message = response.choices[0]['message']

    response_string = "{}: {}".format("Tutor commentary", message['content'])

    if "not possible" in response_string or "illegal" in response_string:
        response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "user", "content": try_again_message},
            {"role": "user", "content": current_board_string},

        ],
        max_tokens=100
        )

        message = response.choices[0]['message']
        response_string = "{}: {}".format("Tutor commentary", message['content'])

    print(response_string)


def play_game_max_moves(player1, player2, board = None, max_moves = 0, per_side = True):
    if board == None:
        board = chess.Board()
    game_moves = []

    if per_side:
        max_moves *= 2
    print("============================ START GAME ============================")

    while max_moves > 0 and not board.is_game_over(claim_draw=True):
        if board.turn == player1.color:
            print("White's turn")
            move = player1.get_move(board)
        else:
            print("Black's turn")

            move = player2.get_move(board)

        print("current move: {}".format(str(move)))
        current_move = board.turn
        get_ChatGPT_response(move, current_move, str(board))

        # update game variables.
        game_moves.append(move.uci())
        board.push(move)
        max_moves -= 1

        print(str(board))

        print("================================================================")

    if not board.is_game_over(claim_draw=True):
        print("Game not over")
    else:
        outcome = board.outcome()
        if outcome == None:
            t = "DRAW"
            w = None
        else:
            t = str(outcome.termination).split('.')[1]
            w = who(outcome.winner)
        print(f"Outcome: {t}\nWinner: {w}\nNumber of moves: {len(game_moves)}")
    print("================================================================")
    print("Moves:\tWHITE\tBLACK\n        -------------")
    for i in range(int(np.ceil(len(game_moves) / 2))):
        next_moves = game_moves[(i*2):(i*2 + 2)]
        if len(next_moves) == 1:
            print(f"{i+1:>6}  {next_moves[0]}")
        else:
            print(f"{i+1:>6}  {next_moves[0]}\t{next_moves[1]}")

    return board


def play_game(player1, player2, board = None):
    if board == None:
        board = chess.Board()
    game_moves = []

    resign = False

    while not board.is_game_over(claim_draw=True):
        print("--------------------------------")
        if isinstance(player2, HumanPlayer):
            print_board(board, False)
        else:
            print_board(board, True)
        # app = QApplication([])
        # window = MainWindow()
        # window.show()
        # app.exec()
        if board.turn == player1.color:
            move = player1.get_move(board)
            if move == None:
                print("Game ended.")
                resign = True
                break
            if not isinstance(player1, HumanPlayer):
                print(f"White move: {move.uci()}")
        else:
            move = player2.get_move(board)
            if move == None:
                print("Game ended.")
                resign = True
                break
            if not isinstance(player2, HumanPlayer):
                print(f"Black move: {move.uci()}")
        game_moves.append(move.uci())
        board.push(move)

    if isinstance(player1, HumanPlayer):
        player1.tutor.close_engine()
    if isinstance(player2, HumanPlayer):
        player2.tutor.close_engine()
    if isinstance(player1, StockfishPlayer):
        player1.close_engine()
    if isinstance(player2, StockfishPlayer):
        player2.close_engine()

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
    f.write(f"{t},{w},{len(game_moves)}")

    print("================================================================")
    print(f"Outcome: {t}\nWinner: {w}\nNumber of moves: {len(game_moves)}")
    print("================================================================")
    print("Moves:\tWHITE\tBLACK\n        -------------")
    for i in range(int(np.ceil(len(game_moves) / 2))):
        next_moves = game_moves[(i*2):(i*2 + 2)]
        if len(next_moves) == 1:
            print(f"{i+1:>6}  {next_moves[0]}")
        else:
            print(f"{i+1:>6}  {next_moves[0]}\t{next_moves[1]}")

    f.close()
    print("Game data available at game_data.csv")
