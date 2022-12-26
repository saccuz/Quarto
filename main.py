# Free for personal or classroom use; see 'LICENSE.md' for details.
# https://github.com/squillero/computational-intelligence

import logging
import argparse
import random
import quarto

class examPlayer(quarto.Player):
    """ Our player for the exam """
    
    import strategy

    dict_of_states = dict() # dictionary to store the possible states
    moves_counter = 0 # duration of the not searching minMax
    
    def __init__(self, quarto: quarto.Quarto) -> None:
        super().__init__(quarto)
    
    # interface to the minMax function 
    def game_control(self):
        if self.strategy.get_depth_limit(): # control to limit the depth search
            if self.moves_counter == 3:
                self.strategy.set_dict_size(0)
                self.moves_counter = 0
            self.moves_counter += 1
            
        ply, _  = self.strategy.minMax(quarto, self.dict_of_states)
        return ply

    def choose_piece(self) -> int:
        x = self.game_control()
        return x[1]

    def place_piece(self) -> tuple[int, int]:
        x = self.game_control()
        return x[0]

class RandomPlayer(quarto.Player):
    """Random player"""

    def __init__(self, quarto: quarto.Quarto) -> None:
        super().__init__(quarto)

    def choose_piece(self) -> int:
        return random.randint(0, 15)

    def place_piece(self) -> tuple[int, int]:
        return random.randint(0, 3), random.randint(0, 3)


def main():
    game = quarto.Quarto()
    game.set_players((RandomPlayer(game), RandomPlayer(game)))
    winner = game.run()
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