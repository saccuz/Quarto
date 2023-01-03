# Free for personal or classroom use; see 'LICENSE.md' for details.
# https://github.com/squillero/computational-intelligence

import logging
import argparse
import random
import quarto

collisions = 0
len_dict = 0
random_moves = 0


class ExamPlayer(quarto.Player):
    """ Our player for the exam """
    
    import strategy

    passed = 0
    move = tuple()

    dict_of_states = dict() # dictionary to store the possible states
    moves_counter = 0 # duration of the not searching minMax
    __quarto = None
    
    def __init__(self, quarto: quarto.Quarto) -> None:
        super().__init__(quarto)
        self.__quarto = quarto
    
    # interface to the minMax function 
    def game_control(self):
        if self.strategy.get_depth_limit(): # control to limit the depth search
            if self.moves_counter == 2:
                self.strategy.set_dict_size(0)
                self.moves_counter = 0
            else:
                self.moves_counter += 1
            
        ply, _  = self.strategy.minMax(self.__quarto, self.dict_of_states)
        return ply

    def choose_piece(self) -> int:        
        if self.__quarto.get_selected_piece() == -1:
            return random.randint(0, 15)

        if self.passed == 0:
            self.move = self.game_control()
            self.passed = 1
            return self.move[1]
        else:
            self.passed = 0
            return self.move[1]

    def place_piece(self) -> tuple:
        global collisions, len_dict, random_moves
        collisions = self.strategy.collisions
        len_dict = len(self.dict_of_states)
        random_moves = self.strategy.random_moves

        if self.passed == 0:
            self.move = self.game_control()
            self.passed = 1
            return self.move[0]
        else:
            self.passed = 0
            return self.move[0]


class RandomPlayer(quarto.Player):
    """Random player"""

    def __init__(self, quarto: quarto.Quarto) -> None:
        super().__init__(quarto)

    def choose_piece(self) -> int:
        return random.randint(0, 15)

    def place_piece(self) -> tuple:
        return random.randint(0, 3), random.randint(0, 3)

class WePlayer(quarto.Player):
    """Us as a player"""

    def __init__(self, quarto: quarto.Quarto) -> None:
        super().__init__(quarto)

    def choose_piece(self) -> int:
        value = input("Which did he chose? \n(0-15): ")
        print(f'You entered {value}')
        return int(value)

    def place_piece(self) -> tuple:
        print("Where did he put it?")
        value1 = input("X (0-3): ")
        value2 = input("Y (0-3): ")
        print(f'You entered {value1, value2}')
        return int(value1), int(value2)

def main():
    game = quarto.Quarto()
    game.set_players((ExamPlayer(game), WePlayer(game)))
    winner = game.run()
    logging.warning(f"Collisions: {collisions}")   
    logging.warning(f"Length of dict: {len_dict}")   
    logging.warning(f"Random moves: {random_moves}")   
    logging.warning(f"main: Winner: player {winner}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', default=0, help='increase log verbosity')
    parser.add_argument('-d',
                        '--debug',
                        action='store_const',
                        dest='verbose',
                        const=2,
                        help='log debug messages (same as -vv)')
    args = parser.parse_args()

    if args.verbose == 0:
        logging.getLogger().setLevel(level=logging.WARNING)
    elif args.verbose == 1:
        logging.getLogger().setLevel(level=logging.INFO)
    elif args.verbose == 2:
        logging.getLogger().setLevel(level=logging.DEBUG)

    main()
