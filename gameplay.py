import chess
from chess import Move
import chess.svg
import openai
import numpy as np
from search import minimax, alpha_beta_fail_hard, alpha_beta_fail_soft
import random, re, json, time, os, sys
import pygame
import math


#initialise display

# blog for gui:
# CITATION:
# https://blog.devgenius.io/simple-interactive-chess-gui-in-python-c6d6569f7b6c
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
scrn = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
pygame.init()

#basic colours
WHITE = (255, 255, 255)
BLUE = (50, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND = (232, 181, 132)
BOARD_OUTLINE = (79, 40, 3)
DARK_SQUARE = (216, 140, 68)
LIGHT_SQUARE = (255, 204, 156)
LATEST_MOVE = (120,148,84)

#initialise chess board
b = chess.Board()
print("Setting up the board")

IMAGE_PATH = "./images/"

SQUARE_SIZE = 100
BOARD_OFFSET = 50
BORDER_OFFSET = 6

#load piece images
og_pieces = {'p': pygame.image.load(IMAGE_PATH + 'bP.png').convert_alpha(),
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

pieces = {k: pygame.transform.scale(v, (SQUARE_SIZE, SQUARE_SIZE)) for k, v in og_pieces.items()}


# def get_aspect_size(h):
#     w = h * 14.0 / 9.0
#     return w

# Board

# text wrap function:

# https://www.pygame.org/wiki/TextWrap

# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
def drawText(surface, text, color, rect, font, aa, bkg):
    rect = pygame.Rect(rect)
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word
        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], True, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return text

def update(scrn, board, suggested_move, chatGPT_text, human_black, highlight_squares = None, latest_move = False):
    '''
    updates the screen basis the board class
    '''
    scrn.fill(BACKGROUND)

    # create a font object.
    # 1st parameter is the font file
    # which is present in pygame.
    # 2nd parameter is size of the font
    font = pygame.font.Font('freesansbold.ttf', math.floor(32 * SCREEN_HEIGHT / 900))

    CHARACTER_LIST = ['A','B','C','D','E','F','G','H']
    NUMBER_LIST = ['8','7','6','5','4','3','2','1']

    # draw border
    pygame.draw.rect(scrn, BOARD_OUTLINE, pygame.Rect(BOARD_OFFSET - (SQUARE_SIZE / 100 * BORDER_OFFSET), BOARD_OFFSET - (SQUARE_SIZE / 100 * BORDER_OFFSET),
                                                      8*SQUARE_SIZE + (2 * SQUARE_SIZE / 100)*BORDER_OFFSET, 8*SQUARE_SIZE + (2 * SQUARE_SIZE / 100)*BORDER_OFFSET), 5)

    if human_black:
        board = board.transform(chess.flip_vertical).transform(chess.flip_horizontal)

    dark_square = True

    for i in range(64):
        # draw board squares
        if dark_square:
            pygame.draw.rect(scrn, DARK_SQUARE, pygame.Rect(BOARD_OFFSET+(i%8)*SQUARE_SIZE, BOARD_OFFSET+(7*SQUARE_SIZE)-(i//8)*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        else:
            pygame.draw.rect(scrn, LIGHT_SQUARE, pygame.Rect(BOARD_OFFSET+(i%8)*SQUARE_SIZE, BOARD_OFFSET+(7*SQUARE_SIZE)-(i//8)*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        if i % 8 != 7:
            dark_square = not dark_square

        # draw pieces
        piece = board.piece_at(i)
        if piece == None:
            pass
        else:
            scrn.blit(pieces[str(piece)], (BOARD_OFFSET+(i%8)*SQUARE_SIZE, BOARD_OFFSET+(7*SQUARE_SIZE)-(i//8)*SQUARE_SIZE))
    
    # draw letters and numbers
    for i in range(8):

        # create a text surface object,
        # on which text is drawn on it.
        if human_black:
            text_letter = font.render(CHARACTER_LIST[7-i], True, BLACK, BACKGROUND)
        else:
            text_letter = font.render(CHARACTER_LIST[i], True, BLACK, BACKGROUND)
        
        # create a rectangular object for the
        # text surface object
        textLetterRect = text_letter.get_rect()
        
        # set the center of the rectangular object.
        textLetterRect.center = (2*BOARD_OFFSET + i*SQUARE_SIZE, int(BOARD_OFFSET/2))

        scrn.blit(text_letter, textLetterRect)

        # create a text surface object,
        # on which text is drawn on it.
        if human_black:
            text_number = font.render(NUMBER_LIST[7-i], True, BLACK, BACKGROUND)
        else:
            text_number = font.render(NUMBER_LIST[i], True, BLACK, BACKGROUND)
        
        # create a rectangular object for the
        # text surface object
        textNumberRect = text_number.get_rect()
        
        # set the center of the rectangular object.
        textNumberRect.center = (int(BOARD_OFFSET/2), 2*BOARD_OFFSET + i*SQUARE_SIZE)

        scrn.blit(text_number, textNumberRect)

    # draw lines
    for i in range(7):
        i = i + 1
        pygame.draw.line(scrn, WHITE, (BOARD_OFFSET+0, BOARD_OFFSET+i*SQUARE_SIZE), (BOARD_OFFSET+(8*SQUARE_SIZE), BOARD_OFFSET+i*SQUARE_SIZE))
        pygame.draw.line(scrn, WHITE, (BOARD_OFFSET+i*SQUARE_SIZE, BOARD_OFFSET), (BOARD_OFFSET+i*SQUARE_SIZE, BOARD_OFFSET+(8*SQUARE_SIZE)))

    if highlight_squares != None:
        if latest_move:
            for square in highlight_squares:
                x = BOARD_OFFSET + SQUARE_SIZE * chess.square_file(square)
                y = BOARD_OFFSET + SQUARE_SIZE * (7 - chess.square_rank(square))
                pygame.draw.rect(scrn, LATEST_MOVE, pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE), 5)
        else:
            for square in highlight_squares:
                x = BOARD_OFFSET + SQUARE_SIZE * chess.square_file(square)
                y = BOARD_OFFSET + SQUARE_SIZE * (7 - chess.square_rank(square))
                pygame.draw.rect(scrn, BLUE, pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE), 5)

    # create a text surface object,
    # on which text is drawn on it.

    current_turn = who(board.turn).title()
    turn_text = "Current turn: {}".format(current_turn)
    text_letter = font.render(turn_text, True, BLACK, WHITE)
    
    # create a rectangular object for the
    # text surface object
    textLetterRect = text_letter.get_rect()
    
    # set the center of the rectangular object.
    textLetterRect.center = (2*BOARD_OFFSET+ 10*SQUARE_SIZE, int(BOARD_OFFSET/2))

    # scrn.blit(text_letter, textLetterRect)

    text = drawText(scrn, turn_text, BLACK,
                    pygame.Rect(2*BOARD_OFFSET + 8*SQUARE_SIZE, int(BOARD_OFFSET/2),
                                math.floor(SCREEN_WIDTH * 5 / 14), math.floor(SCREEN_HEIGHT / 9)),
                    font, True, None)
    print(text)

    if suggested_move != None and chatGPT_text != None:

        stockfish_text = "Stockfish suggestion: {}".format(suggested_move)

        text = drawText(scrn, stockfish_text, BLACK,
                        pygame.Rect(2*BOARD_OFFSET + 8*SQUARE_SIZE, int(BOARD_OFFSET/2) + BOARD_OFFSET,
                                    math.floor(SCREEN_WIDTH * 5 / 14), math.floor(SCREEN_HEIGHT / 9)),
                        font, True, None)
        print(text)

        intro_text = "ChatGPT's commentary:"

        text = drawText(scrn, intro_text, BLACK,
                        pygame.Rect(2*BOARD_OFFSET + 8*SQUARE_SIZE, int(BOARD_OFFSET/2) + BOARD_OFFSET*2,
                                    math.floor(SCREEN_WIDTH * 5 / 14), math.floor(SCREEN_HEIGHT / 9)),
                        font, True, None)
        print(text)

        chatGPT_text = "{}".format(chatGPT_text)

        text = drawText(scrn, chatGPT_text, BLACK,
                        pygame.Rect(2*BOARD_OFFSET + 8*SQUARE_SIZE, int(BOARD_OFFSET/2) + BOARD_OFFSET*3,
                                    math.floor(SCREEN_WIDTH * 5 / 14), math.floor(SCREEN_HEIGHT / 9 * 6)),
                        font, True, None)
        print(text)
    
    else:

        sleep_text = "Opponent is thinking..."

        text = drawText(scrn, sleep_text, BLACK,
                        pygame.Rect(2*BOARD_OFFSET + 8*SQUARE_SIZE, int(BOARD_OFFSET/2) + BOARD_OFFSET,
                                    math.floor(SCREEN_WIDTH * 5 / 14), math.floor(SCREEN_HEIGHT / 18)),
                        font, True, None)
        print(text)

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
    
    def get_move(self, board, opponent=False):
        if opponent:
            time.sleep(10)
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

    response_string = "{}".format(message['content'])

    if "not possible" in response_string or "illegal" in response_string or "not legal" in response_string or "not valid" in response_string or "invalid" in response_string:
        response_string = "Sorry, I'm having a hard time understanding this move and board."
        # # response_string = "I'm having a hard time understanding the board right now"
        # response = openai.ChatCompletion.create(
        # model='gpt-3.5-turbo',
        # messages=[
        #     {"role": "user", "content": try_again_message},
        #     {"role": "user", "content": current_board_string},

        # ],
        # max_tokens=100
        # )

        # message = response.choices[0]['message']
        # response_string = "{}".format(message['content'])

    print(response_string)

    return response_string


def play_game(player1, player2, human_black, board = None):
    global SCREEN_WIDTH, SCREEN_HEIGHT, SQUARE_SIZE, BOARD_OFFSET, scrn, pieces

    if board == None:
        board = chess.Board()
    game_moves = []

    resign = False

    print("=================================== START GAME ===================================")

    #name window
    pygame.display.set_caption('Chess')
    
    #variable to be used later
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
        if isinstance(player2, HumanPlayer):
            print_board(board, False)
        else:
            print_board(board, True)

        if board.turn == player1.color:
            current_player = player1
        else:
            current_player = player2

        if isinstance(current_player, HumanPlayer):

            move = current_player.tutor.get_move(board)
            try:
                chatGPT_text = get_ChatGPT_response(move, board.turn, str(board))
            except:
                chatGPT_text = "ChatGPT has received too many requests. Commentary will resume in a couple moves."
            suggested_move = "{}".format(move)

            update(scrn, board, suggested_move, chatGPT_text, human_black, highlight_squares, latest_move=True)

            move = None

            while move is None:
                for event in pygame.event.get():
                    # if event object type is QUIT
                    # then quitting the pygame
                    # and program both.
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        if isinstance(player1, HumanPlayer):
                            player1.tutor.close_engine()
                        if isinstance(player2, HumanPlayer):
                            player2.tutor.close_engine()
                        if isinstance(player1, StockfishPlayer):
                            player1.close_engine()
                        if isinstance(player2, StockfishPlayer):
                            player2.close_engine()
                        sys.exit(0)

                    elif event.type == pygame.VIDEORESIZE:
                        SQUARE_SIZE = SQUARE_SIZE * event.dict['size'][1] / SCREEN_HEIGHT
                        BOARD_OFFSET = SQUARE_SIZE / 2
                        # SCREEN_HEIGHT = event.dict['size'][1]
                        # SCREEN_WIDTH = get_aspect_size(SCREEN_HEIGHT)
                        SCREEN_WIDTH, SCREEN_HEIGHT = event.dict['size']
                        pieces = {k: pygame.transform.scale(v, (SQUARE_SIZE, SQUARE_SIZE)) for k, v in og_pieces.items()}
                        scrn = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
                        update(scrn, board, suggested_move, chatGPT_text, human_black, highlight_squares, latest_move=True)

                    # if mouse clicked
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        #get position of mouse
                        pos = pygame.mouse.get_pos()

                        #find which square was clicked and index of it
                        if human_black:
                            square = (7 - math.floor((pos[0]-BOARD_OFFSET)/SQUARE_SIZE), 7 - math.floor((pos[1]-BOARD_OFFSET)/SQUARE_SIZE))
                        else:
                            square = (math.floor((pos[0]-BOARD_OFFSET)/SQUARE_SIZE), math.floor((pos[1]-BOARD_OFFSET)/SQUARE_SIZE))
                        if square[0] < 0 or square[0] > 7 or square[1] < 0 or square[1] > 7:
                            continue

                        index = (7-square[1])*8+(square[0])
                        print(index)
                        
                        # if we are moving a piece
                        if index in index_moves: 
                            
                            move = moves[index_moves.index(index)]

                            print(move)
                            
                            #reset index and moves
                            index=None
                            index_moves = []
                            
                            
                        # show possible moves
                        else:
                            #check the square that is clicked
                            piece = board.piece_at(index)
                            #if empty pass
                            if piece == None:
                                
                                pass
                            else:
                                
                                #figure out what moves this piece can make
                                all_moves = list(board.legal_moves)
                                moves = []
                                highlight_squares = []
                                for m in all_moves:
                                    if m.from_square == index:
                                        
                                        moves.append(m)

                                        t = m.to_square
                                        if human_black:
                                            t = 63 - t

                                        #highlight squares it can move to
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
            move = current_player.get_move(board, opponent=True)
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
    # deactivates the pygame library
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
