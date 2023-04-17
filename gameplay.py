import chess
from chess import Move
import chess.svg
import openai
import numpy as np
from search import minimax, alpha_beta_fail_hard, alpha_beta_fail_soft
import random, re, json, time, os

# importing required librarys
import pygame
import chess
import math
#initialise display

# blog for gui:
# CITATION:
# https://blog.devgenius.io/simple-interactive-chess-gui-in-python-c6d6569f7b6c
X = 1200
Y = 900
scrn = pygame.display.set_mode((X, Y))
pygame.init()

#basic colours
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
YELLOW = (204, 204, 0)
BLUE = (50, 255, 255)
BLACK = (0, 0, 0)

#initialise chess board
b = chess.Board()
print("Setting up the board")

IMAGE_PATH = "./images/"

BOARD_OFFSET = 50

#load piece images
pieces = {'p': pygame.image.load(IMAGE_PATH + 'bP.png').convert_alpha(),
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
          'K': pygame.image.load(IMAGE_PATH + 'wK.png').convert_alpha(),
          }


# Board

def update(scrn,board):
    '''
    updates the screen basis the board class
    '''
    # create a font object.
    # 1st parameter is the font file
    # which is present in pygame.
    # 2nd parameter is size of the font
    font = pygame.font.Font('freesansbold.ttf', 32)

    CHARACTER_LIST = [' A ',' B ',' C ',' D ',' E ',' F ',' G ',' H ']
    # NUMBER_LIST = ['1','2','3','4','5','6','7','8']
    NUMBER_LIST = [' 8 ', ' 7 ', ' 6 ', ' 5 ', ' 4 ',' 3 ',' 2 ',' 1 ']

    
    for i in range(64):
        piece = board.piece_at(i)
        if piece == None:
            pass
        else:
            scrn.blit(pieces[str(piece)],(BOARD_OFFSET+(i%8)*100,BOARD_OFFSET+700-(i//8)*100))
    
    # draw letters and numbers
    for i in range(8):

        # create a text surface object,
        # on which text is drawn on it.
        text_letter = font.render(CHARACTER_LIST[i], True, BLACK, WHITE)
        
        # create a rectangular object for the
        # text surface object
        textLetterRect = text_letter.get_rect()
        
        # set the center of the rectangular object.
        textLetterRect.center = (2*BOARD_OFFSET+ i*100 , int(BOARD_OFFSET/2) )

        scrn.blit(text_letter, textLetterRect)

        # create a text surface object,
        # on which text is drawn on it.
        text_number = font.render(NUMBER_LIST[i], True, BLACK, WHITE)
        
        # create a rectangular object for the
        # text surface object
        textNumberRect = text_number.get_rect()
        
        # set the center of the rectangular object.
        textNumberRect.center = (int(BOARD_OFFSET/2), 2*BOARD_OFFSET+ i*100)

        scrn.blit(text_number, textNumberRect)


    # draw lines
    for i in range(7):
        i=i+1
        pygame.draw.line(scrn,WHITE,(BOARD_OFFSET+0,BOARD_OFFSET+i*100),(BOARD_OFFSET+800,BOARD_OFFSET+i*100))
        pygame.draw.line(scrn,WHITE,(BOARD_OFFSET+i*100,BOARD_OFFSET),(BOARD_OFFSET+i*100,BOARD_OFFSET+800))

    pygame.display.flip()

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

        #make background black
    scrn.fill(GREY)
    #name window
    pygame.display.set_caption('Chess')
    
    #variable to be used later
    index_moves = []
    update(scrn,board)

    while not board.is_game_over(claim_draw=True):

        print("--------------------------------")
        if isinstance(player2, HumanPlayer):
            print_board(board, False)
        else:
            print_board(board, True)


        if board.turn == player1.color:
            move = player1.get_move(board)

            # move = None

            # while move is None:
            #     for event in pygame.event.get():
            #         # if event object type is QUIT
            #         # then quitting the pygame
            #         # and program both.
            #         if event.type == pygame.QUIT:
            #             status = False

            #         # if mouse clicked
            #         if event.type == pygame.MOUSEBUTTONDOWN:
            #             #remove previous highlights
            #             scrn.fill(GREY)
            #             #get position of mouse
            #             pos = pygame.mouse.get_pos()

            #             #find which square was clicked and index of it
            #             square = (math.floor((pos[0]-BOARD_OFFSET)/100),math.floor((pos[1]-BOARD_OFFSET)/100))
            #             index = (7-square[1])*8+(square[0])
            #             print(index)
                        
            #             # if we are moving a piece
            #             if index in index_moves: 
                            
            #                 move = moves[index_moves.index(index)]

            #                 print(move)
                            
            #                 #reset index and moves
            #                 index=None
            #                 index_moves = []
                            
                            
            #             # show possible moves
            #             else:
            #                 #check the square that is clicked
            #                 piece = board.piece_at(index)
            #                 #if empty pass
            #                 if piece == None:
                                
            #                     pass
            #                 else:
                                
            #                     #figure out what moves this piece can make
            #                     all_moves = list(board.legal_moves)
            #                     moves = []
            #                     for m in all_moves:
            #                         if m.from_square == index:
                                        
            #                             moves.append(m)

            #                             t = m.to_square

            #                             TX1 = 100*(t%8)+BOARD_OFFSET
            #                             TY1 = 100*(7-t//8)+BOARD_OFFSET

            #                             #highlight squares it can move to
            #                             pygame.draw.rect(scrn,BLUE,pygame.Rect(TX1,TY1,100,100),5)
            #                     update(scrn,board)

            #                     index_moves = [a.to_square for a in moves]

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
        scrn.fill(GREY)
        update(scrn,board)

     
    # deactivates the pygame library
        if board.outcome() != None:
            print(board.outcome())
            print(board)
    pygame.quit()

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
