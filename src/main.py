from kivy.app import App
from kivy.clock import Clock

import gui
import snake
from ai import ag
from ai import neuralnet as nn


class GameHandler:
    def __init__(self, print_board=False, indv=None, manual=False):
        self.manual = manual
        self.indv = indv
        self.print_board = print_board
        self.snake_game = snake.Game(max_moves=40, print=print_board, use_keyboard=manual)
        self.snake_pop = None
        self._configure_pop()
        self.generation = 0
        self.curr_indv = 0
        self.max_fit = 0

    def _configure_pop(self):
        if self.indv is None:
            LAYERS_SIZE = [16, 8, 3]
            INPUT_SIZE = 4
            neural_net_configs = [nn.ActivationFcn2(), nn.ActivationFcn(), LAYERS_SIZE, INPUT_SIZE]
            self.snake_pop = ag.Population(nn.NeuralFactory(*neural_net_configs), 150)
        else:
            self.snake_pop = ag.Population(factory=None, pop_size=1,
                                           individuals=[self.indv])

    def play_snake(self):
        input_array = self.snake_game.board.get_features(normalize=False)
        print('Angle =', input_array[3], '\n')
        is_alive = self.snake_game.run()
        if not is_alive:
            self.snake_game = snake.Game(max_moves=400, print=self.print_board,
                                         use_keyboard=self.manual)
            return False
        return True

    def watch_snake(self):
        input_array = self.snake_game.board.get_features(normalize=True)
        next_move = self.snake_pop.population[0].get_mov(input_array)
        is_alive = self.snake_game.run(next_move)
        if not is_alive:
            self.snake_game = snake.Game(max_moves=40, print=self.print_board)
            return False
        return True

    def train_snakes_step(self):
        input_array = self.snake_game.board.get_features(normalize=True)
        next_move = self.snake_pop.population[self.curr_indv].get_mov(input_array)

        is_alive = self.snake_game.run(next_move)

        if not is_alive:
            self.snake_pop.population[self.curr_indv].add_fit(self.snake_game.score)
            self.curr_indv += 1
            if self.curr_indv == self.snake_pop.pop_size:
                self.curr_indv = 0
                if self.generation == 500:
                    quit()
                self.generation += 1
                self.snake_pop.improve_pop()
                print('G =', self.generation)
                print('best fit =', self.snake_pop.population[0].get_fit())
                if self.snake_pop.population[0].get_fit() > self.max_fit:
                    self.max_fit = self.snake_pop.population[0].get_fit()
                    self.snake_pop.population[0].indv.save_neural_net('save.pkl')
                print('max fit =', self.max_fit, '\n')
            self.snake_game = snake.Game(max_moves=40, print=self.print_board)
            return False
        return True


class SnakeApp(App):

    def configure(self, saved_indv=None, manual=False):

        if saved_indv is not None:
            indv = ag.Individual(factory=None, indv=saved_indv)
            self.game_handler = GameHandler(print_board=False, indv=indv)
            self.play_game = self.game_handler.watch_snake
        elif manual:
            self.game_handler = GameHandler(print_board=False, indv=None, manual=True)
            self.play_game = self.game_handler.play_snake
        else:
            self.game_handler = GameHandler(print_board=False, indv=None)
            self.play_game = self.game_handler.train_snakes_step

    def build(self):
        self.gui = gui.SnakeGUI()

        update_freq_hz = 10
        Clock.schedule_interval(self.update_game, 1 / update_freq_hz)
        return self.gui

    def update_game(self, dt):
        self.gui.update_gui(self.game_handler.snake_game.board)
        lived = self.play_game()
        if not lived:
            self.gui.update_unit_measurements()
        self.gui.update_gui(self.game_handler.snake_game.board)


def no_gui_game():
    game_handler = GameHandler(print_board=True)
    while True:
        game_handler.train_snakes_step()


if __name__ == '__main__':
    USE_GUI = True
    USE_SAVE = True
    MANUAL = False

    if MANUAL:
        sa = SnakeApp()
        sa.configure(saved_indv=None, manual=True)
        sa.run()
    else:
        if USE_GUI:
            sa = SnakeApp()
            params = []
            if USE_SAVE:
                params.append(nn.load_neural_net('save.pkl'))
            sa.configure(*params)
            sa.run()
        else:
            no_gui_game()
