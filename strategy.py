import quarto
import random
import numpy as np
from itertools import product
from copy import deepcopy

DEPTH = 400000#400000
dict_size = 0
collisions = 0
random_moves = 0
player = 0

# utility function to interface with the player
def get_depth_limit() -> bool:
    global dict_size
    return dict_size >= DEPTH

# utility function to interface with the player
def set_dict_size(x: int) -> None:
    global dict_size
    dict_size = x

def deSymmetrize(symmetry, value):
    x, y = value[0][0]
    piece = value[0][1]
    val = value[1]
    if symmetry == 'rot0':
        return ((x, y), piece), val
    elif symmetry == 'rot1':
        return ((3-y, 3-x), piece), val
    elif symmetry == 'rot2':
        return ((3-y, 3-x), piece), val
    elif symmetry == 'rot3':
        return ((y, 3-x), piece), val
    elif symmetry == 'Trot0':
        return ((y, x), piece), val
    elif symmetry == 'Trot1':
        return ((3-x, y), piece), val
    elif symmetry == 'Trot2':
        return ((3-y, 3-x), piece), val
    elif symmetry == 'Trot3':
        return ((x, 3-y), piece), val
    #TODO: glides (?)

# check state's symmetries generating all possible dictionary's key
def generate_keys(board, piece) -> list:
    possible_keys = []
    #reflections = {}
    for rot in range(0,4):
        sym = np.rot90(board,k=rot)
        possible_keys.append(((sym.tobytes(), piece), f'rot{rot}'))
        possible_keys.append(((sym.T.tobytes(), piece), f'Trot{rot}'))
        #if (rot == 1):
        #    reflections['horizontal'] = sym.T
        #if (rot == 3):
        #    reflections['vertical'] = sym.T

    #for axis in ['horizontal', 'vertical']:
    #    for distance in range(1, 4):
    #        glide_reflection = np.vstack((reflections[axis][distance:], reflections[axis][:distance]))
    #        possible_keys.append(((np.asarray(glide_reflection).tobytes(), piece), f'g_{axis[0]}_{distance}'))
    
    return possible_keys

# check if any key is already present in the dictionary
def check_dict(dict_of_states: dict, state: quarto.Quarto) -> tuple:
    board = state._Quarto__board #get_board_status()
    piece = state._Quarto__selected_piece_index #get_selected_piece()
    possible_keys = generate_keys(board, piece)

    for k, s in possible_keys:
        if k in dict_of_states:
            return k, s, True
    return (board.tobytes(), piece), None, False

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
    pieces_free = [p for p in list(range(0,16)) if p not in state._Quarto__board and p != state._Quarto__selected_piece_index]
    if pieces_free == []:
        return [(x, None) for x in positions] # we reached terminal position, so we have no spare piece to place
    return [x for x in product(positions, pieces_free)]

# check if the move is at least not bad
def check_move(coord, piece, state: quarto.Quarto) -> bool:
    state.place(coord[0], coord[1])
    if evaluate(state) != 0:
        # if is a win or a draw, it is not a bad move for sure
        return True
    else:
        state.select(piece)
        for pp in [(x,y) for x,y in product(list(range(0,4)), repeat=2) if state._Quarto__placeable(x,y)]:

            # check if the opponent can win with this piece
            state.place(pp[0], pp[1])
            if evaluate(state) != 0:
                return False
            state._Quarto__board[pp[0]][pp[1]] = -1 # undo the placing of the piece
        return True

# generate a possible move without exploring too much (just a little to avoid suicidal moves if possible)
def generate_fast(state: quarto.Quarto):
    tmp_state = deepcopy(state)
    for coord, piece in generate_possible_moves(state):
        if check_move(coord, piece, tmp_state):
            # take the first not suicidal move found
            return (coord, piece), 100
    return (coord, piece), 100

# check if there are three pieces in a row, column or diagonal
def check_three(state: quarto.Quarto) -> list:
    board = state._Quarto__board
    ret = [[],[],[],[]]
    # check row
    r = np.count_nonzero(board == -1, axis=1) # check how many void places there are in any row
    c = np.count_nonzero(board == -1, axis=0) # check how many void places there are in any column
    d = np.count_nonzero(np.diag(board == -1)) # check how many void places there are in the main diagonal
    d_i = np.count_nonzero(np.diag(np.fliplr(board == -1))) # check how many void places there are in the inverse diagonal
    ret[0] = np.where(r == 1)[0].tolist()
    ret[1] = np.where(c == 1)[0].tolist()
    ret[2] = np.where(d == 1)[0].tolist()
    ret[3] = np.where(d_i == 1)[0].tolist()
    return ret

# order moves in order to prioritize those who place the fourth piece in a line
def order_moves(moves: list, three: list):
    vip = []
    not_vip = []
    for m, _ in moves:
        if m[0] in three[0] or m[1] in three[1] or (m[0]==m[1] and three[2] != []) or (m[0] == 3-m[1] and three[3] != []):
            vip.append((m,_))
        else:
            not_vip.append((m,_))
    return [*vip, *not_vip], vip

def minMax(state: quarto.Quarto, dict_of_states: dict, player: int):
    global dict_size, random_moves

    # check if the game is finished
    val = evaluate(state)
    if val != 0:
        return None, val

    # depth checking
    if dict_size >= DEPTH:
        k, s, f = check_dict(dict_of_states, state)
        if not f:
            random_moves += 1
            return generate_fast(state)
        else:
            return deSymmetrize(s, max(dict_of_states[k], key=lambda x: x[1]))

    result = list()
    _key, s, found = check_dict(dict_of_states, state)
    if not found:
        dict_of_states[_key] = list()
        dict_size += 1

        three = check_three(state)
        moves, vip = order_moves(generate_possible_moves(state),three)
        tmp_state = deepcopy(state)

        for m in vip: # rapid scan of possible suicidal moves
            if not check_move(m[0],m[1], tmp_state):
                moves.remove(m)
                dict_of_states[_key].append((m,-100))

        for ply in moves:
            dict_of_states[_key].append((ply,-100))
            # Trying the move and recursively calling the min max on the new state
            tmp_state = deepcopy(state)
            tmp_state.place(ply[0][0],ply[0][1])
            if ply[1] != None: #we check if we have spare piece to place
                tmp_state.select(ply[1])
            _ , val = minMax(tmp_state, dict_of_states, 1-player)
            result.append((ply, -val))

            # alpha beta pruning, if dict_size is increasing, we accept also a draft result -> maybe not right
            if -val == 100 or (-val == 50 and dict_size >= DEPTH):
                dict_of_states[_key] = [(ply, -val)]
                break
            
    else:
        global collisions
        collisions += 1
        # Already explored state
        return deSymmetrize(s, max(dict_of_states[_key], key=lambda x: x[1]))

    return max(result, key=lambda x: x[1])
