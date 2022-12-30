import quarto
import random
import numpy as np
from itertools import product
from copy import deepcopy

DEPTH = 500000
dict_size = 0

# utility function to interface with the player
def get_depth_limit() -> bool:
    global dict_size
    return dict_size >= DEPTH

# utility function to interface with the player
def set_dict_size(x: int) -> None:
    global dict_size
    dict_size = x

# check state's symmetries generating all possible dictionary's key
def generate_keys(board, piece) -> list:
    possible_keys = []
    for rot in range(0,4):
        sym = np.rot90(board,k=rot)
        possible_keys.append((str(sym), piece)) #str is used to make ndarray (return of get_board_status) hashable
        possible_keys.append((str(sym.T), piece))
    return possible_keys

# check if any key is already present in the dictionary
def check_dict(dict_of_states: dict, state: quarto.Quarto) -> tuple:
    board = state.get_board_status()
    piece = state.get_selected_piece()
    possible_keys = generate_keys(board, piece)

    for k in possible_keys:
        if k in dict_of_states:
            return k, True
    return (str(board),piece), False

# stop condition
def evaluate(state: quarto.Quarto) -> int:
    if state.check_winner() != -1:
        return -100
    elif state.check_finished(): # it's a draw (no one wins(==-1) and the game is finished)
        return -50
    else:
        return 0

# generate every possible piece placement and piece selection
def generate_possible_moves(state: quarto.Quarto):
    positions = [(x,y) for x,y in product(list(range(0,4)), repeat=2) if state._Quarto__placeable(x,y)]
    pieces_free = [p for p in list(range(0,16)) if p not in state._Quarto__board and p != state.get_selected_piece()]
    return [x for x in product(positions, pieces_free)]
    
def minMax(state: quarto.Quarto, dict_of_states: dict):
    global dict_size
    # check if the game is finished
    val = evaluate(state)
    if val != 0:
        return None, val

    # depth checking
    if dict_size >= DEPTH:
        k, f = check_dict(dict_of_states, state)
        if not f:
            return ((random.randint(0,3), random.randint(0,3)),random.randint(0,15)),100
        else:
            return max(dict_of_states[k], key=lambda x: x[1])

    result = list()
    _key, found = check_dict(dict_of_states, state)
    if not found:
        dict_of_states[_key] = list()
        dict_size += 1

        for ply in generate_possible_moves(state):
            dict_of_states[_key].append((ply,val))
            # Trying the move and recursively calling the min max on the new state
            tmp_state = deepcopy(state)
            tmp_state.place(ply[0][0],ply[0][1])
            tmp_state.select(ply[1])
            _ , val = minMax(tmp_state, dict_of_states)
            result.append((ply, -val))

            # alpha beta pruning, if dict_size is increasing, we accept also a draft result -> maybe not right
            if -val == 100 or (-val == 50 and dict_size > DEPTH):
                dict_of_states[_key] = [(ply, -val)]
                break
    else:
        # Already explored state
        return max(dict_of_states[_key], key=lambda x: x[1])
    
    return max(result, key=lambda x: x[1])