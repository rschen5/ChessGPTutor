import chess
import numpy as np


# Reference: https://www.chessprogramming.org/Simplified_Evaluation_Function

# Fixed piece points
points = {
    'P': 100,   # Pawn
    'N': 320,   # Knight
    'B': 330,   # Bishop
    'R': 500,   # Rook
    'Q': 900,   # Queen
    'K': 20000  # King
}

# Piece square tables (modified to match square coordinates in python-chess library)
#   top left: a1, top right: a8, bottom left: h1, bottom right: h8
pst = {
    # Pawn
    'P': np.array([[  0,   5,   5,   0,   5,  10,  50,   0],
                   [  0,  10,  -5,   0,   5,  10,  50,   0],
                   [  0,  10, -10,   0,  10,  20,  50,   0],
                   [  0, -20,   0,  20,  25,  30,  50,   0],
                   [  0, -20,   0,  20,  25,  30,  50,   0],
                   [  0,  10, -10,   0,  10,  20,  50,   0],
                   [  0,  10,  -5,   0,   5,  10,  50,   0],
                   [  0,   5,   5,   0,   5,  10,  50,   0]]),
    # Knight
    'N': np.array([[-50, -40, -30, -30, -30, -30, -40, -50],
                   [-40, -20,   5,   0,   5,   0, -20, -40],
                   [-30,   0,  10,  15,  15,  10,   0, -30],
                   [-30,   5,  15,  20,  20,  15,   0, -30],
                   [-30,   5,  15,  20,  20,  15,   0, -30],
                   [-30,   0,  10,  15,  15,  10,   0, -30],
                   [-40, -20,   5,   0,   5,   0, -20, -40],
                   [-50, -40, -30, -30, -30, -30, -40, -50]]),
    # Bishop
    'B': np.array([[-20, -10, -10, -10, -10, -10, -10, -20],
                   [-10,   5,  10,   0,   5,   0,   0, -10],
                   [-10,   0,  10,  10,   5,   5,   0, -10],
                   [-10,   0,  10,  10,  10,  10,   0, -10],
                   [-10,   0,  10,  10,  10,  10,   0, -10],
                   [-10,   0,  10,  10,   5,   5,   0, -10],
                   [-10,   5,  10,   0,   5,   0,   0, -10],
                   [-20, -10, -10, -10, -10, -10, -10, -20]]),
    # Rook
    'R': np.array([[ 0, -5, -5, -5, -5, -5,  5,  0],
                   [ 0,  0,  0,  0,  0,  0, 10,  0],
                   [ 0,  0,  0,  0,  0,  0, 10,  0],
                   [ 5,  0,  0,  0,  0,  0, 10,  0],
                   [ 5,  0,  0,  0,  0,  0, 10,  0],
                   [ 0,  0,  0,  0,  0,  0, 10,  0],
                   [ 0,  0,  0,  0,  0,  0, 10,  0],
                   [ 0, -5, -5, -5, -5, -5,  5,  0]]),
    # Queen
    'Q': np.array([[-20, -10, -10,   0,  -5, -10, -10, -20],
                   [-10,   0,   5,   0,   0,   0,   0, -10],
                   [-10,   5,   5,   5,   5,   5,   0, -10],
                   [ -5,   0,   5,   5,   5,   5,   0,  -5],
                   [ -5,   0,   5,   5,   5,   5,   0,  -5],
                   [-10,   0,   5,   5,   5,   5,   0, -10],
                   [-10,   0,   0,   0,   0,   0,   0, -10],
                   [-20, -10, -10,  -5,  -5, -10, -10, -20]]),
    # King - beginning and middle of game
    'K_middle': np.array([[ 20,  20, -10, -20, -30, -30, -30, -30],
                          [ 30,  20, -20, -30, -40, -40, -40, -40],
                          [ 10,   0, -20, -30, -40, -40, -40, -40],
                          [  0,   0, -20, -40, -50, -50, -50, -50],
                          [  0,   0, -20, -40, -50, -50, -50, -50],
                          [ 10,   0, -20, -30, -40, -40, -40, -40],
                          [ 30,  20, -20, -30, -40, -40, -40, -40],
                          [ 20,  20, -10, -20, -30, -30, -30, -30]]),
    # King - endgame
    'K_end': np.array([[-50, -30, -30, -30, -30, -30, -30, -50],
                       [-30, -30, -10, -10, -10, -10, -20, -40],
                       [-30,   0,  20,  30,  30,  20, -10, -30],
                       [-30,   0,  30,  40,  40,  30,   0, -20],
                       [-30,   0,  30,  40,  40,  30,   0, -20],
                       [-30,   0,  20,  30,  30,  20, -10, -30],
                       [-30, -30, -10, -10, -10, -10, -20, -40],
                       [-50, -30, -30, -30, -30, -30, -30, -50]])
 }

def is_endgame(board):
    """
    Pick which piece square table to use for king. End of game starts if:
        Both sides have no queens or
        Every side which has a queen has additionally no other pieces or one minorpiece maximum
    """
    fen_str = board.board_fen()
    if fen_str.lower().count('q') == 0:
        # Both sides have no queen
        return True
    else:
        # True if side doesn't have a queen
        white_check = not ('Q' in fen_str)
        black_check = not ('q' in fen_str)
        # Check if every side that has a queen has additionally
        # no other pieces or one minor (not king or queen) piece maximum
        if not white_check and sum(int(c.isupper()) for c in fen_str) <= 3:
            white_check = True
        if not black_check and sum(int(c.islower()) for c in fen_str) <= 3:
            black_check = True
        return white_check and black_check

def get_board_points(board):
    """
    Get fixed points for pieces on board + bonus points for piece positions (piece square tables)
    for each side then take the difference
    """
    points_diff = 0
    for square_num, piece in board.piece_map().items():
        symbol = piece.symbol()
        if symbol.islower():
            square_num = chess.square_mirror(square_num)
            pts_sign = -1
        else:
            pts_sign = 1
        
        square_coords = (chess.square_file(square_num), chess.square_rank(square_num))

        if symbol.upper() == "K":
            if is_endgame(board):
                symbol += "_end"
            else:
                symbol += "_middle"
        
        points_diff += pts_sign * pst[symbol.capitalize()][square_coords]

    return points_diff
