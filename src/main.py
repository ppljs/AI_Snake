from kivy.app import App
from kivy.clock import Clock

import gui
import snake
from ai import ag
from ai import neuralnet as nn
    

class SnakeApp(App):
    
    def build(self):
        LAYERS_SIZE = [6, 6, 3]
        INPUT_SIZE = 4
        self.gui = gui.SnakeGUI()
        self.game = snake.Game()
        self.neural_net_configs = [nn.ActivationFcn(), nn.ActivationFcn(), LAYERS_SIZE, INPUT_SIZE]
        self.snake_pop = ag.Population(nn.NeuralFactory(*self.neural_net_configs), 15)

        self.gui.update_gui(self.game.board)
        
        Clock.schedule_interval(self.update_game, 0.5)

        return self.gui

    def update_game(self, dt):
        #for ind in self.snake_pop.population:
            #while True:
        input_array = self.game.board.get_features()
        print('Input Array', input_array)
        #next_move = ind.predict(input_array)

        is_alive = self.game.run(None, True)

        self.gui.update_gui(self.game.board)
        if not is_alive:
            quit()

if __name__ == '__main__':
    sa = SnakeApp()
    gui.config_gui()
    sa.run()
