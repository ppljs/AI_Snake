from kivy.app import App
from kivy.clock import Clock

import gui
import snake
from ai import ag
from ai import neuralnet as nn


class GameHandler:
    def __init__(self):
        self.snake_game = snake.Game()
        self.snake_pop = None
        self._configure_pop()

        self.generation = 0
        self.curr_indv = 0

    def _configure_pop(self):
        LAYERS_SIZE = [6, 6, 3]
        INPUT_SIZE = 4
        neural_net_configs = [nn.ActivationFcn(), nn.ActivationFcn(), LAYERS_SIZE, INPUT_SIZE]
        self.snake_pop = ag.Population(nn.NeuralFactory(*neural_net_configs), 15)

    def train_snakes_step(self):

        input_array = self.snake_game.board.get_features()
        print('Input array =', input_array)
        next_move = self.snake_pop.population[self.curr_indv].get_mov(input_array)
        print('Next move =', next_move, '\n\n')
        # have to calculate the fitness of the predicted mov here
        is_alive = self.snake_game.run(next_move, False)

        if not is_alive:
            self.curr_indv += 1
            if self.curr_indv == self.snake_pop.pop_size:
                self.curr_indv = 0
                self.generation += 1
                # Probably some other actions need to go here
            self.snake_game = snake.Game()


class SnakeApp(App):

    def build(self):
        self.game_handler = GameHandler()
        self.gui = gui.SnakeGUI()

        self.gui.update_gui(self.game_handler.snake_game.board)

        update_freq_hz = 2.0
        Clock.schedule_interval(self.update_game, 1 / update_freq_hz)

        return self.gui

    def update_game(self, dt):
        self.gui.update_gui(self.game_handler.snake_game.board)
        self.game_handler.train_snakes_step()
        self.gui.update_gui(self.game_handler.snake_game.board)


if __name__ == '__main__':
    sa = SnakeApp()
    gui.config_gui()
    sa.run()
