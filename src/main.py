from kivy.app import App
from kivy.clock import Clock

import gui


class SnakeApp(App):
    def build(self):
        self.snake_game = gui.SnakeGUI()
        Clock.schedule_interval(self.snake_game.update_game, 1.0 / 4.0)
        return self.snake_game


if __name__ == '__main__':
    sa = SnakeApp()
    sa.run()
