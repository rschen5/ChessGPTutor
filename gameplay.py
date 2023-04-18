import chess
from chess import Move
import chess.svg
import openai
import numpy as np
from search import minimax, alpha_beta_fail_hard, alpha_beta_fail_soft
import random, re, json, time, os


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

            if move[0:2] == move[2:4]:
                print([move[0:2], move[2:4]])
                return chess.Move.null()

            print('-----')
            if move == "resign":
                return None

            elif move == "display":
                boardsvg = chess.svg.board(board, size=600, coordinates=True)
                with open('board.svg', 'w') as outputfile:
                    outputfile.write(boardsvg)
                print('Board written to board.svg')
                time.sleep(0.1)
                os.startfile('board.svg')

            elif move == "tutor":
                move = self.tutor.get_move(board)
                print("The tutor's suggested move is {}".format(move))
                get_ChatGPT_response(move, board.turn, str(board))

            else:
                try:
                    move = Move.from_uci(move)
                except:
                    print("Incorrect input format\n---------------")
                    continue
                if move in list(board.legal_moves):
                    break
                else:
                    print("{} is not a legal move.".format(move))
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
            fen_str = re.sub(str(i), "." * i, fen_str)
    
    pieces = [list(s) for s in fen_str.split('/')]
    pieces = [list(map(__convert, l)) for l in pieces]

    print("Current board:\n")

    if is_white:
        for i in range(8):
            print("{} | {}".format(8-i, ' '.join(pieces[i])))
        print("  -------------------------")
        print("    a  b  c  d  e  f  g  h\n")
    else:
        for i in range(8):
            print("{} | {}".format(i+1, ' '.join(pieces[7-i][::-1])))
        print("  -------------------------")
        print("    h  g  f  e  d  c  b  a\n")


def get_ChatGPT_response(current_move, is_white, current_board_string):
    system_message = "You will comment on the current state of this chess game described in an ASCII format. Answer as concisely as possible."
    board_state_message = "This is the current chess board state in ASCII format:"

    current_color = "black"
    if is_white:
        current_color = "white"

    comment_message = "Please comment on the quality of move {} for {}".format(current_move, current_color)

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


def play_game(player1, player2, board = None):
    if board == None:
        board = chess.Board()
    game_moves = []

    resign = False

    print("=================================== START GAME ===================================")

    while not board.is_game_over(claim_draw=True):
        print("--------------------------------")
        if isinstance(player2, HumanPlayer):
            print_board(board, False)
        else:
            print_board(board, True)

        if board.turn == player1.color:
            move = player1.get_move(board)
            if move == None:
                print("Game ended.")
                resign = True
                break
            if not isinstance(player1, HumanPlayer):
                print("White move: {}".format(move.uci()))
        else:
            move = player2.get_move(board)
            if move == None:
                print("Game ended.")
                resign = True
                break
            if not isinstance(player2, HumanPlayer):
                print("Black move: {}".format(move.uci()))
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
    f.write("{},{},{}\n".format(t, w, len(game_moves)))

    print("================================================================")
    print("Outcome: {}\nWinner: {}\nNumber of moves: {}".format(t, w, len(game_moves)))
    print("================================================================")
    print("Moves:\tWHITE\tBLACK\n        -------------")
    for i in range(int(np.ceil(len(game_moves) / 2))):
        next_moves = game_moves[(i*2):(i*2 + 2)]
        if len(next_moves) == 1:
            print("{:>6}  {}\n".format(i+1, next_moves[0]))
            f.write("{}".format(next_moves[0]))
        else:
            print("{:>6}  {}\t{}".format(i+1, next_moves[0], next_moves[1]))
            f.write("{next_moves[0]},{next_moves[1]}\n")

    f.close()

    print("================================== GAME ENDED ==================================")
    print("Game data available at game_data.csv")
