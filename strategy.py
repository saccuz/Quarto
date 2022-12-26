import quarto
import random
import numpy as np
from itertools import product

def generate_keys(state: quarto.Quarto) -> list:
    tmp_b = state.get_board_status()
    tmp_piece = state.get_selected_piece()
    possible_keys = []
    for rot in range(0,4):
        sym = np.rot90(tmp_b,k=rot)
        possible_keys.append((str(sym), tmp_piece)) #str is used to make ndarray (return of get_board_status) hashable
        possible_keys.append((str(sym.T), tmp_piece))
    return possible_keys

def check_dict(dict_of_states: dict, state: quarto.Quarto) -> tuple:
    possible_keys = generate_keys(state)
    for k in possible_keys:
        if k in dict_of_states:
            return k
    return (None,None)

def evaluate(state: quarto.Quarto) -> int:
    if state.check_winner() != -1:
        return -100
    elif state.check_finished(): # it's a draw (no one wins(==-1) and the game is finished)
        return -50
    else:
        return 0

def generate_possible_moves(state: quarto.Quarto):
    positions = [(x,y) for x,y in product(list(range(0,4)), repeat=2) if state.__placeable(x,y)]
    piecesFree = [p for p in list(range(0,16)) if p not in state.__board]
    