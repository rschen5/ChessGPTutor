from evaluation import get_board_points


def minimax(board, depth, maximizing_player, moves_list = ()):
    if depth == 0 or len(list(board.legal_moves)) == 0:
        return moves_list, get_board_points(board)

    if maximizing_player:
        value = float('-inf')
        final_moves_list = ()

        for move in list(board.legal_moves):
            board_copy = board.copy()
            board_copy.push(move)
            new_moves_list = moves_list + (move.uci(),)

            best_move, move_points = minimax(board_copy, depth - 1, not maximizing_player, new_moves_list)
            if move_points > value:
                final_moves_list = best_move
                value = move_points

        return final_moves_list, value

    else:
        value = float('inf')
        final_moves_list = ()

        for move in list(board.legal_moves):
            board_copy = board.copy()
            board_copy.push(move)
            new_moves_list = moves_list + (move.uci(),)

            best_move, move_points = minimax(board_copy, depth - 1, not maximizing_player, new_moves_list)
            if move_points < value:
                final_moves_list = best_move
                value = move_points

        return final_moves_list, value


def alpha_beta_fail_hard(board, depth, maximizing_player, alpha = float('-inf'), beta = float('inf'), moves_list = ()):
    if depth == 0 or len(list(board.legal_moves)) == 0:
        return moves_list, get_board_points(board)

    if maximizing_player:
        value = float('-inf')
        final_moves_list = ()

        for move in list(board.legal_moves):
            board_copy = board.copy()
            board_copy.push(move)
            new_moves_list = moves_list + (move.uci(),)

            best_move, move_points = alpha_beta_fail_hard(board_copy, depth - 1, not maximizing_player, alpha, beta, new_moves_list)
            if move_points > value:
                final_moves_list = best_move
                value = move_points

            if value > beta:
                break
            alpha = max(alpha, value)

        return final_moves_list, value

    else:
        value = float('inf')
        final_moves_list = ()

        for move in list(board.legal_moves):
            board_copy = board.copy()
            board_copy.push(move)
            new_moves_list = moves_list + (move.uci(),)

            best_move, move_points = alpha_beta_fail_hard(board_copy, depth - 1, not maximizing_player, alpha, beta, new_moves_list)
            if move_points < value:
                final_moves_list = best_move
                value = move_points

            if value < alpha:
                break
            beta = min(beta, value)

        return final_moves_list, value


def alpha_beta_fail_soft(board, depth, maximizing_player, alpha = float('-inf'), beta = float('inf'), moves_list = ()):
    if depth == 0 or len(list(board.legal_moves)) == 0:
        return moves_list, get_board_points(board)

    if maximizing_player:
        value = float('-inf')
        final_moves_list = ()

        for move in list(board.legal_moves):
            board_copy = board.copy()
            board_copy.push(move)
            new_moves_list = moves_list + (move.uci(),)

            best_move, move_points = alpha_beta_fail_soft(board_copy, depth - 1, not maximizing_player, alpha, beta, new_moves_list)
            if move_points > value:
                final_moves_list = best_move
                value = move_points

            alpha = max(alpha, value)
            if value >= beta:
                break

        return final_moves_list, value

    else:
        value = float('inf')
        final_moves_list = ()

        for move in list(board.legal_moves):
            board_copy = board.copy()
            board_copy.push(move)
            new_moves_list = moves_list + (move.uci(),)

            best_move, move_points = alpha_beta_fail_soft(board_copy, depth - 1, not maximizing_player, alpha, beta, new_moves_list)
            if move_points < value:
                final_moves_list = best_move
                value = move_points

            beta = min(beta, value)
            if value <= alpha:
                break

        return final_moves_list, value
