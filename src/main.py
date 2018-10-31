from kivy.app import App
from kivy.clock import Clock

import gui
import snake
from ai import ag
from ai import neuralnet as nn


class GameHandler:
    def __init__(self, print_board=False):
        self.print_board = print_board
        self.snake_game = snake.Game(max_moves=40, print=print_board)
        self.snake_pop = None
        self._configure_pop()
        self.generation = 0
        self.curr_indv = 0

    def _configure_pop(self):
        LAYERS_SIZE = [16, 3]
        INPUT_SIZE = 4
        neural_net_configs = [nn.ActivationFcn2(), nn.ActivationFcn(), LAYERS_SIZE, INPUT_SIZE]
        self.snake_pop = ag.Population(nn.NeuralFactory(*neural_net_configs), 15)

    def train_snakes_step(self):
        input_array = self.snake_game.board.get_features(normalize=True)
        print('Input array =', input_array)
        next_move = self.snake_pop.population[self.curr_indv].get_mov(input_array)
        print('Score =', self.snake_game.score)
        print('Next move =', next_move)
        print('G =', self.generation, '\n\n')

        is_alive = self.snake_game.run(next_move, False)

        if not is_alive:
            self.snake_pop.population[self.curr_indv].fit = self.snake_game.score
            self.curr_indv += 1
            if self.curr_indv == self.snake_pop.pop_size:
                self.curr_indv = 0
                self.generation += 1
                self.snake_pop.improve_pop()
            self.snake_game = snake.Game(max_moves=40, print=self.print_board)
            return False
        return True


class SnakeApp(App):

    def build(self):
        self.game_handler = GameHandler()
        self.gui = gui.SnakeGUI()

        self.gui.update_gui(self.game_handler.snake_game.board)

        update_freq_hz = 4.0
        # Clock.schedule_interval(self.update_game, 1 / update_freq_hz)
        Clock.schedule_interval(self.update_game, 0)
        return self.gui

    def update_game(self, dt):
        self.gui.update_gui(self.game_handler.snake_game.board)
        lived = self.game_handler.train_snakes_step()
        if not lived:
            self.gui.update_unit_measurements()
        self.gui.update_gui(self.game_handler.snake_game.board)


def no_gui_game():
    game_handler = GameHandler(print_board=True)
    while True:
        game_handler.train_snakes_step()


if __name__ == '__main__':
    USE_GUI = False

    if USE_GUI:
        sa = SnakeApp()
        gui.config_gui()
        sa.run()
    else:
        no_gui_game()
