from src.evaluation import get_board_points


def alpha_beta_fail_hard(board, depth, maximizing_player, alpha = float('-inf'), beta = float('inf'), moves_list = ()):
    """
    Alpha-beta pruning, fail-hard version.

    Parameters
    ----------
    board : chess.Board
        Chess board representing the current board state.
    depth : int
        The maximum search depth for alpha-beta.
    maximizing_player : bool
        Whether or not the current tree depth aims to maximize or minimize the returned heuristic value.
    alpha : float, default=float('-inf')
        The minimum score that the maximizing player is assured of.
    beta : float, default=float('inf')
        The maximum score that the minimizing player is assured of.
    moves_list : tuple of str, default=()
        List of chess moves taken to get to the current board state.

    Returns
    -------
    tuple of str
        List of chess moves to get to the board state corresponding to the returned heuristic value.
    int
        Final heuristic value.
    """
    # Maximum search depth reached or no possible moves for current board state
    if depth == 0 or len(list(board.legal_moves)) == 0:
        return moves_list, get_board_points(board)

    # Maximizing level
    if maximizing_player:
        value = float('-inf')
        final_moves_list = ()

        # Iterate through all possible moves from current board state
        for move in list(board.legal_moves):
            board_copy = board.copy()
            board_copy.push(move)
            new_moves_list = moves_list + (move.uci(),)

            # Get move list and minimized heuristic value for board state resulting from possible move
            best_move, move_points = alpha_beta_fail_hard(board_copy, depth - 1, not maximizing_player, alpha, beta, new_moves_list)
            if move_points > value:
                final_moves_list = best_move
                value = move_points

            # Beta cutoff
            if value > beta:
                break

            # Update alpha
            alpha = max(alpha, value)

        return final_moves_list, value

    # Minimizing level
    else:
        value = float('inf')
        final_moves_list = ()

        # Iterate through all possible moves from current board state
        for move in list(board.legal_moves):
            board_copy = board.copy()
            board_copy.push(move)
            new_moves_list = moves_list + (move.uci(),)

            # Get move list and maximized heuristic value for board state resulting from possible move
            best_move, move_points = alpha_beta_fail_hard(board_copy, depth - 1, not maximizing_player, alpha, beta, new_moves_list)
            if move_points < value:
                final_moves_list = best_move
                value = move_points

            # Alpha cutoff
            if value < alpha:
                break

            # Update beta
            beta = min(beta, value)

        return final_moves_list, value


def alpha_beta_fail_soft(board, depth, maximizing_player, alpha = float('-inf'), beta = float('inf'), moves_list = ()):
    """
    Alpha-beta pruning, fail-soft version.

    Parameters
    ----------
    board : chess.Board
        Chess board representing the current board state.
    depth : int
        The maximum search depth for alpha-beta.
    maximizing_player : bool
        Whether or not the current tree depth aims to maximize or minimize the returned heuristic value.
    alpha : float, default=float('-inf')
        The minimum score that the maximizing player is assured of.
    beta : float, default=float('inf')
        The maximum score that the minimizing player is assured of.
    moves_list : tuple of str, default=()
        List of chess moves taken to get to the current board state.

    Returns
    -------
    tuple of str
        List of chess moves to get to the board state corresponding to the returned heuristic value.
    int
        Final heuristic value.
    """
    # Maximum search depth reached or no possible moves for current board state
    if depth == 0 or len(list(board.legal_moves)) == 0:
        return moves_list, get_board_points(board)

    # Maximizing level
    if maximizing_player:
        value = float('-inf')
        final_moves_list = ()

        # Iterate through all possible moves from current board state
        for move in list(board.legal_moves):
            board_copy = board.copy()
            board_copy.push(move)
            new_moves_list = moves_list + (move.uci(),)

            # Get move list and minimized heuristic value for board state resulting from possible move
            best_move, move_points = alpha_beta_fail_soft(board_copy, depth - 1, not maximizing_player, alpha, beta, new_moves_list)
            if move_points > value:
                final_moves_list = best_move
                value = move_points

            # Update alpha
            alpha = max(alpha, value)

            # Beta cutoff
            if value >= beta:
                break

        return final_moves_list, value

    # Minimizing level
    else:
        value = float('inf')
        final_moves_list = ()

        # Iterate through all possible moves from current board state
        for move in list(board.legal_moves):
            board_copy = board.copy()
            board_copy.push(move)
            new_moves_list = moves_list + (move.uci(),)

            # Get move list and maximized heuristic value for board state resulting from possible move
            best_move, move_points = alpha_beta_fail_soft(board_copy, depth - 1, not maximizing_player, alpha, beta, new_moves_list)
            if move_points < value:
                final_moves_list = best_move
                value = move_points

            # Update beta
            beta = min(beta, value)

            # Alpha cutoff
            if value <= alpha:
                break

        return final_moves_list, value
